#!/usr/bin/env python3
"""
Database Migration Planning Tools
===============================

Comprehensive tools for planning and managing database migrations, including
schema comparison, migration script generation, rollback planning, and 
migration execution tracking.

Features:
- Schema difference analysis
- Migration script generation
- Rollback script creation
- Migration dependency management
- Pre-migration validation
- Migration execution tracking
- Risk assessment and impact analysis
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from collections import defaultdict, OrderedDict
import re


class MigrationDatabase:
    """Manages migration history and tracking database."""
    
    def __init__(self, db_path: str = "migrations.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the migration database with required tables."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Migration plans
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    source_database TEXT NOT NULL,
                    target_database TEXT,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'draft', -- 'draft', 'validated', 'approved', 'executed', 'failed', 'cancelled'
                    description TEXT,
                    migration_data TEXT, -- JSON with migration details
                    risk_level TEXT, -- 'low', 'medium', 'high', 'critical'
                    estimated_duration INTEGER, -- in minutes
                    dependencies TEXT -- JSON array of dependent migrations
                )
            """)
            
            # Migration execution history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER,
                    execution_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'rolled_back'
                    executed_by TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    execution_log TEXT,
                    rollback_required BOOLEAN DEFAULT 0,
                    rollback_timestamp DATETIME,
                    rollback_log TEXT,
                    FOREIGN KEY (plan_id) REFERENCES migration_plans (id)
                )
            """)
            
            # Migration validation results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER,
                    validation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    validation_type TEXT, -- 'syntax', 'dependency', 'impact', 'compatibility'
                    status TEXT, -- 'pass', 'fail', 'warning'
                    message TEXT,
                    details TEXT, -- JSON with detailed validation info
                    FOREIGN KEY (plan_id) REFERENCES migration_plans (id)
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def save_migration_plan(self, name: str, source_db: str, target_db: str, 
                           description: str, migration_data: Dict, risk_level: str,
                           estimated_duration: int, dependencies: List[str]) -> int:
        """Save a migration plan."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Check if plan exists
            cursor.execute("SELECT id FROM migration_plans WHERE name = ?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing plan
                cursor.execute("""
                    UPDATE migration_plans SET 
                        source_database = ?, target_database = ?, description = ?,
                        migration_data = ?, risk_level = ?, estimated_duration = ?,
                        dependencies = ?, updated_timestamp = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (source_db, target_db, description, json.dumps(migration_data),
                     risk_level, estimated_duration, json.dumps(dependencies), name))
                plan_id = existing[0]
            else:
                # Create new plan
                cursor.execute("""
                    INSERT INTO migration_plans 
                    (name, source_database, target_database, description, migration_data,
                     risk_level, estimated_duration, dependencies)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, source_db, target_db, description, json.dumps(migration_data),
                     risk_level, estimated_duration, json.dumps(dependencies)))
                plan_id = cursor.lastrowid
            
            conn.commit()
            return plan_id
        finally:
            conn.close()
    
    def get_migration_plans(self) -> List[Dict]:
        """Get all migration plans."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM migration_plans ORDER BY updated_timestamp DESC
            """)
            
            columns = [desc[0] for desc in cursor.description]
            plans = []
            for row in cursor.fetchall():
                plan = dict(zip(columns, row))
                plan['migration_data'] = json.loads(plan['migration_data']) if plan['migration_data'] else {}
                plan['dependencies'] = json.loads(plan['dependencies']) if plan['dependencies'] else []
                plans.append(plan)
            return plans
        finally:
            conn.close()
    
    def log_migration_execution(self, plan_id: int, status: str, executed_by: str,
                              execution_log: str = None) -> int:
        """Log migration execution."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO migration_executions 
                (plan_id, status, executed_by, start_time, execution_log)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (plan_id, status, executed_by, execution_log))
            
            execution_id = cursor.lastrowid
            conn.commit()
            return execution_id
        finally:
            conn.close()


class SchemaAnalyzer:
    """Analyzes schema differences and generates migration plans."""
    
    def __init__(self):
        self.supported_operations = {
            'CREATE_TABLE', 'DROP_TABLE', 'ALTER_TABLE',
            'ADD_COLUMN', 'DROP_COLUMN', 'ALTER_COLUMN',
            'CREATE_INDEX', 'DROP_INDEX',
            'CREATE_CONSTRAINT', 'DROP_CONSTRAINT',
            'CREATE_VIEW', 'DROP_VIEW', 'ALTER_VIEW',
            'CREATE_PROCEDURE', 'DROP_PROCEDURE', 'ALTER_PROCEDURE',
            'CREATE_FUNCTION', 'DROP_FUNCTION', 'ALTER_FUNCTION'
        }
    
    def analyze_schema_differences(self, source_schema: Dict, target_schema: Dict) -> Dict[str, List]:
        """Analyze differences between source and target schemas."""
        differences = {
            'tables': self._analyze_table_differences(source_schema, target_schema),
            'views': self._analyze_view_differences(source_schema, target_schema),
            'procedures': self._analyze_procedure_differences(source_schema, target_schema),
            'functions': self._analyze_function_differences(source_schema, target_schema),
            'indexes': self._analyze_index_differences(source_schema, target_schema)
        }
        
        return differences
    
    def _analyze_table_differences(self, source_schema: Dict, target_schema: Dict) -> List[Dict]:
        """Analyze table differences."""
        differences = []
        
        source_tables = {t['table_name']: t for t in source_schema.get('tables', [])}
        target_tables = {t['table_name']: t for t in target_schema.get('tables', [])}
        
        # Tables only in target (need to create)
        for table_name in target_tables:
            if table_name not in source_tables:
                differences.append({
                    'operation': 'CREATE_TABLE',
                    'object_name': table_name,
                    'object_type': 'TABLE',
                    'details': target_tables[table_name],
                    'risk_level': 'low',
                    'rollback_operation': 'DROP_TABLE'
                })
        
        # Tables only in source (need to drop)
        for table_name in source_tables:
            if table_name not in target_tables:
                differences.append({
                    'operation': 'DROP_TABLE',
                    'object_name': table_name,
                    'object_type': 'TABLE',
                    'details': source_tables[table_name],
                    'risk_level': 'high',
                    'rollback_operation': 'CREATE_TABLE'
                })
        
        # Tables in both (need to compare structure)
        for table_name in source_tables:
            if table_name in target_tables:
                table_diffs = self._analyze_table_structure_differences(
                    source_tables[table_name], target_tables[table_name]
                )
                differences.extend(table_diffs)
        
        return differences
    
    def _analyze_table_structure_differences(self, source_table: Dict, target_table: Dict) -> List[Dict]:
        """Analyze differences in table structure."""
        differences = []
        table_name = target_table['table_name']
        
        source_columns = {c['column_name']: c for c in source_table.get('columns', [])}
        target_columns = {c['column_name']: c for c in target_table.get('columns', [])}
        
        # Columns to add
        for col_name in target_columns:
            if col_name not in source_columns:
                differences.append({
                    'operation': 'ADD_COLUMN',
                    'object_name': f"{table_name}.{col_name}",
                    'object_type': 'COLUMN',
                    'details': {
                        'table': table_name,
                        'column': target_columns[col_name]
                    },
                    'risk_level': self._assess_column_add_risk(target_columns[col_name]),
                    'rollback_operation': 'DROP_COLUMN'
                })
        
        # Columns to drop
        for col_name in source_columns:
            if col_name not in target_columns:
                differences.append({
                    'operation': 'DROP_COLUMN',
                    'object_name': f"{table_name}.{col_name}",
                    'object_type': 'COLUMN',
                    'details': {
                        'table': table_name,
                        'column': source_columns[col_name]
                    },
                    'risk_level': 'high',
                    'rollback_operation': 'ADD_COLUMN'
                })
        
        # Columns to alter
        for col_name in source_columns:
            if col_name in target_columns:
                if self._columns_differ(source_columns[col_name], target_columns[col_name]):
                    differences.append({
                        'operation': 'ALTER_COLUMN',
                        'object_name': f"{table_name}.{col_name}",
                        'object_type': 'COLUMN',
                        'details': {
                            'table': table_name,
                            'source_column': source_columns[col_name],
                            'target_column': target_columns[col_name]
                        },
                        'risk_level': self._assess_column_alter_risk(
                            source_columns[col_name], target_columns[col_name]
                        ),
                        'rollback_operation': 'ALTER_COLUMN'
                    })
        
        return differences
    
    def _columns_differ(self, source_col: Dict, target_col: Dict) -> bool:
        """Check if two columns have differences."""
        compare_fields = ['data_type', 'max_length', 'precision', 'scale', 'is_nullable', 'default_value']
        
        for field in compare_fields:
            if source_col.get(field) != target_col.get(field):
                return True
        return False
    
    def _assess_column_add_risk(self, column: Dict) -> str:
        """Assess risk level for adding a column."""
        if column.get('is_nullable') == 'NO' and not column.get('default_value'):
            return 'high'  # Adding non-nullable column without default to existing table
        return 'low'
    
    def _assess_column_alter_risk(self, source_col: Dict, target_col: Dict) -> str:
        """Assess risk level for altering a column."""
        # Data type changes are high risk
        if source_col.get('data_type') != target_col.get('data_type'):
            return 'critical'
        
        # Making column not nullable is high risk
        if source_col.get('is_nullable') == 'YES' and target_col.get('is_nullable') == 'NO':
            return 'high'
        
        # Reducing column size is medium risk
        if (source_col.get('max_length', 0) > target_col.get('max_length', 0) and 
            target_col.get('max_length', 0) > 0):
            return 'medium'
        
        return 'low'
    
    def _analyze_view_differences(self, source_schema: Dict, target_schema: Dict) -> List[Dict]:
        """Analyze view differences."""
        differences = []
        
        source_views = {v['view_name']: v for v in source_schema.get('views', [])}
        target_views = {v['view_name']: v for v in target_schema.get('views', [])}
        
        # Views to create
        for view_name in target_views:
            if view_name not in source_views:
                differences.append({
                    'operation': 'CREATE_VIEW',
                    'object_name': view_name,
                    'object_type': 'VIEW',
                    'details': target_views[view_name],
                    'risk_level': 'low',
                    'rollback_operation': 'DROP_VIEW'
                })
        
        # Views to drop
        for view_name in source_views:
            if view_name not in target_views:
                differences.append({
                    'operation': 'DROP_VIEW',
                    'object_name': view_name,
                    'object_type': 'VIEW',
                    'details': source_views[view_name],
                    'risk_level': 'medium',
                    'rollback_operation': 'CREATE_VIEW'
                })
        
        # Views to alter (definition changed)
        for view_name in source_views:
            if view_name in target_views:
                if source_views[view_name].get('definition') != target_views[view_name].get('definition'):
                    differences.append({
                        'operation': 'ALTER_VIEW',
                        'object_name': view_name,
                        'object_type': 'VIEW',
                        'details': {
                            'source': source_views[view_name],
                            'target': target_views[view_name]
                        },
                        'risk_level': 'low',
                        'rollback_operation': 'ALTER_VIEW'
                    })
        
        return differences
    
    def _analyze_procedure_differences(self, source_schema: Dict, target_schema: Dict) -> List[Dict]:
        """Analyze stored procedure differences."""
        return self._analyze_routine_differences(
            source_schema.get('stored_procedures', []),
            target_schema.get('stored_procedures', []),
            'PROCEDURE'
        )
    
    def _analyze_function_differences(self, source_schema: Dict, target_schema: Dict) -> List[Dict]:
        """Analyze function differences."""
        return self._analyze_routine_differences(
            source_schema.get('functions', []),
            target_schema.get('functions', []),
            'FUNCTION'
        )
    
    def _analyze_routine_differences(self, source_routines: List, target_routines: List, routine_type: str) -> List[Dict]:
        """Analyze differences in routines (procedures/functions)."""
        differences = []
        
        source_dict = {r['routine_name']: r for r in source_routines}
        target_dict = {r['routine_name']: r for r in target_routines}
        
        # Routines to create
        for routine_name in target_dict:
            if routine_name not in source_dict:
                differences.append({
                    'operation': f'CREATE_{routine_type}',
                    'object_name': routine_name,
                    'object_type': routine_type,
                    'details': target_dict[routine_name],
                    'risk_level': 'low',
                    'rollback_operation': f'DROP_{routine_type}'
                })
        
        # Routines to drop
        for routine_name in source_dict:
            if routine_name not in target_dict:
                differences.append({
                    'operation': f'DROP_{routine_type}',
                    'object_name': routine_name,
                    'object_type': routine_type,
                    'details': source_dict[routine_name],
                    'risk_level': 'medium',
                    'rollback_operation': f'CREATE_{routine_type}'
                })
        
        # Routines to alter
        for routine_name in source_dict:
            if routine_name in target_dict:
                if source_dict[routine_name].get('definition') != target_dict[routine_name].get('definition'):
                    differences.append({
                        'operation': f'ALTER_{routine_type}',
                        'object_name': routine_name,
                        'object_type': routine_type,
                        'details': {
                            'source': source_dict[routine_name],
                            'target': target_dict[routine_name]
                        },
                        'risk_level': 'medium',
                        'rollback_operation': f'ALTER_{routine_type}'
                    })
        
        return differences
    
    def _analyze_index_differences(self, source_schema: Dict, target_schema: Dict) -> List[Dict]:
        """Analyze index differences."""
        differences = []
        
        # Extract indexes from tables
        source_indexes = {}
        target_indexes = {}
        
        for table in source_schema.get('tables', []):
            for index in table.get('indexes', []):
                index_name = index.get('index_name')
                if index_name:
                    source_indexes[index_name] = index
        
        for table in target_schema.get('tables', []):
            for index in table.get('indexes', []):
                index_name = index.get('index_name')
                if index_name:
                    target_indexes[index_name] = index
        
        # Indexes to create
        for index_name in target_indexes:
            if index_name not in source_indexes:
                differences.append({
                    'operation': 'CREATE_INDEX',
                    'object_name': index_name,
                    'object_type': 'INDEX',
                    'details': target_indexes[index_name],
                    'risk_level': 'low',
                    'rollback_operation': 'DROP_INDEX'
                })
        
        # Indexes to drop
        for index_name in source_indexes:
            if index_name not in target_indexes:
                differences.append({
                    'operation': 'DROP_INDEX',
                    'object_name': index_name,
                    'object_type': 'INDEX',
                    'details': source_indexes[index_name],
                    'risk_level': 'low',
                    'rollback_operation': 'CREATE_INDEX'
                })
        
        return differences


class MigrationScriptGenerator:
    """Generates migration and rollback scripts."""
    
    def __init__(self, dialect: str = 'sqlserver'):
        self.dialect = dialect.lower()
        self.script_templates = self._load_script_templates()
    
    def _load_script_templates(self) -> Dict[str, str]:
        """Load script templates for different operations."""
        return {
            'CREATE_TABLE': """
CREATE TABLE [{table_name}] (
{columns}
{constraints}
);""",
            'DROP_TABLE': "DROP TABLE [{table_name}];",
            'ADD_COLUMN': "ALTER TABLE [{table_name}] ADD [{column_name}] {column_definition};",
            'DROP_COLUMN': "ALTER TABLE [{table_name}] DROP COLUMN [{column_name}];",
            'ALTER_COLUMN': "ALTER TABLE [{table_name}] ALTER COLUMN [{column_name}] {column_definition};",
            'CREATE_INDEX': "CREATE {unique}INDEX [{index_name}] ON [{table_name}] ({columns});",
            'DROP_INDEX': "DROP INDEX [{index_name}] ON [{table_name}];",
            'CREATE_VIEW': "CREATE VIEW [{view_name}] AS\n{definition}",
            'DROP_VIEW': "DROP VIEW [{view_name}];",
            'ALTER_VIEW': "ALTER VIEW [{view_name}] AS\n{definition}",
            'CREATE_PROCEDURE': "CREATE PROCEDURE [{procedure_name}]\n{definition}",
            'DROP_PROCEDURE': "DROP PROCEDURE [{procedure_name}];",
            'ALTER_PROCEDURE': "ALTER PROCEDURE [{procedure_name}]\n{definition}",
            'CREATE_FUNCTION': "CREATE FUNCTION [{function_name}]\n{definition}",
            'DROP_FUNCTION': "DROP FUNCTION [{function_name}];",
            'ALTER_FUNCTION': "ALTER FUNCTION [{function_name}]\n{definition}"
        }
    
    def generate_migration_script(self, differences: List[Dict]) -> Tuple[str, str]:
        """Generate forward migration and rollback scripts."""
        forward_script_parts = ["-- Migration Script Generated on " + datetime.now().isoformat()]
        rollback_script_parts = ["-- Rollback Script Generated on " + datetime.now().isoformat()]
        
        # Order operations by dependency and risk
        ordered_operations = self._order_operations(differences)
        
        for operation in ordered_operations:
            forward_sql = self._generate_operation_sql(operation)
            rollback_sql = self._generate_rollback_sql(operation)
            
            if forward_sql:
                forward_script_parts.append(f"\n-- {operation['operation']} {operation['object_name']}")
                forward_script_parts.append(forward_sql)
            
            if rollback_sql:
                rollback_script_parts.insert(2, rollback_sql)  # Insert at beginning for reverse order
                rollback_script_parts.insert(2, f"-- Rollback {operation['operation']} {operation['object_name']}")
        
        forward_script = "\n".join(forward_script_parts)
        rollback_script = "\n".join(rollback_script_parts)
        
        return forward_script, rollback_script
    
    def _order_operations(self, differences: List[Dict]) -> List[Dict]:
        """Order operations by dependency and risk level."""
        # Define operation order priorities
        operation_priority = {
            'DROP_CONSTRAINT': 1,
            'DROP_INDEX': 2,
            'DROP_VIEW': 3,
            'DROP_PROCEDURE': 4,
            'DROP_FUNCTION': 5,
            'ALTER_TABLE': 6,
            'DROP_COLUMN': 7,
            'ALTER_COLUMN': 8,
            'ADD_COLUMN': 9,
            'CREATE_TABLE': 10,
            'CREATE_INDEX': 11,
            'CREATE_VIEW': 12,
            'CREATE_PROCEDURE': 13,
            'CREATE_FUNCTION': 14,
            'CREATE_CONSTRAINT': 15
        }
        
        return sorted(differences, key=lambda x: (
            operation_priority.get(x['operation'], 99),
            x['risk_level'],
            x['object_name']
        ))
    
    def _generate_operation_sql(self, operation: Dict) -> str:
        """Generate SQL for a single operation."""
        op_type = operation['operation']
        details = operation['details']
        
        if op_type == 'CREATE_TABLE':
            return self._generate_create_table_sql(details)
        elif op_type == 'DROP_TABLE':
            return f"DROP TABLE [{details['table_name']}];"
        elif op_type == 'ADD_COLUMN':
            return self._generate_add_column_sql(details)
        elif op_type == 'DROP_COLUMN':
            return f"ALTER TABLE [{details['table']}] DROP COLUMN [{details['column']['column_name']}];"
        elif op_type == 'ALTER_COLUMN':
            return self._generate_alter_column_sql(details)
        elif op_type == 'CREATE_VIEW':
            return f"CREATE VIEW [{details['view_name']}] AS\n{details['definition']}"
        elif op_type == 'DROP_VIEW':
            return f"DROP VIEW [{details['view_name']}];"
        elif op_type == 'ALTER_VIEW':
            return f"ALTER VIEW [{details['target']['view_name']}] AS\n{details['target']['definition']}"
        elif op_type == 'CREATE_INDEX':
            return self._generate_create_index_sql(details)
        elif op_type == 'DROP_INDEX':
            return f"DROP INDEX [{details['index_name']}] ON [{details['table_name']}];"
        
        # Add more operation types as needed
        return f"-- TODO: Implement {op_type} for {operation['object_name']}"
    
    def _generate_create_table_sql(self, table_details: Dict) -> str:
        """Generate CREATE TABLE SQL."""
        table_name = table_details['table_name']
        columns = table_details.get('columns', [])
        
        column_definitions = []
        for col in columns:
            col_def = self._format_column_definition(col)
            column_definitions.append(f"    {col_def}")
        
        columns_sql = ",\n".join(column_definitions)
        
        return f"CREATE TABLE [{table_name}] (\n{columns_sql}\n);"
    
    def _generate_add_column_sql(self, details: Dict) -> str:
        """Generate ADD COLUMN SQL."""
        table_name = details['table']
        column = details['column']
        col_def = self._format_column_definition(column)
        
        return f"ALTER TABLE [{table_name}] ADD {col_def};"
    
    def _generate_alter_column_sql(self, details: Dict) -> str:
        """Generate ALTER COLUMN SQL."""
        table_name = details['table']
        target_column = details['target_column']
        col_def = self._format_column_definition(target_column, for_alter=True)
        
        return f"ALTER TABLE [{table_name}] ALTER COLUMN {col_def};"
    
    def _format_column_definition(self, column: Dict, for_alter: bool = False) -> str:
        """Format a column definition."""
        col_name = column['column_name']
        data_type = column['data_type'].upper()
        
        # Handle data type with precision/scale
        if column.get('max_length') and column.get('max_length') > 0:
            if data_type in ['VARCHAR', 'NVARCHAR', 'CHAR', 'NCHAR']:
                data_type = f"{data_type}({column['max_length']})"
        elif column.get('precision') and column.get('scale') is not None:
            data_type = f"{data_type}({column['precision']},{column['scale']})"
        elif column.get('precision'):
            data_type = f"{data_type}({column['precision']})"
        
        col_def = f"[{col_name}] {data_type}"
        
        # Nullable
        if column.get('is_nullable') == 'NO':
            col_def += " NOT NULL"
        elif column.get('is_nullable') == 'YES' and for_alter:
            col_def += " NULL"
        
        # Default value
        if column.get('default_value'):
            col_def += f" DEFAULT {column['default_value']}"
        
        return col_def
    
    def _generate_create_index_sql(self, index_details: Dict) -> str:
        """Generate CREATE INDEX SQL."""
        index_name = index_details['index_name']
        table_name = index_details['table_name']
        columns = index_details.get('columns', [])
        is_unique = index_details.get('is_unique', False)
        
        unique_keyword = "UNIQUE " if is_unique else ""
        columns_list = ", ".join([f"[{col}]" for col in columns])
        
        return f"CREATE {unique_keyword}INDEX [{index_name}] ON [{table_name}] ({columns_list});"
    
    def _generate_rollback_sql(self, operation: Dict) -> str:
        """Generate rollback SQL for an operation."""
        rollback_op = operation.get('rollback_operation')
        details = operation['details']
        
        if rollback_op == 'DROP_TABLE':
            return f"DROP TABLE [{operation['object_name']}];"
        elif rollback_op == 'CREATE_TABLE' and isinstance(details, dict):
            return self._generate_create_table_sql(details)
        elif rollback_op == 'DROP_COLUMN':
            table_name = details.get('table', operation['object_name'].split('.')[0])
            column_name = operation['object_name'].split('.')[-1]
            return f"ALTER TABLE [{table_name}] DROP COLUMN [{column_name}];"
        elif rollback_op == 'ADD_COLUMN' and 'column' in details:
            table_name = details['table']
            col_def = self._format_column_definition(details['column'])
            return f"ALTER TABLE [{table_name}] ADD {col_def};"
        elif rollback_op == 'ALTER_COLUMN' and 'source_column' in details:
            table_name = details['table']
            col_def = self._format_column_definition(details['source_column'], for_alter=True)
            return f"ALTER TABLE [{table_name}] ALTER COLUMN {col_def};"
        
        return f"-- TODO: Implement rollback for {operation['operation']}"


class MigrationValidator:
    """Validates migration plans for potential issues."""
    
    def __init__(self):
        self.validation_rules = [
            self._validate_syntax,
            self._validate_dependencies,
            self._validate_data_integrity,
            self._validate_performance_impact
        ]
    
    def validate_migration_plan(self, migration_data: Dict) -> List[Dict]:
        """Validate a complete migration plan."""
        validation_results = []
        
        for rule in self.validation_rules:
            try:
                result = rule(migration_data)
                if result:
                    validation_results.extend(result)
            except Exception as e:
                validation_results.append({
                    'type': 'validation_error',
                    'status': 'fail',
                    'message': f"Validation rule failed: {str(e)}",
                    'details': {'rule': rule.__name__, 'error': str(e)}
                })
        
        return validation_results
    
    def _validate_syntax(self, migration_data: Dict) -> List[Dict]:
        """Validate SQL syntax in migration scripts."""
        results = []
        
        forward_script = migration_data.get('forward_script', '')
        rollback_script = migration_data.get('rollback_script', '')
        
        # Basic syntax checks
        if not forward_script.strip():
            results.append({
                'type': 'syntax',
                'status': 'fail',
                'message': 'Forward migration script is empty',
                'details': {}
            })
        
        if not rollback_script.strip():
            results.append({
                'type': 'syntax',
                'status': 'warning',
                'message': 'Rollback script is empty',
                'details': {}
            })
        
        # Check for basic SQL syntax issues
        syntax_issues = self._check_basic_syntax(forward_script)
        for issue in syntax_issues:
            results.append({
                'type': 'syntax',
                'status': 'fail',
                'message': issue,
                'details': {'script_type': 'forward'}
            })
        
        return results
    
    def _check_basic_syntax(self, script: str) -> List[str]:
        """Basic SQL syntax validation."""
        issues = []
        
        # Check for unmatched brackets
        bracket_count = script.count('[') - script.count(']')
        if bracket_count != 0:
            issues.append("Unmatched square brackets in SQL script")
        
        paren_count = script.count('(') - script.count(')')
        if paren_count != 0:
            issues.append("Unmatched parentheses in SQL script")
        
        # Check for missing semicolons on major statements
        lines = script.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if (line.upper().startswith(('CREATE ', 'DROP ', 'ALTER ')) and 
                not line.endswith(';') and not line.endswith('AS')):
                issues.append(f"Line {i+1} may be missing semicolon: {line[:50]}...")
        
        return issues
    
    def _validate_dependencies(self, migration_data: Dict) -> List[Dict]:
        """Validate operation dependencies."""
        results = []
        
        differences = migration_data.get('differences', {})
        all_operations = []
        
        for category in differences.values():
            all_operations.extend(category)
        
        # Check for dependency violations
        table_operations = self._group_operations_by_table(all_operations)
        
        for table_name, operations in table_operations.items():
            dependency_issues = self._check_table_operation_dependencies(operations)
            for issue in dependency_issues:
                results.append({
                    'type': 'dependency',
                    'status': 'fail',
                    'message': issue,
                    'details': {'table': table_name}
                })
        
        return results
    
    def _group_operations_by_table(self, operations: List[Dict]) -> Dict[str, List[Dict]]:
        """Group operations by affected table."""
        table_ops = defaultdict(list)
        
        for op in operations:
            object_name = op.get('object_name', '')
            
            if '.' in object_name:
                table_name = object_name.split('.')[0]
            elif op.get('object_type') == 'TABLE':
                table_name = object_name
            elif 'table' in op.get('details', {}):
                table_name = op['details']['table']
            else:
                table_name = 'unknown'
            
            table_ops[table_name].append(op)
        
        return table_ops
    
    def _check_table_operation_dependencies(self, operations: List[Dict]) -> List[str]:
        """Check dependencies within table operations."""
        issues = []
        
        has_drop_table = any(op['operation'] == 'DROP_TABLE' for op in operations)
        has_create_table = any(op['operation'] == 'CREATE_TABLE' for op in operations)
        has_alter_operations = any(op['operation'].startswith('ALTER_') for op in operations)
        
        if has_drop_table and (has_create_table or has_alter_operations):
            issues.append("Table is both dropped and modified in same migration")
        
        return issues
    
    def _validate_data_integrity(self, migration_data: Dict) -> List[Dict]:
        """Validate potential data integrity issues."""
        results = []
        
        differences = migration_data.get('differences', {})
        table_ops = differences.get('tables', [])
        
        for op in table_ops:
            if op['operation'] == 'DROP_COLUMN':
                results.append({
                    'type': 'data_integrity',
                    'status': 'warning',
                    'message': f"Dropping column {op['object_name']} will result in data loss",
                    'details': {'operation': op}
                })
            
            elif op['operation'] == 'ALTER_COLUMN':
                details = op.get('details', {})
                source_col = details.get('source_column', {})
                target_col = details.get('target_column', {})
                
                # Check for potentially lossy type changes
                if self._is_lossy_type_change(source_col, target_col):
                    results.append({
                        'type': 'data_integrity',
                        'status': 'fail',
                        'message': f"Column {op['object_name']} type change may cause data loss",
                        'details': {'source_type': source_col.get('data_type'),
                                   'target_type': target_col.get('data_type')}
                    })
        
        return results
    
    def _is_lossy_type_change(self, source_col: Dict, target_col: Dict) -> bool:
        """Check if column type change is potentially lossy."""
        source_type = source_col.get('data_type', '').upper()
        target_type = target_col.get('data_type', '').upper()
        
        # Size reductions
        source_length = source_col.get('max_length', 0)
        target_length = target_col.get('max_length', 0)
        
        if source_length > 0 and target_length > 0 and source_length > target_length:
            return True
        
        # Precision reductions
        source_precision = source_col.get('precision', 0)
        target_precision = target_col.get('precision', 0)
        
        if source_precision > 0 and target_precision > 0 and source_precision > target_precision:
            return True
        
        return False
    
    def _validate_performance_impact(self, migration_data: Dict) -> List[Dict]:
        """Validate potential performance impacts."""
        results = []
        
        differences = migration_data.get('differences', {})
        
        # Check for operations that might impact performance
        index_drops = [op for ops in differences.values() for op in ops 
                      if op['operation'] == 'DROP_INDEX']
        
        if len(index_drops) > 5:
            results.append({
                'type': 'performance_impact',
                'status': 'warning',
                'message': f"Migration drops {len(index_drops)} indexes, which may impact query performance",
                'details': {'dropped_indexes': len(index_drops)}
            })
        
        # Check for large table alterations
        alter_table_ops = [op for ops in differences.values() for op in ops 
                          if op['operation'].startswith('ALTER_TABLE')]
        
        if len(alter_table_ops) > 10:
            results.append({
                'type': 'performance_impact',
                'status': 'warning',
                'message': "Migration includes many table alterations, consider breaking into smaller migrations",
                'details': {'table_alterations': len(alter_table_ops)}
            })
        
        return results


class MigrationPlannerGUI:
    """GUI for database migration planning."""
    
    def __init__(self, parent):
        self.parent = parent
        self.migration_db = MigrationDatabase()
        self.schema_analyzer = SchemaAnalyzer()
        self.script_generator = MigrationScriptGenerator()
        self.validator = MigrationValidator()
        
        self.current_plan_data = None
        self.source_schema_data = None
        self.target_schema_data = None
    
    def create_migration_tab(self, notebook: ttk.Notebook):
        """Create the migration planning tab."""
        # Create main frame
        migration_frame = ttk.Frame(notebook)
        notebook.add(migration_frame, text="🔄 Migration Planning")
        
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(migration_frame)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Schema comparison tab
        self.create_comparison_tab(sub_notebook)
        
        # Migration plan tab
        self.create_plan_tab(sub_notebook)
        
        # Script generation tab
        self.create_script_tab(sub_notebook)
        
        # Validation tab
        self.create_validation_tab(sub_notebook)
    
    def create_comparison_tab(self, notebook: ttk.Notebook):
        """Create schema comparison tab."""
        comparison_frame = ttk.Frame(notebook)
        notebook.add(comparison_frame, text="Schema Comparison")
        
        # Top section - Schema selection
        selection_frame = ttk.LabelFrame(comparison_frame, text="Schema Selection", padding="10")
        selection_frame.pack(fill='x', padx=5, pady=5)
        
        # Source schema section
        source_frame = ttk.Frame(selection_frame)
        source_frame.pack(fill='x', pady=5)
        
        ttk.Label(source_frame, text="Source Schema:").pack(side='left')
        self.source_schema_var = tk.StringVar()
        self.source_combo = ttk.Combobox(source_frame, textvariable=self.source_schema_var, 
                                       state="readonly", width=40)
        self.source_combo.pack(side='left', padx=10)
        ttk.Button(source_frame, text="Load from File", 
                  command=self.load_source_schema).pack(side='left', padx=5)
        
        # Target schema section  
        target_frame = ttk.Frame(selection_frame)
        target_frame.pack(fill='x', pady=5)
        
        ttk.Label(target_frame, text="Target Schema:").pack(side='left')
        self.target_schema_var = tk.StringVar()
        self.target_combo = ttk.Combobox(target_frame, textvariable=self.target_schema_var,
                                       state="readonly", width=40)
        self.target_combo.pack(side='left', padx=10)
        ttk.Button(target_frame, text="Load from File",
                  command=self.load_target_schema).pack(side='left', padx=5)
        
        # Compare button
        ttk.Button(selection_frame, text="Compare Schemas",
                  command=self.compare_schemas).pack(pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(comparison_frame, text="Schema Differences", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview for differences
        columns = ('Operation', 'Object', 'Type', 'Risk Level', 'Details')
        self.differences_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.differences_tree.heading(col, text=col)
            self.differences_tree.column(col, width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.differences_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient='horizontal', command=self.differences_tree.xview)
        self.differences_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.differences_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Context menu for differences
        self.differences_tree.bind("<Button-3>", self.show_difference_context_menu)
    
    def create_plan_tab(self, notebook: ttk.Notebook):
        """Create migration plan tab."""
        plan_frame = ttk.Frame(notebook)
        notebook.add(plan_frame, text="Migration Plan")
        
        # Plan details section
        details_frame = ttk.LabelFrame(plan_frame, text="Plan Details", padding="10")
        details_frame.pack(fill='x', padx=5, pady=5)
        
        # Plan name
        name_frame = ttk.Frame(details_frame)
        name_frame.pack(fill='x', pady=2)
        ttk.Label(name_frame, text="Plan Name:").pack(side='left')
        self.plan_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.plan_name_var, width=50).pack(side='left', padx=10)
        
        # Description
        desc_frame = ttk.Frame(details_frame)
        desc_frame.pack(fill='x', pady=2)
        ttk.Label(desc_frame, text="Description:").pack(anchor='w')
        self.plan_description_text = tk.Text(desc_frame, height=3, width=80)
        self.plan_description_text.pack(fill='x', pady=5)
        
        # Risk and timing
        risk_frame = ttk.Frame(details_frame)
        risk_frame.pack(fill='x', pady=2)
        
        ttk.Label(risk_frame, text="Risk Level:").pack(side='left')
        self.risk_level_var = tk.StringVar(value="medium")
        risk_combo = ttk.Combobox(risk_frame, textvariable=self.risk_level_var,
                                values=["low", "medium", "high", "critical"], state="readonly")
        risk_combo.pack(side='left', padx=10)
        
        ttk.Label(risk_frame, text="Estimated Duration (minutes):").pack(side='left', padx=(20, 0))
        self.duration_var = tk.IntVar(value=30)
        ttk.Spinbox(risk_frame, from_=1, to=9999, textvariable=self.duration_var, width=10).pack(side='left', padx=10)
        
        # Plan operations section
        operations_frame = ttk.LabelFrame(plan_frame, text="Migration Operations", padding="5")
        operations_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Operations treeview
        op_columns = ('Order', 'Operation', 'Object', 'Risk', 'Status')
        self.operations_tree = ttk.Treeview(operations_frame, columns=op_columns, show='headings', height=12)
        
        for col in op_columns:
            self.operations_tree.heading(col, text=col)
            self.operations_tree.column(col, width=80)
        
        self.operations_tree.pack(side='left', fill='both', expand=True)
        
        op_scrollbar = ttk.Scrollbar(operations_frame, orient='vertical', command=self.operations_tree.yview)
        self.operations_tree.configure(yscrollcommand=op_scrollbar.set)
        op_scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = ttk.Frame(plan_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Save Plan", command=self.save_migration_plan).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Plan", command=self.load_migration_plan).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Generate Scripts", command=self.generate_migration_scripts).pack(side='left', padx=5)
    
    def create_script_tab(self, notebook: ttk.Notebook):
        """Create script generation tab."""
        script_frame = ttk.Frame(notebook)
        notebook.add(script_frame, text="Generated Scripts")
        
        # Script display notebook
        script_notebook = ttk.Notebook(script_frame)
        script_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Forward migration script
        forward_frame = ttk.Frame(script_notebook)
        script_notebook.add(forward_frame, text="Migration Script")
        
        self.forward_script_text = scrolledtext.ScrolledText(forward_frame, wrap='none', 
                                                           font=('Consolas', 10))
        self.forward_script_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Rollback script
        rollback_frame = ttk.Frame(script_notebook)
        script_notebook.add(rollback_frame, text="Rollback Script")
        
        self.rollback_script_text = scrolledtext.ScrolledText(rollback_frame, wrap='none',
                                                            font=('Consolas', 10))
        self.rollback_script_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Script actions
        actions_frame = ttk.Frame(script_frame)
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Export Scripts", command=self.export_scripts).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Copy to Clipboard", command=self.copy_script_to_clipboard).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Execute Migration", command=self.execute_migration).pack(side='right', padx=5)
    
    def create_validation_tab(self, notebook: ttk.Notebook):
        """Create validation results tab."""
        validation_frame = ttk.Frame(notebook)
        notebook.add(validation_frame, text="Validation Results")
        
        # Validation controls
        controls_frame = ttk.Frame(validation_frame)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Validate Plan", command=self.validate_migration_plan).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Clear Results", command=self.clear_validation_results).pack(side='left', padx=5)
        
        # Validation results
        results_frame = ttk.LabelFrame(validation_frame, text="Validation Results", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        val_columns = ('Type', 'Status', 'Message', 'Details')
        self.validation_tree = ttk.Treeview(results_frame, columns=val_columns, show='headings', height=15)
        
        for col in val_columns:
            self.validation_tree.heading(col, text=col)
            if col == 'Message':
                self.validation_tree.column(col, width=300)
            else:
                self.validation_tree.column(col, width=100)
        
        self.validation_tree.pack(side='left', fill='both', expand=True)
        
        val_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.validation_tree.yview)
        self.validation_tree.configure(yscrollcommand=val_scrollbar.set)
        val_scrollbar.pack(side='right', fill='y')
    
    def load_source_schema(self):
        """Load source schema from file."""
        filename = filedialog.askopenfilename(
            title="Load Source Schema",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.source_schema_data = json.load(f)
                self.source_schema_var.set(f"File: {os.path.basename(filename)}")
                messagebox.showinfo("Success", "Source schema loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load source schema: {str(e)}")
    
    def load_target_schema(self):
        """Load target schema from file."""
        filename = filedialog.askopenfilename(
            title="Load Target Schema",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.target_schema_data = json.load(f)
                self.target_schema_var.set(f"File: {os.path.basename(filename)}")
                messagebox.showinfo("Success", "Target schema loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load target schema: {str(e)}")
    
    def compare_schemas(self):
        """Compare source and target schemas."""
        if not self.source_schema_data:
            messagebox.showwarning("Missing Source", "Please load source schema first")
            return
        
        if not self.target_schema_data:
            messagebox.showwarning("Missing Target", "Please load target schema first")
            return
        
        try:
            # Analyze differences
            differences = self.schema_analyzer.analyze_schema_differences(
                self.source_schema_data, self.target_schema_data
            )
            
            # Clear existing results
            for item in self.differences_tree.get_children():
                self.differences_tree.delete(item)
            
            # Populate differences tree
            for category, ops in differences.items():
                for op in ops:
                    self.differences_tree.insert('', 'end', values=(
                        op['operation'],
                        op['object_name'],
                        op['object_type'],
                        op['risk_level'],
                        str(op['details'])[:100] + "..." if len(str(op['details'])) > 100 else str(op['details'])
                    ))
            
            # Store differences for later use
            self.current_plan_data = {'differences': differences}
            
            messagebox.showinfo("Success", f"Schema comparison completed. Found {sum(len(ops) for ops in differences.values())} differences.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare schemas: {str(e)}")
    
    def save_migration_plan(self):
        """Save the current migration plan."""
        if not self.current_plan_data:
            messagebox.showwarning("No Plan", "Please compare schemas first to generate a plan")
            return
        
        plan_name = self.plan_name_var.get().strip()
        if not plan_name:
            messagebox.showwarning("Missing Name", "Please enter a plan name")
            return
        
        try:
            description = self.plan_description_text.get(1.0, tk.END).strip()
            risk_level = self.risk_level_var.get()
            duration = self.duration_var.get()
            
            # Save to database
            plan_id = self.migration_db.save_migration_plan(
                name=plan_name,
                source_db=self.source_schema_var.get(),
                target_db=self.target_schema_var.get(),
                description=description,
                migration_data=self.current_plan_data,
                risk_level=risk_level,
                estimated_duration=duration,
                dependencies=[]
            )
            
            messagebox.showinfo("Success", f"Migration plan saved with ID: {plan_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save migration plan: {str(e)}")
    
    def load_migration_plan(self):
        """Load an existing migration plan."""
        try:
            plans = self.migration_db.get_migration_plans()
            
            if not plans:
                messagebox.showinfo("No Plans", "No migration plans found")
                return
            
            # Show plan selection dialog
            plan_names = [f"{plan['name']} ({plan['status']}) - {plan['created_timestamp']}" 
                         for plan in plans]
            
            selection_dialog = PlanSelectionDialog(self.parent, plan_names, plans)
            if selection_dialog.selected_plan:
                self._load_plan_data(selection_dialog.selected_plan)
                messagebox.showinfo("Success", "Migration plan loaded successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load migration plans: {str(e)}")
    
    def _load_plan_data(self, plan_data: Dict):
        """Load plan data into the GUI."""
        self.plan_name_var.set(plan_data['name'])
        self.plan_description_text.delete(1.0, tk.END)
        self.plan_description_text.insert(1.0, plan_data.get('description', ''))
        self.risk_level_var.set(plan_data.get('risk_level', 'medium'))
        self.duration_var.set(plan_data.get('estimated_duration', 30))
        
        self.current_plan_data = plan_data.get('migration_data', {})
        
        # Update operations tree
        self._update_operations_tree()
    
    def _update_operations_tree(self):
        """Update the operations tree view."""
        # Clear existing items
        for item in self.operations_tree.get_children():
            self.operations_tree.delete(item)
        
        if not self.current_plan_data or 'differences' not in self.current_plan_data:
            return
        
        differences = self.current_plan_data['differences']
        order = 1
        
        for category, ops in differences.items():
            for op in ops:
                self.operations_tree.insert('', 'end', values=(
                    order,
                    op['operation'],
                    op['object_name'],
                    op['risk_level'],
                    'pending'
                ))
                order += 1
    
    def generate_migration_scripts(self):
        """Generate migration and rollback scripts."""
        if not self.current_plan_data or 'differences' not in self.current_plan_data:
            messagebox.showwarning("No Plan", "Please create a migration plan first")
            return
        
        try:
            differences = self.current_plan_data['differences']
            all_operations = []
            
            # Flatten all operations
            for category, ops in differences.items():
                all_operations.extend(ops)
            
            # Generate scripts
            forward_script, rollback_script = self.script_generator.generate_migration_script(all_operations)
            
            # Display scripts
            self.forward_script_text.delete(1.0, tk.END)
            self.forward_script_text.insert(1.0, forward_script)
            
            self.rollback_script_text.delete(1.0, tk.END)
            self.rollback_script_text.insert(1.0, rollback_script)
            
            # Store scripts in plan data
            self.current_plan_data['forward_script'] = forward_script
            self.current_plan_data['rollback_script'] = rollback_script
            
            messagebox.showinfo("Success", "Migration scripts generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate scripts: {str(e)}")
    
    def validate_migration_plan(self):
        """Validate the current migration plan."""
        if not self.current_plan_data:
            messagebox.showwarning("No Plan", "Please create a migration plan first")
            return
        
        try:
            validation_results = self.validator.validate_migration_plan(self.current_plan_data)
            
            # Clear existing results
            for item in self.validation_tree.get_children():
                self.validation_tree.delete(item)
            
            # Add validation results
            for result in validation_results:
                self.validation_tree.insert('', 'end', values=(
                    result['type'],
                    result['status'],
                    result['message'],
                    json.dumps(result.get('details', {}))[:100] + "..."
                ))
            
            # Show summary
            total_issues = len(validation_results)
            errors = len([r for r in validation_results if r['status'] == 'fail'])
            warnings = len([r for r in validation_results if r['status'] == 'warning'])
            
            messagebox.showinfo("Validation Complete", 
                              f"Validation completed.\nTotal issues: {total_issues}\nErrors: {errors}\nWarnings: {warnings}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate migration plan: {str(e)}")
    
    def clear_validation_results(self):
        """Clear validation results."""
        for item in self.validation_tree.get_children():
            self.validation_tree.delete(item)
    
    def export_scripts(self):
        """Export generated scripts to files."""
        if not self.current_plan_data or 'forward_script' not in self.current_plan_data:
            messagebox.showwarning("No Scripts", "Please generate scripts first")
            return
        
        try:
            directory = filedialog.askdirectory(title="Select Export Directory")
            if directory:
                plan_name = self.plan_name_var.get().strip() or "migration"
                
                # Export forward script
                forward_file = os.path.join(directory, f"{plan_name}_migration.sql")
                with open(forward_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_plan_data['forward_script'])
                
                # Export rollback script
                rollback_file = os.path.join(directory, f"{plan_name}_rollback.sql")
                with open(rollback_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_plan_data['rollback_script'])
                
                messagebox.showinfo("Success", f"Scripts exported to:\n{forward_file}\n{rollback_file}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export scripts: {str(e)}")
    
    def copy_script_to_clipboard(self):
        """Copy current script to clipboard."""
        # This would need to be implemented based on the active tab
        messagebox.showinfo("TODO", "Copy to clipboard functionality to be implemented")
    
    def execute_migration(self):
        """Execute the migration (placeholder)."""
        messagebox.showwarning("Not Implemented", 
                             "Migration execution requires careful implementation with proper backup and rollback mechanisms. "
                             "This feature should include:\n"
                             "- Pre-migration backup\n"
                             "- Transaction management\n" 
                             "- Progress monitoring\n"
                             "- Automatic rollback on failure")
    
    def show_difference_context_menu(self, event):
        """Show context menu for schema differences."""
        # This would show options like "View Details", "Exclude from Migration", etc.
        pass


class PlanSelectionDialog:
    """Dialog for selecting migration plans."""
    
    def __init__(self, parent, plan_names: List[str], plans: List[Dict]):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Migration Plan")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.plans = plans
        self.selected_plan = None
        
        self.create_widgets(plan_names)
        
        # Center dialog
        self.dialog.geometry(f"+{parent.winfo_rootx() + 100}+{parent.winfo_rooty() + 100}")
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self, plan_names: List[str]):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Select a migration plan:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Plans listbox
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.plans_listbox = tk.Listbox(listbox_frame, height=15)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.plans_listbox.yview)
        self.plans_listbox.configure(yscrollcommand=scrollbar.set)
        
        for name in plan_names:
            self.plans_listbox.insert(tk.END, name)
        
        self.plans_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Select", command=self.select_plan).pack(side="right")
    
    def select_plan(self):
        """Select the chosen plan."""
        selection = self.plans_listbox.curselection()
        if selection:
            self.selected_plan = self.plans[selection[0]]
            self.dialog.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select a migration plan.")
    
    def cancel(self):
        """Cancel plan selection."""
        self.dialog.destroy()


# Test function for standalone execution
if __name__ == "__main__":
    # Create sample schema data for testing
    source_schema = {
        'tables': [
            {
                'table_name': 'Users',
                'columns': [
                    {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO'},
                    {'column_name': 'name', 'data_type': 'varchar', 'max_length': 100, 'is_nullable': 'NO'},
                    {'column_name': 'email', 'data_type': 'varchar', 'max_length': 255, 'is_nullable': 'YES'}
                ]
            }
        ],
        'views': [],
        'stored_procedures': [],
        'functions': []
    }
    
    target_schema = {
        'tables': [
            {
                'table_name': 'Users',
                'columns': [
                    {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO'},
                    {'column_name': 'name', 'data_type': 'varchar', 'max_length': 150, 'is_nullable': 'NO'},
                    {'column_name': 'email', 'data_type': 'varchar', 'max_length': 255, 'is_nullable': 'NO'},
                    {'column_name': 'created_date', 'data_type': 'datetime', 'is_nullable': 'NO', 'default_value': 'GETDATE()'}
                ]
            },
            {
                'table_name': 'Products',
                'columns': [
                    {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO'},
                    {'column_name': 'name', 'data_type': 'varchar', 'max_length': 200, 'is_nullable': 'NO'}
                ]
            }
        ],
        'views': [],
        'stored_procedures': [],
        'functions': []
    }
    
    # Test schema analysis
    analyzer = SchemaAnalyzer()
    differences = analyzer.analyze_schema_differences(source_schema, target_schema)
    
    print("Schema Analysis Results:")
    for category, ops in differences.items():
        if ops:
            print(f"\n{category.title()}:")
            for op in ops:
                print(f"  - {op['operation']} {op['object_name']} (Risk: {op['risk_level']})")
    
    # Test script generation
    generator = MigrationScriptGenerator()
    all_operations = []
    for ops in differences.values():
        all_operations.extend(ops)
    
    forward_script, rollback_script = generator.generate_migration_script(all_operations)
    
    print("\n" + "="*50)
    print("FORWARD MIGRATION SCRIPT:")
    print("="*50)
    print(forward_script)
    
    print("\n" + "="*50)
    print("ROLLBACK SCRIPT:")
    print("="*50)
    print(rollback_script)
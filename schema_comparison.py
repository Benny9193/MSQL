#!/usr/bin/env python3
"""
Schema Comparison Module
=======================

Advanced schema comparison functionality for analyzing differences between
database schemas. Supports comparing schemas between different databases,
different time periods, or against baseline configurations.

Features:
- Table structure comparison
- Column differences (added, removed, modified)
- Index and constraint analysis
- Stored procedure and function changes
- Relationship mapping differences
- Change summary and impact analysis
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"

@dataclass
class SchemaChange:
    """Represents a single schema change."""
    object_type: str  # table, column, index, procedure, etc.
    object_name: str
    change_type: ChangeType
    details: Dict[str, Any]
    impact_level: str  # low, medium, high, critical
    description: str

class SchemaComparator:
    """Comprehensive schema comparison engine."""
    
    def __init__(self):
        self.changes = []
        self.comparison_metadata = {}
    
    def compare_schemas(self, schema_a: Dict[str, Any], schema_b: Dict[str, Any], 
                       comparison_name: str = "Schema Comparison") -> Dict[str, Any]:
        """
        Compare two complete database schemas.
        
        Args:
            schema_a: First schema (baseline/source)
            schema_b: Second schema (target/current)
            comparison_name: Name for this comparison
            
        Returns:
            Comprehensive comparison result
        """
        self.changes = []
        self.comparison_metadata = {
            'name': comparison_name,
            'timestamp': datetime.now().isoformat(),
            'schema_a_info': schema_a.get('database_info', {}),
            'schema_b_info': schema_b.get('database_info', {}),
            'comparison_summary': {}
        }
        
        logger.info(f"Starting schema comparison: {comparison_name}")
        
        # Compare different schema components
        self._compare_tables(schema_a.get('tables', []), schema_b.get('tables', []))
        self._compare_views(schema_a.get('views', []), schema_b.get('views', []))
        self._compare_procedures(schema_a.get('stored_procedures', []), schema_b.get('stored_procedures', []))
        self._compare_functions(schema_a.get('functions', []), schema_b.get('functions', []))
        self._compare_relationships(schema_a.get('relationships', {}), schema_b.get('relationships', {}))
        
        # Generate summary
        summary = self._generate_summary()
        self.comparison_metadata['comparison_summary'] = summary
        
        return {
            'metadata': self.comparison_metadata,
            'changes': self.changes,
            'summary': summary,
            'impact_analysis': self._analyze_impact(),
            'recommendations': self._generate_recommendations()
        }
    
    def _compare_tables(self, tables_a: List[Dict], tables_b: List[Dict]):
        """Compare table structures between schemas."""
        # Create lookup dictionaries
        tables_a_dict = {f"{t.get('schema_name', 'dbo')}.{t.get('table_name')}": t for t in tables_a}
        tables_b_dict = {f"{t.get('schema_name', 'dbo')}.{t.get('table_name')}": t for t in tables_b}
        
        all_table_names = set(tables_a_dict.keys()) | set(tables_b_dict.keys())
        
        for table_name in all_table_names:
            table_a = tables_a_dict.get(table_name)
            table_b = tables_b_dict.get(table_name)
            
            if table_a and not table_b:
                # Table removed
                self.changes.append(SchemaChange(
                    object_type="table",
                    object_name=table_name,
                    change_type=ChangeType.REMOVED,
                    details={"table_info": table_a},
                    impact_level="high",
                    description=f"Table {table_name} has been removed"
                ))
            elif table_b and not table_a:
                # Table added
                self.changes.append(SchemaChange(
                    object_type="table",
                    object_name=table_name,
                    change_type=ChangeType.ADDED,
                    details={"table_info": table_b},
                    impact_level="medium",
                    description=f"Table {table_name} has been added"
                ))
            elif table_a and table_b:
                # Compare table details
                self._compare_table_details(table_name, table_a, table_b)
    
    def _compare_table_details(self, table_name: str, table_a: Dict, table_b: Dict):
        """Compare detailed table structure."""
        # Compare columns
        columns_a = {c.get('column_name'): c for c in table_a.get('columns', [])}
        columns_b = {c.get('column_name'): c for c in table_b.get('columns', [])}
        
        all_column_names = set(columns_a.keys()) | set(columns_b.keys())
        
        for column_name in all_column_names:
            column_a = columns_a.get(column_name)
            column_b = columns_b.get(column_name)
            
            if column_a and not column_b:
                # Column removed
                self.changes.append(SchemaChange(
                    object_type="column",
                    object_name=f"{table_name}.{column_name}",
                    change_type=ChangeType.REMOVED,
                    details={"column_info": column_a, "table_name": table_name},
                    impact_level="high",
                    description=f"Column {column_name} removed from table {table_name}"
                ))
            elif column_b and not column_a:
                # Column added
                self.changes.append(SchemaChange(
                    object_type="column",
                    object_name=f"{table_name}.{column_name}",
                    change_type=ChangeType.ADDED,
                    details={"column_info": column_b, "table_name": table_name},
                    impact_level="medium",
                    description=f"Column {column_name} added to table {table_name}"
                ))
            elif column_a and column_b:
                # Compare column properties
                changes = self._compare_column_properties(column_a, column_b)
                if changes:
                    self.changes.append(SchemaChange(
                        object_type="column",
                        object_name=f"{table_name}.{column_name}",
                        change_type=ChangeType.MODIFIED,
                        details={
                            "changes": changes,
                            "old_column": column_a,
                            "new_column": column_b,
                            "table_name": table_name
                        },
                        impact_level=self._assess_column_change_impact(changes),
                        description=f"Column {column_name} in table {table_name} has been modified: {', '.join(changes.keys())}"
                    ))
        
        # Compare indexes
        self._compare_table_indexes(table_name, table_a.get('indexes', []), table_b.get('indexes', []))
        
        # Compare constraints
        self._compare_table_constraints(table_name, table_a.get('constraints', []), table_b.get('constraints', []))
    
    def _compare_column_properties(self, column_a: Dict, column_b: Dict) -> Dict[str, Tuple]:
        """Compare properties of two columns."""
        changes = {}
        
        # Properties to compare
        properties = [
            'data_type', 'max_length', 'precision', 'scale', 
            'is_nullable', 'default_value', 'is_identity'
        ]
        
        for prop in properties:
            val_a = column_a.get(prop)
            val_b = column_b.get(prop)
            
            if val_a != val_b:
                changes[prop] = (val_a, val_b)
        
        return changes
    
    def _assess_column_change_impact(self, changes: Dict) -> str:
        """Assess the impact level of column changes."""
        critical_changes = {'data_type', 'max_length', 'precision', 'is_nullable'}
        medium_changes = {'default_value', 'scale'}
        
        if any(change in critical_changes for change in changes.keys()):
            return "critical"
        elif any(change in medium_changes for change in changes.keys()):
            return "medium"
        else:
            return "low"
    
    def _compare_table_indexes(self, table_name: str, indexes_a: List[Dict], indexes_b: List[Dict]):
        """Compare table indexes."""
        indexes_a_dict = {idx.get('index_name'): idx for idx in indexes_a}
        indexes_b_dict = {idx.get('index_name'): idx for idx in indexes_b}
        
        all_index_names = set(indexes_a_dict.keys()) | set(indexes_b_dict.keys())
        
        for index_name in all_index_names:
            index_a = indexes_a_dict.get(index_name)
            index_b = indexes_b_dict.get(index_name)
            
            if index_a and not index_b:
                self.changes.append(SchemaChange(
                    object_type="index",
                    object_name=f"{table_name}.{index_name}",
                    change_type=ChangeType.REMOVED,
                    details={"index_info": index_a, "table_name": table_name},
                    impact_level="medium",
                    description=f"Index {index_name} removed from table {table_name}"
                ))
            elif index_b and not index_a:
                self.changes.append(SchemaChange(
                    object_type="index",
                    object_name=f"{table_name}.{index_name}",
                    change_type=ChangeType.ADDED,
                    details={"index_info": index_b, "table_name": table_name},
                    impact_level="low",
                    description=f"Index {index_name} added to table {table_name}"
                ))
    
    def _compare_table_constraints(self, table_name: str, constraints_a: List[Dict], constraints_b: List[Dict]):
        """Compare table constraints."""
        constraints_a_dict = {c.get('constraint_name'): c for c in constraints_a}
        constraints_b_dict = {c.get('constraint_name'): c for c in constraints_b}
        
        all_constraint_names = set(constraints_a_dict.keys()) | set(constraints_b_dict.keys())
        
        for constraint_name in all_constraint_names:
            constraint_a = constraints_a_dict.get(constraint_name)
            constraint_b = constraints_b_dict.get(constraint_name)
            
            if constraint_a and not constraint_b:
                impact = "critical" if constraint_a.get('constraint_type') in ['PRIMARY KEY', 'FOREIGN KEY'] else "medium"
                self.changes.append(SchemaChange(
                    object_type="constraint",
                    object_name=f"{table_name}.{constraint_name}",
                    change_type=ChangeType.REMOVED,
                    details={"constraint_info": constraint_a, "table_name": table_name},
                    impact_level=impact,
                    description=f"Constraint {constraint_name} removed from table {table_name}"
                ))
            elif constraint_b and not constraint_a:
                impact = "medium" if constraint_b.get('constraint_type') in ['PRIMARY KEY', 'FOREIGN KEY'] else "low"
                self.changes.append(SchemaChange(
                    object_type="constraint",
                    object_name=f"{table_name}.{constraint_name}",
                    change_type=ChangeType.ADDED,
                    details={"constraint_info": constraint_b, "table_name": table_name},
                    impact_level=impact,
                    description=f"Constraint {constraint_name} added to table {table_name}"
                ))
    
    def _compare_views(self, views_a: List[Dict], views_b: List[Dict]):
        """Compare views between schemas."""
        views_a_dict = {f"{v.get('schema_name', 'dbo')}.{v.get('view_name')}": v for v in views_a}
        views_b_dict = {f"{v.get('schema_name', 'dbo')}.{v.get('view_name')}": v for v in views_b}
        
        all_view_names = set(views_a_dict.keys()) | set(views_b_dict.keys())
        
        for view_name in all_view_names:
            view_a = views_a_dict.get(view_name)
            view_b = views_b_dict.get(view_name)
            
            if view_a and not view_b:
                self.changes.append(SchemaChange(
                    object_type="view",
                    object_name=view_name,
                    change_type=ChangeType.REMOVED,
                    details={"view_info": view_a},
                    impact_level="medium",
                    description=f"View {view_name} has been removed"
                ))
            elif view_b and not view_a:
                self.changes.append(SchemaChange(
                    object_type="view",
                    object_name=view_name,
                    change_type=ChangeType.ADDED,
                    details={"view_info": view_b},
                    impact_level="low",
                    description=f"View {view_name} has been added"
                ))
            elif view_a and view_b:
                # Compare view definitions
                if view_a.get('definition') != view_b.get('definition'):
                    self.changes.append(SchemaChange(
                        object_type="view",
                        object_name=view_name,
                        change_type=ChangeType.MODIFIED,
                        details={
                            "old_definition": view_a.get('definition'),
                            "new_definition": view_b.get('definition')
                        },
                        impact_level="medium",
                        description=f"View {view_name} definition has been modified"
                    ))
    
    def _compare_procedures(self, procedures_a: List[Dict], procedures_b: List[Dict]):
        """Compare stored procedures between schemas."""
        procs_a_dict = {f"{p.get('schema_name', 'dbo')}.{p.get('procedure_name')}": p for p in procedures_a}
        procs_b_dict = {f"{p.get('schema_name', 'dbo')}.{p.get('procedure_name')}": p for p in procedures_b}
        
        all_proc_names = set(procs_a_dict.keys()) | set(procs_b_dict.keys())
        
        for proc_name in all_proc_names:
            proc_a = procs_a_dict.get(proc_name)
            proc_b = procs_b_dict.get(proc_name)
            
            if proc_a and not proc_b:
                self.changes.append(SchemaChange(
                    object_type="procedure",
                    object_name=proc_name,
                    change_type=ChangeType.REMOVED,
                    details={"procedure_info": proc_a},
                    impact_level="high",
                    description=f"Stored procedure {proc_name} has been removed"
                ))
            elif proc_b and not proc_a:
                self.changes.append(SchemaChange(
                    object_type="procedure",
                    object_name=proc_name,
                    change_type=ChangeType.ADDED,
                    details={"procedure_info": proc_b},
                    impact_level="medium",
                    description=f"Stored procedure {proc_name} has been added"
                ))
            elif proc_a and proc_b:
                # Compare procedure definitions
                if proc_a.get('definition') != proc_b.get('definition'):
                    self.changes.append(SchemaChange(
                        object_type="procedure",
                        object_name=proc_name,
                        change_type=ChangeType.MODIFIED,
                        details={
                            "old_definition": proc_a.get('definition'),
                            "new_definition": proc_b.get('definition')
                        },
                        impact_level="high",
                        description=f"Stored procedure {proc_name} definition has been modified"
                    ))
    
    def _compare_functions(self, functions_a: List[Dict], functions_b: List[Dict]):
        """Compare functions between schemas."""
        funcs_a_dict = {f"{f.get('schema_name', 'dbo')}.{f.get('function_name')}": f for f in functions_a}
        funcs_b_dict = {f"{f.get('schema_name', 'dbo')}.{f.get('function_name')}": f for f in functions_b}
        
        all_func_names = set(funcs_a_dict.keys()) | set(funcs_b_dict.keys())
        
        for func_name in all_func_names:
            func_a = funcs_a_dict.get(func_name)
            func_b = funcs_b_dict.get(func_name)
            
            if func_a and not func_b:
                self.changes.append(SchemaChange(
                    object_type="function",
                    object_name=func_name,
                    change_type=ChangeType.REMOVED,
                    details={"function_info": func_a},
                    impact_level="medium",
                    description=f"Function {func_name} has been removed"
                ))
            elif func_b and not func_a:
                self.changes.append(SchemaChange(
                    object_type="function",
                    object_name=func_name,
                    change_type=ChangeType.ADDED,
                    details={"function_info": func_b},
                    impact_level="low",
                    description=f"Function {func_name} has been added"
                ))
    
    def _compare_relationships(self, relationships_a: Dict, relationships_b: Dict):
        """Compare foreign key relationships between schemas."""
        rels_a = relationships_a.get('foreign_keys', [])
        rels_b = relationships_b.get('foreign_keys', [])
        
        # Create unique identifiers for relationships
        rels_a_dict = {}
        for rel in rels_a:
            key = f"{rel.get('table_schema')}.{rel.get('table_name')}.{rel.get('constraint_name')}"
            rels_a_dict[key] = rel
        
        rels_b_dict = {}
        for rel in rels_b:
            key = f"{rel.get('table_schema')}.{rel.get('table_name')}.{rel.get('constraint_name')}"
            rels_b_dict[key] = rel
        
        all_rel_names = set(rels_a_dict.keys()) | set(rels_b_dict.keys())
        
        for rel_name in all_rel_names:
            rel_a = rels_a_dict.get(rel_name)
            rel_b = rels_b_dict.get(rel_name)
            
            if rel_a and not rel_b:
                self.changes.append(SchemaChange(
                    object_type="relationship",
                    object_name=rel_name,
                    change_type=ChangeType.REMOVED,
                    details={"relationship_info": rel_a},
                    impact_level="high",
                    description=f"Foreign key relationship {rel_name} has been removed"
                ))
            elif rel_b and not rel_a:
                self.changes.append(SchemaChange(
                    object_type="relationship",
                    object_name=rel_name,
                    change_type=ChangeType.ADDED,
                    details={"relationship_info": rel_b},
                    impact_level="medium",
                    description=f"Foreign key relationship {rel_name} has been added"
                ))
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all changes."""
        summary = {
            'total_changes': len(self.changes),
            'changes_by_type': {},
            'changes_by_impact': {},
            'objects_affected': set()
        }
        
        for change in self.changes:
            # Count by object type
            obj_type = change.object_type
            if obj_type not in summary['changes_by_type']:
                summary['changes_by_type'][obj_type] = {'added': 0, 'removed': 0, 'modified': 0}
            summary['changes_by_type'][obj_type][change.change_type.value] += 1
            
            # Count by impact level
            impact = change.impact_level
            if impact not in summary['changes_by_impact']:
                summary['changes_by_impact'][impact] = 0
            summary['changes_by_impact'][impact] += 1
            
            # Track affected objects
            summary['objects_affected'].add(change.object_name)
        
        # Convert set to count
        summary['objects_affected'] = len(summary['objects_affected'])
        
        return summary
    
    def _analyze_impact(self) -> Dict[str, Any]:
        """Analyze the impact of all changes."""
        impact_analysis = {
            'overall_risk': 'low',
            'breaking_changes': [],
            'compatibility_issues': [],
            'recommendations': []
        }
        
        critical_count = sum(1 for c in self.changes if c.impact_level == 'critical')
        high_count = sum(1 for c in self.changes if c.impact_level == 'high')
        
        # Assess overall risk
        if critical_count > 0:
            impact_analysis['overall_risk'] = 'critical'
        elif high_count > 5:
            impact_analysis['overall_risk'] = 'high'
        elif high_count > 0:
            impact_analysis['overall_risk'] = 'medium'
        
        # Identify breaking changes
        for change in self.changes:
            if change.change_type == ChangeType.REMOVED and change.object_type in ['table', 'column']:
                impact_analysis['breaking_changes'].append(change.description)
            elif change.impact_level == 'critical':
                impact_analysis['compatibility_issues'].append(change.description)
        
        return impact_analysis
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on the comparison."""
        recommendations = []
        
        # Check for removed tables/columns
        removed_tables = [c for c in self.changes if c.change_type == ChangeType.REMOVED and c.object_type == 'table']
        removed_columns = [c for c in self.changes if c.change_type == ChangeType.REMOVED and c.object_type == 'column']
        
        if removed_tables:
            recommendations.append(f"Consider data migration for {len(removed_tables)} removed table(s)")
        
        if removed_columns:
            recommendations.append(f"Review application code for {len(removed_columns)} removed column(s)")
        
        # Check for data type changes
        type_changes = [c for c in self.changes if c.object_type == 'column' and 
                      c.change_type == ChangeType.MODIFIED and 
                      'data_type' in c.details.get('changes', {})]
        
        if type_changes:
            recommendations.append("Test data compatibility for column data type changes")
        
        # Check for constraint changes
        constraint_changes = [c for c in self.changes if c.object_type == 'constraint']
        if constraint_changes:
            recommendations.append("Validate constraint changes don't violate existing data")
        
        return recommendations
    
    def export_comparison(self, comparison_result: Dict[str, Any], file_path: str):
        """Export comparison results to a file."""
        # Convert enum values to strings for JSON serialization
        serializable_result = self._make_serializable(comparison_result)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_result, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Schema comparison exported to {file_path}")
    
    def _make_serializable(self, obj):
        """Convert object to JSON serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, SchemaChange):
            return {
                'object_type': obj.object_type,
                'object_name': obj.object_name,
                'change_type': obj.change_type.value,
                'details': self._make_serializable(obj.details),
                'impact_level': obj.impact_level,
                'description': obj.description
            }
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj
#!/usr/bin/env python3
"""
Compliance and Security Auditing Module
=====================================

Comprehensive security and compliance auditing tools for database documentation
and schema analysis, including security policy enforcement, compliance reporting,
and vulnerability assessment.

Features:
- Security policy definition and enforcement
- Compliance framework support (GDPR, HIPAA, SOX, PCI-DSS)
- Vulnerability scanning and assessment
- Security audit reporting
- Access control analysis
- Data classification and sensitivity analysis
- Encryption and security configuration checks
"""

import sqlite3
import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from collections import defaultdict, Counter
import threading


class ComplianceDatabase:
    """Manages compliance audit results and security policies database."""
    
    def __init__(self, db_path: str = "compliance.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the compliance database with required tables."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Security policies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    framework TEXT, -- 'GDPR', 'HIPAA', 'SOX', 'PCI-DSS', 'Custom'
                    category TEXT, -- 'access_control', 'data_protection', 'encryption', etc.
                    severity TEXT, -- 'critical', 'high', 'medium', 'low'
                    description TEXT,
                    rule_definition TEXT, -- JSON with rule logic
                    remediation TEXT,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Audit results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    database_name TEXT NOT NULL,
                    policy_id INTEGER,
                    object_name TEXT,
                    object_type TEXT, -- 'TABLE', 'VIEW', 'PROCEDURE', etc.
                    compliance_status TEXT, -- 'compliant', 'non_compliant', 'warning', 'unknown'
                    finding_severity TEXT,
                    finding_description TEXT,
                    evidence TEXT, -- JSON with supporting evidence
                    remediation_required BOOLEAN DEFAULT 0,
                    remediation_steps TEXT,
                    false_positive BOOLEAN DEFAULT 0,
                    acknowledged BOOLEAN DEFAULT 0,
                    acknowledged_by TEXT,
                    acknowledged_timestamp DATETIME,
                    FOREIGN KEY (policy_id) REFERENCES security_policies (id)
                )
            """)
            
            # Compliance reports
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    database_name TEXT NOT NULL,
                    framework TEXT,
                    report_type TEXT, -- 'full_audit', 'delta', 'summary'
                    total_checks INTEGER,
                    compliant_checks INTEGER,
                    non_compliant_checks INTEGER,
                    warning_checks INTEGER,
                    overall_score REAL, -- compliance score 0-100
                    report_data TEXT, -- JSON with detailed report data
                    generated_by TEXT
                )
            """)
            
            # Data classification rules
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_classification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    classification_name TEXT NOT NULL,
                    sensitivity_level TEXT, -- 'public', 'internal', 'confidential', 'restricted'
                    detection_rules TEXT, -- JSON with column/data detection patterns
                    protection_requirements TEXT, -- JSON with required protections
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def save_security_policy(self, name: str, framework: str, category: str, 
                           severity: str, description: str, rule_definition: Dict,
                           remediation: str) -> int:
        """Save a security policy."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO security_policies 
                (name, framework, category, severity, description, rule_definition, remediation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, framework, category, severity, description, 
                  json.dumps(rule_definition), remediation))
            
            policy_id = cursor.lastrowid
            conn.commit()
            return policy_id
        finally:
            conn.close()
    
    def get_security_policies(self, framework: str = None, active_only: bool = True) -> List[Dict]:
        """Get security policies, optionally filtered by framework."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            query = "SELECT * FROM security_policies"
            params = []
            conditions = []
            
            if framework:
                conditions.append("framework = ?")
                params.append(framework)
            
            if active_only:
                conditions.append("is_active = 1")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY severity DESC, category, name"
            
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            policies = []
            for row in cursor.fetchall():
                policy = dict(zip(columns, row))
                policy['rule_definition'] = json.loads(policy['rule_definition']) if policy['rule_definition'] else {}
                policies.append(policy)
            return policies
        finally:
            conn.close()
    
    def save_audit_results(self, results: List[Dict]) -> None:
        """Save audit results to database."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            for result in results:
                cursor.execute("""
                    INSERT INTO audit_results 
                    (database_name, policy_id, object_name, object_type, compliance_status,
                     finding_severity, finding_description, evidence, remediation_required,
                     remediation_steps)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result['database_name'],
                    result.get('policy_id'),
                    result.get('object_name'),
                    result.get('object_type'),
                    result['compliance_status'],
                    result.get('finding_severity'),
                    result.get('finding_description'),
                    json.dumps(result.get('evidence', {})),
                    result.get('remediation_required', False),
                    result.get('remediation_steps')
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_audit_results(self, database_name: str = None, days: int = 30) -> List[Dict]:
        """Get recent audit results."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT ar.*, sp.name as policy_name, sp.framework
                FROM audit_results ar
                LEFT JOIN security_policies sp ON ar.policy_id = sp.id
                WHERE ar.audit_timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if database_name:
                query += " AND ar.database_name = ?"
                params.append(database_name)
            
            query += " ORDER BY ar.audit_timestamp DESC, ar.finding_severity DESC"
            
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                result['evidence'] = json.loads(result['evidence']) if result['evidence'] else {}
                results.append(result)
            return results
        finally:
            conn.close()


class SecurityPolicyEngine:
    """Engine for defining and evaluating security policies."""
    
    def __init__(self):
        self.policy_rules = {
            'column_naming': self._check_column_naming,
            'sensitive_data': self._check_sensitive_data,
            'encryption': self._check_encryption_requirements,
            'access_control': self._check_access_control,
            'data_retention': self._check_data_retention,
            'audit_trails': self._check_audit_trails,
            'primary_keys': self._check_primary_keys,
            'foreign_keys': self._check_foreign_keys,
            'data_masking': self._check_data_masking,
            'backup_encryption': self._check_backup_encryption
        }
        
        # Predefined compliance frameworks
        self.compliance_frameworks = self._load_compliance_frameworks()
    
    def _load_compliance_frameworks(self) -> Dict[str, List[Dict]]:
        """Load predefined compliance framework policies."""
        return {
            'GDPR': [
                {
                    'name': 'Personal Data Identification',
                    'category': 'data_protection',
                    'severity': 'critical',
                    'description': 'Identify columns containing personal data that require GDPR protection',
                    'rule_definition': {
                        'rule_type': 'sensitive_data',
                        'patterns': ['name', 'email', 'phone', 'address', 'ssn', 'birthdate'],
                        'data_types': ['varchar', 'nvarchar', 'text']
                    },
                    'remediation': 'Implement data masking, encryption, or access controls for personal data'
                },
                {
                    'name': 'Right to be Forgotten',
                    'category': 'data_retention',
                    'severity': 'high',
                    'description': 'Ensure tables with personal data support deletion/anonymization',
                    'rule_definition': {
                        'rule_type': 'data_retention',
                        'requires_delete_capability': True
                    },
                    'remediation': 'Add delete/update procedures for personal data tables'
                },
                {
                    'name': 'Data Processing Audit Trail',
                    'category': 'audit_trails',
                    'severity': 'medium',
                    'description': 'Tables with personal data should have audit trail capabilities',
                    'rule_definition': {
                        'rule_type': 'audit_trails',
                        'required_columns': ['created_date', 'modified_date', 'created_by', 'modified_by']
                    },
                    'remediation': 'Add audit columns to track data processing activities'
                }
            ],
            'HIPAA': [
                {
                    'name': 'PHI Data Encryption',
                    'category': 'encryption',
                    'severity': 'critical',
                    'description': 'Protected Health Information must be encrypted',
                    'rule_definition': {
                        'rule_type': 'encryption',
                        'phi_patterns': ['medical', 'health', 'patient', 'diagnosis', 'treatment'],
                        'encryption_required': True
                    },
                    'remediation': 'Enable Transparent Data Encryption (TDE) or column-level encryption'
                },
                {
                    'name': 'PHI Access Controls',
                    'category': 'access_control',
                    'severity': 'critical',
                    'description': 'PHI data requires role-based access controls',
                    'rule_definition': {
                        'rule_type': 'access_control',
                        'minimum_access_level': 'role_based'
                    },
                    'remediation': 'Implement role-based security and row-level security where appropriate'
                }
            ],
            'PCI-DSS': [
                {
                    'name': 'Credit Card Data Protection',
                    'category': 'data_protection',
                    'severity': 'critical',
                    'description': 'Credit card data must be properly protected',
                    'rule_definition': {
                        'rule_type': 'sensitive_data',
                        'patterns': ['card', 'credit', 'ccv', 'cvv', 'pan', 'expiry'],
                        'protection_required': True
                    },
                    'remediation': 'Implement tokenization or encryption for credit card data'
                },
                {
                    'name': 'PAN Data Masking',
                    'category': 'data_masking',
                    'severity': 'high',
                    'description': 'Primary Account Numbers should be masked in non-production environments',
                    'rule_definition': {
                        'rule_type': 'data_masking',
                        'column_patterns': ['pan', 'card_number', 'account_number']
                    },
                    'remediation': 'Implement data masking for PAN data in development/test environments'
                }
            ],
            'SOX': [
                {
                    'name': 'Financial Data Integrity',
                    'category': 'data_integrity',
                    'severity': 'high',
                    'description': 'Financial data must have integrity controls',
                    'rule_definition': {
                        'rule_type': 'audit_trails',
                        'financial_patterns': ['revenue', 'expense', 'asset', 'liability', 'financial'],
                        'change_tracking_required': True
                    },
                    'remediation': 'Enable change data capture or audit triggers on financial tables'
                },
                {
                    'name': 'Segregation of Duties',
                    'category': 'access_control',
                    'severity': 'medium',
                    'description': 'Financial data access should follow segregation of duties principle',
                    'rule_definition': {
                        'rule_type': 'access_control',
                        'segregation_required': True
                    },
                    'remediation': 'Implement role separation for financial data access and modifications'
                }
            ]
        }
    
    def evaluate_policy(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Evaluate a security policy against schema data."""
        rule_type = policy['rule_definition'].get('rule_type')
        
        if rule_type in self.policy_rules:
            return self.policy_rules[rule_type](policy, schema_data)
        else:
            return [{
                'policy_id': policy.get('id'),
                'compliance_status': 'unknown',
                'finding_description': f"Unknown rule type: {rule_type}",
                'finding_severity': 'low'
            }]
    
    def _check_column_naming(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check column naming compliance."""
        results = []
        rule_def = policy['rule_definition']
        required_patterns = rule_def.get('required_patterns', [])
        forbidden_patterns = rule_def.get('forbidden_patterns', [])
        
        for table in schema_data.get('tables', []):
            table_name = table['table_name']
            
            for column in table.get('columns', []):
                column_name = column['column_name'].lower()
                
                # Check required patterns
                for pattern in required_patterns:
                    if pattern.lower() in column_name:
                        results.append({
                            'policy_id': policy.get('id'),
                            'object_name': f"{table_name}.{column['column_name']}",
                            'object_type': 'COLUMN',
                            'compliance_status': 'compliant',
                            'finding_description': f"Column follows naming convention: {pattern}",
                            'finding_severity': 'low'
                        })
                
                # Check forbidden patterns
                for pattern in forbidden_patterns:
                    if pattern.lower() in column_name:
                        results.append({
                            'policy_id': policy.get('id'),
                            'object_name': f"{table_name}.{column['column_name']}",
                            'object_type': 'COLUMN',
                            'compliance_status': 'non_compliant',
                            'finding_description': f"Column uses forbidden naming pattern: {pattern}",
                            'finding_severity': 'medium',
                            'remediation_required': True,
                            'remediation_steps': f"Rename column to avoid forbidden pattern: {pattern}"
                        })
        
        return results
    
    def _check_sensitive_data(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check for sensitive data that requires protection."""
        results = []
        rule_def = policy['rule_definition']
        patterns = rule_def.get('patterns', [])
        data_types = rule_def.get('data_types', [])
        
        for table in schema_data.get('tables', []):
            table_name = table['table_name']
            
            for column in table.get('columns', []):
                column_name = column['column_name'].lower()
                column_type = column.get('data_type', '').lower()
                
                # Check if column matches sensitive data patterns
                is_sensitive = False
                matched_pattern = None
                
                for pattern in patterns:
                    if pattern.lower() in column_name:
                        is_sensitive = True
                        matched_pattern = pattern
                        break
                
                # Also check data types if specified
                if data_types and column_type in [dt.lower() for dt in data_types]:
                    is_sensitive = True
                
                if is_sensitive:
                    # Check if protection is in place (this would need actual database inspection)
                    has_protection = self._check_column_protection(table_name, column)
                    
                    status = 'compliant' if has_protection else 'non_compliant'
                    severity = 'critical' if not has_protection else 'low'
                    
                    results.append({
                        'policy_id': policy.get('id'),
                        'object_name': f"{table_name}.{column['column_name']}",
                        'object_type': 'COLUMN',
                        'compliance_status': status,
                        'finding_description': f"Sensitive data column detected: {matched_pattern or 'data type match'}",
                        'finding_severity': severity,
                        'evidence': {
                            'column_name': column['column_name'],
                            'data_type': column.get('data_type'),
                            'matched_pattern': matched_pattern,
                            'has_protection': has_protection
                        },
                        'remediation_required': not has_protection,
                        'remediation_steps': 'Implement encryption, masking, or access controls for sensitive data'
                    })
        
        return results
    
    def _check_column_protection(self, table_name: str, column: Dict) -> bool:
        """Check if a column has protection mechanisms (placeholder - would need actual DB inspection)."""
        # This would need to query the actual database for:
        # - Column encryption
        # - Row-level security
        # - Data masking
        # - Access control policies
        
        # For now, return False to highlight potential issues
        return False
    
    def _check_encryption_requirements(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check encryption requirements."""
        results = []
        rule_def = policy['rule_definition']
        encryption_required = rule_def.get('encryption_required', False)
        patterns = rule_def.get('phi_patterns', rule_def.get('patterns', []))
        
        if not encryption_required:
            return results
        
        for table in schema_data.get('tables', []):
            table_name = table['table_name'].lower()
            
            # Check if table contains data requiring encryption
            requires_encryption = False
            matched_patterns = []
            
            for pattern in patterns:
                if pattern.lower() in table_name:
                    requires_encryption = True
                    matched_patterns.append(pattern)
            
            # Also check column names
            for column in table.get('columns', []):
                column_name = column['column_name'].lower()
                for pattern in patterns:
                    if pattern.lower() in column_name:
                        requires_encryption = True
                        matched_patterns.append(pattern)
            
            if requires_encryption:
                # Check if encryption is enabled (placeholder)
                has_encryption = self._check_table_encryption(table_name)
                
                status = 'compliant' if has_encryption else 'non_compliant'
                severity = 'critical' if not has_encryption else 'low'
                
                results.append({
                    'policy_id': policy.get('id'),
                    'object_name': table['table_name'],
                    'object_type': 'TABLE',
                    'compliance_status': status,
                    'finding_description': f"Table requires encryption due to patterns: {', '.join(matched_patterns)}",
                    'finding_severity': severity,
                    'evidence': {
                        'matched_patterns': matched_patterns,
                        'has_encryption': has_encryption
                    },
                    'remediation_required': not has_encryption,
                    'remediation_steps': 'Enable Transparent Data Encryption (TDE) or Always Encrypted for sensitive tables'
                })
        
        return results
    
    def _check_table_encryption(self, table_name: str) -> bool:
        """Check if a table has encryption enabled (placeholder)."""
        # This would need to query sys.dm_database_encryption_keys or similar
        return False
    
    def _check_access_control(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check access control requirements."""
        results = []
        rule_def = policy['rule_definition']
        minimum_access_level = rule_def.get('minimum_access_level', 'basic')
        
        # This would need actual database permission analysis
        # For now, generate warnings for all tables
        
        for table in schema_data.get('tables', []):
            results.append({
                'policy_id': policy.get('id'),
                'object_name': table['table_name'],
                'object_type': 'TABLE',
                'compliance_status': 'warning',
                'finding_description': f"Access control validation required (minimum level: {minimum_access_level})",
                'finding_severity': 'medium',
                'evidence': {
                    'required_access_level': minimum_access_level
                },
                'remediation_required': False,
                'remediation_steps': 'Review and validate access control permissions for this table'
            })
        
        return results
    
    def _check_data_retention(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check data retention policy compliance."""
        results = []
        rule_def = policy['rule_definition']
        requires_delete_capability = rule_def.get('requires_delete_capability', False)
        
        if not requires_delete_capability:
            return results
        
        for table in schema_data.get('tables', []):
            table_name = table['table_name']
            
            # Check if table has delete/update capabilities
            has_primary_key = any(col.get('is_primary_key') for col in table.get('columns', []))
            
            # Check for soft delete columns
            has_soft_delete = any(
                col['column_name'].lower() in ['deleted', 'is_deleted', 'deleted_at', 'archived']
                for col in table.get('columns', [])
            )
            
            compliance_status = 'compliant' if (has_primary_key or has_soft_delete) else 'non_compliant'
            severity = 'high' if not (has_primary_key or has_soft_delete) else 'low'
            
            results.append({
                'policy_id': policy.get('id'),
                'object_name': table_name,
                'object_type': 'TABLE',
                'compliance_status': compliance_status,
                'finding_description': 'Table requires data retention/deletion capability',
                'finding_severity': severity,
                'evidence': {
                    'has_primary_key': has_primary_key,
                    'has_soft_delete_columns': has_soft_delete
                },
                'remediation_required': not (has_primary_key or has_soft_delete),
                'remediation_steps': 'Add primary key or soft delete columns to support data retention policies'
            })
        
        return results
    
    def _check_audit_trails(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check audit trail requirements."""
        results = []
        rule_def = policy['rule_definition']
        required_columns = rule_def.get('required_columns', [])
        financial_patterns = rule_def.get('financial_patterns', [])
        
        for table in schema_data.get('tables', []):
            table_name = table['table_name'].lower()
            
            # Check if table requires audit trails
            requires_audit = False
            if financial_patterns:
                for pattern in financial_patterns:
                    if pattern.lower() in table_name:
                        requires_audit = True
                        break
            else:
                requires_audit = True  # All tables if no patterns specified
            
            if requires_audit:
                existing_columns = [col['column_name'].lower() for col in table.get('columns', [])]
                missing_columns = []
                
                for req_col in required_columns:
                    if req_col.lower() not in existing_columns:
                        missing_columns.append(req_col)
                
                compliance_status = 'compliant' if not missing_columns else 'non_compliant'
                severity = 'medium' if missing_columns else 'low'
                
                results.append({
                    'policy_id': policy.get('id'),
                    'object_name': table['table_name'],
                    'object_type': 'TABLE',
                    'compliance_status': compliance_status,
                    'finding_description': f"Audit trail validation - Missing columns: {', '.join(missing_columns)}" if missing_columns else "Audit trail columns present",
                    'finding_severity': severity,
                    'evidence': {
                        'required_columns': required_columns,
                        'existing_columns': [col['column_name'] for col in table.get('columns', [])],
                        'missing_columns': missing_columns
                    },
                    'remediation_required': len(missing_columns) > 0,
                    'remediation_steps': f"Add missing audit columns: {', '.join(missing_columns)}" if missing_columns else None
                })
        
        return results
    
    def _check_primary_keys(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check primary key requirements."""
        results = []
        
        for table in schema_data.get('tables', []):
            has_primary_key = any(
                col.get('is_primary_key') or 'PRIMARY KEY' in str(col.get('constraints', ''))
                for col in table.get('columns', [])
            )
            
            compliance_status = 'compliant' if has_primary_key else 'non_compliant'
            severity = 'medium' if not has_primary_key else 'low'
            
            results.append({
                'policy_id': policy.get('id'),
                'object_name': table['table_name'],
                'object_type': 'TABLE',
                'compliance_status': compliance_status,
                'finding_description': 'Primary key validation',
                'finding_severity': severity,
                'evidence': {
                    'has_primary_key': has_primary_key
                },
                'remediation_required': not has_primary_key,
                'remediation_steps': 'Add a primary key to ensure data integrity and performance'
            })
        
        return results
    
    def _check_foreign_keys(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check foreign key constraints."""
        results = []
        
        relationships = schema_data.get('relationships', {})
        foreign_keys = relationships.get('foreign_keys', [])
        
        # This is a basic check - could be enhanced with more sophisticated analysis
        fk_count = len(foreign_keys)
        table_count = len(schema_data.get('tables', []))
        
        if table_count > 1 and fk_count == 0:
            results.append({
                'policy_id': policy.get('id'),
                'object_name': 'Database Schema',
                'object_type': 'SCHEMA',
                'compliance_status': 'warning',
                'finding_description': 'No foreign key relationships found in multi-table schema',
                'finding_severity': 'medium',
                'evidence': {
                    'table_count': table_count,
                    'foreign_key_count': fk_count
                },
                'remediation_required': False,
                'remediation_steps': 'Review table relationships and add foreign key constraints where appropriate'
            })
        
        return results
    
    def _check_data_masking(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check data masking requirements."""
        results = []
        rule_def = policy['rule_definition']
        column_patterns = rule_def.get('column_patterns', [])
        
        for table in schema_data.get('tables', []):
            for column in table.get('columns', []):
                column_name = column['column_name'].lower()
                
                for pattern in column_patterns:
                    if pattern.lower() in column_name:
                        # Check if masking is in place (placeholder)
                        has_masking = self._check_column_masking(table['table_name'], column['column_name'])
                        
                        compliance_status = 'compliant' if has_masking else 'non_compliant'
                        severity = 'high' if not has_masking else 'low'
                        
                        results.append({
                            'policy_id': policy.get('id'),
                            'object_name': f"{table['table_name']}.{column['column_name']}",
                            'object_type': 'COLUMN',
                            'compliance_status': compliance_status,
                            'finding_description': f"Data masking required for pattern: {pattern}",
                            'finding_severity': severity,
                            'evidence': {
                                'column_pattern': pattern,
                                'has_masking': has_masking
                            },
                            'remediation_required': not has_masking,
                            'remediation_steps': 'Implement data masking for sensitive columns in non-production environments'
                        })
        
        return results
    
    def _check_column_masking(self, table_name: str, column_name: str) -> bool:
        """Check if column has data masking (placeholder)."""
        # This would check actual masking policies in the database
        return False
    
    def _check_backup_encryption(self, policy: Dict, schema_data: Dict) -> List[Dict]:
        """Check backup encryption requirements."""
        results = []
        
        # This would need to check actual backup configuration
        # For now, generate a general finding
        results.append({
            'policy_id': policy.get('id'),
            'object_name': 'Database Backups',
            'object_type': 'BACKUP',
            'compliance_status': 'warning',
            'finding_description': 'Backup encryption validation required',
            'finding_severity': 'medium',
            'evidence': {},
            'remediation_required': False,
            'remediation_steps': 'Verify that database backups are encrypted and stored securely'
        })
        
        return results


class ComplianceAuditor:
    """Main compliance auditing engine."""
    
    def __init__(self):
        self.db = ComplianceDatabase()
        self.policy_engine = SecurityPolicyEngine()
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default compliance policies."""
        try:
            for framework, policies in self.policy_engine.compliance_frameworks.items():
                for policy in policies:
                    self.db.save_security_policy(
                        name=policy['name'],
                        framework=framework,
                        category=policy['category'],
                        severity=policy['severity'],
                        description=policy['description'],
                        rule_definition=policy['rule_definition'],
                        remediation=policy['remediation']
                    )
        except Exception as e:
            print(f"Error initializing default policies: {e}")
    
    def run_compliance_audit(self, database_name: str, schema_data: Dict, 
                           frameworks: List[str] = None) -> Dict[str, Any]:
        """Run a complete compliance audit."""
        audit_results = []
        
        # Get policies to evaluate
        all_policies = []
        if frameworks:
            for framework in frameworks:
                policies = self.db.get_security_policies(framework=framework)
                all_policies.extend(policies)
        else:
            all_policies = self.db.get_security_policies()
        
        # Evaluate each policy
        for policy in all_policies:
            try:
                policy_results = self.policy_engine.evaluate_policy(policy, schema_data)
                
                # Add common fields to results
                for result in policy_results:
                    result['database_name'] = database_name
                    result['policy_id'] = policy['id']
                    if 'finding_severity' not in result:
                        result['finding_severity'] = policy['severity']
                
                audit_results.extend(policy_results)
                
            except Exception as e:
                # Log policy evaluation error
                audit_results.append({
                    'database_name': database_name,
                    'policy_id': policy['id'],
                    'compliance_status': 'unknown',
                    'finding_description': f"Policy evaluation error: {str(e)}",
                    'finding_severity': 'low',
                    'evidence': {'error': str(e)}
                })
        
        # Save results to database
        self.db.save_audit_results(audit_results)
        
        # Generate summary
        summary = self._generate_audit_summary(audit_results, frameworks or ['All'])
        
        return {
            'audit_timestamp': datetime.now().isoformat(),
            'database_name': database_name,
            'frameworks': frameworks or ['All'],
            'total_policies': len(all_policies),
            'total_findings': len(audit_results),
            'summary': summary,
            'detailed_results': audit_results
        }
    
    def _generate_audit_summary(self, results: List[Dict], frameworks: List[str]) -> Dict[str, Any]:
        """Generate audit summary statistics."""
        status_counts = Counter(result['compliance_status'] for result in results)
        severity_counts = Counter(result['finding_severity'] for result in results)
        
        total_checks = len(results)
        compliant_checks = status_counts.get('compliant', 0)
        non_compliant_checks = status_counts.get('non_compliant', 0)
        warning_checks = status_counts.get('warning', 0)
        
        # Calculate compliance score
        if total_checks > 0:
            compliance_score = (compliant_checks / total_checks) * 100
        else:
            compliance_score = 0
        
        # Risk assessment
        risk_level = 'low'
        if severity_counts.get('critical', 0) > 0:
            risk_level = 'critical'
        elif severity_counts.get('high', 0) > 0:
            risk_level = 'high'
        elif severity_counts.get('medium', 0) > 0:
            risk_level = 'medium'
        
        return {
            'compliance_score': compliance_score,
            'risk_level': risk_level,
            'total_checks': total_checks,
            'compliant_checks': compliant_checks,
            'non_compliant_checks': non_compliant_checks,
            'warning_checks': warning_checks,
            'status_breakdown': dict(status_counts),
            'severity_breakdown': dict(severity_counts),
            'frameworks_audited': frameworks
        }
    
    def generate_compliance_report(self, database_name: str, audit_results: Dict) -> str:
        """Generate a formatted compliance report."""
        summary = audit_results['summary']
        
        report = f"""
COMPLIANCE AUDIT REPORT
=======================

Database: {database_name}
Audit Date: {audit_results['audit_timestamp']}
Frameworks: {', '.join(audit_results['frameworks'])}

EXECUTIVE SUMMARY
-----------------
Overall Compliance Score: {summary['compliance_score']:.1f}%
Risk Level: {summary['risk_level'].upper()}

AUDIT RESULTS
-------------
Total Policies Evaluated: {audit_results['total_policies']}
Total Findings: {audit_results['total_findings']}

Status Breakdown:
- Compliant: {summary['compliant_checks']} ({summary['compliant_checks']/summary['total_checks']*100:.1f}%)
- Non-Compliant: {summary['non_compliant_checks']} ({summary['non_compliant_checks']/summary['total_checks']*100:.1f}%)
- Warnings: {summary['warning_checks']} ({summary['warning_checks']/summary['total_checks']*100:.1f}%)

Severity Breakdown:
"""
        
        for severity, count in summary['severity_breakdown'].items():
            percentage = (count / summary['total_checks']) * 100
            report += f"- {severity.title()}: {count} ({percentage:.1f}%)\n"
        
        report += "\nDETAILED FINDINGS\n"
        report += "-" * 17 + "\n"
        
        # Group findings by severity
        findings_by_severity = defaultdict(list)
        for result in audit_results['detailed_results']:
            findings_by_severity[result['finding_severity']].append(result)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            findings = findings_by_severity.get(severity, [])
            if findings:
                report += f"\n{severity.upper()} SEVERITY FINDINGS:\n"
                for i, finding in enumerate(findings, 1):
                    report += f"{i}. {finding.get('object_name', 'N/A')} ({finding.get('object_type', 'N/A')})\n"
                    report += f"   Status: {finding['compliance_status']}\n"
                    report += f"   Description: {finding.get('finding_description', 'N/A')}\n"
                    if finding.get('remediation_steps'):
                        report += f"   Remediation: {finding['remediation_steps']}\n"
                    report += "\n"
        
        return report


class ComplianceAuditorGUI:
    """GUI for compliance and security auditing."""
    
    def __init__(self, parent):
        self.parent = parent
        self.auditor = ComplianceAuditor()
        self.current_audit_results = None
        self.current_schema_data = None
    
    def create_compliance_tab(self, notebook: ttk.Notebook):
        """Create the compliance auditing tab."""
        # Create main frame
        compliance_frame = ttk.Frame(notebook)
        notebook.add(compliance_frame, text="🔒 Compliance & Security")
        
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(compliance_frame)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Audit configuration tab
        self.create_audit_config_tab(sub_notebook)
        
        # Policy management tab
        self.create_policy_management_tab(sub_notebook)
        
        # Audit results tab
        self.create_audit_results_tab(sub_notebook)
        
        # Compliance reports tab
        self.create_reports_tab(sub_notebook)
    
    def create_audit_config_tab(self, notebook: ttk.Notebook):
        """Create audit configuration tab."""
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Audit Configuration")
        
        # Schema selection
        schema_frame = ttk.LabelFrame(config_frame, text="Schema Selection", padding="10")
        schema_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(schema_frame, text="Database Schema:").pack(anchor='w')
        self.schema_var = tk.StringVar()
        schema_combo = ttk.Combobox(schema_frame, textvariable=self.schema_var, state="readonly", width=50)
        schema_combo.pack(fill='x', pady=5)
        
        ttk.Button(schema_frame, text="Load Schema from File", command=self.load_schema).pack(pady=5)
        
        # Framework selection
        framework_frame = ttk.LabelFrame(config_frame, text="Compliance Frameworks", padding="10")
        framework_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.framework_vars = {}
        frameworks = ['GDPR', 'HIPAA', 'PCI-DSS', 'SOX', 'Custom']
        
        for framework in frameworks:
            var = tk.BooleanVar()
            self.framework_vars[framework] = var
            ttk.Checkbutton(framework_frame, text=framework, variable=var).pack(anchor='w', pady=2)
        
        # Additional options
        options_frame = ttk.LabelFrame(config_frame, text="Audit Options", padding="10")
        options_frame.pack(fill='x', padx=5, pady=5)
        
        self.include_warnings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include warnings in results", 
                       variable=self.include_warnings_var).pack(anchor='w')
        
        self.detailed_evidence_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Collect detailed evidence", 
                       variable=self.detailed_evidence_var).pack(anchor='w')
        
        # Run audit button
        ttk.Button(config_frame, text="Run Compliance Audit", 
                  command=self.run_audit).pack(pady=20)
    
    def create_policy_management_tab(self, notebook: ttk.Notebook):
        """Create policy management tab."""
        policy_frame = ttk.Frame(notebook)
        notebook.add(policy_frame, text="Security Policies")
        
        # Policy list
        list_frame = ttk.LabelFrame(policy_frame, text="Security Policies", padding="5")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Policy treeview
        columns = ('Name', 'Framework', 'Category', 'Severity', 'Status')
        self.policy_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.policy_tree.heading(col, text=col)
            if col == 'Name':
                self.policy_tree.column(col, width=200)
            else:
                self.policy_tree.column(col, width=100)
        
        # Add scrollbars
        policy_v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.policy_tree.yview)
        policy_h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.policy_tree.xview)
        self.policy_tree.configure(yscrollcommand=policy_v_scrollbar.set, xscrollcommand=policy_h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.policy_tree.pack(side='left', fill='both', expand=True)
        policy_v_scrollbar.pack(side='right', fill='y')
        policy_h_scrollbar.pack(side='bottom', fill='x')
        
        # Policy buttons
        button_frame = ttk.Frame(policy_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Refresh Policies", command=self.refresh_policies).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Add Custom Policy", command=self.add_custom_policy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Policy", command=self.edit_policy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Disable Policy", command=self.disable_policy).pack(side='left', padx=5)
        
        # Load initial policies
        self.refresh_policies()
    
    def create_audit_results_tab(self, notebook: ttk.Notebook):
        """Create audit results tab."""
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Audit Results")
        
        # Results summary
        summary_frame = ttk.LabelFrame(results_frame, text="Audit Summary", padding="10")
        summary_frame.pack(fill='x', padx=5, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=6, state='disabled')
        self.summary_text.pack(fill='x')
        
        # Detailed results
        details_frame = ttk.LabelFrame(results_frame, text="Detailed Findings", padding="5")
        details_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results treeview
        result_columns = ('Status', 'Severity', 'Object', 'Type', 'Policy', 'Description')
        self.results_tree = ttk.Treeview(details_frame, columns=result_columns, show='headings', height=15)
        
        for col in result_columns:
            self.results_tree.heading(col, text=col)
            if col == 'Description':
                self.results_tree.column(col, width=300)
            else:
                self.results_tree.column(col, width=100)
        
        # Add scrollbars
        results_v_scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.results_tree.yview)
        results_h_scrollbar = ttk.Scrollbar(details_frame, orient='horizontal', command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=results_v_scrollbar.set, xscrollcommand=results_h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.results_tree.pack(side='left', fill='both', expand=True)
        results_v_scrollbar.pack(side='right', fill='y')
        results_h_scrollbar.pack(side='bottom', fill='x')
        
        # Results actions
        actions_frame = ttk.Frame(results_frame)
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(actions_frame, text="View Details", command=self.view_finding_details).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Mark as False Positive", command=self.mark_false_positive).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Acknowledge Finding", command=self.acknowledge_finding).pack(side='left', padx=5)
        ttk.Button(actions_frame, text="Export Results", command=self.export_results).pack(side='right', padx=5)
    
    def create_reports_tab(self, notebook: ttk.Notebook):
        """Create compliance reports tab."""
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Compliance Reports")
        
        # Report generation
        generation_frame = ttk.LabelFrame(reports_frame, text="Generate Report", padding="10")
        generation_frame.pack(fill='x', padx=5, pady=5)
        
        # Report type selection
        type_frame = ttk.Frame(generation_frame)
        type_frame.pack(fill='x', pady=5)
        
        ttk.Label(type_frame, text="Report Type:").pack(side='left')
        self.report_type_var = tk.StringVar(value="full")
        report_types = [("Full Compliance Report", "full"), ("Executive Summary", "summary"), ("Finding Details", "details")]
        for text, value in report_types:
            ttk.Radiobutton(type_frame, text=text, variable=self.report_type_var, value=value).pack(side='left', padx=10)
        
        # Generate button
        ttk.Button(generation_frame, text="Generate Report", command=self.generate_report).pack(pady=10)
        
        # Report display
        display_frame = ttk.LabelFrame(reports_frame, text="Generated Report", padding="5")
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(display_frame, wrap='word', font=('Consolas', 10))
        self.report_text.pack(fill='both', expand=True)
        
        # Report actions
        report_actions_frame = ttk.Frame(reports_frame)
        report_actions_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(report_actions_frame, text="Save Report", command=self.save_report).pack(side='left', padx=5)
        ttk.Button(report_actions_frame, text="Print Report", command=self.print_report).pack(side='left', padx=5)
        ttk.Button(report_actions_frame, text="Email Report", command=self.email_report).pack(side='left', padx=5)
    
    def load_schema(self):
        """Load schema data from file."""
        filename = filedialog.askopenfilename(
            title="Load Schema Data",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.current_schema_data = json.load(f)
                
                db_name = self.current_schema_data.get('database_info', {}).get('database_name', 'Unknown')
                self.schema_var.set(f"{db_name} (from file)")
                messagebox.showinfo("Success", "Schema data loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load schema data: {str(e)}")
    
    def run_audit(self):
        """Run compliance audit."""
        if not self.current_schema_data:
            messagebox.showwarning("No Schema", "Please load schema data first")
            return
        
        # Get selected frameworks
        selected_frameworks = [
            framework for framework, var in self.framework_vars.items()
            if var.get()
        ]
        
        if not selected_frameworks:
            messagebox.showwarning("No Frameworks", "Please select at least one compliance framework")
            return
        
        try:
            # Show progress
            progress_dialog = AuditProgressDialog(self.parent)
            
            def run_audit_thread():
                try:
                    database_name = self.current_schema_data.get('database_info', {}).get('database_name', 'Unknown')
                    
                    # Run audit
                    audit_results = self.auditor.run_compliance_audit(
                        database_name=database_name,
                        schema_data=self.current_schema_data,
                        frameworks=selected_frameworks
                    )
                    
                    # Update UI with results
                    self.parent.after(0, lambda: self._update_audit_results(audit_results))
                    self.parent.after(0, progress_dialog.close)
                    
                except Exception as e:
                    self.parent.after(0, lambda: messagebox.showerror("Audit Failed", str(e)))
                    self.parent.after(0, progress_dialog.close)
            
            # Start audit in background thread
            thread = threading.Thread(target=run_audit_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start audit: {str(e)}")
    
    def _update_audit_results(self, audit_results: Dict):
        """Update GUI with audit results."""
        self.current_audit_results = audit_results
        
        # Update summary
        summary = audit_results['summary']
        summary_text = f"""Audit completed for {audit_results['database_name']}
Frameworks: {', '.join(audit_results['frameworks'])}
Total Policies: {audit_results['total_policies']}
Overall Compliance Score: {summary['compliance_score']:.1f}%
Risk Level: {summary['risk_level'].upper()}

Status Breakdown:
- Compliant: {summary['compliant_checks']}
- Non-Compliant: {summary['non_compliant_checks']} 
- Warnings: {summary['warning_checks']}"""
        
        self.summary_text.configure(state='normal')
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary_text)
        self.summary_text.configure(state='disabled')
        
        # Update results tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for result in audit_results['detailed_results']:
            self.results_tree.insert('', 'end', values=(
                result['compliance_status'],
                result['finding_severity'],
                result.get('object_name', 'N/A'),
                result.get('object_type', 'N/A'),
                result.get('policy_name', 'Unknown'),
                result.get('finding_description', '')[:100] + "..." if len(result.get('finding_description', '')) > 100 else result.get('finding_description', '')
            ))
        
        messagebox.showinfo("Audit Complete", f"Compliance audit completed successfully.\nOverall Score: {summary['compliance_score']:.1f}%")
    
    def refresh_policies(self):
        """Refresh the policy list."""
        try:
            policies = self.auditor.db.get_security_policies()
            
            # Clear existing items
            for item in self.policy_tree.get_children():
                self.policy_tree.delete(item)
            
            # Add policies
            for policy in policies:
                self.policy_tree.insert('', 'end', values=(
                    policy['name'],
                    policy['framework'],
                    policy['category'],
                    policy['severity'],
                    'Active' if policy['is_active'] else 'Inactive'
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load policies: {str(e)}")
    
    def add_custom_policy(self):
        """Add a custom security policy."""
        dialog = CustomPolicyDialog(self.parent)
        if dialog.policy_data:
            try:
                self.auditor.db.save_security_policy(**dialog.policy_data)
                self.refresh_policies()
                messagebox.showinfo("Success", "Custom policy added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add policy: {str(e)}")
    
    def edit_policy(self):
        """Edit selected policy (placeholder)."""
        messagebox.showinfo("Not Implemented", "Policy editing functionality to be implemented")
    
    def disable_policy(self):
        """Disable selected policy (placeholder)."""
        messagebox.showinfo("Not Implemented", "Policy disable functionality to be implemented")
    
    def view_finding_details(self):
        """View details of selected finding."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a finding to view details")
            return
        
        # Get the finding data
        item_values = self.results_tree.item(selection[0])['values']
        
        # Find the corresponding result
        if self.current_audit_results:
            for result in self.current_audit_results['detailed_results']:
                if (result.get('object_name') == item_values[2] and 
                    result.get('compliance_status') == item_values[0]):
                    FindingDetailsDialog(self.parent, result)
                    break
    
    def mark_false_positive(self):
        """Mark finding as false positive (placeholder)."""
        messagebox.showinfo("Not Implemented", "False positive marking to be implemented")
    
    def acknowledge_finding(self):
        """Acknowledge finding (placeholder)."""
        messagebox.showinfo("Not Implemented", "Finding acknowledgment to be implemented")
    
    def export_results(self):
        """Export audit results."""
        if not self.current_audit_results:
            messagebox.showwarning("No Results", "No audit results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Audit Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.csv'):
                    self._export_results_csv(filename)
                else:
                    self._export_results_json(filename)
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def _export_results_json(self, filename: str):
        """Export results as JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.current_audit_results, f, indent=2)
    
    def _export_results_csv(self, filename: str):
        """Export results as CSV."""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Status', 'Severity', 'Object', 'Type', 'Policy', 'Description', 'Remediation'])
            
            # Write results
            for result in self.current_audit_results['detailed_results']:
                writer.writerow([
                    result['compliance_status'],
                    result['finding_severity'],
                    result.get('object_name', ''),
                    result.get('object_type', ''),
                    result.get('policy_name', ''),
                    result.get('finding_description', ''),
                    result.get('remediation_steps', '')
                ])
    
    def generate_report(self):
        """Generate compliance report."""
        if not self.current_audit_results:
            messagebox.showwarning("No Results", "Please run an audit first to generate a report")
            return
        
        try:
            database_name = self.current_audit_results['database_name']
            report_type = self.report_type_var.get()
            
            if report_type == "full":
                report_content = self.auditor.generate_compliance_report(database_name, self.current_audit_results)
            elif report_type == "summary":
                report_content = self._generate_executive_summary()
            else:  # details
                report_content = self._generate_finding_details()
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, report_content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary report."""
        summary = self.current_audit_results['summary']
        return f"""EXECUTIVE COMPLIANCE SUMMARY
============================

Database: {self.current_audit_results['database_name']}
Audit Date: {self.current_audit_results['audit_timestamp']}
Frameworks: {', '.join(self.current_audit_results['frameworks'])}

COMPLIANCE SCORE: {summary['compliance_score']:.1f}%
RISK LEVEL: {summary['risk_level'].upper()}

KEY METRICS:
- Total Policies Evaluated: {self.current_audit_results['total_policies']}
- Compliant Findings: {summary['compliant_checks']}
- Non-Compliant Findings: {summary['non_compliant_checks']}
- Warning Findings: {summary['warning_checks']}

RECOMMENDATIONS:
{'• Address critical and high severity findings immediately' if summary['severity_breakdown'].get('critical', 0) > 0 or summary['severity_breakdown'].get('high', 0) > 0 else '• Continue maintaining current compliance levels'}
{'• Review and remediate non-compliant findings' if summary['non_compliant_checks'] > 0 else ''}
{'• Implement regular compliance monitoring' if summary['compliance_score'] < 95 else ''}"""
    
    def _generate_finding_details(self) -> str:
        """Generate finding details report."""
        report = "DETAILED COMPLIANCE FINDINGS\n"
        report += "=" * 30 + "\n\n"
        
        # Group by severity
        findings_by_severity = defaultdict(list)
        for result in self.current_audit_results['detailed_results']:
            findings_by_severity[result['finding_severity']].append(result)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            findings = findings_by_severity.get(severity, [])
            if findings:
                report += f"\n{severity.upper()} SEVERITY FINDINGS:\n"
                report += "-" * (len(severity) + 20) + "\n"
                
                for i, finding in enumerate(findings, 1):
                    report += f"\n{i}. {finding.get('object_name', 'N/A')} ({finding.get('object_type', 'N/A')})\n"
                    report += f"   Status: {finding['compliance_status']}\n"
                    report += f"   Framework: {finding.get('framework', 'N/A')}\n"
                    report += f"   Description: {finding.get('finding_description', 'N/A')}\n"
                    if finding.get('remediation_steps'):
                        report += f"   Remediation: {finding['remediation_steps']}\n"
        
        return report
    
    def save_report(self):
        """Save generated report."""
        content = self.report_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Report", "Please generate a report first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Compliance Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def print_report(self):
        """Print report (placeholder)."""
        messagebox.showinfo("Not Implemented", "Print functionality to be implemented")
    
    def email_report(self):
        """Email report (placeholder)."""
        messagebox.showinfo("Not Implemented", "Email functionality to be implemented")


class AuditProgressDialog:
    """Progress dialog for compliance audits."""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Running Compliance Audit")
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry(f"+{parent.winfo_rootx() + 200}+{parent.winfo_rooty() + 200}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Running compliance audit...", font=("Arial", 12)).pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=10)
        self.progress.start()
        
        ttk.Label(main_frame, text="This may take a few moments.", font=("Arial", 10)).pack()
    
    def close(self):
        """Close the progress dialog."""
        self.progress.stop()
        self.dialog.destroy()


class CustomPolicyDialog:
    """Dialog for creating custom security policies."""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create Custom Policy")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.policy_data = None
        
        # Center dialog
        self.dialog.geometry(f"+{parent.winfo_rootx() + 100}+{parent.winfo_rooty() + 100}")
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Policy name
        ttk.Label(main_frame, text="Policy Name:").pack(anchor="w")
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=60).pack(fill="x", pady=(0, 10))
        
        # Framework
        ttk.Label(main_frame, text="Framework:").pack(anchor="w")
        self.framework_var = tk.StringVar()
        ttk.Combobox(main_frame, textvariable=self.framework_var, 
                    values=["Custom", "GDPR", "HIPAA", "PCI-DSS", "SOX"], 
                    state="readonly").pack(fill="x", pady=(0, 10))
        
        # Category
        ttk.Label(main_frame, text="Category:").pack(anchor="w")
        self.category_var = tk.StringVar()
        ttk.Combobox(main_frame, textvariable=self.category_var,
                    values=["data_protection", "access_control", "encryption", "audit_trails", "data_integrity"],
                    state="readonly").pack(fill="x", pady=(0, 10))
        
        # Severity
        ttk.Label(main_frame, text="Severity:").pack(anchor="w")
        self.severity_var = tk.StringVar()
        ttk.Combobox(main_frame, textvariable=self.severity_var,
                    values=["low", "medium", "high", "critical"],
                    state="readonly").pack(fill="x", pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor="w")
        self.description_text = tk.Text(main_frame, height=4, width=60)
        self.description_text.pack(fill="x", pady=(0, 10))
        
        # Rule definition (simplified)
        ttk.Label(main_frame, text="Rule Type:").pack(anchor="w")
        self.rule_type_var = tk.StringVar()
        ttk.Combobox(main_frame, textvariable=self.rule_type_var,
                    values=["sensitive_data", "column_naming", "primary_keys", "audit_trails"],
                    state="readonly").pack(fill="x", pady=(0, 10))
        
        # Remediation
        ttk.Label(main_frame, text="Remediation Steps:").pack(anchor="w")
        self.remediation_text = tk.Text(main_frame, height=3, width=60)
        self.remediation_text.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Create Policy", command=self.create_policy).pack(side="right")
    
    def create_policy(self):
        """Create the policy."""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a policy name")
            return
        
        framework = self.framework_var.get()
        category = self.category_var.get()
        severity = self.severity_var.get()
        description = self.description_text.get(1.0, tk.END).strip()
        rule_type = self.rule_type_var.get()
        remediation = self.remediation_text.get(1.0, tk.END).strip()
        
        if not all([framework, category, severity, rule_type]):
            messagebox.showwarning("Missing Information", "Please fill in all required fields")
            return
        
        self.policy_data = {
            'name': name,
            'framework': framework,
            'category': category,
            'severity': severity,
            'description': description,
            'rule_definition': {'rule_type': rule_type},
            'remediation': remediation
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel policy creation."""
        self.dialog.destroy()


class FindingDetailsDialog:
    """Dialog for viewing finding details."""
    
    def __init__(self, parent, finding: Dict):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Finding Details")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        
        self.finding = finding
        
        # Center dialog
        self.dialog.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Finding summary
        summary_frame = ttk.LabelFrame(main_frame, text="Finding Summary", padding="10")
        summary_frame.pack(fill="x", pady=(0, 10))
        
        summary_text = f"""Object: {self.finding.get('object_name', 'N/A')}
Type: {self.finding.get('object_type', 'N/A')}
Status: {self.finding['compliance_status']}
Severity: {self.finding['finding_severity']}
Policy: {self.finding.get('policy_name', 'Unknown')}
Framework: {self.finding.get('framework', 'Unknown')}"""
        
        ttk.Label(summary_frame, text=summary_text, font=("Arial", 10)).pack(anchor="w")
        
        # Description
        desc_frame = ttk.LabelFrame(main_frame, text="Description", padding="10")
        desc_frame.pack(fill="x", pady=(0, 10))
        
        desc_text = tk.Text(desc_frame, height=4, wrap="word", state="disabled")
        desc_text.pack(fill="x")
        desc_text.configure(state="normal")
        desc_text.insert(1.0, self.finding.get('finding_description', 'No description available'))
        desc_text.configure(state="disabled")
        
        # Evidence
        if self.finding.get('evidence'):
            evidence_frame = ttk.LabelFrame(main_frame, text="Evidence", padding="10")
            evidence_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            evidence_text = scrolledtext.ScrolledText(evidence_frame, height=8, wrap="word")
            evidence_text.pack(fill="both", expand=True)
            evidence_text.insert(1.0, json.dumps(self.finding['evidence'], indent=2))
        
        # Remediation
        if self.finding.get('remediation_steps'):
            remediation_frame = ttk.LabelFrame(main_frame, text="Remediation Steps", padding="10")
            remediation_frame.pack(fill="x", pady=(0, 10))
            
            remediation_text = tk.Text(remediation_frame, height=4, wrap="word", state="disabled")
            remediation_text.pack(fill="x")
            remediation_text.configure(state="normal")
            remediation_text.insert(1.0, self.finding['remediation_steps'])
            remediation_text.configure(state="disabled")
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=10)


# Test function for standalone execution
if __name__ == "__main__":
    # Test the compliance auditor with sample data
    sample_schema = {
        'database_info': {
            'database_name': 'TestDB',
            'server_name': 'test-server'
        },
        'tables': [
            {
                'table_name': 'Users',
                'columns': [
                    {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO'},
                    {'column_name': 'username', 'data_type': 'varchar', 'max_length': 50, 'is_nullable': 'NO'},
                    {'column_name': 'email', 'data_type': 'varchar', 'max_length': 255, 'is_nullable': 'YES'},
                    {'column_name': 'password_hash', 'data_type': 'varchar', 'max_length': 255, 'is_nullable': 'NO'},
                    {'column_name': 'created_date', 'data_type': 'datetime', 'is_nullable': 'NO'}
                ]
            },
            {
                'table_name': 'PaymentInfo',
                'columns': [
                    {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO'},
                    {'column_name': 'user_id', 'data_type': 'int', 'is_nullable': 'NO'},
                    {'column_name': 'card_number', 'data_type': 'varchar', 'max_length': 19, 'is_nullable': 'NO'},
                    {'column_name': 'cvv', 'data_type': 'varchar', 'max_length': 4, 'is_nullable': 'NO'},
                    {'column_name': 'expiry_date', 'data_type': 'varchar', 'max_length': 7, 'is_nullable': 'NO'}
                ]
            }
        ],
        'views': [],
        'stored_procedures': [],
        'functions': [],
        'relationships': {'foreign_keys': []}
    }
    
    # Initialize auditor
    auditor = ComplianceAuditor()
    
    # Run audit
    results = auditor.run_compliance_audit('TestDB', sample_schema, ['GDPR', 'PCI-DSS'])
    
    print("Compliance Audit Results:")
    print(f"Database: {results['database_name']}")
    print(f"Compliance Score: {results['summary']['compliance_score']:.1f}%")
    print(f"Risk Level: {results['summary']['risk_level']}")
    print(f"Total Findings: {results['total_findings']}")
    
    print("\nFindings:")
    for finding in results['detailed_results']:
        print(f"- {finding['object_name']}: {finding['finding_description']} ({finding['finding_severity']})")
    
    # Generate report
    report = auditor.generate_compliance_report('TestDB', results)
    print("\n" + "="*50)
    print("COMPLIANCE REPORT")
    print("="*50)
    print(report[:1000] + "..." if len(report) > 1000 else report)
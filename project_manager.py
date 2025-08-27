#!/usr/bin/env python3
"""
Multi-Database Project Management System
========================================

Provides comprehensive project workspace management for handling multiple databases,
environments, and complex documentation workflows across enterprise deployments.

Features:
- Project workspace creation and management
- Multi-database coordination and batch operations
- Environment comparison (Dev/Test/Prod)
- Centralized configuration management
- Project templates and presets
- Collaborative project sharing
"""

import os
import json
import shutil
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import hashlib
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class DatabaseProject:
    """Represents a database documentation project."""
    
    def __init__(self, project_data: Dict[str, Any]):
        """Initialize project from data dictionary."""
        self.id = project_data.get('id')
        self.name = project_data.get('name')
        self.description = project_data.get('description', '')
        self.created_at = project_data.get('created_at')
        self.updated_at = project_data.get('updated_at')
        self.databases = project_data.get('databases', [])
        self.environments = project_data.get('environments', [])
        self.settings = project_data.get('settings', {})
        self.metadata = project_data.get('metadata', {})
    
    def add_database(self, database_config: Dict[str, Any]):
        """Add a database to the project."""
        database_config['added_at'] = datetime.now().isoformat()
        self.databases.append(database_config)
        self.updated_at = datetime.now().isoformat()
    
    def remove_database(self, database_id: str) -> bool:
        """Remove a database from the project."""
        original_count = len(self.databases)
        self.databases = [db for db in self.databases if db.get('id') != database_id]
        
        if len(self.databases) < original_count:
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def get_database(self, database_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific database configuration."""
        for db in self.databases:
            if db.get('id') == database_id:
                return db
        return None
    
    def add_environment(self, env_name: str, env_config: Dict[str, Any]):
        """Add an environment configuration."""
        env_data = {
            'name': env_name,
            'config': env_config,
            'created_at': datetime.now().isoformat()
        }
        self.environments.append(env_data)
        self.updated_at = datetime.now().isoformat()
    
    def get_environment(self, env_name: str) -> Optional[Dict[str, Any]]:
        """Get environment configuration."""
        for env in self.environments:
            if env.get('name') == env_name:
                return env
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'databases': self.databases,
            'environments': self.environments,
            'settings': self.settings,
            'metadata': self.metadata
        }


class ProjectManager:
    """Manages database documentation projects."""
    
    def __init__(self, projects_dir: str = "projects"):
        """Initialize the project manager.
        
        Args:
            projects_dir: Directory to store project files
        """
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)
        
        self.projects_db = self.projects_dir / "projects.db"
        self.templates_dir = self.projects_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_projects_db()
        
        # Load project templates
        self._create_default_templates()
    
    def _init_projects_db(self):
        """Initialize the projects database."""
        try:
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                
                # Projects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        project_data TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        tags TEXT
                    )
                ''')
                
                # Project database mappings
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_databases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT NOT NULL,
                        database_id TEXT NOT NULL,
                        database_name TEXT NOT NULL,
                        environment TEXT,
                        connection_config TEXT NOT NULL,
                        last_documented TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                ''')
                
                # Project execution history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT NOT NULL,
                        execution_type TEXT NOT NULL,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        status TEXT NOT NULL,
                        results TEXT,
                        error_message TEXT,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                ''')
                
                # Environment configurations
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_environments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT NOT NULL,
                        environment_name TEXT NOT NULL,
                        environment_config TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize projects database: {e}")
    
    def create_project(self, name: str, description: str = "", 
                      template_name: str = "default") -> str:
        """Create a new project.
        
        Args:
            name: Project name
            description: Project description
            template_name: Template to use for project creation
            
        Returns:
            Project ID
        """
        try:
            # Generate project ID
            project_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Load template
            template = self._load_template(template_name)
            
            # Create project data
            project_data = {
                'id': project_id,
                'name': name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'databases': [],
                'environments': template.get('environments', []),
                'settings': template.get('settings', {}),
                'metadata': {
                    'template_used': template_name,
                    'version': '1.0',
                    'created_by': 'Project Manager'
                }
            }
            
            # Save to database
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO projects (id, name, description, project_data)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, name, description, json.dumps(project_data)))
                conn.commit()
            
            # Create project directory structure
            self._create_project_structure(project_id, name)
            
            logger.info(f"Created project: {name} ({project_id})")
            return project_id
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    def _create_project_structure(self, project_id: str, project_name: str):
        """Create directory structure for a project."""
        project_path = self.projects_dir / project_id
        project_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (project_path / "documentation").mkdir(exist_ok=True)
        (project_path / "exports").mkdir(exist_ok=True)
        (project_path / "comparisons").mkdir(exist_ok=True)
        (project_path / "reports").mkdir(exist_ok=True)
        (project_path / "configurations").mkdir(exist_ok=True)
        
        # Create project info file
        project_info = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "directory_structure": {
                "documentation": "Generated documentation files",
                "exports": "Exported data and schemas",
                "comparisons": "Schema comparison results",
                "reports": "Analysis and monitoring reports",
                "configurations": "Saved configurations and templates"
            }
        }
        
        with open(project_path / "project_info.json", 'w') as f:
            json.dump(project_info, f, indent=2)
    
    def get_project(self, project_id: str) -> Optional[DatabaseProject]:
        """Get a project by ID."""
        try:
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT project_data FROM projects WHERE id = ?
                ''', (project_id,))
                
                result = cursor.fetchone()
                if result:
                    project_data = json.loads(result[0])
                    return DatabaseProject(project_data)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Get list of all projects."""
        try:
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, created_at, updated_at, status, tags
                    FROM projects
                    ORDER BY updated_at DESC
                ''')
                
                columns = [desc[0] for desc in cursor.description]
                projects = []
                
                for row in cursor.fetchall():
                    project_info = dict(zip(columns, row))
                    
                    # Get database count
                    cursor.execute('''
                        SELECT COUNT(*) FROM project_databases 
                        WHERE project_id = ? AND status = 'active'
                    ''', (project_info['id'],))
                    project_info['database_count'] = cursor.fetchone()[0]
                    
                    projects.append(project_info)
                
                return projects
                
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update project information."""
        try:
            project = self.get_project(project_id)
            if not project:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            project.updated_at = datetime.now().isoformat()
            
            # Save to database
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE projects 
                    SET name = ?, description = ?, updated_at = ?, project_data = ?
                    WHERE id = ?
                ''', (project.name, project.description, project.updated_at,
                      json.dumps(project.to_dict()), project_id))
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated data."""
        try:
            # Remove from database
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                
                # Delete related records
                cursor.execute('DELETE FROM project_databases WHERE project_id = ?', (project_id,))
                cursor.execute('DELETE FROM project_executions WHERE project_id = ?', (project_id,))
                cursor.execute('DELETE FROM project_environments WHERE project_id = ?', (project_id,))
                cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                
                conn.commit()
            
            # Remove project directory
            project_path = self.projects_dir / project_id
            if project_path.exists():
                shutil.rmtree(project_path)
            
            logger.info(f"Deleted project: {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            return False
    
    def add_database_to_project(self, project_id: str, database_config: Dict[str, Any], 
                               environment: str = "default") -> bool:
        """Add a database to a project."""
        try:
            # Generate database ID
            database_id = hashlib.md5(f"{database_config.get('server', '')}_{database_config.get('database', '')}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            # Add to project databases table
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO project_databases 
                    (project_id, database_id, database_name, environment, connection_config)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, database_id, database_config.get('database', 'Unknown'),
                      environment, json.dumps(database_config)))
                conn.commit()
            
            # Update project
            project = self.get_project(project_id)
            if project:
                database_config['id'] = database_id
                database_config['environment'] = environment
                project.add_database(database_config)
                
                with sqlite3.connect(str(self.projects_db)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE projects 
                        SET updated_at = ?, project_data = ?
                        WHERE id = ?
                    ''', (project.updated_at, json.dumps(project.to_dict()), project_id))
                    conn.commit()
            
            logger.info(f"Added database to project {project_id}: {database_config.get('database', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add database to project {project_id}: {e}")
            return False
    
    def get_project_databases(self, project_id: str, 
                             environment: str = None) -> List[Dict[str, Any]]:
        """Get databases associated with a project."""
        try:
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                
                if environment:
                    cursor.execute('''
                        SELECT database_id, database_name, environment, connection_config, 
                               last_documented, status
                        FROM project_databases 
                        WHERE project_id = ? AND environment = ? AND status = 'active'
                        ORDER BY database_name
                    ''', (project_id, environment))
                else:
                    cursor.execute('''
                        SELECT database_id, database_name, environment, connection_config, 
                               last_documented, status
                        FROM project_databases 
                        WHERE project_id = ? AND status = 'active'
                        ORDER BY environment, database_name
                    ''', (project_id,))
                
                columns = [desc[0] for desc in cursor.description]
                databases = []
                
                for row in cursor.fetchall():
                    db_info = dict(zip(columns, row))
                    db_info['connection_config'] = json.loads(db_info['connection_config'])
                    databases.append(db_info)
                
                return databases
                
        except Exception as e:
            logger.error(f"Failed to get project databases: {e}")
            return []
    
    def execute_batch_operation(self, project_id: str, operation_type: str, 
                               operation_config: Dict[str, Any],
                               target_databases: List[str] = None) -> str:
        """Execute a batch operation across multiple databases in a project.
        
        Args:
            project_id: Project ID
            operation_type: Type of operation (documentation, comparison, analysis)
            operation_config: Operation configuration
            target_databases: List of database IDs to target (None = all)
            
        Returns:
            Execution ID for tracking
        """
        try:
            # Create execution record
            execution_id = str(hash(f"{project_id}_{operation_type}_{datetime.now().isoformat()}"))
            
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO project_executions 
                    (id, project_id, execution_type, status, results)
                    VALUES (?, ?, ?, 'running', ?)
                ''', (execution_id, project_id, operation_type, 
                      json.dumps({'config': operation_config, 'target_databases': target_databases})))
                conn.commit()
            
            # Get target databases
            if target_databases:
                databases = []
                for db_id in target_databases:
                    with sqlite3.connect(str(self.projects_db)) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT database_id, database_name, connection_config
                            FROM project_databases 
                            WHERE project_id = ? AND database_id = ? AND status = 'active'
                        ''', (project_id, db_id))
                        
                        result = cursor.fetchone()
                        if result:
                            databases.append({
                                'id': result[0],
                                'name': result[1],
                                'config': json.loads(result[2])
                            })
            else:
                databases = self.get_project_databases(project_id)
            
            # Execute operation (this would be implemented based on operation type)
            results = self._execute_operation(operation_type, databases, operation_config)
            
            # Update execution record
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE project_executions 
                    SET completed_at = CURRENT_TIMESTAMP, status = 'completed', results = ?
                    WHERE id = ?
                ''', (json.dumps(results), execution_id))
                conn.commit()
            
            logger.info(f"Batch operation {operation_type} completed for project {project_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute batch operation: {e}")
            
            # Update execution record with error
            try:
                with sqlite3.connect(str(self.projects_db)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE project_executions 
                        SET completed_at = CURRENT_TIMESTAMP, status = 'error', error_message = ?
                        WHERE id = ?
                    ''', (str(e), execution_id))
                    conn.commit()
            except:
                pass
            
            raise
    
    def _execute_operation(self, operation_type: str, databases: List[Dict[str, Any]], 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified operation on databases."""
        results = {
            'operation_type': operation_type,
            'databases_processed': len(databases),
            'results': [],
            'summary': {}
        }
        
        for db in databases:
            try:
                if operation_type == "documentation":
                    # Generate documentation for database
                    result = self._generate_documentation(db, config)
                    results['results'].append({
                        'database': db['name'],
                        'status': 'success',
                        'result': result
                    })
                elif operation_type == "comparison":
                    # Perform schema comparison
                    result = self._perform_comparison(db, config)
                    results['results'].append({
                        'database': db['name'],
                        'status': 'success',
                        'result': result
                    })
                elif operation_type == "analysis":
                    # Perform analysis
                    result = self._perform_analysis(db, config)
                    results['results'].append({
                        'database': db['name'],
                        'status': 'success',
                        'result': result
                    })
                else:
                    results['results'].append({
                        'database': db['name'],
                        'status': 'error',
                        'error': f"Unknown operation type: {operation_type}"
                    })
                    
            except Exception as e:
                results['results'].append({
                    'database': db.get('name', 'Unknown'),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate summary
        successful = len([r for r in results['results'] if r['status'] == 'success'])
        failed = len([r for r in results['results'] if r['status'] == 'error'])
        
        results['summary'] = {
            'total': len(databases),
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful / len(databases) * 100):.1f}%" if databases else "0%"
        }
        
        return results
    
    def _generate_documentation(self, database: Dict[str, Any], 
                              config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for a database (placeholder)."""
        # This would integrate with the existing documentation generation system
        return {
            'files_generated': ['example.html', 'example.json'],
            'size_mb': 2.5,
            'objects_documented': 150
        }
    
    def _perform_comparison(self, database: Dict[str, Any], 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform schema comparison (placeholder)."""
        # This would integrate with the schema comparison system
        return {
            'comparison_type': config.get('comparison_type', 'baseline'),
            'changes_detected': 5,
            'change_summary': 'Minor schema updates detected'
        }
    
    def _perform_analysis(self, database: Dict[str, Any], 
                         config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform database analysis (placeholder)."""
        # This would integrate with analysis tools
        return {
            'analysis_type': config.get('analysis_type', 'health_check'),
            'score': 85,
            'recommendations': 3
        }
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch execution."""
        try:
            with sqlite3.connect(str(self.projects_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT execution_type, started_at, completed_at, status, results, error_message
                    FROM project_executions 
                    WHERE id = ?
                ''', (execution_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'execution_id': execution_id,
                        'execution_type': result[0],
                        'started_at': result[1],
                        'completed_at': result[2],
                        'status': result[3],
                        'results': json.loads(result[4]) if result[4] else None,
                        'error_message': result[5]
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get execution status: {e}")
            return None
    
    def export_project(self, project_id: str, export_path: str, 
                      include_data: bool = True) -> bool:
        """Export a project to a zip file."""
        try:
            project = self.get_project(project_id)
            if not project:
                return False
            
            project_path = self.projects_dir / project_id
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add project metadata
                project_info = {
                    'project': project.to_dict(),
                    'databases': self.get_project_databases(project_id),
                    'export_timestamp': datetime.now().isoformat(),
                    'export_version': '1.0'
                }
                
                zipf.writestr('project_metadata.json', json.dumps(project_info, indent=2))
                
                # Add project files
                if project_path.exists() and include_data:
                    for file_path in project_path.rglob('*'):
                        if file_path.is_file():
                            archive_path = file_path.relative_to(project_path)
                            zipf.write(file_path, archive_path)
            
            logger.info(f"Exported project {project_id} to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            return False
    
    def import_project(self, import_path: str, new_name: str = None) -> Optional[str]:
        """Import a project from a zip file."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract zip file
                with zipfile.ZipFile(import_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Load project metadata
                metadata_path = Path(temp_dir) / 'project_metadata.json'
                with open(metadata_path, 'r') as f:
                    import_data = json.load(f)
                
                project_data = import_data['project']
                
                # Create new project
                project_name = new_name or f"{project_data['name']}_imported"
                new_project_id = self.create_project(
                    project_name,
                    f"Imported from {import_path}",
                    "default"
                )
                
                # Import databases
                for db in import_data.get('databases', []):
                    self.add_database_to_project(new_project_id, db['connection_config'], 
                                               db.get('environment', 'default'))
                
                # Copy project files
                new_project_path = self.projects_dir / new_project_id
                temp_project_path = Path(temp_dir)
                
                for file_path in temp_project_path.rglob('*'):
                    if file_path.is_file() and file_path.name != 'project_metadata.json':
                        relative_path = file_path.relative_to(temp_project_path)
                        target_path = new_project_path / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, target_path)
                
                logger.info(f"Imported project as {project_name} ({new_project_id})")
                return new_project_id
                
        except Exception as e:
            logger.error(f"Failed to import project: {e}")
            return None
    
    def _load_template(self, template_name: str) -> Dict[str, Any]:
        """Load a project template."""
        template_path = self.templates_dir / f"{template_name}.json"
        
        if not template_path.exists():
            return self._get_default_template()
        
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return self._get_default_template()
    
    def _get_default_template(self) -> Dict[str, Any]:
        """Get the default project template."""
        return {
            "environments": [
                {"name": "development", "config": {"priority": "low"}},
                {"name": "testing", "config": {"priority": "medium"}},
                {"name": "production", "config": {"priority": "high"}}
            ],
            "settings": {
                "auto_backup": True,
                "notification_level": "important",
                "retention_days": 30,
                "documentation_formats": ["html", "json"]
            }
        }
    
    def _create_default_templates(self):
        """Create default project templates."""
        templates = {
            "default": self._get_default_template(),
            "enterprise": {
                "environments": [
                    {"name": "development", "config": {"priority": "low", "backup_frequency": "daily"}},
                    {"name": "testing", "config": {"priority": "medium", "backup_frequency": "daily"}},
                    {"name": "staging", "config": {"priority": "high", "backup_frequency": "hourly"}},
                    {"name": "production", "config": {"priority": "critical", "backup_frequency": "hourly"}}
                ],
                "settings": {
                    "auto_backup": True,
                    "notification_level": "all",
                    "retention_days": 90,
                    "documentation_formats": ["html", "json", "markdown"],
                    "compliance_reporting": True,
                    "change_tracking": True
                }
            },
            "simple": {
                "environments": [
                    {"name": "main", "config": {"priority": "medium"}}
                ],
                "settings": {
                    "auto_backup": False,
                    "notification_level": "errors",
                    "retention_days": 7,
                    "documentation_formats": ["html"]
                }
            }
        }
        
        for template_name, template_data in templates.items():
            template_path = self.templates_dir / f"{template_name}.json"
            if not template_path.exists():
                with open(template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)


# GUI Integration Classes
class ProjectSelectionDialog:
    """Dialog for selecting projects."""
    
    def __init__(self, parent, project_manager: ProjectManager):
        self.parent = parent
        self.project_manager = project_manager
        self.selected_project = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """Show project selection dialog."""
        import tkinter as tk
        from tkinter import ttk
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Project")
        self.dialog.geometry("600x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Project list
        list_frame = ttk.LabelFrame(main_frame, text="Available Projects", padding="10")
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("Name", "Description", "Databases", "Updated")
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        
        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=150 if col == "Description" else 100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar.set)
        
        self.project_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Select", command=self._on_select).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right")
        
        # Load projects
        self._load_projects()
        
        # Wait for dialog
        self.dialog.wait_window()
        return self.selected_project
    
    def _load_projects(self):
        """Load projects into the tree."""
        projects = self.project_manager.list_projects()
        
        for project in projects:
            self.project_tree.insert("", "end", values=(
                project['name'],
                project['description'][:50] + "..." if len(project.get('description', '')) > 50 else project.get('description', ''),
                project.get('database_count', 0),
                project.get('updated_at', '')[:10] if project.get('updated_at') else ''
            ), tags=(project['id'],))
    
    def _on_select(self):
        """Handle project selection."""
        selection = self.project_tree.selection()
        if selection:
            item = self.project_tree.item(selection[0])
            self.selected_project = item['tags'][0]
            self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel."""
        self.dialog.destroy()


class CreateProjectDialog:
    """Dialog for creating new projects."""
    
    def __init__(self, parent, project_manager: ProjectManager):
        self.parent = parent
        self.project_manager = project_manager
        self.project_id = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """Show create project dialog."""
        import tkinter as tk
        from tkinter import ttk
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Create New Project")
        self.dialog.geometry("400x300")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Project details
        details_frame = ttk.LabelFrame(main_frame, text="Project Details", padding="10")
        details_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="ew", pady=(0, 5))
        
        ttk.Label(details_frame, text="Description:").grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=(0, 5))
        self.description_text = tk.Text(details_frame, width=30, height=4)
        self.description_text.grid(row=1, column=1, sticky="ew", pady=(0, 5))
        
        details_frame.columnconfigure(1, weight=1)
        
        # Template selection
        template_frame = ttk.LabelFrame(main_frame, text="Project Template", padding="10")
        template_frame.pack(fill="x", pady=(0, 10))
        
        self.template_var = tk.StringVar(value="default")
        ttk.Radiobutton(template_frame, text="Default (Dev/Test/Prod)", 
                       variable=self.template_var, value="default").pack(anchor="w")
        ttk.Radiobutton(template_frame, text="Enterprise (Dev/Test/Staging/Prod)", 
                       variable=self.template_var, value="enterprise").pack(anchor="w")
        ttk.Radiobutton(template_frame, text="Simple (Single Environment)", 
                       variable=self.template_var, value="simple").pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Create", command=self._on_create).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right")
        
        # Wait for dialog
        self.dialog.wait_window()
        return self.project_id
    
    def _on_create(self):
        """Handle project creation."""
        name = self.name_var.get().strip()
        if not name:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", "Please enter a project name.")
            return
        
        try:
            description = self.description_text.get(1.0, "end-1c")
            template = self.template_var.get()
            
            self.project_id = self.project_manager.create_project(name, description, template)
            self.dialog.destroy()
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
    
    def _on_cancel(self):
        """Handle cancel."""
        self.dialog.destroy()


class BatchOperationDialog:
    """Dialog for configuring batch operations."""
    
    def __init__(self, parent, project_manager: ProjectManager, project_id: str):
        self.parent = parent
        self.project_manager = project_manager
        self.project_id = project_id
        self.operation_config = None
        self.dialog = None
    
    def show(self) -> Optional[Dict[str, Any]]:
        """Show batch operation dialog."""
        import tkinter as tk
        from tkinter import ttk
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Batch Operation Configuration")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Operation type
        type_frame = ttk.LabelFrame(main_frame, text="Operation Type", padding="10")
        type_frame.pack(fill="x", pady=(0, 10))
        
        self.operation_type = tk.StringVar(value="documentation")
        ttk.Radiobutton(type_frame, text="Generate Documentation", 
                       variable=self.operation_type, value="documentation").pack(anchor="w")
        ttk.Radiobutton(type_frame, text="Schema Comparison", 
                       variable=self.operation_type, value="comparison").pack(anchor="w")
        ttk.Radiobutton(type_frame, text="Database Analysis", 
                       variable=self.operation_type, value="analysis").pack(anchor="w")
        
        # Configuration options
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # This would be expanded based on operation type
        ttk.Label(config_frame, text="Additional options would appear here based on operation type").pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Execute", command=self._on_execute).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right")
        
        # Wait for dialog
        self.dialog.wait_window()
        return self.operation_config
    
    def _on_execute(self):
        """Handle operation execution."""
        self.operation_config = {
            "operation_type": self.operation_type.get(),
            "config": {}  # This would be populated based on the UI
        }
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel."""
        self.dialog.destroy()
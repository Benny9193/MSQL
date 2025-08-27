#!/usr/bin/env python3
"""
Automated Scheduling and Monitoring System
==========================================

Provides automated scheduling for documentation generation, database monitoring
for schema changes, and notification systems for alerts and updates.

Features:
- Scheduled documentation generation with cron-like syntax
- Real-time database change monitoring
- Email and webhook notifications
- Background service mode
- Job history and status tracking
- Configurable monitoring intervals
"""

import os
import json
import time
import threading
import schedule
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import logging
import sqlite3
import hashlib

# Optional email support
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.application import MimeApplication
    EMAIL_SUPPORT = True
except ImportError:
    EMAIL_SUPPORT = False

logger = logging.getLogger(__name__)

class JobScheduler:
    """Handles scheduling of automated tasks."""
    
    def __init__(self, config_dir: str = "scheduler"):
        """Initialize the scheduler.
        
        Args:
            config_dir: Directory to store scheduler configuration and data
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "scheduler_config.json"
        self.jobs_db = self.config_dir / "jobs.db"
        
        self.running = False
        self.scheduler_thread = None
        self.monitor_thread = None
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize database
        self._init_jobs_db()
        
        # Job registry
        self.registered_jobs = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load scheduler configuration."""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": []
            },
            "webhooks": {
                "enabled": False,
                "urls": []
            },
            "monitoring": {
                "enabled": True,
                "interval_minutes": 30,
                "change_threshold": 0.1  # 10% change to trigger alert
            },
            "jobs": []
        }
        
        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            logger.error(f"Failed to load scheduler config: {e}")
            return default_config
    
    def _save_config(self):
        """Save scheduler configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save scheduler config: {e}")
    
    def _init_jobs_db(self):
        """Initialize the jobs database."""
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                
                # Jobs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        job_type TEXT NOT NULL,
                        schedule TEXT NOT NULL,
                        config TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_run TIMESTAMP,
                        next_run TIMESTAMP,
                        run_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Job history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS job_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        started_at TIMESTAMP NOT NULL,
                        completed_at TIMESTAMP,
                        status TEXT NOT NULL,
                        result TEXT,
                        error_message TEXT,
                        FOREIGN KEY (job_id) REFERENCES jobs (id)
                    )
                ''')
                
                # Monitoring snapshots table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitoring_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        database_name TEXT NOT NULL,
                        connection_id TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        schema_hash TEXT NOT NULL,
                        object_counts TEXT NOT NULL,
                        change_detected BOOLEAN DEFAULT 0,
                        change_summary TEXT
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize jobs database: {e}")
    
    def register_job_type(self, job_type: str, handler: Callable):
        """Register a job type handler.
        
        Args:
            job_type: Type identifier for the job
            handler: Function to execute for this job type
        """
        self.registered_jobs[job_type] = handler
        logger.info(f"Registered job type: {job_type}")
    
    def add_job(self, name: str, job_type: str, schedule_spec: str, 
                config: Dict[str, Any]) -> str:
        """Add a new scheduled job.
        
        Args:
            name: Human-readable job name
            job_type: Type of job (must be registered)
            schedule_spec: Schedule specification (e.g., "daily", "weekly", "0 8 * * 1")
            config: Job-specific configuration
            
        Returns:
            Job ID
        """
        if job_type not in self.registered_jobs:
            raise ValueError(f"Unknown job type: {job_type}")
        
        job_id = hashlib.md5(f"{name}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO jobs (id, name, job_type, schedule, config)
                    VALUES (?, ?, ?, ?, ?)
                ''', (job_id, name, job_type, schedule_spec, json.dumps(config)))
                conn.commit()
            
            # Update in-memory config
            job_config = {
                "id": job_id,
                "name": name,
                "type": job_type,
                "schedule": schedule_spec,
                "config": config,
                "enabled": True
            }
            self.config["jobs"].append(job_config)
            self._save_config()
            
            # Schedule the job
            self._schedule_job(job_config)
            
            logger.info(f"Added job: {name} ({job_id})")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to add job: {e}")
            raise
    
    def _schedule_job(self, job_config: Dict[str, Any]):
        """Schedule a job with the schedule library."""
        job_id = job_config["id"]
        schedule_spec = job_config["schedule"]
        
        def job_wrapper():
            self._execute_job(job_id)
        
        # Parse schedule specification
        if schedule_spec == "daily":
            schedule.every().day.do(job_wrapper)
        elif schedule_spec == "weekly":
            schedule.every().week.do(job_wrapper)
        elif schedule_spec == "hourly":
            schedule.every().hour.do(job_wrapper)
        elif schedule_spec.startswith("every_"):
            # e.g., "every_30_minutes"
            parts = schedule_spec.split("_")
            if len(parts) == 3 and parts[2] == "minutes":
                minutes = int(parts[1])
                schedule.every(minutes).minutes.do(job_wrapper)
            elif len(parts) == 3 and parts[2] == "hours":
                hours = int(parts[1])
                schedule.every(hours).hours.do(job_wrapper)
        else:
            # Try to parse as time specification (e.g., "08:30")
            try:
                schedule.every().day.at(schedule_spec).do(job_wrapper)
            except Exception as e:
                logger.error(f"Invalid schedule specification: {schedule_spec}")
    
    def _execute_job(self, job_id: str):
        """Execute a scheduled job."""
        try:
            # Get job details
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, job_type, config FROM jobs 
                    WHERE id = ? AND enabled = 1
                ''', (job_id,))
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"Job not found or disabled: {job_id}")
                    return
                
                name, job_type, config_json = result
                config = json.loads(config_json)
            
            # Record job start
            start_time = datetime.now()
            history_id = self._record_job_start(job_id, start_time)
            
            logger.info(f"Starting job: {name} ({job_id})")
            
            # Execute job
            if job_type in self.registered_jobs:
                handler = self.registered_jobs[job_type]
                result = handler(config)
                
                # Record success
                self._record_job_completion(history_id, "success", result)
                
                # Send notifications
                self._send_job_notification(name, "success", result)
                
            else:
                error_msg = f"Unknown job type: {job_type}"
                logger.error(error_msg)
                self._record_job_completion(history_id, "error", None, error_msg)
            
            # Update job statistics
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE jobs 
                    SET last_run = ?, run_count = run_count + 1
                    WHERE id = ?
                ''', (start_time.isoformat(), job_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            self._record_job_completion(history_id, "error", None, str(e))
            self._send_job_notification(name, "error", str(e))
    
    def _record_job_start(self, job_id: str, start_time: datetime) -> int:
        """Record job start in history."""
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO job_history (job_id, started_at, status)
                    VALUES (?, ?, 'running')
                ''', (job_id, start_time.isoformat()))
                history_id = cursor.lastrowid
                conn.commit()
                return history_id
        except Exception as e:
            logger.error(f"Failed to record job start: {e}")
            return -1
    
    def _record_job_completion(self, history_id: int, status: str, 
                             result: Any = None, error_message: str = None):
        """Record job completion in history."""
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE job_history 
                    SET completed_at = ?, status = ?, result = ?, error_message = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), status, 
                      json.dumps(result) if result else None, 
                      error_message, history_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record job completion: {e}")
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        # Load and schedule all jobs
        self._load_and_schedule_jobs()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Start monitoring thread if enabled
        if self.config.get("monitoring", {}).get("enabled", True):
            self.monitor_thread = threading.Thread(target=self._run_monitoring, daemon=True)
            self.monitor_thread.start()
        
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        
        # Clear scheduled jobs
        schedule.clear()
        
        logger.info("Scheduler stopped")
    
    def _load_and_schedule_jobs(self):
        """Load jobs from database and schedule them."""
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, job_type, schedule, config 
                    FROM jobs WHERE enabled = 1
                ''')
                
                for job_id, name, job_type, schedule_spec, config_json in cursor.fetchall():
                    job_config = {
                        "id": job_id,
                        "name": name,
                        "type": job_type,
                        "schedule": schedule_spec,
                        "config": json.loads(config_json),
                        "enabled": True
                    }
                    self._schedule_job(job_config)
                    
        except Exception as e:
            logger.error(f"Failed to load jobs: {e}")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _run_monitoring(self):
        """Database monitoring loop."""
        interval = self.config.get("monitoring", {}).get("interval_minutes", 30) * 60
        
        while self.running:
            try:
                self._check_database_changes()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def _check_database_changes(self):
        """Check for database schema changes."""
        # This would integrate with the existing database connection and schema analyzer
        logger.info("Checking for database changes...")
        # Implementation would go here
    
    def _send_job_notification(self, job_name: str, status: str, result: Any):
        """Send notifications for job completion."""
        message = f"Job '{job_name}' completed with status: {status}"
        
        # Email notification
        if self.config.get("email", {}).get("enabled", False):
            self._send_email_notification(job_name, status, result)
        
        # Webhook notification
        if self.config.get("webhooks", {}).get("enabled", False):
            self._send_webhook_notification(job_name, status, result)
    
    def _send_email_notification(self, job_name: str, status: str, result: Any):
        """Send email notification."""
        if not EMAIL_SUPPORT:
            logger.warning("Email support not available - skipping email notification")
            return
            
        try:
            email_config = self.config.get("email", {})
            
            msg = MimeMultipart()
            msg['From'] = email_config.get("from_address")
            msg['To'] = ", ".join(email_config.get("to_addresses", []))
            msg['Subject'] = f"Database Documentation Job: {job_name} - {status.title()}"
            
            body = f"""
Database Documentation Job Report

Job Name: {job_name}
Status: {status.title()}
Completed At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{f'Result: {json.dumps(result, indent=2)}' if result else ''}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            with smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port", 587)) as server:
                server.starttls()
                server.login(email_config.get("username"), email_config.get("password"))
                server.send_message(msg)
            
            logger.info(f"Email notification sent for job: {job_name}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _send_webhook_notification(self, job_name: str, status: str, result: Any):
        """Send webhook notification."""
        try:
            webhook_config = self.config.get("webhooks", {})
            urls = webhook_config.get("urls", [])
            
            payload = {
                "job_name": job_name,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
            for url in urls:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
            
            logger.info(f"Webhook notifications sent for job: {job_name}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    def get_job_history(self, job_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get job execution history."""
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                
                if job_id:
                    cursor.execute('''
                        SELECT h.*, j.name 
                        FROM job_history h 
                        JOIN jobs j ON h.job_id = j.id 
                        WHERE h.job_id = ?
                        ORDER BY h.started_at DESC 
                        LIMIT ?
                    ''', (job_id, limit))
                else:
                    cursor.execute('''
                        SELECT h.*, j.name 
                        FROM job_history h 
                        JOIN jobs j ON h.job_id = j.id 
                        ORDER BY h.started_at DESC 
                        LIMIT ?
                    ''', (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get job history: {e}")
            return []
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get list of active scheduled jobs."""
        try:
            with sqlite3.connect(str(self.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, job_type, schedule, enabled, last_run, run_count
                    FROM jobs
                    ORDER BY name
                ''')
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get active jobs: {e}")
            return []


class DatabaseMonitor:
    """Monitors database for changes and triggers alerts."""
    
    def __init__(self, scheduler: JobScheduler):
        """Initialize the monitor.
        
        Args:
            scheduler: JobScheduler instance for notifications
        """
        self.scheduler = scheduler
    
    def monitor_database(self, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor a database for changes.
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Monitoring result with change detection info
        """
        try:
            from db_connection import AzureSQLConnection
            from documentation_extractor import DocumentationExtractor
            
            # Connect to database
            with AzureSQLConnection() as db:
                # Connect based on method
                method = connection_config.get('method', 'credentials')
                
                if method == 'credentials':
                    success = db.connect_with_credentials(
                        server=connection_config['server'],
                        database=connection_config['database'],
                        username=connection_config['username'],
                        password=connection_config['password']
                    )
                elif method == 'azure_ad':
                    success = db.connect_with_azure_ad(
                        server=connection_config['server'],
                        database=connection_config['database']
                    )
                else:
                    raise ValueError(f"Unsupported connection method: {method}")
                
                if not success:
                    raise Exception("Failed to connect to database")
                
                # Extract current schema
                extractor = DocumentationExtractor(db)
                current_schema = extractor.extract_complete_documentation()
                
                # Calculate schema hash
                schema_hash = self._calculate_schema_hash(current_schema)
                
                # Get object counts
                object_counts = {
                    'tables': len(current_schema.get('tables', [])),
                    'views': len(current_schema.get('views', [])),
                    'procedures': len(current_schema.get('stored_procedures', [])),
                    'functions': len(current_schema.get('functions', []))
                }
                
                # Check for changes
                change_detected, change_summary = self._check_for_changes(
                    connection_config['database'], schema_hash, object_counts
                )
                
                # Store snapshot
                self._store_snapshot(
                    connection_config['database'],
                    connection_config.get('connection_id', 'default'),
                    schema_hash,
                    object_counts,
                    change_detected,
                    change_summary
                )
                
                return {
                    'database': connection_config['database'],
                    'schema_hash': schema_hash,
                    'object_counts': object_counts,
                    'change_detected': change_detected,
                    'change_summary': change_summary,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Database monitoring failed: {e}")
            raise
    
    def _calculate_schema_hash(self, schema_data: Dict[str, Any]) -> str:
        """Calculate hash of schema structure."""
        # Create a simplified representation for hashing
        hash_data = {
            'tables': [
                {
                    'name': table.get('name'),
                    'columns': [col.get('name') + col.get('data_type', '') 
                               for col in table.get('columns', [])],
                    'constraints': len(table.get('constraints', []))
                }
                for table in schema_data.get('tables', [])
            ],
            'views': [view.get('name') for view in schema_data.get('views', [])],
            'procedures': [proc.get('name') for proc in schema_data.get('stored_procedures', [])],
            'functions': [func.get('name') for func in schema_data.get('functions', [])]
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _check_for_changes(self, database_name: str, current_hash: str, 
                          current_counts: Dict[str, int]) -> tuple[bool, str]:
        """Check if changes occurred since last snapshot."""
        try:
            with sqlite3.connect(str(self.scheduler.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT schema_hash, object_counts FROM monitoring_snapshots
                    WHERE database_name = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (database_name,))
                
                result = cursor.fetchone()
                if not result:
                    return False, "First monitoring snapshot"
                
                last_hash, last_counts_json = result
                last_counts = json.loads(last_counts_json)
                
                # Check hash change
                if current_hash != last_hash:
                    # Calculate specific changes
                    changes = []
                    for obj_type, current_count in current_counts.items():
                        last_count = last_counts.get(obj_type, 0)
                        if current_count != last_count:
                            diff = current_count - last_count
                            changes.append(f"{obj_type}: {diff:+d}")
                    
                    change_summary = f"Schema changes detected. {', '.join(changes) if changes else 'Structure modified'}"
                    return True, change_summary
                
                return False, "No changes detected"
                
        except Exception as e:
            logger.error(f"Failed to check for changes: {e}")
            return False, f"Error checking changes: {e}"
    
    def _store_snapshot(self, database_name: str, connection_id: str, 
                       schema_hash: str, object_counts: Dict[str, int],
                       change_detected: bool, change_summary: str):
        """Store monitoring snapshot."""
        try:
            with sqlite3.connect(str(self.scheduler.jobs_db)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO monitoring_snapshots 
                    (database_name, connection_id, schema_hash, object_counts, 
                     change_detected, change_summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (database_name, connection_id, schema_hash, 
                      json.dumps(object_counts), change_detected, change_summary))
                
                # Keep only last 100 snapshots per database
                cursor.execute('''
                    DELETE FROM monitoring_snapshots 
                    WHERE database_name = ? AND id NOT IN (
                        SELECT id FROM monitoring_snapshots 
                        WHERE database_name = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 100
                    )
                ''', (database_name, database_name))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to store snapshot: {e}")


# Example usage and integration
def create_documentation_job_handler():
    """Create a job handler for documentation generation."""
    
    def documentation_job(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation generation job."""
        try:
            from db_connection import AzureSQLConnection
            from documentation_extractor import DocumentationExtractor
            from documentation_generator import DocumentationGenerator
            
            connection_config = config.get('connection', {})
            doc_config = config.get('documentation', {})
            
            # Connect and generate documentation
            with AzureSQLConnection() as db:
                # Connection logic here...
                pass
            
            return {
                'status': 'success',
                'files_generated': ['example.html', 'example.json'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Documentation job failed: {e}")
    
    return documentation_job


# Example configuration for GUI integration
def get_default_scheduler_config():
    """Get default configuration for the scheduler."""
    return {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_address": "",
            "to_addresses": []
        },
        "webhooks": {
            "enabled": False,
            "urls": []
        },
        "monitoring": {
            "enabled": True,
            "interval_minutes": 30,
            "change_threshold": 0.1
        }
    }
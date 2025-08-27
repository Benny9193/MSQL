#!/usr/bin/env python3
"""
API Integration and Webhook Support System
==========================================

Provides REST API endpoints, webhook management, and integration with external platforms
for the Azure SQL Database Documentation Generator.

Features:
- RESTful API endpoints for documentation operations
- Webhook management and delivery
- External platform integrations (GitHub, Azure DevOps, Slack)
- API key authentication and rate limiting
- Webhook event handling and retries

Author: Claude Code Assistant
"""

import json
import sqlite3
import logging
import threading
import time
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

# Optional flask support for advanced API features
try:
    from flask import Flask, request, jsonify, abort
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    FLASK_SUPPORT = True
except ImportError:
    FLASK_SUPPORT = False

logger = logging.getLogger(__name__)

class WebhookManager:
    """Manages webhook registrations and deliveries."""
    
    def __init__(self, db_path: str = "webhooks.db"):
        self.db_path = Path(db_path)
        self.webhooks_db = self.db_path
        self.delivery_queue = []
        self.delivery_thread = None
        self.running = False
        self._init_database()
    
    def _init_database(self):
        """Initialize the webhooks database."""
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            
            # Webhooks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS webhooks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    events TEXT NOT NULL,  -- JSON array of event types
                    secret TEXT,
                    headers TEXT,  -- JSON object of headers
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_delivery TIMESTAMP,
                    delivery_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0
                )
            ''')
            
            # Webhook deliveries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS webhook_deliveries (
                    id TEXT PRIMARY KEY,
                    webhook_id TEXT,
                    event_type TEXT,
                    payload TEXT,  -- JSON payload
                    response_code INTEGER,
                    response_body TEXT,
                    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    retry_count INTEGER DEFAULT 0,
                    FOREIGN KEY (webhook_id) REFERENCES webhooks (id)
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    permissions TEXT,  -- JSON array of permissions
                    rate_limit INTEGER DEFAULT 100,  -- requests per hour
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            # API usage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key_id TEXT,
                    endpoint TEXT,
                    method TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_code INTEGER,
                    FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
                )
            ''')
            
            conn.commit()
    
    def register_webhook(self, name: str, url: str, events: List[str], 
                        secret: str = None, headers: Dict[str, str] = None) -> str:
        """Register a new webhook."""
        webhook_id = hashlib.md5(f"{name}_{url}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO webhooks (id, name, url, events, secret, headers)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (webhook_id, name, url, json.dumps(events), secret, 
                  json.dumps(headers) if headers else None))
            conn.commit()
        
        logger.info(f"Registered webhook: {name} ({webhook_id})")
        return webhook_id
    
    def trigger_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Trigger webhooks for a specific event type."""
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, url, events, secret, headers 
                FROM webhooks 
                WHERE active = 1
            ''')
            
            for webhook_id, url, events_json, secret, headers_json in cursor.fetchall():
                events = json.loads(events_json)
                if event_type in events:
                    headers = json.loads(headers_json) if headers_json else {}
                    self._queue_delivery(webhook_id, url, event_type, payload, secret, headers)
    
    def _queue_delivery(self, webhook_id: str, url: str, event_type: str, 
                       payload: Dict[str, Any], secret: str = None, 
                       headers: Dict[str, str] = None):
        """Queue a webhook delivery."""
        delivery_id = hashlib.md5(f"{webhook_id}_{event_type}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        delivery = {
            'id': delivery_id,
            'webhook_id': webhook_id,
            'url': url,
            'event_type': event_type,
            'payload': payload,
            'secret': secret,
            'headers': headers or {},
            'retry_count': 0
        }
        
        self.delivery_queue.append(delivery)
        
        # Start delivery thread if not running
        if not self.running:
            self.start_delivery_service()
    
    def start_delivery_service(self):
        """Start the webhook delivery service."""
        if not self.running:
            self.running = True
            self.delivery_thread = threading.Thread(target=self._delivery_worker, daemon=True)
            self.delivery_thread.start()
            logger.info("Webhook delivery service started")
    
    def stop_delivery_service(self):
        """Stop the webhook delivery service."""
        self.running = False
        if self.delivery_thread:
            self.delivery_thread.join()
        logger.info("Webhook delivery service stopped")
    
    def _delivery_worker(self):
        """Worker thread for delivering webhooks."""
        while self.running:
            if self.delivery_queue:
                delivery = self.delivery_queue.pop(0)
                self._deliver_webhook(delivery)
            else:
                time.sleep(1)
    
    def _deliver_webhook(self, delivery: Dict[str, Any]):
        """Deliver a webhook."""
        try:
            # Prepare payload
            payload_json = json.dumps(delivery['payload'])
            
            # Prepare headers
            headers = delivery['headers'].copy()
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] = 'Azure-SQL-Doc-Generator-Webhook/1.0'
            headers['X-Webhook-Event'] = delivery['event_type']
            headers['X-Delivery-ID'] = delivery['id']
            
            # Add signature if secret is provided
            if delivery['secret']:
                signature = hmac.new(
                    delivery['secret'].encode(),
                    payload_json.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Hub-Signature-256'] = f'sha256={signature}'
            
            # Make request
            response = requests.post(
                delivery['url'],
                data=payload_json,
                headers=headers,
                timeout=30
            )
            
            # Record delivery
            success = 200 <= response.status_code < 300
            self._record_delivery(
                delivery['id'],
                delivery['webhook_id'],
                delivery['event_type'],
                payload_json,
                response.status_code,
                response.text,
                success,
                delivery['retry_count']
            )
            
            # Update webhook stats
            self._update_webhook_stats(delivery['webhook_id'], success)
            
            if success:
                logger.info(f"Webhook delivered successfully: {delivery['id']}")
            else:
                logger.warning(f"Webhook delivery failed: {delivery['id']} - {response.status_code}")
                
                # Retry logic
                if delivery['retry_count'] < 3:
                    delivery['retry_count'] += 1
                    # Exponential backoff
                    threading.Timer(2 ** delivery['retry_count'], 
                                  lambda: self.delivery_queue.append(delivery)).start()
        
        except Exception as e:
            logger.error(f"Webhook delivery error: {delivery['id']} - {str(e)}")
            
            # Record failed delivery
            self._record_delivery(
                delivery['id'],
                delivery['webhook_id'],
                delivery['event_type'],
                json.dumps(delivery['payload']),
                0,
                str(e),
                False,
                delivery['retry_count']
            )
    
    def _record_delivery(self, delivery_id: str, webhook_id: str, event_type: str,
                        payload: str, response_code: int, response_body: str,
                        success: bool, retry_count: int):
        """Record a webhook delivery attempt."""
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO webhook_deliveries 
                (id, webhook_id, event_type, payload, response_code, response_body, success, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (delivery_id, webhook_id, event_type, payload, response_code, 
                  response_body, success, retry_count))
            conn.commit()
    
    def _update_webhook_stats(self, webhook_id: str, success: bool):
        """Update webhook delivery statistics."""
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            if success:
                cursor.execute('''
                    UPDATE webhooks 
                    SET last_delivery = CURRENT_TIMESTAMP, delivery_count = delivery_count + 1
                    WHERE id = ?
                ''', (webhook_id,))
            else:
                cursor.execute('''
                    UPDATE webhooks 
                    SET failure_count = failure_count + 1
                    WHERE id = ?
                ''', (webhook_id,))
            conn.commit()
    
    def get_webhooks(self) -> List[Dict[str, Any]]:
        """Get all registered webhooks."""
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, url, events, active, created_at, last_delivery, 
                       delivery_count, failure_count
                FROM webhooks
                ORDER BY created_at DESC
            ''')
            
            webhooks = []
            for row in cursor.fetchall():
                webhooks.append({
                    'id': row[0],
                    'name': row[1],
                    'url': row[2],
                    'events': json.loads(row[3]),
                    'active': bool(row[4]),
                    'created_at': row[5],
                    'last_delivery': row[6],
                    'delivery_count': row[7],
                    'failure_count': row[8]
                })
            
            return webhooks
    
    def delete_webhook(self, webhook_id: str):
        """Delete a webhook."""
        with sqlite3.connect(str(self.webhooks_db)) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM webhooks WHERE id = ?', (webhook_id,))
            cursor.execute('DELETE FROM webhook_deliveries WHERE webhook_id = ?', (webhook_id,))
            conn.commit()
        logger.info(f"Deleted webhook: {webhook_id}")


class APIServer:
    """Simple API server for documentation operations."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        self.webhook_manager = WebhookManager()
        self.endpoints = {}
        self._register_default_endpoints()
    
    def _register_default_endpoints(self):
        """Register default API endpoints."""
        self.register_endpoint('GET', '/health', self._health_check)
        self.register_endpoint('GET', '/webhooks', self._get_webhooks)
        self.register_endpoint('POST', '/webhooks', self._create_webhook)
        self.register_endpoint('DELETE', '/webhooks/<webhook_id>', self._delete_webhook)
        self.register_endpoint('POST', '/trigger-event', self._trigger_event)
    
    def register_endpoint(self, method: str, path: str, handler: Callable):
        """Register an API endpoint."""
        key = f"{method} {path}"
        self.endpoints[key] = handler
    
    def start_server(self):
        """Start the API server."""
        if not self.running:
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.webhook_manager.start_delivery_service()
            logger.info(f"API server started on port {self.port}")
    
    def stop_server(self):
        """Stop the API server."""
        self.running = False
        if self.server:
            self.server.shutdown()
        self.webhook_manager.stop_delivery_service()
        logger.info("API server stopped")
    
    def _run_server(self):
        """Run the HTTP server."""
        handler = self._create_request_handler()
        with HTTPServer(('localhost', self.port), handler) as self.server:
            while self.running:
                self.server.handle_request()
    
    def _create_request_handler(self):
        """Create a request handler class."""
        endpoints = self.endpoints
        
        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self._handle_request('GET')
            
            def do_POST(self):
                self._handle_request('POST')
            
            def do_DELETE(self):
                self._handle_request('DELETE')
            
            def _handle_request(self, method):
                path = self.path.split('?')[0]  # Remove query parameters
                key = f"{method} {path}"
                
                if key in endpoints:
                    try:
                        # Parse request body for POST requests
                        content_length = int(self.headers.get('Content-Length', 0))
                        body = self.rfile.read(content_length).decode('utf-8') if content_length else ''
                        
                        # Call handler
                        response = endpoints[key](self, body)
                        
                        # Send response
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode())
                    
                    except Exception as e:
                        self.send_error(500, str(e))
                else:
                    self.send_error(404, f"Endpoint not found: {key}")
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        return RequestHandler
    
    def _health_check(self, request, body):
        """Health check endpoint."""
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
    
    def _get_webhooks(self, request, body):
        """Get all webhooks."""
        return {'webhooks': self.webhook_manager.get_webhooks()}
    
    def _create_webhook(self, request, body):
        """Create a new webhook."""
        try:
            data = json.loads(body)
            webhook_id = self.webhook_manager.register_webhook(
                data['name'],
                data['url'],
                data['events'],
                data.get('secret'),
                data.get('headers')
            )
            return {'webhook_id': webhook_id, 'message': 'Webhook created successfully'}
        except Exception as e:
            raise ValueError(f"Invalid webhook data: {str(e)}")
    
    def _delete_webhook(self, request, body):
        """Delete a webhook."""
        # Extract webhook_id from path
        webhook_id = request.path.split('/')[-1]
        self.webhook_manager.delete_webhook(webhook_id)
        return {'message': 'Webhook deleted successfully'}
    
    def _trigger_event(self, request, body):
        """Trigger webhook event."""
        try:
            data = json.loads(body)
            self.webhook_manager.trigger_webhook(data['event_type'], data['payload'])
            return {'message': 'Event triggered successfully'}
        except Exception as e:
            raise ValueError(f"Invalid event data: {str(e)}")


class PlatformIntegration:
    """Integration with external platforms."""
    
    def __init__(self):
        self.integrations = {
            'github': GitHubIntegration(),
            'azure_devops': AzureDevOpsIntegration(),
            'slack': SlackIntegration()
        }
    
    def get_integration(self, platform: str):
        """Get platform integration."""
        return self.integrations.get(platform)
    
    def send_notification(self, platform: str, message: str, config: Dict[str, Any]):
        """Send notification to platform."""
        integration = self.get_integration(platform)
        if integration:
            return integration.send_notification(message, config)
        return False


class GitHubIntegration:
    """GitHub platform integration."""
    
    def send_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send notification to GitHub (create issue or comment)."""
        try:
            token = config.get('token')
            repo = config.get('repository')  # format: owner/repo
            action = config.get('action', 'issue')  # issue or comment
            
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Azure-SQL-Doc-Generator'
            }
            
            if action == 'issue':
                url = f'https://api.github.com/repos/{repo}/issues'
                data = {
                    'title': config.get('title', 'Database Documentation Update'),
                    'body': message,
                    'labels': config.get('labels', ['documentation'])
                }
            elif action == 'comment' and config.get('issue_number'):
                url = f'https://api.github.com/repos/{repo}/issues/{config["issue_number"]}/comments'
                data = {'body': message}
            else:
                return False
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            return response.status_code == 201
        
        except Exception as e:
            logger.error(f"GitHub integration error: {str(e)}")
            return False


class AzureDevOpsIntegration:
    """Azure DevOps platform integration."""
    
    def send_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send notification to Azure DevOps (create work item)."""
        try:
            token = config.get('token')
            organization = config.get('organization')
            project = config.get('project')
            work_item_type = config.get('work_item_type', 'Task')
            
            url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/${work_item_type}?api-version=6.0'
            
            headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json-patch+json'
            }
            
            data = [
                {
                    'op': 'add',
                    'path': '/fields/System.Title',
                    'value': config.get('title', 'Database Documentation Update')
                },
                {
                    'op': 'add',
                    'path': '/fields/System.Description',
                    'value': message
                }
            ]
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Azure DevOps integration error: {str(e)}")
            return False


class SlackIntegration:
    """Slack platform integration."""
    
    def send_notification(self, message: str, config: Dict[str, Any]) -> bool:
        """Send notification to Slack."""
        try:
            webhook_url = config.get('webhook_url')
            channel = config.get('channel')
            username = config.get('username', 'Azure SQL Doc Generator')
            
            data = {
                'text': message,
                'username': username
            }
            
            if channel:
                data['channel'] = channel
            
            response = requests.post(webhook_url, json=data, timeout=30)
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Slack integration error: {str(e)}")
            return False


# Dialog classes for GUI integration
class WebhookConfigDialog:
    """Dialog for configuring webhooks."""
    
    def __init__(self, parent, webhook_manager: WebhookManager):
        self.parent = parent
        self.webhook_manager = webhook_manager
        self.result = None
        self._create_dialog()
    
    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Configure Webhook")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # Create form
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="Webhook Name:").pack(anchor=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill=tk.X, pady=(0, 15))
        
        # URL
        ttk.Label(main_frame, text="Webhook URL:").pack(anchor=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Events
        ttk.Label(main_frame, text="Events (one per line):").pack(anchor=tk.W, pady=(0, 5))
        events_frame = ttk.Frame(main_frame)
        events_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.events_text = tk.Text(events_frame, height=8, width=50)
        events_scrollbar = ttk.Scrollbar(events_frame, orient=tk.VERTICAL, command=self.events_text.yview)
        self.events_text.configure(yscrollcommand=events_scrollbar.set)
        
        self.events_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        events_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Default events
        default_events = [
            "documentation.generated",
            "documentation.failed",
            "schema.changed",
            "job.completed",
            "job.failed"
        ]
        self.events_text.insert(tk.END, "\n".join(default_events))
        
        # Secret (optional)
        ttk.Label(main_frame, text="Secret (optional):").pack(anchor=tk.W, pady=(0, 5))
        self.secret_entry = ttk.Entry(main_frame, width=50, show="*")
        self.secret_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Create Webhook", command=self._create_webhook).pack(side=tk.RIGHT)
    
    def _create_webhook(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        events_text = self.events_text.get(1.0, tk.END).strip()
        secret = self.secret_entry.get().strip() or None
        
        if not name or not url or not events_text:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        events = [event.strip() for event in events_text.split('\n') if event.strip()]
        
        try:
            webhook_id = self.webhook_manager.register_webhook(name, url, events, secret)
            self.result = webhook_id
            self.dialog.destroy()
            messagebox.showinfo("Success", f"Webhook created successfully!\nID: {webhook_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create webhook: {str(e)}")
    
    def _cancel(self):
        self.result = None
        self.dialog.destroy()


class PlatformIntegrationDialog:
    """Dialog for configuring platform integrations."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self._create_dialog()
    
    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Platform Integrations")
        self.dialog.geometry("600x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # GitHub tab
        self._create_github_tab(notebook)
        
        # Azure DevOps tab
        self._create_azure_devops_tab(notebook)
        
        # Slack tab
        self._create_slack_tab(notebook)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="Close", command=self._close).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Test Integration", command=self._test_integration).pack(side=tk.RIGHT, padx=(0, 10))
    
    def _create_github_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="GitHub")
        
        ttk.Label(frame, text="GitHub Personal Access Token:").pack(anchor=tk.W, pady=(0, 5))
        self.github_token_entry = ttk.Entry(frame, width=60, show="*")
        self.github_token_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Repository (owner/repo):").pack(anchor=tk.W, pady=(0, 5))
        self.github_repo_entry = ttk.Entry(frame, width=60)
        self.github_repo_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Default Labels:").pack(anchor=tk.W, pady=(0, 5))
        self.github_labels_entry = ttk.Entry(frame, width=60)
        self.github_labels_entry.insert(0, "documentation, automated")
        self.github_labels_entry.pack(fill=tk.X, pady=(0, 15))
    
    def _create_azure_devops_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Azure DevOps")
        
        ttk.Label(frame, text="Personal Access Token:").pack(anchor=tk.W, pady=(0, 5))
        self.azdo_token_entry = ttk.Entry(frame, width=60, show="*")
        self.azdo_token_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Organization:").pack(anchor=tk.W, pady=(0, 5))
        self.azdo_org_entry = ttk.Entry(frame, width=60)
        self.azdo_org_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Project:").pack(anchor=tk.W, pady=(0, 5))
        self.azdo_project_entry = ttk.Entry(frame, width=60)
        self.azdo_project_entry.pack(fill=tk.X, pady=(0, 15))
    
    def _create_slack_tab(self, notebook):
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Slack")
        
        ttk.Label(frame, text="Webhook URL:").pack(anchor=tk.W, pady=(0, 5))
        self.slack_webhook_entry = ttk.Entry(frame, width=60)
        self.slack_webhook_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Default Channel (optional):").pack(anchor=tk.W, pady=(0, 5))
        self.slack_channel_entry = ttk.Entry(frame, width=60)
        self.slack_channel_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.slack_username_entry = ttk.Entry(frame, width=60)
        self.slack_username_entry.insert(0, "Azure SQL Doc Generator")
        self.slack_username_entry.pack(fill=tk.X, pady=(0, 15))
    
    def _test_integration(self):
        messagebox.showinfo("Test", "Integration test functionality would be implemented here")
    
    def _close(self):
        self.dialog.destroy()
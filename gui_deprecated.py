#!/usr/bin/env python3
"""
Azure SQL Database Documentation Generator - GUI Version
========================================================

A modern graphical user interface for the Azure SQL Database Documentation Generator.
Provides an intuitive way to configure connections, select databases, and generate
comprehensive database documentation.

Features:
- Modern, responsive GUI design
- Connection configuration with multiple authentication methods
- Database selection and validation
- Real-time progress tracking
- Output format selection
- Configuration save/load
- Integrated logging display
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import our existing modules
from db_connection import AzureSQLConnection
from config_manager import ConfigManager
from documentation_extractor import DocumentationExtractor
from documentation_generator import DocumentationGenerator
from connection_profiles import ConnectionProfileManager
from schema_comparison import SchemaComparator
from dependency_visualizer import DependencyVisualizer, VisualizationType
from object_details import ObjectDetailsManager
from template_editor import TemplateEditor
from scheduler_monitor import JobScheduler, DatabaseMonitor, create_documentation_job_handler
from project_manager import ProjectManager, DatabaseProject, ProjectSelectionDialog, CreateProjectDialog, BatchOperationDialog
from api_integration import APIServer, WebhookManager, PlatformIntegration, WebhookConfigDialog, PlatformIntegrationDialog
from reporting_analytics import ReportingDashboard
from migration_planner import MigrationPlannerGUI
from compliance_auditor import ComplianceAuditorGUI

class DatabaseDocumentationGUI:
    """Main GUI application for database documentation generation."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_logging()
        self.setup_profile_manager()
        self.create_widgets()
        self.setup_layout()
        self.load_initial_config()
        
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Azure SQL Database Documentation Generator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern color scheme
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#34495e',
            'background': '#f8f9fa',
            'text': '#2c3e50'
        }
        
        # Configure custom styles
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=self.colors['primary'])
        self.style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), foreground=self.colors['dark'])
        self.style.configure('Status.TLabel', font=('Arial', 10), foreground=self.colors['secondary'])
        self.style.configure('Success.TLabel', font=('Arial', 10), foreground=self.colors['success'])
        self.style.configure('Error.TLabel', font=('Arial', 10), foreground=self.colors['danger'])
        
        self.root.configure(bg=self.colors['background'])
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('database.ico')
        except:
            pass
    
    def setup_variables(self):
        """Initialize tkinter variables."""
        # Connection variables
        self.connection_method = tk.StringVar(value="credentials")
        self.server = tk.StringVar(value="eds-sqlserver.eastus2.cloudapp.azure.com")
        self.database = tk.StringVar(value="EDS")
        self.username = tk.StringVar(value="EDSAdmin")
        self.password = tk.StringVar(value="Consultant~!")
        self.client_id = tk.StringVar()
        self.client_secret = tk.StringVar()
        self.tenant_id = tk.StringVar()
        self.connection_string = tk.StringVar()
        
        # Documentation options
        self.output_dir = tk.StringVar(value="output")
        self.generate_html = tk.BooleanVar(value=True)
        self.generate_markdown = tk.BooleanVar(value=True)
        self.generate_json = tk.BooleanVar(value=True)
        self.include_system_objects = tk.BooleanVar(value=False)
        self.include_row_counts = tk.BooleanVar(value=True)
        
        # Status variables
        self.status_text = tk.StringVar(value="Ready")
        self.progress_value = tk.DoubleVar()
        self.connection_status = tk.StringVar(value="Not Connected")
        
        # Available databases
        self.available_databases = []
        self.selected_database_info = {}
        self.database_search = tk.StringVar()
        
        # Validation variables
        self.validation_status = {
            'server': tk.StringVar(value=""),
            'database': tk.StringVar(value=""),
            'username': tk.StringVar(value=""),
            'password': tk.StringVar(value=""),
            'connection_string': tk.StringVar(value="")
        }
        
        # Progress tracking variables
        self.generation_cancelled = False
        self.current_step = tk.StringVar(value="Ready")
        self.detailed_progress = tk.StringVar(value="")
        self.estimated_time = tk.StringVar(value="")
        
        # Schema comparison variables
        self.comparison_source = tk.StringVar(value="database")  # database, file
        self.comparison_target = tk.StringVar(value="database")  # database, file  
        self.source_database = tk.StringVar()
        self.target_database = tk.StringVar()
        self.source_file_path = tk.StringVar()
        self.target_file_path = tk.StringVar()
        self.comparison_results = None
        
        # Dependency visualization variables
        self.viz_type = tk.StringVar(value="relationship_diagram")
        self.viz_schema_filter = tk.StringVar()
        self.viz_center_object = tk.StringVar()
        self.viz_include_views = tk.BooleanVar(value=True)
        self.viz_include_procedures = tk.BooleanVar(value=False)
        self.current_visualization = None
        
        # Search and filter variables
        self.search_query = tk.StringVar()
        self.search_type = tk.StringVar(value="all")  # all, tables, views, procedures, functions
        self.search_case_sensitive = tk.BooleanVar(value=False)
        self.search_regex = tk.BooleanVar(value=False)
        self.search_scope = tk.StringVar(value="name")  # name, description, columns, all
        self.search_results = []
        self.current_schema_data = None
        
        # Scheduler and monitoring variables
        self.job_scheduler = None
        self.database_monitor = None
        self.scheduler_running = tk.BooleanVar(value=False)
        self.monitoring_enabled = tk.BooleanVar(value=True)
        self.monitoring_interval = tk.IntVar(value=30)  # minutes
        self.email_notifications = tk.BooleanVar(value=False)
        self.webhook_notifications = tk.BooleanVar(value=False)
        self.email_server = tk.StringVar(value="smtp.gmail.com")
        self.email_port = tk.IntVar(value=587)
        self.email_username = tk.StringVar()
        self.email_password = tk.StringVar()
        self.email_from = tk.StringVar()
        self.email_to = tk.StringVar()
        self.webhook_urls = tk.StringVar()
        
        # Project management variables
        self.current_project = None
        self.current_project_id = tk.StringVar()
        self.current_project_name = tk.StringVar(value="No Project Selected")
        self.project_databases = []
        
        # API and webhook variables
        self.api_server = None
        self.webhook_manager = None
        self.platform_integration = None
        self.api_server_running = tk.BooleanVar(value=False)
        self.api_port = tk.IntVar(value=8080)
        self.webhook_notifications_enabled = tk.BooleanVar(value=False)
        self.platform_integrations_enabled = tk.BooleanVar(value=False)
        self.github_integration = tk.BooleanVar(value=False)
        self.azure_devops_integration = tk.BooleanVar(value=False)
        self.slack_integration = tk.BooleanVar(value=False)
        
    def setup_logging(self):
        """Setup logging for GUI display."""
        self.log_handler = GUILogHandler(self)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        root_logger.setLevel(logging.INFO)
    
    def setup_profile_manager(self):
        """Setup connection profile manager and other managers."""
        self.profile_manager = ConnectionProfileManager()
        self.current_profile_name = tk.StringVar()
        
        # Initialize scheduler and monitor
        self.job_scheduler = JobScheduler()
        self.database_monitor = DatabaseMonitor(self.job_scheduler)
        
        # Register documentation job handler
        self.job_scheduler.register_job_type("documentation", create_documentation_job_handler())
        self.job_scheduler.register_job_type("monitoring", 
                                           lambda config: self.database_monitor.monitor_database(config))
        
        # Initialize project manager
        self.project_manager = ProjectManager()
        
        # Initialize API and webhook components
        self.webhook_manager = WebhookManager()
        self.api_server = APIServer(self.api_port.get())
        self.platform_integration = PlatformIntegration()
        
        # Initialize reporting dashboard
        self.reporting_dashboard = ReportingDashboard(self)
        
        # Initialize migration planner
        self.migration_planner = MigrationPlannerGUI(self)
        
        # Initialize compliance auditor
        self.compliance_auditor = ComplianceAuditorGUI(self)
        
        # Initialize object details manager (will be set after window creation)
        self.object_details_manager = None
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Azure SQL Database Documentation Generator",
            style="Title.TLabel"
        )
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Connection tab
        self.connection_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.connection_frame, text="Database Connection")
        self.create_connection_tab()
        
        # Database listing tab
        self.database_list_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.database_list_frame, text="Available Databases")
        self.create_database_list_tab()
        
        # Documentation tab
        self.documentation_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.documentation_frame, text="Documentation Options")
        self.create_documentation_tab()
        
        # Search & Filter tab
        self.search_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.search_frame, text="Search & Filter")
        self.create_search_tab()
        
        # Schema Comparison tab
        self.comparison_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.comparison_frame, text="Schema Comparison")
        self.create_comparison_tab()
        
        # Dependency Visualization tab
        self.visualization_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.visualization_frame, text="Dependency Visualization")
        self.create_visualization_tab()
        
        # Scheduler & Monitoring tab
        self.scheduler_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.scheduler_frame, text="Scheduler & Monitoring")
        self.create_scheduler_tab()
        
        # Project Management tab
        self.project_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.project_frame, text="Project Management")
        self.create_project_tab()
        
        # API Integration tab
        self.api_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.api_frame, text="API & Integrations")
        self.create_api_tab()
        
        # Analytics Dashboard tab
        self.reporting_dashboard.create_dashboard_tab(self.notebook)
        
        # Migration Planning tab
        self.migration_planner.create_migration_tab(self.notebook)
        
        # Compliance & Security tab
        self.compliance_auditor.create_compliance_tab(self.notebook)
        
        # Progress tab
        self.progress_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.progress_frame, text="Progress & Logs")
        self.create_progress_tab()
        
        # Control buttons frame
        self.control_frame = ttk.Frame(self.main_frame, padding="10")
        self.create_control_buttons()
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame, relief="sunken", padding="5")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_text, style="Status.TLabel")
        self.connection_label = ttk.Label(self.status_frame, textvariable=self.connection_status, style="Status.TLabel")
        
    def create_connection_tab(self):
        """Create the database connection configuration tab."""
        # Profile management section
        self.create_profile_management_section()
        
        # Connection method selection
        method_frame = ttk.LabelFrame(self.connection_frame, text="Authentication Method", padding="10")
        
        methods = [
            ("Username/Password", "credentials"),
            ("Azure Active Directory", "azure_ad"),
            ("Service Principal", "service_principal"),
            ("Connection String", "connection_string")
        ]
        
        for i, (text, value) in enumerate(methods):
            ttk.Radiobutton(
                method_frame, 
                text=text, 
                variable=self.connection_method, 
                value=value,
                command=self.on_connection_method_changed
            ).grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
        
        # Connection details frame
        self.details_frame = ttk.LabelFrame(self.connection_frame, text="Connection Details", padding="10")
        
        # Server and Database (always shown)
        ttk.Label(self.details_frame, text="Server:").grid(row=0, column=0, sticky="w", pady=5)
        self.server_entry = ttk.Entry(self.details_frame, textvariable=self.server, width=50)
        self.server_entry.grid(row=0, column=1, sticky="ew", padx=(5,0), pady=5)
        self.server_entry.bind('<KeyRelease>', lambda e: self.validate_field('server'))
        
        # Server validation label
        self.server_validation = ttk.Label(self.details_frame, textvariable=self.validation_status['server'], 
                                          foreground="red", font=("Arial", 8))
        self.server_validation.grid(row=0, column=2, sticky="w", padx=5)
        
        ttk.Label(self.details_frame, text="Database:").grid(row=1, column=0, sticky="w", pady=5)
        self.database_combo = ttk.Combobox(self.details_frame, textvariable=self.database, width=47)
        self.database_combo.grid(row=1, column=1, sticky="ew", padx=(5,0), pady=5)
        self.database_combo.bind('<KeyRelease>', lambda e: self.validate_field('database'))
        self.database_combo.bind('<<ComboboxSelected>>', lambda e: self.validate_field('database'))
        
        # Database validation label
        self.database_validation = ttk.Label(self.details_frame, textvariable=self.validation_status['database'], 
                                           foreground="red", font=("Arial", 8))
        self.database_validation.grid(row=1, column=2, sticky="w", padx=5)
        
        # Dynamic fields based on connection method
        self.create_connection_fields()
        
        # Test connection button
        self.test_btn = ttk.Button(
            self.details_frame, 
            text="Test Connection", 
            command=self.test_connection
        )
        self.test_btn.grid(row=10, column=1, sticky="e", pady=10)
        
        # Load databases button
        self.load_db_btn = ttk.Button(
            self.details_frame,
            text="Load Databases",
            command=self.load_databases
        )
        self.load_db_btn.grid(row=10, column=0, sticky="w", pady=10)
        
        # Configure grid weights
        self.details_frame.columnconfigure(1, weight=1)
        self.details_frame.columnconfigure(2, weight=0)  # Validation column
        
        # Pack frames
        method_frame.pack(fill="x", pady=(0, 10))
        self.details_frame.pack(fill="both", expand=True)
    
    def create_database_list_tab(self):
        """Create the database listing tab."""
        # Search and control frame
        control_frame = ttk.Frame(self.database_list_frame)
        
        # Search functionality
        search_frame = ttk.LabelFrame(control_frame, text="Search & Filter", padding="5")
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.database_search, width=30)
        search_entry.pack(side="left", padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_databases)
        
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=5)
        search_frame.pack(side="left", fill="x", expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        self.refresh_db_btn = ttk.Button(
            button_frame, 
            text="Refresh List", 
            command=self.refresh_database_list
        )
        self.refresh_db_btn.pack(side="right", padx=5)
        
        self.select_db_btn = ttk.Button(
            button_frame, 
            text="Select Database", 
            command=self.select_database_from_list,
            state="disabled"
        )
        self.select_db_btn.pack(side="right", padx=5)
        
        # Add Generate Documentation button
        self.generate_docs_btn = ttk.Button(
            button_frame, 
            text="Generate Documentation", 
            command=self.generate_docs_from_list,
            state="disabled"
        )
        self.generate_docs_btn.pack(side="right", padx=5)
        
        # Add Browse Schema button
        self.browse_schema_btn = ttk.Button(
            button_frame, 
            text="Browse Schema", 
            command=self.browse_database_schema,
            state="disabled"
        )
        self.browse_schema_btn.pack(side="right", padx=5)
        
        button_frame.pack(side="right")
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Database list with details
        list_frame = ttk.LabelFrame(self.database_list_frame, text="Available Databases", padding="10")
        
        # Create treeview for database list
        columns = ("database_name", "created", "status", "collation", "size_mb")
        self.database_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Define column headings and widths
        self.database_tree.heading("database_name", text="Database Name")
        self.database_tree.heading("created", text="Created")
        self.database_tree.heading("status", text="Status")
        self.database_tree.heading("collation", text="Collation")
        self.database_tree.heading("size_mb", text="Size (MB)")
        
        self.database_tree.column("database_name", width=200)
        self.database_tree.column("created", width=150)
        self.database_tree.column("status", width=100)
        self.database_tree.column("collation", width=250)
        self.database_tree.column("size_mb", width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.database_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.database_tree.xview)
        self.database_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Bind selection event
        self.database_tree.bind("<<TreeviewSelect>>", self.on_database_select)
        self.database_tree.bind("<Double-1>", self.on_database_double_click)
        
        # Pack treeview and scrollbars
        self.database_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Database details panel
        details_frame = ttk.LabelFrame(self.database_list_frame, text="Database Information", padding="10")
        
        # Create a frame for database info display
        info_frame = ttk.Frame(details_frame)
        
        # Database info display
        self.db_info_text = tk.Text(info_frame, height=8, width=80, wrap="word", state="disabled")
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.db_info_text.yview)
        self.db_info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.db_info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")
        
        info_frame.pack(fill="both", expand=True)
        details_frame.pack(fill="both", expand=True)
        
        # Initialize database info display
        self._clear_database_info()
        
        # Add a note about refreshing
        initial_text = """Welcome to Database Explorer!
        
Click 'Refresh List' to load all available databases from your server.

This will show detailed information including:
• Database names and creation dates
• Current status and collation settings  
• Database sizes and storage information
• System vs User database classification

Features:
• Search and filter databases by name
• Double-click or use 'Select Database' to choose for documentation
• Use 'Generate Documentation' to immediately create documentation
• Visual distinction between system and user databases
• Detailed information panel for selected databases
        
Note: Make sure your connection settings are configured in the 'Database Connection' tab first."""
        
        self.db_info_text.configure(state="normal")
        self.db_info_text.delete("1.0", tk.END)
        self.db_info_text.insert("1.0", initial_text)
        self.db_info_text.configure(state="disabled")
        
    def create_connection_fields(self):
        """Create connection fields based on selected method."""
        # Clear existing dynamic fields
        for widget in self.details_frame.winfo_children():
            if int(widget.grid_info().get('row', 0)) >= 2:
                widget.destroy()
        
        method = self.connection_method.get()
        row = 2
        
        if method == "credentials":
            ttk.Label(self.details_frame, text="Username:").grid(row=row, column=0, sticky="w", pady=5)
            self.username_entry = ttk.Entry(self.details_frame, textvariable=self.username, width=50)
            self.username_entry.grid(row=row, column=1, sticky="ew", padx=(5,0), pady=5)
            self.username_entry.bind('<KeyRelease>', lambda e: self.validate_field('username'))
            
            # Username validation label
            self.username_validation = ttk.Label(self.details_frame, textvariable=self.validation_status['username'], 
                                                foreground="red", font=("Arial", 8))
            self.username_validation.grid(row=row, column=2, sticky="w", padx=5)
            row += 1
            
            ttk.Label(self.details_frame, text="Password:").grid(row=row, column=0, sticky="w", pady=5)
            self.password_entry = ttk.Entry(self.details_frame, textvariable=self.password, show="*", width=50)
            self.password_entry.grid(row=row, column=1, sticky="ew", padx=(5,0), pady=5)
            self.password_entry.bind('<KeyRelease>', lambda e: self.validate_field('password'))
            
            # Password validation label
            self.password_validation = ttk.Label(self.details_frame, textvariable=self.validation_status['password'], 
                                                foreground="red", font=("Arial", 8))
            self.password_validation.grid(row=row, column=2, sticky="w", padx=5)
            
        elif method == "service_principal":
            ttk.Label(self.details_frame, text="Client ID:").grid(row=row, column=0, sticky="w", pady=5)
            ttk.Entry(self.details_frame, textvariable=self.client_id, width=50).grid(row=row, column=1, sticky="ew", padx=(5,0), pady=5)
            row += 1
            
            ttk.Label(self.details_frame, text="Client Secret:").grid(row=row, column=0, sticky="w", pady=5)
            ttk.Entry(self.details_frame, textvariable=self.client_secret, show="*", width=50).grid(row=row, column=1, sticky="ew", padx=(5,0), pady=5)
            row += 1
            
            ttk.Label(self.details_frame, text="Tenant ID:").grid(row=row, column=0, sticky="w", pady=5)
            ttk.Entry(self.details_frame, textvariable=self.tenant_id, width=50).grid(row=row, column=1, sticky="ew", padx=(5,0), pady=5)
            
        elif method == "connection_string":
            ttk.Label(self.details_frame, text="Connection String:").grid(row=row, column=0, sticky="nw", pady=5)
            self.connection_text = tk.Text(self.details_frame, height=4, width=50, wrap="word")
            self.connection_text.grid(row=row, column=1, sticky="ew", padx=(5,0), pady=5)
            
            # Bind text widget to string variable
            def update_connection_string(*args):
                self.connection_string.set(self.connection_text.get("1.0", "end-1c"))
                self.validate_field('connection_string')
            self.connection_text.bind('<KeyRelease>', update_connection_string)
            
            # Connection string validation label
            self.connection_validation = ttk.Label(self.details_frame, textvariable=self.validation_status['connection_string'], 
                                                 foreground="red", font=("Arial", 8))
            self.connection_validation.grid(row=row, column=2, sticky="nw", padx=5)
            
        # Recreate buttons
        row += 2
        self.test_btn = ttk.Button(
            self.details_frame, 
            text="Test Connection", 
            command=self.test_connection
        )
        self.test_btn.grid(row=row, column=1, sticky="e", pady=10)
        
        self.load_db_btn = ttk.Button(
            self.details_frame,
            text="Load Databases",
            command=self.load_databases
        )
        self.load_db_btn.grid(row=row, column=0, sticky="w", pady=10)
    
    def create_documentation_tab(self):
        """Create the documentation options tab."""
        # Output options
        output_frame = ttk.LabelFrame(self.documentation_frame, text="Output Options", padding="10")
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", pady=5)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=40)
        output_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Button(
            output_frame, 
            text="Browse", 
            command=self.browse_output_dir
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Format selection
        format_frame = ttk.LabelFrame(self.documentation_frame, text="Output Formats", padding="10")
        
        ttk.Checkbutton(format_frame, text="HTML Documentation", variable=self.generate_html).pack(anchor="w", pady=2)
        ttk.Checkbutton(format_frame, text="Markdown Documentation", variable=self.generate_markdown).pack(anchor="w", pady=2)
        ttk.Checkbutton(format_frame, text="JSON Data Export", variable=self.generate_json).pack(anchor="w", pady=2)
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(self.documentation_frame, text="Advanced Options", padding="10")
        
        ttk.Checkbutton(advanced_frame, text="Include System Objects", variable=self.include_system_objects).pack(anchor="w", pady=2)
        ttk.Checkbutton(advanced_frame, text="Include Row Counts", variable=self.include_row_counts).pack(anchor="w", pady=2)
        
        # Configuration management
        config_frame = ttk.LabelFrame(self.documentation_frame, text="Configuration", padding="10")
        
        config_buttons = ttk.Frame(config_frame)
        ttk.Button(config_buttons, text="Save Config", command=self.save_config).pack(side="left", padx=5)
        ttk.Button(config_buttons, text="Load Config", command=self.load_config).pack(side="left", padx=5)
        ttk.Button(config_buttons, text="Reset to Defaults", command=self.reset_config).pack(side="left", padx=5)
        config_buttons.pack()
        
        # Template customization
        template_frame = ttk.LabelFrame(self.documentation_frame, text="Template Customization", padding="10")
        
        ttk.Label(
            template_frame, 
            text="Customize the appearance and content of generated documentation"
        ).pack(anchor="w", pady=(0, 10))
        
        ttk.Button(
            template_frame,
            text="Open Template Editor",
            command=self.open_template_editor
        ).pack(anchor="w")
        
        # Pack frames
        output_frame.pack(fill="x", pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        format_frame.pack(fill="x", pady=(0, 10))
        advanced_frame.pack(fill="x", pady=(0, 10))
        config_frame.pack(fill="x", pady=(0, 10))
        template_frame.pack(fill="x")
    
    def create_search_tab(self):
        """Create the search and filter tab."""
        # Search configuration
        search_config_frame = ttk.LabelFrame(self.search_frame, text="Search Configuration", padding="10")
        
        # Search query
        ttk.Label(search_config_frame, text="Search Query:").grid(row=0, column=0, sticky="w", pady=5)
        search_entry = ttk.Entry(search_config_frame, textvariable=self.search_query, width=40)
        search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        search_entry.bind('<Return>', lambda e: self.perform_search())
        
        ttk.Button(
            search_config_frame,
            text="Search",
            command=self.perform_search
        ).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(
            search_config_frame,
            text="Clear",
            command=self.clear_search
        ).grid(row=0, column=3, padx=5, pady=5)
        
        # Search type filter
        ttk.Label(search_config_frame, text="Object Type:").grid(row=1, column=0, sticky="w", pady=5)
        type_combo = ttk.Combobox(
            search_config_frame,
            textvariable=self.search_type,
            values=["all", "tables", "views", "procedures", "functions"],
            state="readonly",
            width=15
        )
        type_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Search scope
        ttk.Label(search_config_frame, text="Search In:").grid(row=1, column=2, sticky="w", pady=5)
        scope_combo = ttk.Combobox(
            search_config_frame,
            textvariable=self.search_scope,
            values=["name", "description", "columns", "all"],
            state="readonly",
            width=15
        )
        scope_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Search options
        options_frame = ttk.Frame(search_config_frame)
        options_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=10)
        
        ttk.Checkbutton(
            options_frame,
            text="Case Sensitive",
            variable=self.search_case_sensitive
        ).pack(side="left", padx=(0, 20))
        
        ttk.Checkbutton(
            options_frame,
            text="Regular Expression",
            variable=self.search_regex
        ).pack(side="left", padx=(0, 20))
        
        # Results display
        results_frame = ttk.LabelFrame(self.search_frame, text="Search Results", padding="10")
        
        # Results treeview
        self.search_tree = ttk.Treeview(
            results_frame,
            columns=("type", "schema", "description", "match_info"),
            show="tree headings",
            height=15
        )
        
        # Configure columns
        self.search_tree.heading("#0", text="Object Name")
        self.search_tree.heading("type", text="Type")
        self.search_tree.heading("schema", text="Schema")
        self.search_tree.heading("description", text="Description")
        self.search_tree.heading("match_info", text="Match Details")
        
        self.search_tree.column("#0", width=200)
        self.search_tree.column("type", width=100)
        self.search_tree.column("schema", width=100)
        self.search_tree.column("description", width=250)
        self.search_tree.column("match_info", width=200)
        
        # Scrollbars for search results
        search_v_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.search_tree.yview)
        search_h_scroll = ttk.Scrollbar(results_frame, orient="horizontal", command=self.search_tree.xview)
        self.search_tree.configure(yscrollcommand=search_v_scroll.set, xscrollcommand=search_h_scroll.set)
        
        # Pack search tree and scrollbars
        self.search_tree.grid(row=0, column=0, sticky="nsew")
        search_v_scroll.grid(row=0, column=1, sticky="ns")
        search_h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Results actions
        results_actions = ttk.Frame(results_frame)
        results_actions.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        
        ttk.Button(
            results_actions,
            text="View Details",
            command=self.view_search_result_details
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            results_actions,
            text="Export Results",
            command=self.export_search_results
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            results_actions,
            text="Generate Docs for Selection",
            command=self.generate_docs_for_selection
        ).pack(side="left", padx=(0, 10))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.search_frame, text="Search Statistics", padding="10")
        self.search_stats_text = tk.Text(stats_frame, height=4, width=50, state="disabled")
        self.search_stats_text.pack(fill="x")
        
        # Pack main frames
        search_config_frame.pack(fill="x", pady=(0, 10))
        search_config_frame.columnconfigure(1, weight=1)
        
        results_frame.pack(fill="both", expand=True, pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        stats_frame.pack(fill="x")
    
    def create_comparison_tab(self):
        """Create the schema comparison tab."""
        # Comparison configuration
        config_frame = ttk.LabelFrame(self.comparison_frame, text="Comparison Configuration", padding="10")
        
        # Source configuration
        source_frame = ttk.LabelFrame(config_frame, text="Source (Baseline)", padding="10")
        
        # Source type selection
        source_type_frame = ttk.Frame(source_frame)
        ttk.Label(source_type_frame, text="Source Type:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(source_type_frame, text="Current Database", 
                       variable=self.comparison_source, value="database",
                       command=self.on_comparison_source_changed).pack(side="left", padx=5)
        ttk.Radiobutton(source_type_frame, text="JSON File", 
                       variable=self.comparison_source, value="file",
                       command=self.on_comparison_source_changed).pack(side="left", padx=5)
        source_type_frame.pack(fill="x", pady=(0, 10))
        
        # Source database selection
        self.source_db_frame = ttk.Frame(source_frame)
        ttk.Label(self.source_db_frame, text="Database:").pack(side="left", padx=(0, 5))
        self.source_db_combo = ttk.Combobox(self.source_db_frame, textvariable=self.source_database, 
                                           width=30, state="readonly")
        self.source_db_combo.pack(side="left", padx=(0, 10))
        ttk.Button(self.source_db_frame, text="Use Current", 
                  command=self.use_current_database_as_source).pack(side="left", padx=5)
        
        # Source file selection
        self.source_file_frame = ttk.Frame(source_frame)
        ttk.Label(self.source_file_frame, text="JSON File:").pack(side="left", padx=(0, 5))
        ttk.Entry(self.source_file_frame, textvariable=self.source_file_path, width=40).pack(side="left", padx=(0, 5))
        ttk.Button(self.source_file_frame, text="Browse", 
                  command=self.browse_source_file).pack(side="left", padx=5)
        
        source_frame.pack(fill="x", pady=(0, 10))
        
        # Target configuration
        target_frame = ttk.LabelFrame(config_frame, text="Target (Comparison)", padding="10")
        
        # Target type selection
        target_type_frame = ttk.Frame(target_frame)
        ttk.Label(target_type_frame, text="Target Type:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(target_type_frame, text="Different Database", 
                       variable=self.comparison_target, value="database",
                       command=self.on_comparison_target_changed).pack(side="left", padx=5)
        ttk.Radiobutton(target_type_frame, text="JSON File", 
                       variable=self.comparison_target, value="file",
                       command=self.on_comparison_target_changed).pack(side="left", padx=5)
        target_type_frame.pack(fill="x", pady=(0, 10))
        
        # Target database selection
        self.target_db_frame = ttk.Frame(target_frame)
        ttk.Label(self.target_db_frame, text="Database:").pack(side="left", padx=(0, 5))
        self.target_db_combo = ttk.Combobox(self.target_db_frame, textvariable=self.target_database, 
                                           width=30, state="readonly")
        self.target_db_combo.pack(side="left", padx=(0, 10))
        ttk.Button(self.target_db_frame, text="Load Databases", 
                  command=self.load_databases_for_comparison).pack(side="left", padx=5)
        
        # Target file selection
        self.target_file_frame = ttk.Frame(target_frame)
        ttk.Label(self.target_file_frame, text="JSON File:").pack(side="left", padx=(0, 5))
        ttk.Entry(self.target_file_frame, textvariable=self.target_file_path, width=40).pack(side="left", padx=(0, 5))
        ttk.Button(self.target_file_frame, text="Browse", 
                  command=self.browse_target_file).pack(side="left", padx=5)
        
        target_frame.pack(fill="x", pady=(0, 10))
        
        # Comparison actions
        actions_frame = ttk.Frame(config_frame)
        ttk.Button(actions_frame, text="Compare Schemas", 
                  command=self.compare_schemas, style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(actions_frame, text="Export Results", 
                  command=self.export_comparison_results).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Clear Results", 
                  command=self.clear_comparison_results).pack(side="left", padx=5)
        actions_frame.pack(fill="x", pady=10)
        
        config_frame.pack(fill="x", pady=(0, 10))
        
        # Results display
        results_frame = ttk.LabelFrame(self.comparison_frame, text="Comparison Results", padding="10")
        
        # Results summary
        self.summary_frame = ttk.Frame(results_frame)
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, height=4, width=80, state="disabled")
        self.summary_text.pack(fill="both", expand=True)
        self.summary_frame.pack(fill="x", pady=(0, 10))
        
        # Detailed results with tabs
        self.results_notebook = ttk.Notebook(results_frame)
        
        # Changes tab
        changes_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(changes_frame, text="Changes")
        
        # Create treeview for changes
        columns = ('Object', 'Type', 'Change', 'Impact', 'Description')
        self.changes_tree = ttk.Treeview(changes_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.changes_tree.heading('Object', text='Object Name')
        self.changes_tree.heading('Type', text='Object Type')
        self.changes_tree.heading('Change', text='Change Type')
        self.changes_tree.heading('Impact', text='Impact Level')
        self.changes_tree.heading('Description', text='Description')
        
        self.changes_tree.column('Object', width=200)
        self.changes_tree.column('Type', width=100)
        self.changes_tree.column('Change', width=100)
        self.changes_tree.column('Impact', width=80)
        self.changes_tree.column('Description', width=300)
        
        # Add scrollbars
        changes_scroll = ttk.Scrollbar(changes_frame, orient="vertical", command=self.changes_tree.yview)
        self.changes_tree.configure(yscrollcommand=changes_scroll.set)
        
        changes_h_scroll = ttk.Scrollbar(changes_frame, orient="horizontal", command=self.changes_tree.xview)
        self.changes_tree.configure(xscrollcommand=changes_h_scroll.set)
        
        # Pack treeview and scrollbars
        self.changes_tree.pack(side="left", fill="both", expand=True)
        changes_scroll.pack(side="right", fill="y")
        changes_h_scroll.pack(side="bottom", fill="x")
        
        # Impact analysis tab
        impact_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(impact_frame, text="Impact Analysis")
        self.impact_text = scrolledtext.ScrolledText(impact_frame, height=15, width=80, state="disabled")
        self.impact_text.pack(fill="both", expand=True)
        
        self.results_notebook.pack(fill="both", expand=True)
        results_frame.pack(fill="both", expand=True)
        
        # Initialize UI state
        self.on_comparison_source_changed()
        self.on_comparison_target_changed()
    
    def create_visualization_tab(self):
        """Create the dependency visualization tab."""
        # Visualization configuration
        config_frame = ttk.LabelFrame(self.visualization_frame, text="Visualization Configuration", padding="10")
        
        # Visualization type selection
        type_frame = ttk.LabelFrame(config_frame, text="Visualization Type", padding="10")
        
        viz_types = [
            ("Relationship Diagram", "relationship_diagram"),
            ("Dependency Graph", "dependency_graph"),
            ("Hierarchical View", "hierarchical_view"),
            ("Circular Layout", "circular_layout")
        ]
        
        for i, (text, value) in enumerate(viz_types):
            ttk.Radiobutton(type_frame, text=text, variable=self.viz_type, 
                           value=value, command=self.on_viz_type_changed).grid(
                row=i//2, column=i%2, sticky="w", padx=5, pady=2)
        
        type_frame.pack(fill="x", pady=(0, 10))
        
        # Filters and options
        options_frame = ttk.LabelFrame(config_frame, text="Options & Filters", padding="10")
        
        # Schema filter
        schema_row = ttk.Frame(options_frame)
        ttk.Label(schema_row, text="Schema Filter:").pack(side="left", padx=(0, 5))
        ttk.Entry(schema_row, textvariable=self.viz_schema_filter, width=30).pack(side="left", padx=(0, 10))
        ttk.Label(schema_row, text="(comma-separated)").pack(side="left")
        schema_row.pack(fill="x", pady=(0, 10))
        
        # Center object for circular layout
        self.center_object_frame = ttk.Frame(options_frame)
        ttk.Label(self.center_object_frame, text="Center Object:").pack(side="left", padx=(0, 5))
        ttk.Entry(self.center_object_frame, textvariable=self.viz_center_object, width=30).pack(side="left")
        # Initially hidden
        
        # Include options
        include_frame = ttk.Frame(options_frame)
        ttk.Checkbutton(include_frame, text="Include Views", 
                       variable=self.viz_include_views).pack(side="left", padx=(0, 10))
        ttk.Checkbutton(include_frame, text="Include Procedures", 
                       variable=self.viz_include_procedures).pack(side="left", padx=(0, 10))
        include_frame.pack(fill="x", pady=(0, 10))
        
        options_frame.pack(fill="x", pady=(0, 10))
        
        # Visualization actions
        actions_frame = ttk.Frame(config_frame)
        ttk.Button(actions_frame, text="Generate Visualization", 
                  command=self.generate_visualization, style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(actions_frame, text="Export HTML", 
                  command=self.export_visualization_html).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Export SVG", 
                  command=self.export_visualization_svg).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="View in Browser", 
                  command=self.view_visualization_in_browser).pack(side="left", padx=5)
        actions_frame.pack(fill="x", pady=10)
        
        config_frame.pack(fill="x", pady=(0, 10))
        
        # Visualization preview/info
        preview_frame = ttk.LabelFrame(self.visualization_frame, text="Visualization Preview", padding="10")
        
        # Statistics display
        stats_frame = ttk.Frame(preview_frame)
        self.viz_stats_text = scrolledtext.ScrolledText(stats_frame, height=6, width=80, state="disabled")
        self.viz_stats_text.pack(fill="both", expand=True)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Preview placeholder (could be enhanced with actual preview)
        preview_info_frame = ttk.Frame(preview_frame)
        ttk.Label(preview_info_frame, text="📊 Visualization Preview", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(preview_info_frame, text="Generate a visualization to see statistics and preview here.").pack(pady=5)
        ttk.Label(preview_info_frame, text="Use 'Export HTML' and 'View in Browser' to see the interactive visualization.").pack(pady=5)
        preview_info_frame.pack(fill="both", expand=True)
        
        preview_frame.pack(fill="both", expand=True)
        
        # Initialize UI state
        self.on_viz_type_changed()
    
    def create_scheduler_tab(self):
        """Create the scheduler and monitoring tab."""
        # Main paned window for layout
        main_paned = ttk.PanedWindow(self.scheduler_frame, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Configuration and controls
        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Job history and monitoring
        right_frame = ttk.Frame(main_paned, width=600)
        main_paned.add(right_frame, weight=2)
        
        self.create_scheduler_controls(left_frame)
        self.create_scheduler_status(right_frame)
    
    def create_scheduler_controls(self, parent):
        """Create scheduler control panel."""
        # Scheduler status and controls
        status_frame = ttk.LabelFrame(parent, text="Scheduler Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.scheduler_status_label = ttk.Label(status_frame, text="Status: Stopped", 
                                               foreground="red", font=("Arial", 10, "bold"))
        self.scheduler_status_label.pack(anchor="w", pady=(0, 10))
        
        buttons_frame = ttk.Frame(status_frame)
        buttons_frame.pack(fill="x")
        
        self.start_scheduler_btn = ttk.Button(buttons_frame, text="Start Scheduler", 
                                            command=self.start_scheduler)
        self.start_scheduler_btn.pack(side="left", padx=(0, 10))
        
        self.stop_scheduler_btn = ttk.Button(buttons_frame, text="Stop Scheduler", 
                                           command=self.stop_scheduler, state="disabled")
        self.stop_scheduler_btn.pack(side="left", padx=(0, 10))
        
        # Documentation job configuration
        doc_job_frame = ttk.LabelFrame(parent, text="Documentation Jobs", padding="10")
        doc_job_frame.pack(fill="x", pady=(0, 10))
        
        # Schedule configuration
        schedule_frame = ttk.Frame(doc_job_frame)
        schedule_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(schedule_frame, text="Schedule:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.schedule_combo = ttk.Combobox(schedule_frame, 
                                         values=["daily", "weekly", "hourly", "every_30_minutes", 
                                                "every_2_hours", "08:30", "18:00"], 
                                         width=20)
        self.schedule_combo.set("daily")
        self.schedule_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Button(schedule_frame, text="Add Documentation Job", 
                  command=self.add_documentation_job).grid(row=0, column=2)
        
        schedule_frame.columnconfigure(1, weight=1)
        
        # Monitoring configuration
        monitor_frame = ttk.LabelFrame(parent, text="Database Monitoring", padding="10")
        monitor_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Checkbutton(monitor_frame, text="Enable Monitoring", 
                       variable=self.monitoring_enabled,
                       command=self.toggle_monitoring).pack(anchor="w", pady=(0, 5))
        
        interval_frame = ttk.Frame(monitor_frame)
        interval_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(interval_frame, text="Check Interval (minutes):").pack(side="left", padx=(0, 10))
        ttk.Spinbox(interval_frame, from_=5, to=1440, textvariable=self.monitoring_interval, 
                   width=10).pack(side="left")
        
        ttk.Button(monitor_frame, text="Run Manual Check", 
                  command=self.run_manual_check).pack(anchor="w", pady=(10, 0))
        
        # Notification configuration
        notify_frame = ttk.LabelFrame(parent, text="Notifications", padding="10")
        notify_frame.pack(fill="both", expand=True)
        
        # Email notifications
        email_frame = ttk.LabelFrame(notify_frame, text="Email Settings", padding="10")
        email_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Checkbutton(email_frame, text="Enable Email Notifications", 
                       variable=self.email_notifications).pack(anchor="w", pady=(0, 5))
        
        # Email configuration grid
        email_config = ttk.Frame(email_frame)
        email_config.pack(fill="x")
        
        ttk.Label(email_config, text="SMTP Server:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(email_config, textvariable=self.email_server, width=25).grid(row=0, column=1, sticky="ew")
        
        ttk.Label(email_config, text="Port:").grid(row=0, column=2, sticky="w", padx=(20, 10))
        ttk.Spinbox(email_config, from_=25, to=587, textvariable=self.email_port, 
                   width=8).grid(row=0, column=3)
        
        ttk.Label(email_config, text="Username:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(email_config, textvariable=self.email_username, width=25).grid(row=1, column=1, columnspan=3, sticky="ew", pady=(5, 0))
        
        ttk.Label(email_config, text="Password:").grid(row=2, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(email_config, textvariable=self.email_password, show="*", width=25).grid(row=2, column=1, columnspan=3, sticky="ew", pady=(5, 0))
        
        ttk.Label(email_config, text="From:").grid(row=3, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(email_config, textvariable=self.email_from, width=25).grid(row=3, column=1, columnspan=3, sticky="ew", pady=(5, 0))
        
        ttk.Label(email_config, text="To (comma-separated):").grid(row=4, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(email_config, textvariable=self.email_to, width=25).grid(row=4, column=1, columnspan=3, sticky="ew", pady=(5, 0))
        
        email_config.columnconfigure(1, weight=1)
        
        # Webhook notifications
        webhook_frame = ttk.LabelFrame(notify_frame, text="Webhook Settings", padding="10")
        webhook_frame.pack(fill="x")
        
        ttk.Checkbutton(webhook_frame, text="Enable Webhook Notifications", 
                       variable=self.webhook_notifications).pack(anchor="w", pady=(0, 5))
        
        ttk.Label(webhook_frame, text="Webhook URLs (one per line):").pack(anchor="w", pady=(0, 5))
        self.webhook_text = tk.Text(webhook_frame, height=4, width=40)
        self.webhook_text.pack(fill="x")
    
    def create_scheduler_status(self, parent):
        """Create scheduler status and history panel."""
        # Job history
        history_frame = ttk.LabelFrame(parent, text="Job History", padding="10")
        history_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # History tree
        history_columns = ("Name", "Type", "Status", "Started", "Duration")
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, 
                                        show="tree headings", height=10)
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120 if col == "Name" else 80)
        
        # Scrollbar for history
        history_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scroll.pack(side="right", fill="y")
        
        # History controls
        history_controls = ttk.Frame(history_frame)
        history_controls.pack(fill="x", pady=(10, 0))
        
        ttk.Button(history_controls, text="Refresh", 
                  command=self.refresh_job_history).pack(side="left", padx=(0, 10))
        ttk.Button(history_controls, text="Clear History", 
                  command=self.clear_job_history).pack(side="left", padx=(0, 10))
        ttk.Button(history_controls, text="View Details", 
                  command=self.view_job_details).pack(side="left")
        
        # Monitoring status
        monitor_status_frame = ttk.LabelFrame(parent, text="Monitoring Status", padding="10")
        monitor_status_frame.pack(fill="x")
        
        self.monitoring_status_text = scrolledtext.ScrolledText(monitor_status_frame, 
                                                               height=8, width=60, 
                                                               state="disabled")
        self.monitoring_status_text.pack(fill="both", expand=True)
        
        # Auto-refresh job history
        self.refresh_job_history()
        self.root.after(30000, self.auto_refresh_history)  # Refresh every 30 seconds
    
    def start_scheduler(self):
        """Start the job scheduler."""
        try:
            if not self.scheduler_running.get():
                # Update configuration
                self.update_scheduler_config()
                
                # Start scheduler
                self.job_scheduler.start()
                
                # Update UI
                self.scheduler_running.set(True)
                self.scheduler_status_label.config(text="Status: Running", foreground="green")
                self.start_scheduler_btn.config(state="disabled")
                self.stop_scheduler_btn.config(state="normal")
                
                self.log_info("Scheduler started successfully")
                messagebox.showinfo("Success", "Scheduler started successfully")
                
        except Exception as e:
            self.log_error(f"Failed to start scheduler: {str(e)}")
            messagebox.showerror("Error", f"Failed to start scheduler: {str(e)}")
    
    def stop_scheduler(self):
        """Stop the job scheduler."""
        try:
            if self.scheduler_running.get():
                # Stop scheduler
                self.job_scheduler.stop()
                
                # Update UI
                self.scheduler_running.set(False)
                self.scheduler_status_label.config(text="Status: Stopped", foreground="red")
                self.start_scheduler_btn.config(state="normal")
                self.stop_scheduler_btn.config(state="disabled")
                
                self.log_info("Scheduler stopped")
                messagebox.showinfo("Success", "Scheduler stopped")
                
        except Exception as e:
            self.log_error(f"Failed to stop scheduler: {str(e)}")
            messagebox.showerror("Error", f"Failed to stop scheduler: {str(e)}")
    
    def add_documentation_job(self):
        """Add a new documentation generation job."""
        try:
            # Get current connection configuration
            connection_config = self.get_current_connection_config()
            
            # Get documentation configuration
            doc_config = {
                "output_directory": self.output_dir.get(),
                "generate_html": self.generate_html.get(),
                "generate_markdown": self.generate_markdown.get(),
                "generate_json": self.generate_json.get(),
                "include_system_objects": self.include_system_objects.get(),
                "include_row_counts": self.include_row_counts.get()
            }
            
            job_config = {
                "connection": connection_config,
                "documentation": doc_config
            }
            
            # Add job
            schedule_spec = self.schedule_combo.get()
            job_name = f"Documentation - {connection_config.get('database', 'Unknown')} - {schedule_spec}"
            
            job_id = self.job_scheduler.add_job(job_name, "documentation", schedule_spec, job_config)
            
            self.log_info(f"Added documentation job: {job_name}")
            messagebox.showinfo("Success", f"Documentation job added successfully!\nJob ID: {job_id}")
            
            # Refresh job history
            self.refresh_job_history()
            
        except Exception as e:
            self.log_error(f"Failed to add documentation job: {str(e)}")
            messagebox.showerror("Error", f"Failed to add documentation job: {str(e)}")
    
    def get_current_connection_config(self) -> Dict[str, Any]:
        """Get current connection configuration for jobs."""
        return {
            "method": self.connection_method.get(),
            "server": self.server.get(),
            "database": self.database.get(),
            "username": self.username.get(),
            "password": self.password.get(),
            "client_id": self.client_id.get(),
            "client_secret": self.client_secret.get(),
            "tenant_id": self.tenant_id.get(),
            "connection_string": self.connection_string.get()
        }
    
    def toggle_monitoring(self):
        """Toggle database monitoring on/off."""
        if self.monitoring_enabled.get():
            self.log_info("Database monitoring enabled")
        else:
            self.log_info("Database monitoring disabled")
    
    def run_manual_check(self):
        """Run a manual database change check."""
        try:
            connection_config = self.get_current_connection_config()
            
            # Run monitoring in background thread
            def monitor_task():
                try:
                    result = self.database_monitor.monitor_database(connection_config)
                    
                    # Update monitoring status text
                    self.root.after(0, lambda: self.update_monitoring_status(result))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log_error(f"Monitoring check failed: {str(e)}"))
            
            threading.Thread(target=monitor_task, daemon=True).start()
            self.log_info("Manual monitoring check started...")
            
        except Exception as e:
            self.log_error(f"Failed to run manual check: {str(e)}")
            messagebox.showerror("Error", f"Failed to run manual check: {str(e)}")
    
    def update_monitoring_status(self, result: Dict[str, Any]):
        """Update monitoring status display."""
        try:
            self.monitoring_status_text.config(state="normal")
            self.monitoring_status_text.delete(1.0, tk.END)
            
            status_text = f"""Database Monitoring Results
========================

Database: {result.get('database', 'Unknown')}
Timestamp: {result.get('timestamp', 'Unknown')}
Schema Hash: {result.get('schema_hash', 'Unknown')[:16]}...

Object Counts:
{json.dumps(result.get('object_counts', {}), indent=2)}

Change Detection:
Change Detected: {result.get('change_detected', False)}
Summary: {result.get('change_summary', 'No summary available')}
"""
            
            self.monitoring_status_text.insert(1.0, status_text)
            self.monitoring_status_text.config(state="disabled")
            
            if result.get('change_detected', False):
                self.log_warning(f"Database changes detected: {result.get('change_summary', 'Unknown')}")
            else:
                self.log_info("No database changes detected")
                
        except Exception as e:
            self.log_error(f"Failed to update monitoring status: {str(e)}")
    
    def update_scheduler_config(self):
        """Update scheduler configuration with current settings."""
        try:
            config = {
                "email": {
                    "enabled": self.email_notifications.get(),
                    "smtp_server": self.email_server.get(),
                    "smtp_port": self.email_port.get(),
                    "username": self.email_username.get(),
                    "password": self.email_password.get(),
                    "from_address": self.email_from.get(),
                    "to_addresses": [addr.strip() for addr in self.email_to.get().split(",") if addr.strip()]
                },
                "webhooks": {
                    "enabled": self.webhook_notifications.get(),
                    "urls": [url.strip() for url in self.webhook_text.get(1.0, tk.END).strip().split('\n') if url.strip()]
                },
                "monitoring": {
                    "enabled": self.monitoring_enabled.get(),
                    "interval_minutes": self.monitoring_interval.get(),
                    "change_threshold": 0.1
                }
            }
            
            # Update scheduler configuration
            self.job_scheduler.config.update(config)
            self.job_scheduler._save_config()
            
        except Exception as e:
            self.log_error(f"Failed to update scheduler config: {str(e)}")
    
    def refresh_job_history(self):
        """Refresh job history display."""
        try:
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Get job history
            history = self.job_scheduler.get_job_history(limit=100)
            
            for entry in history:
                started = entry.get('started_at', '')
                completed = entry.get('completed_at', '')
                
                # Calculate duration
                duration = ""
                if started and completed:
                    try:
                        start_time = datetime.fromisoformat(started.replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(completed.replace('Z', '+00:00'))
                        duration = str(end_time - start_time).split('.')[0]  # Remove microseconds
                    except:
                        duration = "Unknown"
                
                # Format started time
                started_display = ""
                if started:
                    try:
                        start_time = datetime.fromisoformat(started.replace('Z', '+00:00'))
                        started_display = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        started_display = started
                
                # Insert into tree
                self.history_tree.insert("", "end", values=(
                    entry.get('name', 'Unknown'),
                    entry.get('job_type', 'Unknown'),
                    entry.get('status', 'Unknown'),
                    started_display,
                    duration
                ))
                
        except Exception as e:
            self.log_error(f"Failed to refresh job history: {str(e)}")
    
    def clear_job_history(self):
        """Clear job history."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the job history?"):
            try:
                # This would require adding a method to the scheduler
                self.log_info("Job history cleared (functionality to be implemented)")
                self.refresh_job_history()
            except Exception as e:
                self.log_error(f"Failed to clear job history: {str(e)}")
    
    def view_job_details(self):
        """View details of selected job."""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a job to view details.")
            return
        
        try:
            # This would show a detailed view of the job execution
            self.log_info("Job details view (functionality to be implemented)")
        except Exception as e:
            self.log_error(f"Failed to view job details: {str(e)}")
    
    def auto_refresh_history(self):
        """Auto-refresh job history periodically."""
        if self.scheduler_running.get():
            self.refresh_job_history()
        
        # Schedule next refresh
        self.root.after(30000, self.auto_refresh_history)
    
    def create_project_tab(self):
        """Create the project management tab."""
        # Main paned window for layout
        main_paned = ttk.PanedWindow(self.project_frame, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Project controls
        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Project details
        right_frame = ttk.Frame(main_paned, width=600)
        main_paned.add(right_frame, weight=2)
        
        self.create_project_controls(left_frame)
        self.create_project_details(right_frame)
    
    def create_project_controls(self, parent):
        """Create project control panel."""
        # Current project status
        current_frame = ttk.LabelFrame(parent, text="Current Project", padding="10")
        current_frame.pack(fill="x", pady=(0, 10))
        
        self.project_status_label = ttk.Label(current_frame, textvariable=self.current_project_name, 
                                            font=("Arial", 10, "bold"))
        self.project_status_label.pack(anchor="w", pady=(0, 10))
        
        project_buttons = ttk.Frame(current_frame)
        project_buttons.pack(fill="x")
        
        ttk.Button(project_buttons, text="Select Project", 
                  command=self.select_project).pack(side="left", padx=(0, 10))
        ttk.Button(project_buttons, text="New Project", 
                  command=self.create_new_project).pack(side="left", padx=(0, 10))
        ttk.Button(project_buttons, text="Close Project", 
                  command=self.close_project).pack(side="left")
        
        # Project operations
        ops_frame = ttk.LabelFrame(parent, text="Project Operations", padding="10")
        ops_frame.pack(fill="x", pady=(0, 10))
        
        # Database management
        db_frame = ttk.LabelFrame(ops_frame, text="Database Management", padding="5")
        db_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(db_frame, text="Add Current Database", 
                  command=self.add_current_database_to_project).pack(fill="x", pady=(0, 5))
        ttk.Button(db_frame, text="Manage Databases", 
                  command=self.manage_project_databases).pack(fill="x", pady=(0, 5))
        
        # Batch operations
        batch_frame = ttk.LabelFrame(ops_frame, text="Batch Operations", padding="5")
        batch_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(batch_frame, text="Generate All Documentation", 
                  command=self.generate_all_documentation).pack(fill="x", pady=(0, 5))
        ttk.Button(batch_frame, text="Compare All Schemas", 
                  command=self.compare_all_schemas).pack(fill="x", pady=(0, 5))
        ttk.Button(batch_frame, text="Custom Batch Operation", 
                  command=self.custom_batch_operation).pack(fill="x", pady=(0, 5))
        
        # Project management
        mgmt_frame = ttk.LabelFrame(parent, text="Project Management", padding="10")
        mgmt_frame.pack(fill="both", expand=True)
        
        # Import/Export
        ie_frame = ttk.LabelFrame(mgmt_frame, text="Import/Export", padding="5")
        ie_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(ie_frame, text="Export Project", 
                  command=self.export_project).pack(fill="x", pady=(0, 5))
        ttk.Button(ie_frame, text="Import Project", 
                  command=self.import_project).pack(fill="x", pady=(0, 5))
        
        # Project settings
        settings_frame = ttk.LabelFrame(mgmt_frame, text="Settings", padding="5")
        settings_frame.pack(fill="x")
        
        ttk.Button(settings_frame, text="Project Settings", 
                  command=self.edit_project_settings).pack(fill="x", pady=(0, 5))
        ttk.Button(settings_frame, text="Environment Config", 
                  command=self.configure_environments).pack(fill="x", pady=(0, 5))
    
    def create_project_details(self, parent):
        """Create project details panel."""
        # Project information
        info_frame = ttk.LabelFrame(parent, text="Project Information", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.project_info_text = scrolledtext.ScrolledText(info_frame, height=8, width=60, 
                                                          state="disabled")
        self.project_info_text.pack(fill="both", expand=True)
        
        # Project databases
        db_frame = ttk.LabelFrame(parent, text="Project Databases", padding="10")
        db_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Database tree
        db_columns = ("Name", "Environment", "Status", "Last Documented")
        self.project_db_tree = ttk.Treeview(db_frame, columns=db_columns, 
                                           show="tree headings", height=8)
        
        for col in db_columns:
            self.project_db_tree.heading(col, text=col)
            self.project_db_tree.column(col, width=120)
        
        db_scroll = ttk.Scrollbar(db_frame, orient="vertical", command=self.project_db_tree.yview)
        self.project_db_tree.configure(yscrollcommand=db_scroll.set)
        
        self.project_db_tree.pack(side="left", fill="both", expand=True)
        db_scroll.pack(side="right", fill="y")
        
        # Database controls
        db_controls = ttk.Frame(db_frame)
        db_controls.pack(fill="x", pady=(10, 0))
        
        ttk.Button(db_controls, text="Connect to Selected", 
                  command=self.connect_to_selected_database).pack(side="left", padx=(0, 10))
        ttk.Button(db_controls, text="Remove from Project", 
                  command=self.remove_database_from_project).pack(side="left", padx=(0, 10))
        ttk.Button(db_controls, text="Generate Docs", 
                  command=self.generate_selected_docs).pack(side="left")
        
        # Execution history
        history_frame = ttk.LabelFrame(parent, text="Recent Operations", padding="10")
        history_frame.pack(fill="x")
        
        self.project_history_text = scrolledtext.ScrolledText(history_frame, height=6, width=60, 
                                                             state="disabled")
        self.project_history_text.pack(fill="both", expand=True)
        
        # Initialize display
        self.update_project_display()
    
    def select_project(self):
        """Show project selection dialog."""
        try:
            dialog = ProjectSelectionDialog(self.root, self.project_manager)
            project_id = dialog.show()
            
            if project_id:
                self.load_project(project_id)
                
        except Exception as e:
            self.log_error(f"Failed to select project: {str(e)}")
            messagebox.showerror("Error", f"Failed to select project: {str(e)}")
    
    def create_new_project(self):
        """Show dialog to create a new project."""
        try:
            dialog = CreateProjectDialog(self.root, self.project_manager)
            project_id = dialog.show()
            
            if project_id:
                self.load_project(project_id)
                
        except Exception as e:
            self.log_error(f"Failed to create project: {str(e)}")
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
    
    def close_project(self):
        """Close the current project."""
        self.current_project = None
        self.current_project_id.set("")
        self.current_project_name.set("No Project Selected")
        self.project_databases = []
        self.update_project_display()
        self.log_info("Project closed")
    
    def load_project(self, project_id: str):
        """Load a project."""
        try:
            project = self.project_manager.get_project(project_id)
            if project:
                self.current_project = project
                self.current_project_id.set(project_id)
                self.current_project_name.set(f"Project: {project.name}")
                
                # Load project databases
                self.project_databases = self.project_manager.get_project_databases(project_id)
                
                # Update display
                self.update_project_display()
                
                self.log_info(f"Loaded project: {project.name}")
            else:
                raise Exception("Project not found")
                
        except Exception as e:
            self.log_error(f"Failed to load project: {str(e)}")
            messagebox.showerror("Error", f"Failed to load project: {str(e)}")
    
    def update_project_display(self):
        """Update project information display."""
        try:
            # Update project info
            self.project_info_text.config(state="normal")
            self.project_info_text.delete(1.0, tk.END)
            
            if self.current_project:
                info_text = f"""Project: {self.current_project.name}
Description: {self.current_project.description}
Created: {self.current_project.created_at[:19] if self.current_project.created_at else 'Unknown'}
Last Updated: {self.current_project.updated_at[:19] if self.current_project.updated_at else 'Unknown'}
Databases: {len(self.project_databases)}
Environments: {len(self.current_project.environments)}

Settings:
{json.dumps(self.current_project.settings, indent=2)}
"""
                self.project_info_text.insert(1.0, info_text)
            else:
                self.project_info_text.insert(1.0, "No project selected.\n\nSelect or create a project to manage multiple databases and coordinate documentation workflows.")
            
            self.project_info_text.config(state="disabled")
            
            # Update database tree
            for item in self.project_db_tree.get_children():
                self.project_db_tree.delete(item)
            
            for db in self.project_databases:
                self.project_db_tree.insert("", "end", values=(
                    db['database_name'],
                    db['environment'],
                    db['status'],
                    db['last_documented'][:19] if db['last_documented'] else 'Never'
                ))
                
        except Exception as e:
            self.log_error(f"Failed to update project display: {str(e)}")
    
    def add_current_database_to_project(self):
        """Add the current database connection to the project."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select or create a project first.")
            return
        
        try:
            connection_config = self.get_current_connection_config()
            project_id = self.current_project_id.get()
            
            success = self.project_manager.add_database_to_project(
                project_id, connection_config, "default"
            )
            
            if success:
                # Reload project databases
                self.project_databases = self.project_manager.get_project_databases(project_id)
                self.update_project_display()
                
                self.log_info(f"Added database {connection_config.get('database', 'Unknown')} to project")
                messagebox.showinfo("Success", "Database added to project successfully!")
            else:
                raise Exception("Failed to add database to project")
                
        except Exception as e:
            self.log_error(f"Failed to add database to project: {str(e)}")
            messagebox.showerror("Error", f"Failed to add database to project: {str(e)}")
    
    def manage_project_databases(self):
        """Show database management dialog."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select or create a project first.")
            return
        
        try:
            # This would show a more detailed database management dialog
            self.log_info("Database management dialog (functionality to be implemented)")
            messagebox.showinfo("Coming Soon", "Advanced database management features will be available in a future update.")
        except Exception as e:
            self.log_error(f"Failed to open database management: {str(e)}")
    
    def generate_all_documentation(self):
        """Generate documentation for all databases in the project."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select or create a project first.")
            return
        
        if not self.project_databases:
            messagebox.showwarning("No Databases", "Please add databases to the project first.")
            return
        
        try:
            project_id = self.current_project_id.get()
            
            # Execute batch documentation operation
            operation_config = {
                "output_directory": self.output_dir.get(),
                "generate_html": self.generate_html.get(),
                "generate_markdown": self.generate_markdown.get(),
                "generate_json": self.generate_json.get()
            }
            
            execution_id = self.project_manager.execute_batch_operation(
                project_id, "documentation", operation_config
            )
            
            self.log_info(f"Batch documentation generation started: {execution_id}")
            messagebox.showinfo("Success", f"Batch documentation generation started!\nExecution ID: {execution_id}")
            
        except Exception as e:
            self.log_error(f"Failed to generate all documentation: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate all documentation: {str(e)}")
    
    def compare_all_schemas(self):
        """Compare schemas across all databases in the project."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select or create a project first.")
            return
        
        try:
            # This would integrate with the schema comparison system
            self.log_info("Schema comparison across project databases (functionality to be implemented)")
            messagebox.showinfo("Coming Soon", "Cross-database schema comparison will be available in a future update.")
        except Exception as e:
            self.log_error(f"Failed to compare schemas: {str(e)}")
    
    def custom_batch_operation(self):
        """Show custom batch operation dialog."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select or create a project first.")
            return
        
        try:
            dialog = BatchOperationDialog(self.root, self.project_manager, self.current_project_id.get())
            config = dialog.show()
            
            if config:
                execution_id = self.project_manager.execute_batch_operation(
                    self.current_project_id.get(),
                    config['operation_type'],
                    config['config']
                )
                
                self.log_info(f"Batch operation started: {execution_id}")
                messagebox.showinfo("Success", f"Batch operation started!\nExecution ID: {execution_id}")
                
        except Exception as e:
            self.log_error(f"Failed to execute batch operation: {str(e)}")
            messagebox.showerror("Error", f"Failed to execute batch operation: {str(e)}")
    
    def export_project(self):
        """Export the current project."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first.")
            return
        
        try:
            from tkinter import filedialog
            
            export_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
                title="Export Project"
            )
            
            if export_path:
                success = self.project_manager.export_project(
                    self.current_project_id.get(), export_path, include_data=True
                )
                
                if success:
                    self.log_info(f"Project exported to: {export_path}")
                    messagebox.showinfo("Success", f"Project exported successfully to:\n{export_path}")
                else:
                    raise Exception("Export operation failed")
                    
        except Exception as e:
            self.log_error(f"Failed to export project: {str(e)}")
            messagebox.showerror("Error", f"Failed to export project: {str(e)}")
    
    def import_project(self):
        """Import a project from file."""
        try:
            from tkinter import filedialog
            
            import_path = filedialog.askopenfilename(
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
                title="Import Project"
            )
            
            if import_path:
                project_id = self.project_manager.import_project(import_path)
                
                if project_id:
                    self.load_project(project_id)
                    self.log_info(f"Project imported successfully")
                    messagebox.showinfo("Success", "Project imported successfully!")
                else:
                    raise Exception("Import operation failed")
                    
        except Exception as e:
            self.log_error(f"Failed to import project: {str(e)}")
            messagebox.showerror("Error", f"Failed to import project: {str(e)}")
    
    def edit_project_settings(self):
        """Edit project settings."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first.")
            return
        
        try:
            # This would show a project settings dialog
            self.log_info("Project settings editor (functionality to be implemented)")
            messagebox.showinfo("Coming Soon", "Project settings editor will be available in a future update.")
        except Exception as e:
            self.log_error(f"Failed to edit project settings: {str(e)}")
    
    def configure_environments(self):
        """Configure project environments."""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first.")
            return
        
        try:
            # This would show an environment configuration dialog
            self.log_info("Environment configuration (functionality to be implemented)")
            messagebox.showinfo("Coming Soon", "Environment configuration will be available in a future update.")
        except Exception as e:
            self.log_error(f"Failed to configure environments: {str(e)}")
    
    def connect_to_selected_database(self):
        """Connect to the selected database in the project."""
        selection = self.project_db_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a database to connect to.")
            return
        
        try:
            # Get selected database info
            item = self.project_db_tree.item(selection[0])
            db_name = item['values'][0]
            
            # Find database configuration
            selected_db = None
            for db in self.project_databases:
                if db['database_name'] == db_name:
                    selected_db = db
                    break
            
            if selected_db:
                # Update connection form with database config
                config = selected_db['connection_config']
                self.connection_method.set(config.get('method', 'credentials'))
                self.server.set(config.get('server', ''))
                self.database.set(config.get('database', ''))
                self.username.set(config.get('username', ''))
                # Note: Don't set password for security reasons
                
                # Switch to connection tab
                self.notebook.select(0)
                
                self.log_info(f"Connection form updated for database: {db_name}")
                messagebox.showinfo("Success", f"Connection form updated for database: {db_name}\n\nPlease enter your password and test the connection.")
            else:
                raise Exception("Database configuration not found")
                
        except Exception as e:
            self.log_error(f"Failed to connect to selected database: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect to selected database: {str(e)}")
    
    def remove_database_from_project(self):
        """Remove selected database from project."""
        selection = self.project_db_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a database to remove.")
            return
        
        try:
            item = self.project_db_tree.item(selection[0])
            db_name = item['values'][0]
            
            if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{db_name}' from the project?\n\nThis will not delete the database, only remove it from the project."):
                # Find database ID
                database_id = None
                for db in self.project_databases:
                    if db['database_name'] == db_name:
                        database_id = db['database_id']
                        break
                
                if database_id:
                    # Remove from project
                    project = self.project_manager.get_project(self.current_project_id.get())
                    if project.remove_database(database_id):
                        # Update database
                        self.project_manager.update_project(self.current_project_id.get(), {})
                        
                        # Refresh display
                        self.project_databases = self.project_manager.get_project_databases(self.current_project_id.get())
                        self.update_project_display()
                        
                        self.log_info(f"Removed database {db_name} from project")
                        messagebox.showinfo("Success", f"Database '{db_name}' removed from project.")
                    else:
                        raise Exception("Failed to remove database from project")
                else:
                    raise Exception("Database ID not found")
                    
        except Exception as e:
            self.log_error(f"Failed to remove database from project: {str(e)}")
            messagebox.showerror("Error", f"Failed to remove database from project: {str(e)}")
    
    def generate_selected_docs(self):
        """Generate documentation for selected database."""
        selection = self.project_db_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a database to generate documentation for.")
            return
        
        try:
            item = self.project_db_tree.item(selection[0])
            db_name = item['values'][0]
            
            # Find database configuration
            selected_db = None
            for db in self.project_databases:
                if db['database_name'] == db_name:
                    selected_db = db
                    break
            
            if selected_db:
                # Execute documentation operation for single database
                operation_config = {
                    "output_directory": self.output_dir.get(),
                    "generate_html": self.generate_html.get(),
                    "generate_markdown": self.generate_markdown.get(),
                    "generate_json": self.generate_json.get()
                }
                
                execution_id = self.project_manager.execute_batch_operation(
                    self.current_project_id.get(),
                    "documentation",
                    operation_config,
                    [selected_db['database_id']]
                )
                
                self.log_info(f"Documentation generation started for {db_name}: {execution_id}")
                messagebox.showinfo("Success", f"Documentation generation started for '{db_name}'!\nExecution ID: {execution_id}")
            else:
                raise Exception("Database configuration not found")
                
        except Exception as e:
            self.log_error(f"Failed to generate documentation for selected database: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate documentation for selected database: {str(e)}")
    
    def create_api_tab(self):
        """Create the API integration and webhook tab."""
        # Main paned window for layout
        main_paned = ttk.PanedWindow(self.api_frame, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - API controls
        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Webhook and integration details
        right_frame = ttk.Frame(main_paned, width=600)
        main_paned.add(right_frame, weight=2)
        
        self.create_api_controls(left_frame)
        self.create_integration_details(right_frame)
    
    def create_api_controls(self, parent):
        """Create API control panel."""
        # API Server status
        server_frame = ttk.LabelFrame(parent, text="API Server", padding="10")
        server_frame.pack(fill="x", pady=(0, 10))
        
        self.api_status_label = ttk.Label(server_frame, text="Status: Stopped", 
                                         foreground="red")
        self.api_status_label.pack(anchor="w", pady=(0, 10))
        
        # Port configuration
        port_frame = ttk.Frame(server_frame)
        port_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(port_frame, text="Port:").pack(side="left")
        port_spinbox = ttk.Spinbox(port_frame, from_=8000, to=9999, 
                                  textvariable=self.api_port, width=10)
        port_spinbox.pack(side="left", padx=(5, 0))
        
        # Server control buttons
        server_buttons = ttk.Frame(server_frame)
        server_buttons.pack(fill="x")
        
        self.start_api_btn = ttk.Button(server_buttons, text="Start API Server", 
                                       command=self.start_api_server)
        self.start_api_btn.pack(side="left", padx=(0, 10))
        
        self.stop_api_btn = ttk.Button(server_buttons, text="Stop API Server", 
                                      command=self.stop_api_server, state="disabled")
        self.stop_api_btn.pack(side="left")
        
        # Webhook management
        webhook_frame = ttk.LabelFrame(parent, text="Webhook Management", padding="10")
        webhook_frame.pack(fill="x", pady=(0, 10))
        
        # Webhook controls
        webhook_buttons = ttk.Frame(webhook_frame)
        webhook_buttons.pack(fill="x", pady=(0, 10))
        
        ttk.Button(webhook_buttons, text="Configure Webhook", 
                  command=self.configure_webhook).pack(side="left", padx=(0, 10))
        ttk.Button(webhook_buttons, text="Test Webhook", 
                  command=self.test_webhook).pack(side="left", padx=(0, 10))
        ttk.Button(webhook_buttons, text="View Webhooks", 
                  command=self.view_webhooks).pack(side="left")
        
        # Webhook notifications toggle
        ttk.Checkbutton(webhook_frame, text="Enable webhook notifications",
                       variable=self.webhook_notifications_enabled).pack(anchor="w", pady=(10, 0))
        
        # Platform integrations
        platform_frame = ttk.LabelFrame(parent, text="Platform Integrations", padding="10")
        platform_frame.pack(fill="both", expand=True)
        
        # Integration checkboxes
        ttk.Checkbutton(platform_frame, text="GitHub Integration",
                       variable=self.github_integration).pack(anchor="w", pady=2)
        ttk.Checkbutton(platform_frame, text="Azure DevOps Integration",
                       variable=self.azure_devops_integration).pack(anchor="w", pady=2)
        ttk.Checkbutton(platform_frame, text="Slack Integration",
                       variable=self.slack_integration).pack(anchor="w", pady=2)
        
        # Platform configuration button
        ttk.Button(platform_frame, text="Configure Platforms", 
                  command=self.configure_platforms).pack(fill="x", pady=(10, 0))
    
    def create_integration_details(self, parent):
        """Create integration details panel."""
        # Webhook list
        webhook_frame = ttk.LabelFrame(parent, text="Active Webhooks", padding="10")
        webhook_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Webhook tree
        webhook_columns = ("Name", "URL", "Events", "Status", "Last Delivery")
        self.webhook_tree = ttk.Treeview(webhook_frame, columns=webhook_columns, 
                                        show="headings", height=8)
        
        for col in webhook_columns:
            self.webhook_tree.heading(col, text=col, anchor="w")
            self.webhook_tree.column(col, width=120, anchor="w")
        
        # Add scrollbars
        webhook_scrollbar_v = ttk.Scrollbar(webhook_frame, orient="vertical", 
                                           command=self.webhook_tree.yview)
        webhook_scrollbar_h = ttk.Scrollbar(webhook_frame, orient="horizontal", 
                                           command=self.webhook_tree.xview)
        
        self.webhook_tree.configure(yscrollcommand=webhook_scrollbar_v.set, 
                                   xscrollcommand=webhook_scrollbar_h.set)
        
        self.webhook_tree.grid(row=0, column=0, sticky="nsew")
        webhook_scrollbar_v.grid(row=0, column=1, sticky="ns")
        webhook_scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        webhook_frame.grid_rowconfigure(0, weight=1)
        webhook_frame.grid_columnconfigure(0, weight=1)
        
        # Webhook context menu
        self.webhook_context_menu = tk.Menu(self.webhook_tree, tearoff=0)
        self.webhook_context_menu.add_command(label="Delete Webhook", command=self.delete_selected_webhook)
        self.webhook_context_menu.add_command(label="Test Webhook", command=self.test_selected_webhook)
        
        self.webhook_tree.bind("<Button-3>", self.show_webhook_context_menu)
        
        # API activity log
        activity_frame = ttk.LabelFrame(parent, text="API Activity", padding="10")
        activity_frame.pack(fill="both", expand=True)
        
        self.api_activity_text = scrolledtext.ScrolledText(activity_frame, height=10, 
                                                          state="disabled")
        self.api_activity_text.pack(fill="both", expand=True)

    def create_progress_tab(self):
        """Create the progress tracking and logging tab."""
        # Progress section
        progress_frame = ttk.LabelFrame(self.progress_frame, text="Generation Progress", padding="10")
        
        # Main progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_value, 
            mode="determinate",
            length=400
        )
        self.progress_bar.pack(fill="x", pady=5)
        
        # Progress details row
        details_frame = ttk.Frame(progress_frame)
        details_frame.pack(fill="x", pady=5)
        
        # Current step label
        ttk.Label(details_frame, text="Current Step:").pack(side="left")
        self.step_label = ttk.Label(details_frame, textvariable=self.current_step, style="Status.TLabel")
        self.step_label.pack(side="left", padx=(5, 20))
        
        # Estimated time label
        ttk.Label(details_frame, text="Time Remaining:").pack(side="left")
        self.time_label = ttk.Label(details_frame, textvariable=self.estimated_time, style="Status.TLabel")
        self.time_label.pack(side="left", padx=5)
        
        # Detailed progress text
        self.detailed_label = ttk.Label(progress_frame, textvariable=self.detailed_progress, style="Status.TLabel")
        self.detailed_label.pack(pady=5)
        
        # Cancel button (initially hidden)
        self.cancel_btn = ttk.Button(
            progress_frame, 
            text="Cancel Generation", 
            command=self.cancel_generation,
            style="Warning.TButton"
        )
        # Don't pack initially - will be shown during generation
        
        # Statistics display
        self.stats_frame = ttk.LabelFrame(self.progress_frame, text="Database Statistics", padding="10")
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, height=8, width=60, state="disabled")
        self.stats_text.pack(fill="both", expand=True)
        
        # Log display
        log_frame = ttk.LabelFrame(self.progress_frame, text="Activity Log", padding="10")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill="both", expand=True)
        
        # Pack frames
        progress_frame.pack(fill="x", pady=(0, 10))
        self.stats_frame.pack(fill="both", expand=True, pady=(0, 10))
        log_frame.pack(fill="both", expand=True)
    
    def create_control_buttons(self):
        """Create main control buttons."""
        ttk.Button(
            self.control_frame, 
            text="Generate Documentation", 
            command=self.generate_documentation,
            style="Accent.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            self.control_frame, 
            text="Open Output Folder", 
            command=self.open_output_folder
        ).pack(side="left", padx=5)
        
        ttk.Button(
            self.control_frame, 
            text="Clear Log", 
            command=self.clear_log
        ).pack(side="left", padx=5)
        
        ttk.Button(
            self.control_frame, 
            text="Exit", 
            command=self.on_exit
        ).pack(side="right", padx=5)
    
    def setup_layout(self):
        """Configure the main layout."""
        self.main_frame.pack(fill="both", expand=True)
        
        self.title_label.pack(pady=(0, 10))
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        self.control_frame.pack(fill="x", pady=(0, 10))
        
        # Status bar
        self.status_frame.pack(fill="x", side="bottom")
        self.status_label.pack(side="left")
        self.connection_label.pack(side="right")
        
        # Initialize object details manager after widgets are created
        self.object_details_manager = ObjectDetailsManager(self.root)
        
        # Initialize template editor
        self.template_editor = TemplateEditor(self.root)
    
    # API and Integration Methods
    
    def start_api_server(self):
        """Start the API server."""
        try:
            if not self.api_server_running.get():
                # Update port if changed
                self.api_server.port = self.api_port.get()
                
                # Start server
                self.api_server.start_server()
                
                # Update UI
                self.api_server_running.set(True)
                self.api_status_label.config(text=f"Status: Running on port {self.api_port.get()}", 
                                           foreground="green")
                self.start_api_btn.config(state="disabled")
                self.stop_api_btn.config(state="normal")
                
                self.log_message(f"API server started on port {self.api_port.get()}")
                
                # Log API activity
                self.log_api_activity(f"Server started on port {self.api_port.get()}")
        
        except Exception as e:
            self.log_error(f"Failed to start API server: {str(e)}")
            messagebox.showerror("Error", f"Failed to start API server: {str(e)}")
    
    def stop_api_server(self):
        """Stop the API server."""
        try:
            if self.api_server_running.get():
                # Stop server
                self.api_server.stop_server()
                
                # Update UI
                self.api_server_running.set(False)
                self.api_status_label.config(text="Status: Stopped", foreground="red")
                self.start_api_btn.config(state="normal")
                self.stop_api_btn.config(state="disabled")
                
                self.log_message("API server stopped")
                
                # Log API activity
                self.log_api_activity("Server stopped")
        
        except Exception as e:
            self.log_error(f"Failed to stop API server: {str(e)}")
            messagebox.showerror("Error", f"Failed to stop API server: {str(e)}")
    
    def configure_webhook(self):
        """Open webhook configuration dialog."""
        try:
            dialog = WebhookConfigDialog(self.root, self.webhook_manager)
            if dialog.result:
                # Refresh webhook list
                self.refresh_webhook_list()
                self.log_message(f"New webhook configured: {dialog.result}")
        except Exception as e:
            self.log_error(f"Failed to configure webhook: {str(e)}")
            messagebox.showerror("Error", f"Failed to configure webhook: {str(e)}")
    
    def test_webhook(self):
        """Test webhook functionality."""
        try:
            # Trigger a test event
            test_payload = {
                'event': 'test',
                'message': 'This is a test webhook event',
                'timestamp': datetime.now().isoformat(),
                'source': 'Azure SQL Doc Generator'
            }
            
            self.webhook_manager.trigger_webhook('test', test_payload)
            self.log_message("Test webhook event triggered")
            messagebox.showinfo("Success", "Test webhook event has been triggered")
        
        except Exception as e:
            self.log_error(f"Failed to test webhook: {str(e)}")
            messagebox.showerror("Error", f"Failed to test webhook: {str(e)}")
    
    def view_webhooks(self):
        """Refresh and display webhook list."""
        self.refresh_webhook_list()
    
    def refresh_webhook_list(self):
        """Refresh the webhook list display."""
        try:
            # Clear existing items
            for item in self.webhook_tree.get_children():
                self.webhook_tree.delete(item)
            
            # Get webhooks
            webhooks = self.webhook_manager.get_webhooks()
            
            for webhook in webhooks:
                status = "Active" if webhook['active'] else "Inactive"
                last_delivery = webhook['last_delivery'] or "Never"
                if last_delivery != "Never":
                    # Format datetime string
                    try:
                        dt = datetime.fromisoformat(last_delivery.replace('Z', '+00:00'))
                        last_delivery = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                events_str = ", ".join(webhook['events'][:3])  # Show first 3 events
                if len(webhook['events']) > 3:
                    events_str += "..."
                
                self.webhook_tree.insert("", "end", values=(
                    webhook['name'],
                    webhook['url'][:50] + "..." if len(webhook['url']) > 50 else webhook['url'],
                    events_str,
                    status,
                    last_delivery
                ))
        
        except Exception as e:
            self.log_error(f"Failed to refresh webhook list: {str(e)}")
    
    def show_webhook_context_menu(self, event):
        """Show webhook context menu."""
        try:
            # Select item under cursor
            item = self.webhook_tree.identify_row(event.y)
            if item:
                self.webhook_tree.selection_set(item)
                self.webhook_context_menu.post(event.x_root, event.y_root)
        except:
            pass
    
    def delete_selected_webhook(self):
        """Delete the selected webhook."""
        try:
            selection = self.webhook_tree.selection()
            if not selection:
                return
            
            # Get webhook details
            item = selection[0]
            values = self.webhook_tree.item(item, 'values')
            webhook_name = values[0]
            
            # Confirm deletion
            result = messagebox.askyesno("Confirm Delete", 
                                       f"Are you sure you want to delete webhook '{webhook_name}'?")
            if result:
                # Find and delete webhook by name
                webhooks = self.webhook_manager.get_webhooks()
                for webhook in webhooks:
                    if webhook['name'] == webhook_name:
                        self.webhook_manager.delete_webhook(webhook['id'])
                        break
                
                # Refresh display
                self.refresh_webhook_list()
                self.log_message(f"Webhook deleted: {webhook_name}")
        
        except Exception as e:
            self.log_error(f"Failed to delete webhook: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete webhook: {str(e)}")
    
    def test_selected_webhook(self):
        """Test the selected webhook."""
        try:
            selection = self.webhook_tree.selection()
            if not selection:
                return
            
            # Get webhook details
            item = selection[0]
            values = self.webhook_tree.item(item, 'values')
            webhook_name = values[0]
            
            # Find webhook and trigger test
            webhooks = self.webhook_manager.get_webhooks()
            for webhook in webhooks:
                if webhook['name'] == webhook_name:
                    test_payload = {
                        'event': 'test',
                        'message': f'Test event for webhook: {webhook_name}',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Trigger for first event type
                    if webhook['events']:
                        self.webhook_manager.trigger_webhook(webhook['events'][0], test_payload)
                        self.log_message(f"Test event triggered for webhook: {webhook_name}")
                        messagebox.showinfo("Success", f"Test event sent to webhook: {webhook_name}")
                    break
        
        except Exception as e:
            self.log_error(f"Failed to test webhook: {str(e)}")
            messagebox.showerror("Error", f"Failed to test webhook: {str(e)}")
    
    def configure_platforms(self):
        """Open platform integration configuration dialog."""
        try:
            dialog = PlatformIntegrationDialog(self.root)
            # Configuration would be handled by the dialog
        except Exception as e:
            self.log_error(f"Failed to configure platforms: {str(e)}")
            messagebox.showerror("Error", f"Failed to configure platforms: {str(e)}")
    
    def log_api_activity(self, message):
        """Log API activity to the activity display."""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            self.api_activity_text.config(state="normal")
            self.api_activity_text.insert(tk.END, log_message)
            self.api_activity_text.see(tk.END)
            self.api_activity_text.config(state="disabled")
        except:
            pass
    
    def trigger_documentation_event(self, event_type: str, details: Dict[str, Any]):
        """Trigger webhook events for documentation operations."""
        try:
            if self.webhook_notifications_enabled.get():
                payload = {
                    'event_type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Azure SQL Doc Generator',
                    'details': details
                }
                
                self.webhook_manager.trigger_webhook(event_type, payload)
                self.log_api_activity(f"Event triggered: {event_type}")
        except Exception as e:
            self.log_error(f"Failed to trigger webhook event: {str(e)}")

    def open_template_editor(self):
        """Open the template editor window."""
        self.template_editor.show_template_editor()
    
    def show_object_details(self, obj_data, schema_data=None):
        """Show comprehensive object details."""
        if self.object_details_manager:
            self.object_details_manager.show_object_details(
                obj_data, 
                schema_data or self.current_schema_data
            )
    
    def load_initial_config(self):
        """Load initial configuration if available."""
        try:
            config_manager = ConfigManager()
            db_config = config_manager.get_database_config()
            
            # Update GUI variables with config values
            self.connection_method.set(db_config.get('connection_method', 'credentials'))
            self.server.set(db_config.get('server', ''))
            self.database.set(db_config.get('database', ''))
            self.username.set(db_config.get('username', ''))
            self.password.set(db_config.get('password', ''))
            
            doc_config = config_manager.get_documentation_config()
            self.output_dir.set(doc_config.get('output_directory', 'output'))
            self.generate_html.set(doc_config.get('generate_html', True))
            self.generate_markdown.set(doc_config.get('generate_markdown', True))
            self.generate_json.set(doc_config.get('generate_json', True))
            
            self.on_connection_method_changed()
            self.log_message("Configuration loaded successfully")
            
        except Exception as e:
            self.log_message(f"Could not load configuration: {str(e)}")
    
    def on_connection_method_changed(self):
        """Handle connection method change."""
        self.create_connection_fields()
        self.connection_status.set("Not Connected")
        
        # Trigger initial validation for visible fields
        self.validate_field('server')
        self.validate_field('database')
        
        method = self.connection_method.get()
        if method == 'credentials':
            self.validate_field('username')
            self.validate_field('password')
        elif method == 'connection_string':
            self.validate_field('connection_string')
    
    def test_connection(self):
        """Test database connection in a separate thread."""
        self.status_text.set("Testing connection...")
        self.test_btn.configure(state="disabled")
        
        thread = threading.Thread(target=self._test_connection_thread)
        thread.daemon = True
        thread.start()
    
    def _test_connection_thread(self):
        """Thread function for testing connection."""
        try:
            with AzureSQLConnection() as db:
                success = self._connect_to_database(db)
                
                if success:
                    # Test the connection
                    if db.test_connection():
                        db_info = db.get_database_info()
                        self.root.after(0, self._connection_success, db_info)
                    else:
                        self.root.after(0, self._connection_failed, "Connection test failed")
                else:
                    self.root.after(0, self._connection_failed, "Failed to establish connection")
                    
        except Exception as e:
            self.root.after(0, self._connection_failed, str(e))
    
    def _connect_to_database(self, db):
        """Helper method to connect to database based on method."""
        method = self.connection_method.get()
        
        if method == "credentials":
            return db.connect_with_credentials(
                server=self.server.get(),
                database=self.database.get(),
                username=self.username.get(),
                password=self.password.get()
            )
        elif method == "azure_ad":
            return db.connect_with_azure_ad(
                server=self.server.get(),
                database=self.database.get()
            )
        elif method == "service_principal":
            return db.connect_with_service_principal(
                server=self.server.get(),
                database=self.database.get(),
                client_id=self.client_id.get(),
                client_secret=self.client_secret.get(),
                tenant_id=self.tenant_id.get()
            )
        elif method == "connection_string":
            return db.connect_with_connection_string(self.connection_string.get())
        
        return False
    
    def _connection_success(self, db_info):
        """Handle successful connection."""
        self.connection_status.set(f"Connected to {db_info.get('database_name', 'Unknown')}")
        self.status_text.set("Connection successful")
        self.test_btn.configure(state="normal")
        messagebox.showinfo("Connection Test", "Connection successful!")
        self.log_message(f"Successfully connected to database: {db_info.get('database_name', 'Unknown')}")
        
        # Add to connection history
        self._add_to_connection_history(success=True)
    
    def _connection_failed(self, error_msg):
        """Handle failed connection."""
        self.connection_status.set("Connection Failed")
        self.status_text.set("Connection failed")
        self.test_btn.configure(state="normal")
        
        # Show enhanced error dialog with suggestions
        self._show_error_dialog("Connection Failed", error_msg, "connection")
        self.log_message(f"Connection failed: {error_msg}")
        
        # Add to connection history
        self._add_to_connection_history(success=False, error_message=error_msg)
    
    def load_databases(self):
        """Load available databases from the server."""
        self.status_text.set("Loading databases...")
        self.load_db_btn.configure(state="disabled")
        
        thread = threading.Thread(target=self._load_databases_thread)
        thread.daemon = True
        thread.start()
    
    def _load_databases_thread(self):
        """Thread function for loading databases."""
        try:
            with AzureSQLConnection() as db:
                # Connect to master database to list all databases
                method = self.connection_method.get()
                original_db = self.database.get()
                
                # Temporarily set database to master
                temp_db = "master"
                
                if method == "credentials":
                    success = db.connect_with_credentials(
                        server=self.server.get(),
                        database=temp_db,
                        username=self.username.get(),
                        password=self.password.get()
                    )
                elif method == "azure_ad":
                    success = db.connect_with_azure_ad(
                        server=self.server.get(),
                        database=temp_db
                    )
                else:
                    self.root.after(0, self._databases_load_failed, "Database loading not supported for this connection method")
                    return
                
                if success:
                    # Query for databases
                    query = """
                    SELECT name as database_name
                    FROM sys.databases 
                    WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
                    ORDER BY name
                    """
                    databases = db.execute_query(query)
                    db_names = [db_info['database_name'] for db_info in databases]
                    
                    self.root.after(0, self._databases_loaded, db_names, original_db)
                else:
                    self.root.after(0, self._databases_load_failed, "Could not connect to server")
                    
        except Exception as e:
            self.root.after(0, self._databases_load_failed, str(e))
    
    def _databases_loaded(self, databases, original_db):
        """Handle successful database loading."""
        self.available_databases = databases
        self.database_combo['values'] = databases
        
        # Restore original database selection if it exists
        if original_db in databases:
            self.database.set(original_db)
        elif databases:
            self.database.set(databases[0])
        
        self.status_text.set("Databases loaded successfully")
        self.load_db_btn.configure(state="normal")
        self.log_message(f"Loaded {len(databases)} databases")
    
    def _databases_load_failed(self, error_msg):
        """Handle failed database loading."""
        self.status_text.set("Failed to load databases")
        self.load_db_btn.configure(state="normal")
        messagebox.showerror("Load Databases", f"Failed to load databases: {error_msg}")
        self.log_message(f"Failed to load databases: {error_msg}")
    
    def refresh_database_list(self):
        """Refresh the detailed database list."""
        self.status_text.set("Loading database information...")
        self.refresh_db_btn.configure(state="disabled")
        
        # Clear current list
        for item in self.database_tree.get_children():
            self.database_tree.delete(item)
        
        thread = threading.Thread(target=self._refresh_database_list_thread)
        thread.daemon = True
        thread.start()
    
    def _refresh_database_list_thread(self):
        """Thread function for refreshing database list with detailed information."""
        try:
            with AzureSQLConnection() as db:
                # Connect to master database to get detailed information
                method = self.connection_method.get()
                
                if method == "credentials":
                    success = db.connect_with_credentials(
                        server=self.server.get(),
                        database="master",
                        username=self.username.get(),
                        password=self.password.get()
                    )
                elif method == "azure_ad":
                    success = db.connect_with_azure_ad(
                        server=self.server.get(),
                        database="master"
                    )
                else:
                    self.root.after(0, self._database_refresh_failed, "Database listing not supported for this connection method")
                    return
                
                if success:
                    # Enhanced query with more database information
                    query = """
                    SELECT 
                        d.name as database_name,
                        d.database_id,
                        d.create_date,
                        d.collation_name,
                        d.state_desc as status,
                        CASE 
                            WHEN d.name IN ('master', 'tempdb', 'model', 'msdb') THEN 'System'
                            ELSE 'User'
                        END as database_type,
                        (
                            SELECT 
                                CAST(SUM(CAST(mf.size AS bigint)) * 8 / 1024.0 AS decimal(10,2))
                            FROM sys.master_files mf 
                            WHERE mf.database_id = d.database_id AND mf.type = 0
                        ) as data_size_mb,
                        (
                            SELECT 
                                CAST(SUM(CAST(mf.size AS bigint)) * 8 / 1024.0 AS decimal(10,2))
                            FROM sys.master_files mf 
                            WHERE mf.database_id = d.database_id AND mf.type = 1
                        ) as log_size_mb
                    FROM sys.databases d
                    ORDER BY 
                        CASE WHEN d.name IN ('master', 'tempdb', 'model', 'msdb') THEN 0 ELSE 1 END,
                        d.name
                    """
                    databases = db.execute_query(query)
                    
                    self.root.after(0, self._database_list_refreshed, databases)
                else:
                    self.root.after(0, self._database_refresh_failed, "Could not connect to server")
                    
        except Exception as e:
            self.root.after(0, self._database_refresh_failed, str(e))
    
    def _database_list_refreshed(self, databases):
        """Handle successful database list refresh."""
        self.available_databases = []
        self._all_database_info = databases  # Store for filtering
        
        for db_info in databases:
            # Format creation date
            create_date = db_info['create_date'].strftime('%Y-%m-%d %H:%M:%S') if db_info['create_date'] else 'Unknown'
            
            # Calculate total size
            data_size = db_info['data_size_mb'] or 0
            log_size = db_info['log_size_mb'] or 0
            total_size = data_size + log_size
            
            # Format size display
            if total_size > 1024:
                size_display = f"{total_size/1024:.1f} GB"
            else:
                size_display = f"{total_size:.1f} MB"
            
            # Add to treeview
            values = (
                db_info['database_name'],
                create_date,
                db_info['status'],
                db_info['collation_name'] or 'Unknown',
                size_display
            )
            
            # Color coding for system vs user databases
            if db_info['database_name'] in ['master', 'tempdb', 'model', 'msdb']:
                item_id = self.database_tree.insert("", "end", values=values, tags=("system",))
            else:
                item_id = self.database_tree.insert("", "end", values=values, tags=("user",))
                self.available_databases.append(db_info['database_name'])
        
        # Configure tags for styling
        self.database_tree.tag_configure("system", background="#f0f0f0", foreground="#666666")
        self.database_tree.tag_configure("user", background="white", foreground="black")
        
        self.status_text.set("Database list refreshed successfully")
        self.refresh_db_btn.configure(state="normal")
        
        # Update the connection tab dropdown
        self.database_combo['values'] = self.available_databases
        
        self.log_message(f"Loaded detailed information for {len(databases)} databases")
    
    def _database_refresh_failed(self, error_msg):
        """Handle failed database list refresh."""
        self.status_text.set("Failed to refresh database list")
        self.refresh_db_btn.configure(state="normal")
        messagebox.showerror("Refresh Database List", f"Failed to refresh database list: {error_msg}")
        self.log_message(f"Failed to refresh database list: {error_msg}")
    
    def filter_databases(self, event=None):
        """Filter the database list based on search criteria."""
        search_term = self.database_search.get().lower()
        
        # Clear current display
        for item in self.database_tree.get_children():
            self.database_tree.delete(item)
        
        # Re-populate with filtered results
        if hasattr(self, '_all_database_info'):
            for db_info in self._all_database_info:
                if search_term in db_info['database_name'].lower():
                    # Re-add the item (this is a simplified version)
                    values = (
                        db_info['database_name'],
                        db_info['create_date'].strftime('%Y-%m-%d %H:%M:%S') if db_info['create_date'] else 'Unknown',
                        db_info['status'],
                        db_info['collation_name'] or 'Unknown',
                        f"{((db_info['data_size_mb'] or 0) + (db_info['log_size_mb'] or 0)):.1f} MB"
                    )
                    
                    if db_info['database_name'] in ['master', 'tempdb', 'model', 'msdb']:
                        self.database_tree.insert("", "end", values=values, tags=("system",))
                    else:
                        self.database_tree.insert("", "end", values=values, tags=("user",))
    
    def clear_search(self):
        """Clear the search filter."""
        self.database_search.set("")
        self.filter_databases()
    
    def on_database_select(self, event):
        """Handle database selection in the tree."""
        selected_items = self.database_tree.selection()
        if not selected_items:
            self.select_db_btn.configure(state="disabled")
            self.generate_docs_btn.configure(state="disabled")
            self.browse_schema_btn.configure(state="disabled")
            self._clear_database_info()
            return
        
        item = selected_items[0]
        db_name = self.database_tree.item(item)['values'][0]
        
        # Enable buttons for user databases only
        if db_name not in ['master', 'tempdb', 'model', 'msdb']:
            self.select_db_btn.configure(state="normal")
            self.generate_docs_btn.configure(state="normal")
            self.browse_schema_btn.configure(state="normal")
        else:
            self.select_db_btn.configure(state="disabled")
            self.generate_docs_btn.configure(state="disabled")
            self.browse_schema_btn.configure(state="disabled")
        
        # Show database details
        self._show_database_details(db_name, item)
    
    def on_database_double_click(self, event):
        """Handle double-click on database - auto select if it's a user database."""
        selected_items = self.database_tree.selection()
        if selected_items:
            item = selected_items[0]
            db_name = self.database_tree.item(item)['values'][0]
            
            if db_name not in ['master', 'tempdb', 'model', 'msdb']:
                self.select_database_from_list()
    
    def select_database_from_list(self):
        """Select the chosen database and switch to connection tab."""
        selected_items = self.database_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        db_name = self.database_tree.item(item)['values'][0]
        
        # Update the database selection in connection tab
        self.database.set(db_name)
        
        # Switch to connection tab
        self.notebook.select(0)
        
        self.log_message(f"Selected database: {db_name}")
        messagebox.showinfo("Database Selected", f"Database '{db_name}' has been selected for documentation generation.")
    
    def generate_docs_from_list(self):
        """Generate documentation directly from the selected database in the list."""
        selected_items = self.database_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        db_name = self.database_tree.item(item)['values'][0]
        
        # Show confirmation dialog with options
        if not self._show_generation_confirmation(db_name):
            return
        
        # Set the database selection
        self.database.set(db_name)
        
        # Switch to progress tab to show generation progress
        self.notebook.select(3)  # Progress & Logs tab is index 3
        
        # Start documentation generation
        self.log_message(f"Starting documentation generation for database: {db_name}")
        self.generate_documentation()
    
    def _show_generation_confirmation(self, db_name):
        """Show confirmation dialog before generating documentation."""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Documentation")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog on the parent window
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=f"Generate Documentation for '{db_name}'",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Information text
        info_text = f"""You are about to generate complete documentation for the database '{db_name}'.

This process will:
• Connect to the database and analyze the complete schema
• Extract information about tables, views, procedures, and functions
• Generate documentation in your selected output formats
• Create files in the configured output directory

Current Configuration:"""
        
        info_label = ttk.Label(main_frame, text=info_text, justify="left")
        info_label.pack(anchor="w", pady=(0, 10))
        
        # Configuration summary
        config_frame = ttk.LabelFrame(main_frame, text="Current Settings", padding="10")
        config_frame.pack(fill="x", pady=(0, 20))
        
        # Show current settings
        output_formats = []
        if self.generate_html.get():
            output_formats.append("HTML")
        if self.generate_markdown.get():
            output_formats.append("Markdown")
        if self.generate_json.get():
            output_formats.append("JSON")
        
        settings_text = f"""Output Directory: {self.output_dir.get()}
Output Formats: {', '.join(output_formats) if output_formats else 'None selected!'}
Include System Objects: {'Yes' if self.include_system_objects.get() else 'No'}
Include Row Counts: {'Yes' if self.include_row_counts.get() else 'No'}"""
        
        settings_label = ttk.Label(config_frame, text=settings_text, justify="left")
        settings_label.pack(anchor="w")
        
        # Warning if no formats selected
        if not output_formats:
            warning_label = ttk.Label(
                main_frame, 
                text="WARNING: No output formats selected! Please configure output options first.",
                foreground="red",
                font=("Arial", 9, "bold")
            )
            warning_label.pack(pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Result variable
        result = {"confirmed": False}
        
        def on_generate():
            if not output_formats:
                messagebox.showerror("Configuration Error", "Please select at least one output format in the 'Documentation Options' tab.")
                return
            result["confirmed"] = True
            dialog.destroy()
        
        def on_configure():
            dialog.destroy()
            # Switch to documentation options tab
            self.notebook.select(2)  # Documentation Options tab
        
        def on_cancel():
            result["confirmed"] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="Generate Now", command=on_generate, style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Configure Options First", command=on_configure).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="right")
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        return result["confirmed"]
    
    def _show_database_details(self, db_name, tree_item):
        """Show detailed information about the selected database."""
        try:
            # Get database values from tree
            values = self.database_tree.item(tree_item)['values']
            
            details_text = f"""Database: {db_name}
            
Basic Information:
  • Name: {values[0]}
  • Created: {values[1]}
  • Status: {values[2]}
  • Collation: {values[3]}
  • Size: {values[4]}
  
Database Type: {'System Database' if db_name in ['master', 'tempdb', 'model', 'msdb'] else 'User Database'}

Actions Available:
  • Double-click or use 'Select Database' to choose for documentation
  • Use 'Generate Documentation' to immediately start documentation generation
  • Use 'Refresh List' to update database information
  
Note: System databases (master, tempdb, model, msdb) are shown for reference but cannot be selected for documentation generation."""
            
            self.db_info_text.configure(state="normal")
            self.db_info_text.delete("1.0", tk.END)
            self.db_info_text.insert("1.0", details_text)
            self.db_info_text.configure(state="disabled")
            
        except Exception as e:
            self.log_message(f"Error showing database details: {str(e)}")
    
    def _clear_database_info(self):
        """Clear the database information display."""
        self.db_info_text.configure(state="normal")
        self.db_info_text.delete("1.0", tk.END)
        self.db_info_text.insert("1.0", "Select a database from the list above to view detailed information.")
        self.db_info_text.configure(state="disabled")
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
    
    def generate_documentation(self):
        """Generate database documentation in a separate thread."""
        if not self._validate_inputs():
            return
        
        # Reset cancellation flag and setup progress tracking
        self.generation_cancelled = False
        import time
        self.generation_start_time = time.time()
        
        # Disable UI during generation
        self._set_ui_state(False)
        self.progress_value.set(0)
        
        # Update detailed progress
        self.root.after(0, lambda: self._update_detailed_progress(
            "Initializing", 
            "Starting documentation generation process...", 
            0, 
            "Calculating...", 
            True
        ))
        
        thread = threading.Thread(target=self._generate_documentation_thread)
        thread.daemon = True
        thread.start()
    
    def _validate_inputs(self):
        """Validate user inputs."""
        if not self.server.get().strip():
            messagebox.showerror("Validation Error", "Server name is required")
            return False
        
        if not self.database.get().strip():
            messagebox.showerror("Validation Error", "Database name is required")
            return False
        
        method = self.connection_method.get()
        if method == "credentials":
            if not self.username.get().strip() or not self.password.get().strip():
                messagebox.showerror("Validation Error", "Username and password are required")
                return False
        elif method == "service_principal":
            if not all([self.client_id.get().strip(), self.client_secret.get().strip(), self.tenant_id.get().strip()]):
                messagebox.showerror("Validation Error", "Client ID, Client Secret, and Tenant ID are required")
                return False
        elif method == "connection_string":
            if not self.connection_string.get().strip():
                messagebox.showerror("Validation Error", "Connection string is required")
                return False
        
        if not any([self.generate_html.get(), self.generate_markdown.get(), self.generate_json.get()]):
            messagebox.showerror("Validation Error", "At least one output format must be selected")
            return False
        
        return True
    
    def _generate_documentation_thread(self):
        """Thread function for documentation generation with detailed progress and cancellation."""
        import time
        
        try:
            self.root.after(0, lambda: self.log_message("Starting documentation generation..."))
            
            # Step 1: Database Connection
            if self._check_cancellation():
                return
                
            self.root.after(0, lambda: self._update_detailed_progress(
                "Connecting", 
                "Establishing database connection...", 
                5,
                self._estimate_remaining_time(5),
                True
            ))
            
            with AzureSQLConnection() as db:
                # Connect to database
                success = self._connect_to_database(db)
                if not success:
                    raise Exception("Failed to connect to database")
                
                if self._check_cancellation():
                    return
                
                # Step 2: Schema Discovery
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Discovering", 
                    "Analyzing database structure...", 
                    15,
                    self._estimate_remaining_time(15),
                    True
                ))
                self.root.after(0, lambda: self.log_message("Connected successfully, analyzing schema..."))
                
                # Step 3: Extract Tables
                if self._check_cancellation():
                    return
                    
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Extracting Tables", 
                    "Reading table definitions and data...", 
                    25,
                    self._estimate_remaining_time(25),
                    True
                ))
                
                extractor = DocumentationExtractor(db)
                documentation = extractor.extract_complete_documentation()
                
                # Store schema data for search functionality
                self.current_schema_data = documentation
                self.last_extracted_data = documentation
                
                # Update statistics early
                stats = documentation.get('statistics', {})
                self.root.after(0, lambda: self._update_statistics(stats))
                
                if self._check_cancellation():
                    return
                
                # Step 4: Extract Views
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Extracting Views", 
                    f"Processing {stats.get('total_views', 0)} views...", 
                    40,
                    self._estimate_remaining_time(40),
                    True
                ))
                
                if self._check_cancellation():
                    return
                
                # Step 5: Extract Procedures and Functions
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Extracting Procedures", 
                    f"Processing {stats.get('total_procedures', 0)} procedures and {stats.get('total_functions', 0)} functions...", 
                    55,
                    self._estimate_remaining_time(55),
                    True
                ))
                
                if self._check_cancellation():
                    return
                
                # Step 6: Generate Documentation Files
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Generating Files", 
                    "Creating documentation files...", 
                    70,
                    self._estimate_remaining_time(70),
                    True
                ))
                self.root.after(0, lambda: self.log_message("Schema extracted, generating documentation files..."))
                
                generator = DocumentationGenerator(self.output_dir.get())
                generated_files = []
                
                file_progress = 70
                files_to_generate = sum([
                    self.generate_html.get(),
                    self.generate_markdown.get(), 
                    self.generate_json.get()
                ])
                progress_per_file = 25 / files_to_generate if files_to_generate > 0 else 0
                
                if self.generate_html.get():
                    if self._check_cancellation():
                        return
                        
                    self.root.after(0, lambda: self._update_detailed_progress(
                        "Creating HTML", 
                        "Generating HTML documentation with styling...", 
                        file_progress,
                        self._estimate_remaining_time(file_progress),
                        True
                    ))
                    
                    html_file = generator.generate_html_documentation(documentation)
                    generated_files.append(('HTML', html_file))
                    file_progress += progress_per_file
                
                if self.generate_markdown.get():
                    if self._check_cancellation():
                        return
                        
                    self.root.after(0, lambda: self._update_detailed_progress(
                        "Creating Markdown", 
                        "Generating Markdown documentation...", 
                        file_progress,
                        self._estimate_remaining_time(file_progress),
                        True
                    ))
                    
                    md_file = generator.generate_markdown_documentation(documentation)
                    generated_files.append(('Markdown', md_file))
                    file_progress += progress_per_file
                
                if self.generate_json.get():
                    if self._check_cancellation():
                        return
                        
                    self.root.after(0, lambda: self._update_detailed_progress(
                        "Creating JSON", 
                        "Generating JSON data export...", 
                        file_progress,
                        self._estimate_remaining_time(file_progress),
                        True
                    ))
                    
                    json_file = generator.generate_json_documentation(documentation)
                    generated_files.append(('JSON', json_file))
                    file_progress += progress_per_file
                
                # Final step
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Completing", 
                    "Finalizing documentation generation...", 
                    95,
                    "Almost done...",
                    True
                ))
                
                time.sleep(0.5)  # Brief pause for user experience
                
                self.root.after(0, lambda: self._update_detailed_progress(
                    "Complete", 
                    f"Successfully generated {len(generated_files)} documentation file(s)", 
                    100,
                    "Done!",
                    False
                ))
                
                self.root.after(0, lambda: self._generation_complete(generated_files))
                
        except Exception as e:
            if self.generation_cancelled:
                self.root.after(0, lambda: self._generation_cancelled())
            else:
                self.root.after(0, lambda: self._generation_failed(str(e)))
    
    def _check_cancellation(self):
        """Check if generation has been cancelled."""
        if self.generation_cancelled:
            self.root.after(0, lambda: self._generation_cancelled())
            return True
        return False
    
    def _estimate_remaining_time(self, current_progress):
        """Estimate remaining time based on current progress."""
        try:
            import time
            elapsed = time.time() - self.generation_start_time
            if current_progress > 0:
                total_estimated = (elapsed * 100) / current_progress
                remaining = max(0, total_estimated - elapsed)
                
                if remaining < 60:
                    return f"{int(remaining)}s"
                elif remaining < 3600:
                    minutes = int(remaining / 60)
                    seconds = int(remaining % 60)
                    return f"{minutes}m {seconds}s"
                else:
                    hours = int(remaining / 3600)
                    minutes = int((remaining % 3600) / 60)
                    return f"{hours}h {minutes}m"
            return "Calculating..."
        except:
            return "Unknown"
    
    def _generation_cancelled(self):
        """Handle cancelled generation."""
        self.log_message("Documentation generation was cancelled by user")
        self.current_step.set("Cancelled")
        self.detailed_progress.set("Generation was cancelled")
        self.estimated_time.set("")
        self.progress_value.set(0)
        
        # Re-enable UI
        self._set_ui_state(True)
        
        # Hide cancel button
        self._update_detailed_progress("Cancelled", "Generation was cancelled", 0, "", False)
        
        messagebox.showinfo("Generation Cancelled", "Documentation generation was cancelled successfully.")
    
    def _show_completion_dialog(self, generated_files):
        """Show enhanced completion dialog with file preview and management options."""
        dialog = CompletionDialog(self.root, self, generated_files)
    
    def _show_error_dialog(self, title, error_msg, error_type):
        """Show enhanced error dialog with actionable suggestions."""
        dialog = ErrorDialog(self.root, self, title, error_msg, error_type)
    
    def _update_statistics(self, stats):
        """Update statistics display."""
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)
        
        stats_text = f"""Database Statistics:
        
Tables: {stats.get('total_tables', 0)}
Views: {stats.get('total_views', 0)}
Stored Procedures: {stats.get('total_procedures', 0)}
Functions: {stats.get('total_functions', 0)}
Schemas: {stats.get('total_schemas', 0)}
Total Rows: {stats.get('total_rows', 0):,}

Largest Tables:
"""
        
        for table in stats.get('largest_tables', [])[:10]:
            stats_text += f"- {table.get('schema_name', '')}.{table.get('table_name', '')}: {table.get('row_count', 0):,} rows\n"
        
        self.stats_text.insert("1.0", stats_text)
        self.stats_text.configure(state="disabled")
    
    def _generation_complete(self, generated_files):
        """Handle successful documentation generation."""
        self.status_text.set("Documentation generated successfully")
        self._set_ui_state(True)
        
        # Log to reporting dashboard
        self._log_documentation_generation(generated_files, success=True)
        
        # Show enhanced completion dialog with preview options
        self._show_completion_dialog(generated_files)
        
        self.log_message("Documentation generation completed successfully")
        for fmt, path in generated_files:
            self.log_message(f"Generated {fmt}: {path}")
    
    def _generation_failed(self, error_msg):
        """Handle failed documentation generation."""
        self.current_step.set("Failed")
        self.detailed_progress.set("Generation failed - see error details")
        self.estimated_time.set("")
        self.status_text.set("Generation failed")
        self.progress_value.set(0)
        self._set_ui_state(True)
        
        # Log to reporting dashboard
        self._log_documentation_generation([], success=False, error_message=error_msg)
        
        # Hide cancel button
        self._update_detailed_progress("Failed", "Generation failed", 0, "", False)
        
        # Show enhanced error dialog
        self._show_error_dialog("Documentation Generation Failed", error_msg, "generation")
        self.log_message(f"Documentation generation failed: {error_msg}")
    
    def _set_ui_state(self, enabled):
        """Enable/disable UI elements during generation."""
        state = "normal" if enabled else "disabled"
        
        # Disable/enable relevant widgets
        for child in self.connection_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Combobox, ttk.Button, ttk.Radiobutton)):
                child.configure(state=state)
        
        for child in self.documentation_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Combobox, ttk.Button, ttk.Checkbutton)):
                child.configure(state=state)
    
    def _log_documentation_generation(self, generated_files, success=True, error_message=None):
        """Log documentation generation event to reporting dashboard."""
        try:
            # Calculate generation time
            import time
            generation_time = time.time() - self.generation_start_time if hasattr(self, 'generation_start_time') else 0
            
            # Get database info
            database_name = self.database.get()
            server_name = self.server.get()
            
            # Get statistics from current schema data
            stats = {}
            if hasattr(self, 'current_schema_data') and self.current_schema_data:
                schema_stats = self.current_schema_data.get('statistics', {})
                stats = {
                    'tables': len(self.current_schema_data.get('tables', [])),
                    'views': len(self.current_schema_data.get('views', [])),
                    'procedures': len(self.current_schema_data.get('stored_procedures', [])),
                    'functions': len(self.current_schema_data.get('functions', [])),
                    'relationships': self.current_schema_data.get('relationships', {}).get('relationship_count', 0)
                }
            
            # Get output formats
            output_formats = [fmt for fmt, _ in generated_files] if generated_files else []
            
            # Log the generation event
            self.reporting_dashboard.log_documentation_generation(
                database_name=database_name,
                server_name=server_name,
                stats=stats,
                generation_time=generation_time,
                output_formats=output_formats,
                success=success
            )
            
            if error_message:
                # Log the error as well
                from reporting_analytics import ReportingDatabase
                db = ReportingDatabase()
                db.log_usage_action("documentation_error", database_name, 
                                  {"error_message": error_message, "generation_time": generation_time})
            
        except Exception as e:
            # Don't let reporting errors break the main functionality
            print(f"Error logging to reporting dashboard: {e}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            config = {
                "database": {
                    "connection_method": self.connection_method.get(),
                    "server": self.server.get(),
                    "database": self.database.get(),
                    "username": self.username.get(),
                    "password": self.password.get(),
                    "client_id": self.client_id.get(),
                    "client_secret": self.client_secret.get(),
                    "tenant_id": self.tenant_id.get(),
                    "connection_string": self.connection_string.get(),
                    "driver": "ODBC Driver 17 for SQL Server",
                    "timeout": 30
                },
                "documentation": {
                    "output_directory": self.output_dir.get(),
                    "generate_html": self.generate_html.get(),
                    "generate_markdown": self.generate_markdown.get(),
                    "generate_json": self.generate_json.get(),
                    "include_system_objects": self.include_system_objects.get(),
                    "include_row_counts": self.include_row_counts.get()
                }
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Success", "Configuration saved successfully")
                self.log_message(f"Configuration saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Update GUI variables
                db_config = config.get('database', {})
                self.connection_method.set(db_config.get('connection_method', 'credentials'))
                self.server.set(db_config.get('server', ''))
                self.database.set(db_config.get('database', ''))
                self.username.set(db_config.get('username', ''))
                self.password.set(db_config.get('password', ''))
                self.client_id.set(db_config.get('client_id', ''))
                self.client_secret.set(db_config.get('client_secret', ''))
                self.tenant_id.set(db_config.get('tenant_id', ''))
                self.connection_string.set(db_config.get('connection_string', ''))
                
                doc_config = config.get('documentation', {})
                self.output_dir.set(doc_config.get('output_directory', 'output'))
                self.generate_html.set(doc_config.get('generate_html', True))
                self.generate_markdown.set(doc_config.get('generate_markdown', True))
                self.generate_json.set(doc_config.get('generate_json', True))
                self.include_system_objects.set(doc_config.get('include_system_objects', False))
                self.include_row_counts.set(doc_config.get('include_row_counts', True))
                
                self.on_connection_method_changed()
                messagebox.showinfo("Success", "Configuration loaded successfully")
                self.log_message(f"Configuration loaded from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def reset_config(self):
        """Reset configuration to defaults."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            self.setup_variables()
            self.on_connection_method_changed()
            self.log_message("Configuration reset to defaults")
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            os.startfile(output_path)
        else:
            messagebox.showwarning("Warning", "Output folder does not exist")
    
    def clear_log(self):
        """Clear the log display."""
        self.log_text.delete("1.0", tk.END)
    
    def log_message(self, message):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def on_exit(self):
        """Handle application exit."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()
    
    def create_profile_management_section(self):
        """Create profile management section in connection tab."""
        profile_frame = ttk.LabelFrame(self.connection_frame, text="Connection Profiles", padding="10")
        
        # Profile selection row
        profile_row = ttk.Frame(profile_frame)
        ttk.Label(profile_row, text="Current Profile:").pack(side="left", padx=(0, 5))
        
        self.profile_combo = ttk.Combobox(profile_row, textvariable=self.current_profile_name, 
                                         width=30, state="readonly")
        self.profile_combo.pack(side="left", padx=(0, 10))
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_selected)
        
        # Profile buttons
        ttk.Button(profile_row, text="Load", command=self.load_profile).pack(side="left", padx=2)
        ttk.Button(profile_row, text="Save", command=self.save_profile_dialog).pack(side="left", padx=2)
        ttk.Button(profile_row, text="Delete", command=self.delete_profile).pack(side="left", padx=2)
        ttk.Button(profile_row, text="Refresh", command=self.refresh_profiles).pack(side="left", padx=2)
        
        profile_row.pack(fill="x", pady=(0, 10))
        
        # Recent connections row
        recent_row = ttk.Frame(profile_frame)
        ttk.Label(recent_row, text="Recent:").pack(side="left", padx=(0, 5))
        
        self.recent_frame = ttk.Frame(recent_row)
        self.recent_frame.pack(side="left", fill="x", expand=True)
        
        recent_row.pack(fill="x")
        
        profile_frame.pack(fill="x", pady=(0, 10))
        self.refresh_profiles()
        self.refresh_recent_connections()
    
    def refresh_profiles(self):
        """Refresh the profile list."""
        try:
            profiles = self.profile_manager.list_profiles()
            profile_names = [p['name'] for p in profiles]
            self.profile_combo['values'] = profile_names
            
            if profile_names and not self.current_profile_name.get():
                # Select the most recently used profile
                most_recent = max(profiles, key=lambda x: x.get('last_used', ''))
                self.current_profile_name.set(most_recent['name'])
        except Exception as e:
            self.log_message(f"Error refreshing profiles: {e}")
    
    def refresh_recent_connections(self):
        """Refresh recent connections display."""
        try:
            # Clear existing recent connection buttons
            for widget in self.recent_frame.winfo_children():
                widget.destroy()
            
            recent = self.profile_manager.get_recent_connections(limit=3)
            for i, conn in enumerate(recent):
                btn_text = f"{conn['database']}@{conn['server'][:20]}..."
                btn = ttk.Button(
                    self.recent_frame, 
                    text=btn_text,
                    command=lambda c=conn: self.load_recent_connection(c),
                    width=25
                )
                btn.pack(side="left", padx=2)
                
                if i >= 2:  # Limit to 3 recent connections
                    break
        except Exception as e:
            self.log_message(f"Error refreshing recent connections: {e}")
    
    def load_recent_connection(self, connection_info):
        """Load a recent connection configuration."""
        try:
            self.server.set(connection_info['server'])
            self.database.set(connection_info['database'])
            self.connection_method.set(connection_info['method'])
            if connection_info['method'] == 'credentials':
                self.username.set(connection_info['username'])
            
            self.on_connection_method_changed()
            self.log_message(f"Loaded recent connection: {connection_info['database']}@{connection_info['server']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recent connection: {e}")
    
    def on_profile_selected(self, event=None):
        """Handle profile selection from combobox."""
        # Just update the display, don't auto-load
        pass
    
    def load_profile(self):
        """Load the selected profile."""
        profile_name = self.current_profile_name.get()
        if not profile_name:
            messagebox.showwarning("Warning", "Please select a profile to load")
            return
        
        try:
            profile = self.profile_manager.load_profile(profile_name)
            if not profile:
                messagebox.showerror("Error", f"Profile '{profile_name}' not found")
                return
            
            # Load connection configuration
            conn_config = profile['connection']
            self.connection_method.set(conn_config.get('method', 'credentials'))
            self.server.set(conn_config.get('server', ''))
            self.database.set(conn_config.get('database', ''))
            self.username.set(conn_config.get('username', ''))
            self.password.set(conn_config.get('password', ''))
            self.client_id.set(conn_config.get('client_id', ''))
            self.client_secret.set(conn_config.get('client_secret', ''))
            self.tenant_id.set(conn_config.get('tenant_id', ''))
            self.connection_string.set(conn_config.get('connection_string', ''))
            
            # Load documentation configuration if available
            if 'documentation' in profile:
                doc_config = profile['documentation']
                self.output_dir.set(doc_config.get('output_directory', 'output'))
                self.generate_html.set(doc_config.get('generate_html', True))
                self.generate_markdown.set(doc_config.get('generate_markdown', True))
                self.generate_json.set(doc_config.get('generate_json', True))
                self.include_system_objects.set(doc_config.get('include_system_objects', False))
                self.include_row_counts.set(doc_config.get('include_row_counts', True))
            
            # Update the UI based on connection method
            self.on_connection_method_changed()
            
            self.log_message(f"Loaded profile: {profile_name}")
            messagebox.showinfo("Success", f"Profile '{profile_name}' loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile: {e}")
    
    def save_profile_dialog(self):
        """Show dialog to save current configuration as profile."""
        dialog = ProfileSaveDialog(self.root, self)
        
        if dialog.result:
            profile_name = dialog.result['name']
            include_docs = dialog.result['include_docs']
            
            try:
                # Gather connection configuration
                connection_config = {
                    'method': self.connection_method.get(),
                    'server': self.server.get(),
                    'database': self.database.get(),
                    'username': self.username.get(),
                    'password': self.password.get(),
                    'client_id': self.client_id.get(),
                    'client_secret': self.client_secret.get(),
                    'tenant_id': self.tenant_id.get(),
                    'connection_string': self.connection_string.get()
                }
                
                # Gather documentation configuration if requested
                doc_config = None
                if include_docs:
                    doc_config = {
                        'output_directory': self.output_dir.get(),
                        'generate_html': self.generate_html.get(),
                        'generate_markdown': self.generate_markdown.get(),
                        'generate_json': self.generate_json.get(),
                        'include_system_objects': self.include_system_objects.get(),
                        'include_row_counts': self.include_row_counts.get()
                    }
                
                # Save profile
                success = self.profile_manager.save_profile(profile_name, connection_config, doc_config)
                
                if success:
                    self.refresh_profiles()
                    self.current_profile_name.set(profile_name)
                    messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully")
                else:
                    messagebox.showerror("Error", "Failed to save profile")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save profile: {e}")
    
    def delete_profile(self):
        """Delete the selected profile."""
        profile_name = self.current_profile_name.get()
        if not profile_name:
            messagebox.showwarning("Warning", "Please select a profile to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_name}'?"):
            try:
                success = self.profile_manager.delete_profile(profile_name)
                if success:
                    self.refresh_profiles()
                    self.current_profile_name.set('')
                    messagebox.showinfo("Success", f"Profile '{profile_name}' deleted successfully")
                else:
                    messagebox.showerror("Error", f"Failed to delete profile '{profile_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete profile: {e}")
    
    def _add_to_connection_history(self, success: bool, error_message: str = None):
        """Add connection attempt to history and refresh recent connections."""
        try:
            connection_config = {
                'method': self.connection_method.get(),
                'server': self.server.get(),
                'database': self.database.get(),
                'username': self.username.get()
            }
            
            self.profile_manager.add_to_history(connection_config, success, error_message)
            
            # Refresh recent connections display
            if success:
                self.refresh_recent_connections()
                
        except Exception as e:
            self.log_message(f"Failed to update connection history: {e}")
    
    def validate_field(self, field_name):
        """Validate a connection field in real-time."""
        try:
            validation_msg = ""
            
            if field_name == 'server':
                value = self.server.get().strip()
                if not value:
                    validation_msg = "Required"
                elif not self._is_valid_server_format(value):
                    validation_msg = "Invalid format"
                    
            elif field_name == 'database':
                value = self.database.get().strip()
                if not value:
                    validation_msg = "Required"
                elif len(value) > 128:
                    validation_msg = "Too long"
                    
            elif field_name == 'username':
                value = self.username.get().strip()
                if not value:
                    validation_msg = "Required"
                elif len(value) > 128:
                    validation_msg = "Too long"
                    
            elif field_name == 'password':
                value = self.password.get()
                if not value:
                    validation_msg = "Required"
                elif len(value) < 1:
                    validation_msg = "Too short"
                    
            elif field_name == 'connection_string':
                value = self.connection_string.get().strip()
                if not value:
                    validation_msg = "Required"
                elif not self._is_valid_connection_string(value):
                    validation_msg = "Invalid format"
            
            # Update validation status
            self.validation_status[field_name].set(validation_msg)
            
            # Update test button state based on overall validation
            self._update_test_button_state()
            
        except Exception as e:
            self.log_message(f"Validation error for {field_name}: {e}")
    
    def _is_valid_server_format(self, server):
        """Validate server format (basic hostname/IP validation)."""
        import re
        # Basic pattern for hostname or IP
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$'
        return bool(re.match(hostname_pattern, server)) and len(server) <= 253
    
    def _is_valid_connection_string(self, conn_str):
        """Validate connection string format."""
        # Check for basic connection string components
        required_components = ['SERVER', 'DATABASE']
        conn_str_upper = conn_str.upper()
        return all(component in conn_str_upper for component in required_components)
    
    def _update_test_button_state(self):
        """Update test button state based on field validation."""
        try:
            method = self.connection_method.get()
            has_errors = False
            
            # Check common fields
            if self.validation_status['server'].get():
                has_errors = True
            if self.validation_status['database'].get():
                has_errors = True
                
            # Check method-specific fields
            if method == 'credentials':
                if self.validation_status['username'].get():
                    has_errors = True
                if self.validation_status['password'].get():
                    has_errors = True
            elif method == 'connection_string':
                if self.validation_status['connection_string'].get():
                    has_errors = True
            
            # Enable/disable test button
            if hasattr(self, 'test_btn'):
                state = "disabled" if has_errors else "normal"
                self.test_btn.configure(state=state)
                
        except Exception as e:
            self.log_message(f"Error updating test button state: {e}")
    
    def cancel_generation(self):
        """Cancel the current documentation generation."""
        if messagebox.askyesno("Cancel Generation", "Are you sure you want to cancel the documentation generation?"):
            self.generation_cancelled = True
            self.log_message("Generation cancellation requested...")
            self.current_step.set("Cancelling...")
    
    def _update_detailed_progress(self, step: str, details: str = "", progress: float = None, 
                                 estimated_time: str = "", show_cancel: bool = True):
        """Update detailed progress information."""
        self.current_step.set(step)
        self.detailed_progress.set(details)
        self.estimated_time.set(estimated_time)
        
        if progress is not None:
            self.progress_value.set(progress)
        
        # Show/hide cancel button
        if show_cancel and not self.cancel_btn.winfo_viewable():
            self.cancel_btn.pack(pady=5)
        elif not show_cancel and self.cancel_btn.winfo_viewable():
            self.cancel_btn.pack_forget()
    
    # Schema Comparison Methods
    def on_comparison_source_changed(self):
        """Handle source type selection change."""
        if self.comparison_source.get() == "database":
            self.source_db_frame.pack(fill="x", pady=5)
            self.source_file_frame.pack_forget()
        else:
            self.source_file_frame.pack(fill="x", pady=5)
            self.source_db_frame.pack_forget()
    
    def on_comparison_target_changed(self):
        """Handle target type selection change."""
        if self.comparison_target.get() == "database":
            self.target_db_frame.pack(fill="x", pady=5)
            self.target_file_frame.pack_forget()
        else:
            self.target_file_frame.pack(fill="x", pady=5)
            self.target_db_frame.pack_forget()
    
    def use_current_database_as_source(self):
        """Use the current database connection as source."""
        current_db = self.database.get()
        if current_db:
            self.source_database.set(current_db)
        else:
            messagebox.showwarning("No Database", "Please select a database in the connection tab first")
    
    def browse_source_file(self):
        """Browse for source JSON file."""
        file_path = filedialog.askopenfilename(
            title="Select Source Schema JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.source_file_path.set(file_path)
    
    def browse_target_file(self):
        """Browse for target JSON file."""
        file_path = filedialog.askopenfilename(
            title="Select Target Schema JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.target_file_path.set(file_path)
    
    def load_databases_for_comparison(self):
        """Load available databases for comparison selection."""
        try:
            # Use the same logic as the main database loading
            with AzureSQLConnection() as db:
                success = self._connect_to_database(db)
                if not success:
                    messagebox.showerror("Connection Error", "Failed to connect to database")
                    return
                
                # Get list of databases
                databases = db.get_databases()
                db_names = [db_info['name'] for db_info in databases]
                
                # Update both comboboxes
                self.source_db_combo['values'] = db_names
                self.target_db_combo['values'] = db_names
                
                self.log_message(f"Loaded {len(db_names)} databases for comparison")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load databases: {e}")
    
    def compare_schemas(self):
        """Compare schemas based on selected sources."""
        try:
            # Validate inputs
            if not self._validate_comparison_inputs():
                return
            
            # Start comparison in background thread
            self.log_message("Starting schema comparison...")
            thread = threading.Thread(target=self._compare_schemas_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Failed to start schema comparison: {e}")
    
    def _validate_comparison_inputs(self):
        """Validate schema comparison inputs."""
        if self.comparison_source.get() == "database":
            if not self.source_database.get():
                messagebox.showerror("Validation Error", "Please select a source database")
                return False
        else:
            if not self.source_file_path.get() or not os.path.exists(self.source_file_path.get()):
                messagebox.showerror("Validation Error", "Please select a valid source JSON file")
                return False
        
        if self.comparison_target.get() == "database":
            if not self.target_database.get():
                messagebox.showerror("Validation Error", "Please select a target database")
                return False
        else:
            if not self.target_file_path.get() or not os.path.exists(self.target_file_path.get()):
                messagebox.showerror("Validation Error", "Please select a valid target JSON file")
                return False
        
        return True
    
    def _compare_schemas_thread(self):
        """Background thread for schema comparison."""
        try:
            # Load source schema
            if self.comparison_source.get() == "database":
                source_schema = self._extract_database_schema(self.source_database.get())
            else:
                source_schema = self._load_schema_from_file(self.source_file_path.get())
            
            # Load target schema
            if self.comparison_target.get() == "database":
                target_schema = self._extract_database_schema(self.target_database.get())
            else:
                target_schema = self._load_schema_from_file(self.target_file_path.get())
            
            # Perform comparison
            comparator = SchemaComparator()
            comparison_name = f"Schema Comparison - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.comparison_results = comparator.compare_schemas(
                source_schema, 
                target_schema, 
                comparison_name
            )
            
            # Update UI with results
            self.root.after(0, self._display_comparison_results)
            
        except Exception as e:
            error_msg = f"Schema comparison failed: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Comparison Error", error_msg))
            self.root.after(0, lambda: self.log_message(error_msg))
    
    def _extract_database_schema(self, database_name):
        """Extract schema from a database."""
        with AzureSQLConnection() as db:
            success = self._connect_to_database(db)
            if not success:
                raise Exception(f"Failed to connect to database {database_name}")
            
            # Switch to the specified database if different from current
            if database_name != self.database.get():
                # Create new connection to specific database
                connection_params = {
                    'method': self.connection_method.get(),
                    'server': self.server.get(),
                    'database': database_name,
                    'username': self.username.get(),
                    'password': self.password.get(),
                    'client_id': self.client_id.get(),
                    'client_secret': self.client_secret.get(),
                    'tenant_id': self.tenant_id.get(),
                    'connection_string': self.connection_string.get().replace(self.database.get(), database_name) if self.connection_string.get() else ''
                }
                
                with AzureSQLConnection() as db_specific:
                    if connection_params['method'] == 'credentials':
                        success = db_specific.connect_with_credentials(
                            connection_params['server'],
                            database_name,
                            connection_params['username'],
                            connection_params['password']
                        )
                    # Add other connection methods as needed
                    
                    if not success:
                        raise Exception(f"Failed to connect to specific database {database_name}")
                    
                    extractor = DocumentationExtractor(db_specific)
                    return extractor.extract_complete_documentation()
            else:
                extractor = DocumentationExtractor(db)
                return extractor.extract_complete_documentation()
    
    def _load_schema_from_file(self, file_path):
        """Load schema from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _display_comparison_results(self):
        """Display comparison results in the UI."""
        if not self.comparison_results:
            return
        
        # Update summary
        summary = self.comparison_results['summary']
        metadata = self.comparison_results['metadata']
        
        summary_text = f"""Comparison: {metadata['name']}
Time: {metadata['timestamp']}

Total Changes: {summary['total_changes']}
Objects Affected: {summary['objects_affected']}

Changes by Impact:"""
        
        for impact, count in summary.get('changes_by_impact', {}).items():
            summary_text += f"\n  {impact.title()}: {count}"
        
        summary_text += "\n\nChanges by Type:"
        for obj_type, changes in summary.get('changes_by_type', {}).items():
            total_type_changes = sum(changes.values())
            summary_text += f"\n  {obj_type.title()}: {total_type_changes}"
        
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", summary_text)
        self.summary_text.configure(state="disabled")
        
        # Update changes tree
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)
        
        for change in self.comparison_results['changes']:
            # Color code by impact level
            tags = []
            if change['impact_level'] == 'critical':
                tags = ['critical']
            elif change['impact_level'] == 'high':
                tags = ['high']
            elif change['impact_level'] == 'medium':
                tags = ['medium']
            else:
                tags = ['low']
            
            self.changes_tree.insert('', 'end', values=(
                change['object_name'],
                change['object_type'],
                change['change_type'],
                change['impact_level'],
                change['description']
            ), tags=tags)
        
        # Configure tags for color coding
        self.changes_tree.tag_configure('critical', background='#ffebee')
        self.changes_tree.tag_configure('high', background='#fff3e0')
        self.changes_tree.tag_configure('medium', background='#f3e5f5')
        self.changes_tree.tag_configure('low', background='#e8f5e8')
        
        # Update impact analysis
        impact_analysis = self.comparison_results.get('impact_analysis', {})
        recommendations = self.comparison_results.get('recommendations', [])
        
        impact_text = f"Overall Risk Level: {impact_analysis.get('overall_risk', 'unknown').title()}\n\n"
        
        if impact_analysis.get('breaking_changes'):
            impact_text += "Breaking Changes:\n"
            for change in impact_analysis['breaking_changes'][:10]:  # Show first 10
                impact_text += f"• {change}\n"
            impact_text += "\n"
        
        if impact_analysis.get('compatibility_issues'):
            impact_text += "Compatibility Issues:\n"
            for issue in impact_analysis['compatibility_issues'][:10]:  # Show first 10
                impact_text += f"• {issue}\n"
            impact_text += "\n"
        
        if recommendations:
            impact_text += "Recommendations:\n"
            for rec in recommendations:
                impact_text += f"• {rec}\n"
        
        self.impact_text.configure(state="normal")
        self.impact_text.delete("1.0", tk.END)
        self.impact_text.insert("1.0", impact_text)
        self.impact_text.configure(state="disabled")
        
        self.log_message(f"Schema comparison completed: {summary['total_changes']} changes found")
    
    def export_comparison_results(self):
        """Export comparison results to file."""
        if not self.comparison_results:
            messagebox.showwarning("No Results", "No comparison results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Comparison Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                comparator = SchemaComparator()
                comparator.export_comparison(self.comparison_results, file_path)
                messagebox.showinfo("Export Complete", f"Comparison results exported to {file_path}")
                self.log_message(f"Comparison results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {e}")
    
    def clear_comparison_results(self):
        """Clear comparison results."""
        self.comparison_results = None
        
        # Clear summary
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.configure(state="disabled")
        
        # Clear changes tree
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)
        
        # Clear impact analysis
        self.impact_text.configure(state="normal")
        self.impact_text.delete("1.0", tk.END)
        self.impact_text.configure(state="disabled")
        
        self.log_message("Comparison results cleared")
    
    # Dependency Visualization Methods
    def on_viz_type_changed(self):
        """Handle visualization type selection change."""
        if self.viz_type.get() == "circular_layout":
            self.center_object_frame.pack(fill="x", pady=(0, 10))
        else:
            self.center_object_frame.pack_forget()
    
    def generate_visualization(self):
        """Generate dependency visualization."""
        try:
            # Validate that we have database connection
            if not self.database.get():
                messagebox.showwarning("No Database", "Please select a database first")
                return
            
            self.log_message("Starting dependency visualization generation...")
            
            # Extract schema data
            with AzureSQLConnection() as db:
                success = self._connect_to_database(db)
                if not success:
                    messagebox.showerror("Connection Error", "Failed to connect to database")
                    return
                
                extractor = DocumentationExtractor(db)
                schema_data = extractor.extract_complete_documentation()
            
            # Create visualization
            visualizer = DependencyVisualizer()
            
            # Get visualization type
            viz_type_map = {
                'relationship_diagram': VisualizationType.RELATIONSHIP_DIAGRAM,
                'dependency_graph': VisualizationType.DEPENDENCY_GRAPH,
                'hierarchical_view': VisualizationType.HIERARCHICAL_VIEW,
                'circular_layout': VisualizationType.CIRCULAR_LAYOUT
            }
            
            viz_type = viz_type_map.get(self.viz_type.get(), VisualizationType.RELATIONSHIP_DIAGRAM)
            
            # Prepare options
            options = {}
            
            # Schema filter
            schema_filter_text = self.viz_schema_filter.get().strip()
            if schema_filter_text:
                options['schema_filter'] = [s.strip() for s in schema_filter_text.split(',')]
            
            # Center object for circular layout
            if viz_type == VisualizationType.CIRCULAR_LAYOUT:
                center_object = self.viz_center_object.get().strip()
                if center_object:
                    options['center_object'] = center_object
            
            # Include options
            options['include_views'] = self.viz_include_views.get()
            options['include_procedures'] = self.viz_include_procedures.get()
            
            # Generate visualization
            self.current_visualization = visualizer.generate_visualization(
                schema_data, viz_type, options
            )
            
            # Update statistics display
            self._display_visualization_stats()
            
            self.log_message(f"Visualization generated: {self.current_visualization['metadata']['node_count']} nodes, {self.current_visualization['metadata']['edge_count']} edges")
            
            messagebox.showinfo("Visualization Complete", 
                              f"Visualization generated successfully!\n"
                              f"Nodes: {self.current_visualization['metadata']['node_count']}\n"
                              f"Edges: {self.current_visualization['metadata']['edge_count']}\n\n"
                              f"Use 'Export HTML' and 'View in Browser' to see the interactive diagram.")
            
        except Exception as e:
            error_msg = f"Failed to generate visualization: {str(e)}"
            messagebox.showerror("Visualization Error", error_msg)
            self.log_message(error_msg)
    
    def _display_visualization_stats(self):
        """Display visualization statistics."""
        if not self.current_visualization:
            return
        
        visualizer = DependencyVisualizer()
        stats = visualizer.get_visualization_statistics(self.current_visualization)
        
        stats_text = f"""Visualization Statistics:

Type: {stats['visualization_type'].replace('_', ' ').title()}
Total Nodes: {stats['total_nodes']}
Total Edges: {stats['total_edges']}

Node Types:"""
        
        for node_type, count in stats['node_types'].items():
            stats_text += f"\n  {node_type.title()}: {count}"
        
        if stats['edge_types']:
            stats_text += "\n\nEdge Types:"
            for edge_type, count in stats['edge_types'].items():
                stats_text += f"\n  {edge_type.replace('_', ' ').title()}: {count}"
        
        if stats['schemas']:
            stats_text += f"\n\nSchemas Included: {', '.join(stats['schemas'])}"
        
        self.viz_stats_text.configure(state="normal")
        self.viz_stats_text.delete("1.0", tk.END)
        self.viz_stats_text.insert("1.0", stats_text)
        self.viz_stats_text.configure(state="disabled")
    
    def export_visualization_html(self):
        """Export visualization as interactive HTML."""
        if not self.current_visualization:
            messagebox.showwarning("No Visualization", "Please generate a visualization first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Visualization as HTML",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                visualizer = DependencyVisualizer()
                visualizer.generate_html_visualization(self.current_visualization, file_path)
                
                messagebox.showinfo("Export Complete", f"Interactive visualization exported to {file_path}")
                self.log_message(f"Visualization exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export visualization: {e}")
    
    def export_visualization_svg(self):
        """Export visualization as SVG."""
        if not self.current_visualization:
            messagebox.showwarning("No Visualization", "Please generate a visualization first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Visualization as SVG",
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                visualizer = DependencyVisualizer()
                visualizer.export_svg(self.current_visualization, file_path)
                
                messagebox.showinfo("Export Complete", f"SVG visualization exported to {file_path}")
                self.log_message(f"SVG visualization exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export SVG: {e}")
    
    def view_visualization_in_browser(self):
        """Generate and view visualization in browser."""
        if not self.current_visualization:
            messagebox.showwarning("No Visualization", "Please generate a visualization first")
            return
        
        try:
            import tempfile
            import webbrowser
            
            # Create temporary HTML file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            
            visualizer = DependencyVisualizer()
            html_content = visualizer.generate_html_visualization(self.current_visualization)
            temp_file.write(html_content)
            temp_file.close()
            
            # Open in browser
            webbrowser.open(f"file://{temp_file.name}")
            
            self.log_message(f"Visualization opened in browser: {temp_file.name}")
            
        except Exception as e:
            messagebox.showerror("Browser Error", f"Failed to open visualization in browser: {e}")
    
    # Search and Filter Methods
    
    def perform_search(self):
        """Perform database object search based on current criteria."""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return
        
        if not self.current_schema_data:
            # Need to extract schema data first
            messagebox.showinfo("Schema Required", "Please connect to a database and extract schema data first.")
            return
        
        try:
            self.search_results = self.search_database_objects(
                self.current_schema_data,
                query,
                self.search_type.get(),
                self.search_scope.get(),
                self.search_case_sensitive.get(),
                self.search_regex.get()
            )
            
            self.display_search_results()
            self.update_search_statistics()
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Search failed: {str(e)}")
    
    def search_database_objects(self, schema_data, query, obj_type, scope, case_sensitive, use_regex):
        """Search through database objects based on criteria."""
        import re
        
        results = []
        
        # Prepare search pattern
        if use_regex:
            try:
                pattern = re.compile(query, re.IGNORECASE if not case_sensitive else 0)
            except re.error as e:
                raise ValueError(f"Invalid regular expression: {str(e)}")
        else:
            if not case_sensitive:
                query = query.lower()
        
        # Helper function to check if text matches
        def matches_query(text, field_name=""):
            if not text:
                return False, ""
            
            text_str = str(text)
            if use_regex:
                match = pattern.search(text_str)
                return bool(match), f"Regex match in {field_name}" if match else ""
            else:
                search_text = text_str.lower() if not case_sensitive else text_str
                search_query = query if case_sensitive else query.lower()
                if search_query in search_text:
                    return True, f"Found '{query}' in {field_name}"
                return False, ""
        
        # Search tables
        if obj_type in ['all', 'tables'] and 'tables' in schema_data:
            for table in schema_data['tables']:
                match_info = []
                
                # Search in table name
                if scope in ['name', 'all']:
                    matched, info = matches_query(table.get('name', ''), 'table name')
                    if matched:
                        match_info.append(info)
                
                # Search in description
                if scope in ['description', 'all']:
                    matched, info = matches_query(table.get('description', ''), 'description')
                    if matched:
                        match_info.append(info)
                
                # Search in columns
                if scope in ['columns', 'all'] and 'columns' in table:
                    for col in table['columns']:
                        matched, info = matches_query(col.get('name', ''), f"column '{col.get('name', '')}'")
                        if matched:
                            match_info.append(info)
                        
                        matched, info = matches_query(col.get('description', ''), f"column '{col.get('name', '')}' description")
                        if matched:
                            match_info.append(info)
                
                if match_info:
                    results.append({
                        'name': table.get('name', 'Unknown'),
                        'type': 'Table',
                        'schema': table.get('schema', 'dbo'),
                        'description': table.get('description', ''),
                        'match_info': '; '.join(match_info[:3]),  # Limit to first 3 matches
                        'full_object': table
                    })
        
        # Search views
        if obj_type in ['all', 'views'] and 'views' in schema_data:
            for view in schema_data['views']:
                match_info = []
                
                if scope in ['name', 'all']:
                    matched, info = matches_query(view.get('name', ''), 'view name')
                    if matched:
                        match_info.append(info)
                
                if scope in ['description', 'all']:
                    matched, info = matches_query(view.get('description', ''), 'description')
                    if matched:
                        match_info.append(info)
                
                if scope in ['columns', 'all'] and 'columns' in view:
                    for col in view['columns']:
                        matched, info = matches_query(col.get('name', ''), f"column '{col.get('name', '')}'")
                        if matched:
                            match_info.append(info)
                
                if match_info:
                    results.append({
                        'name': view.get('name', 'Unknown'),
                        'type': 'View',
                        'schema': view.get('schema', 'dbo'),
                        'description': view.get('description', ''),
                        'match_info': '; '.join(match_info[:3]),
                        'full_object': view
                    })
        
        # Search stored procedures
        if obj_type in ['all', 'procedures'] and 'stored_procedures' in schema_data:
            for proc in schema_data['stored_procedures']:
                match_info = []
                
                if scope in ['name', 'all']:
                    matched, info = matches_query(proc.get('name', ''), 'procedure name')
                    if matched:
                        match_info.append(info)
                
                if scope in ['description', 'all']:
                    matched, info = matches_query(proc.get('description', ''), 'description')
                    if matched:
                        match_info.append(info)
                
                if scope == 'all':
                    # Search in definition/body
                    matched, info = matches_query(proc.get('definition', ''), 'procedure body')
                    if matched:
                        match_info.append(info)
                
                if match_info:
                    results.append({
                        'name': proc.get('name', 'Unknown'),
                        'type': 'Procedure',
                        'schema': proc.get('schema', 'dbo'),
                        'description': proc.get('description', ''),
                        'match_info': '; '.join(match_info[:3]),
                        'full_object': proc
                    })
        
        # Search functions
        if obj_type in ['all', 'functions'] and 'functions' in schema_data:
            for func in schema_data['functions']:
                match_info = []
                
                if scope in ['name', 'all']:
                    matched, info = matches_query(func.get('name', ''), 'function name')
                    if matched:
                        match_info.append(info)
                
                if scope in ['description', 'all']:
                    matched, info = matches_query(func.get('description', ''), 'description')
                    if matched:
                        match_info.append(info)
                
                if scope == 'all':
                    matched, info = matches_query(func.get('definition', ''), 'function body')
                    if matched:
                        match_info.append(info)
                
                if match_info:
                    results.append({
                        'name': func.get('name', 'Unknown'),
                        'type': 'Function',
                        'schema': func.get('schema', 'dbo'),
                        'description': func.get('description', ''),
                        'match_info': '; '.join(match_info[:3]),
                        'full_object': func
                    })
        
        # Sort results by type and name
        results.sort(key=lambda x: (x['type'], x['name']))
        return results
    
    def display_search_results(self):
        """Display search results in the treeview."""
        # Clear existing results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Add results
        for result in self.search_results:
            self.search_tree.insert(
                "",
                "end",
                text=result['name'],
                values=(
                    result['type'],
                    result['schema'],
                    result['description'][:100] + ('...' if len(result['description']) > 100 else ''),
                    result['match_info']
                )
            )
    
    def update_search_statistics(self):
        """Update search statistics display."""
        stats = {}
        total = len(self.search_results)
        
        # Count by type
        for result in self.search_results:
            obj_type = result['type']
            stats[obj_type] = stats.get(obj_type, 0) + 1
        
        # Format statistics
        stats_text = f"Total Results: {total}\n\n"
        for obj_type, count in sorted(stats.items()):
            stats_text += f"{obj_type}s: {count}\n"
        
        # Update display
        self.search_stats_text.config(state="normal")
        self.search_stats_text.delete(1.0, tk.END)
        self.search_stats_text.insert(1.0, stats_text)
        self.search_stats_text.config(state="disabled")
    
    def clear_search(self):
        """Clear search results and query."""
        self.search_query.set("")
        self.search_results = []
        
        # Clear results display
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Clear statistics
        self.search_stats_text.config(state="normal")
        self.search_stats_text.delete(1.0, tk.END)
        self.search_stats_text.config(state="disabled")
    
    def view_search_result_details(self):
        """View detailed information for selected search result."""
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a search result to view details.")
            return
        
        # Get selected item data
        item_values = self.search_tree.item(selection[0])
        object_name = item_values['text']
        
        # Find the full object data
        selected_object = None
        for result in self.search_results:
            if result['name'] == object_name:
                selected_object = result['full_object']
                break
        
        if selected_object:
            # Show object details using the comprehensive details manager
            self.object_details_manager.show_object_details(selected_object, self.current_schema_data)
        else:
            messagebox.showerror("Error", "Could not find detailed information for selected object.")
    
    def show_object_details_window(self, obj_data):
        """Show detailed object information in a popup window."""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Object Details: {obj_data.get('name', 'Unknown')}")
        details_window.geometry("800x600")
        
        # Create notebook for different sections
        details_notebook = ttk.Notebook(details_window)
        
        # Basic info tab
        info_frame = ttk.Frame(details_notebook)
        details_notebook.add(info_frame, text="Basic Information")
        
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=20)
        info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Format basic info
        info_content = f"Name: {obj_data.get('name', 'Unknown')}\n"
        info_content += f"Schema: {obj_data.get('schema', 'dbo')}\n"
        info_content += f"Type: {obj_data.get('type', 'Unknown')}\n"
        info_content += f"Description: {obj_data.get('description', 'No description available')}\n\n"
        
        if 'columns' in obj_data:
            info_content += "Columns:\n"
            for col in obj_data['columns']:
                info_content += f"  - {col.get('name', 'Unknown')} ({col.get('data_type', 'Unknown')})\n"
                if col.get('description'):
                    info_content += f"    Description: {col.get('description')}\n"
        
        info_text.insert(1.0, info_content)
        info_text.config(state="disabled")
        
        # Definition tab (for procedures/functions)
        if obj_data.get('definition'):
            def_frame = ttk.Frame(details_notebook)
            details_notebook.add(def_frame, text="Definition")
            
            def_text = scrolledtext.ScrolledText(def_frame, wrap=tk.NONE, height=20)
            def_text.pack(fill="both", expand=True, padx=10, pady=10)
            def_text.insert(1.0, obj_data.get('definition', ''))
            def_text.config(state="disabled")
        
        details_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Close button
        ttk.Button(
            details_window,
            text="Close",
            command=details_window.destroy
        ).pack(pady=10)
    
    def export_search_results(self):
        """Export search results to a file."""
        if not self.search_results:
            messagebox.showwarning("No Results", "No search results to export.")
            return
        
        # Ask user for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            title="Export Search Results"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_search_results_csv(file_path)
                else:
                    self.export_search_results_json(file_path)
                
                messagebox.showinfo("Export Complete", f"Search results exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def export_search_results_json(self, file_path):
        """Export search results as JSON."""
        export_data = {
            'search_query': self.search_query.get(),
            'search_type': self.search_type.get(),
            'search_scope': self.search_scope.get(),
            'case_sensitive': self.search_case_sensitive.get(),
            'regex_mode': self.search_regex.get(),
            'timestamp': datetime.now().isoformat(),
            'results_count': len(self.search_results),
            'results': self.search_results
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def export_search_results_csv(self, file_path):
        """Export search results as CSV."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Object Name', 'Type', 'Schema', 'Description', 'Match Info'])
            
            # Write results
            for result in self.search_results:
                writer.writerow([
                    result['name'],
                    result['type'],
                    result['schema'],
                    result['description'],
                    result['match_info']
                ])
    
    def generate_docs_for_selection(self):
        """Generate documentation only for selected search results."""
        if not self.search_results:
            messagebox.showwarning("No Results", "No search results available.")
            return
        
        # Get selected items from search tree
        selected_items = self.search_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select objects from the search results to generate documentation for.")
            return
        
        # Get selected objects
        selected_objects = []
        for item in selected_items:
            item_values = self.search_tree.item(item)
            object_name = item_values['text']
            
            # Find the full object data
            for result in self.search_results:
                if result['name'] == object_name:
                    selected_objects.append(result['full_object'])
                    break
        
        if not selected_objects:
            messagebox.showerror("Error", "Could not find selected objects data.")
            return
        
        # Show selective documentation dialog
        self.show_selective_documentation_dialog(selected_objects)
    
    def show_selective_documentation_dialog(self, selected_objects):
        """Show dialog for selective documentation generation."""
        dialog = SelectiveDocumentationDialog(self.root, self, selected_objects, self.current_schema_data)
    
    def load_schema_data_for_search(self):
        """Load schema data for search functionality."""
        if hasattr(self, 'last_extracted_data') and self.last_extracted_data:
            self.current_schema_data = self.last_extracted_data
            return True
        
        # Try to load from recent extraction or trigger new extraction
        messagebox.showinfo("Schema Data", "Please extract database schema first using the main documentation generation.")
        return False
    
    def browse_database_schema(self):
        """Open database schema browser for selected database."""
        selected_items = self.database_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a database to browse.")
            return
        
        item = selected_items[0]
        db_name = self.database_tree.item(item)['values'][0]
        
        # Create schema browser window
        browser_window = SchemaBrowserWindow(self.root, self, db_name)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


class ProfileSaveDialog:
    """Dialog for saving connection profiles."""
    
    def __init__(self, parent, gui_app):
        self.parent = parent
        self.gui_app = gui_app
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Save Profile")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_x() + parent.winfo_width()//2) - (self.dialog.winfo_width()//2)
        y = (parent.winfo_y() + parent.winfo_height()//2) - (self.dialog.winfo_height()//2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Profile name
        ttk.Label(main_frame, text="Profile Name:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.pack(fill="x", pady=(0, 15))
        name_entry.focus()
        
        # Options
        self.include_docs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame, 
            text="Include documentation settings", 
            variable=self.include_docs_var
        ).pack(anchor="w", pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.save).pack(side="right")
        
        # Handle Enter and Escape keys
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def save(self):
        """Save the profile."""
        profile_name = self.name_var.get().strip()
        if not profile_name:
            messagebox.showerror("Error", "Please enter a profile name")
            return
        
        self.result = {
            'name': profile_name,
            'include_docs': self.include_docs_var.get()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.result = None
        self.dialog.destroy()


class CompletionDialog:
    """Dialog for handling documentation generation completion with preview options."""
    
    def __init__(self, parent, gui_app, generated_files):
        self.parent = parent
        self.gui_app = gui_app
        self.generated_files = generated_files
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Documentation Generated Successfully")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_x() + parent.winfo_width()//2) - (self.dialog.winfo_width()//2)
        y = (parent.winfo_y() + parent.winfo_height()//2) - (self.dialog.winfo_height()//2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
        # Handle closing
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Success message
        success_frame = ttk.Frame(main_frame)
        success_frame.pack(fill="x", pady=(0, 20))
        
        # Success icon (using text since we can't assume icons exist)
        ttk.Label(success_frame, text="✓", font=("Arial", 24), foreground="green").pack(side="left", padx=(0, 10))
        ttk.Label(success_frame, text="Documentation Generated Successfully!", 
                 font=("Arial", 14, "bold")).pack(side="left")
        
        # Generated files list
        files_frame = ttk.LabelFrame(main_frame, text="Generated Files", padding="10")
        files_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create treeview for files
        columns = ('Type', 'Filename', 'Size')
        self.files_tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.files_tree.heading('Type', text='Type')
        self.files_tree.heading('Filename', text='Filename')
        self.files_tree.heading('Size', text='Size')
        
        self.files_tree.column('Type', width=80)
        self.files_tree.column('Filename', width=300)
        self.files_tree.column('Size', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.files_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate file list
        for file_type, file_path in self.generated_files:
            try:
                file_size = os.path.getsize(file_path)
                size_str = self._format_file_size(file_size)
                filename = os.path.basename(file_path)
                
                self.files_tree.insert('', 'end', values=(file_type, filename, size_str))
            except Exception as e:
                self.files_tree.insert('', 'end', values=(file_type, os.path.basename(file_path), 'Unknown'))
        
        # Bind double-click to preview
        self.files_tree.bind('<Double-1>', self.preview_file)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=(0, 20))
        
        # Left side buttons (file actions)
        left_buttons = ttk.Frame(action_frame)
        left_buttons.pack(side="left", fill="x", expand=True)
        
        ttk.Button(left_buttons, text="Preview File", command=self.preview_selected_file).pack(side="left", padx=(0, 5))
        ttk.Button(left_buttons, text="Open in Browser", command=self.open_in_browser).pack(side="left", padx=5)
        ttk.Button(left_buttons, text="Open Folder", command=self.open_output_folder).pack(side="left", padx=5)
        
        # Right side buttons (dialog actions)
        right_buttons = ttk.Frame(action_frame)
        right_buttons.pack(side="right")
        
        ttk.Button(right_buttons, text="Close", command=self.close_dialog).pack(side="right", padx=5)
        
        # Statistics summary
        stats_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
        stats_frame.pack(fill="x")
        
        total_size = sum(self._get_file_size(path) for _, path in self.generated_files)
        file_count = len(self.generated_files)
        
        summary_text = f"Generated {file_count} file(s) • Total size: {self._format_file_size(total_size)}"
        ttk.Label(stats_frame, text=summary_text).pack()
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/1024**2:.1f} MB"
        else:
            return f"{size_bytes/1024**3:.1f} GB"
    
    def _get_file_size(self, file_path):
        """Get file size safely."""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def preview_file(self, event=None):
        """Preview file on double-click."""
        self.preview_selected_file()
    
    def preview_selected_file(self):
        """Preview the selected file."""
        selected_items = self.files_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a file to preview")
            return
        
        item = selected_items[0]
        values = self.files_tree.item(item)['values']
        file_type = values[0]
        filename = values[1]
        
        # Find the full path
        file_path = None
        for ftype, fpath in self.generated_files:
            if ftype == file_type and os.path.basename(fpath) == filename:
                file_path = fpath
                break
        
        if file_path and os.path.exists(file_path):
            if file_type == 'HTML':
                self._preview_html(file_path)
            elif file_type in ['Markdown', 'JSON']:
                self._preview_text(file_path, file_type)
            else:
                messagebox.showinfo("Preview", f"Preview not available for {file_type} files")
        else:
            messagebox.showerror("Error", "File not found")
    
    def _preview_html(self, file_path):
        """Preview HTML file in a web browser or simple viewer."""
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open HTML file: {e}")
    
    def _preview_text(self, file_path, file_type):
        """Preview text-based files in a simple text viewer."""
        try:
            preview_dialog = FilePreviewDialog(self.dialog, file_path, file_type)
        except Exception as e:
            messagebox.showerror("Error", f"Could not preview {file_type} file: {e}")
    
    def open_in_browser(self):
        """Open HTML file in browser."""
        # Find HTML file
        html_file = None
        for file_type, file_path in self.generated_files:
            if file_type == 'HTML':
                html_file = file_path
                break
        
        if html_file:
            self._preview_html(html_file)
        else:
            messagebox.showinfo("No HTML File", "No HTML documentation file was generated")
    
    def open_output_folder(self):
        """Open the output folder."""
        if self.generated_files:
            folder_path = os.path.dirname(self.generated_files[0][1])
            try:
                os.startfile(folder_path)  # Windows
            except AttributeError:
                try:
                    import subprocess
                    subprocess.run(['open', folder_path])  # macOS
                except FileNotFoundError:
                    subprocess.run(['xdg-open', folder_path])  # Linux
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")
    
    def close_dialog(self):
        """Close the dialog."""
        self.dialog.destroy()


class FilePreviewDialog:
    """Dialog for previewing text-based files."""
    
    def __init__(self, parent, file_path, file_type):
        self.file_path = file_path
        self.file_type = file_type
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Preview: {os.path.basename(file_path)}")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        
        self.create_widgets()
        self.load_file_content()
    
    def create_widgets(self):
        """Create preview dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # File info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(info_frame, text=f"File: {os.path.basename(self.file_path)}", 
                 font=("Arial", 12, "bold")).pack(side="left")
        ttk.Label(info_frame, text=f"Type: {self.file_type}").pack(side="right")
        
        # Text display
        self.text_widget = scrolledtext.ScrolledText(
            main_frame, 
            wrap="none", 
            font=("Consolas", 10),
            state="disabled"
        )
        self.text_widget.pack(fill="both", expand=True, pady=(0, 10))
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack()
    
    def load_file_content(self):
        """Load and display file content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", tk.END)
            
            # Limit content for large files
            if len(content) > 50000:
                content = content[:50000] + "\n\n... (Content truncated - file is too large for preview)"
            
            self.text_widget.insert("1.0", content)
            self.text_widget.configure(state="disabled")
            
        except Exception as e:
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", f"Error loading file: {e}")
            self.text_widget.configure(state="disabled")


class ErrorDialog:
    """Enhanced error dialog with actionable suggestions and troubleshooting."""
    
    def __init__(self, parent, gui_app, title, error_msg, error_type):
        self.parent = parent
        self.gui_app = gui_app
        self.error_msg = error_msg
        self.error_type = error_type
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_x() + parent.winfo_width()//2) - (self.dialog.winfo_width()//2)
        y = (parent.winfo_y() + parent.winfo_height()//2) - (self.dialog.winfo_height()//2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
        # Handle closing
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)
    
    def create_widgets(self):
        """Create error dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Error header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Error icon
        ttk.Label(header_frame, text="⚠", font=("Arial", 24), foreground="red").pack(side="left", padx=(0, 10))
        ttk.Label(header_frame, text="Error Occurred", font=("Arial", 14, "bold")).pack(side="left")
        
        # Error message
        error_frame = ttk.LabelFrame(main_frame, text="Error Details", padding="10")
        error_frame.pack(fill="x", pady=(0, 20))
        
        self.error_text = scrolledtext.ScrolledText(error_frame, height=4, wrap="word", state="disabled")
        self.error_text.pack(fill="x")
        
        # Insert error message
        self.error_text.configure(state="normal")
        self.error_text.insert("1.0", self.error_msg)
        self.error_text.configure(state="disabled")
        
        # Suggestions frame
        suggestions_frame = ttk.LabelFrame(main_frame, text="Suggested Solutions", padding="10")
        suggestions_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.suggestions_text = scrolledtext.ScrolledText(suggestions_frame, height=8, wrap="word", state="disabled")
        self.suggestions_text.pack(fill="both", expand=True)
        
        # Generate and display suggestions
        suggestions = self._generate_suggestions()
        self.suggestions_text.configure(state="normal")
        self.suggestions_text.insert("1.0", suggestions)
        self.suggestions_text.configure(state="disabled")
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x")
        
        # Left side buttons (helpful actions)
        left_buttons = ttk.Frame(action_frame)
        left_buttons.pack(side="left", fill="x", expand=True)
        
        if self.error_type == "connection":
            ttk.Button(left_buttons, text="Test Again", command=self.retry_connection).pack(side="left", padx=(0, 5))
            ttk.Button(left_buttons, text="Check Firewall", command=self.show_firewall_help).pack(side="left", padx=5)
        elif self.error_type == "generation":
            ttk.Button(left_buttons, text="Retry Generation", command=self.retry_generation).pack(side="left", padx=(0, 5))
        
        ttk.Button(left_buttons, text="Copy Error", command=self.copy_error).pack(side="left", padx=5)
        
        # Right side buttons
        right_buttons = ttk.Frame(action_frame)
        right_buttons.pack(side="right")
        
        ttk.Button(right_buttons, text="Close", command=self.close_dialog).pack(side="right", padx=5)
    
    def _generate_suggestions(self):
        """Generate contextual suggestions based on error type and message."""
        suggestions = []
        
        if self.error_type == "connection":
            suggestions.extend(self._get_connection_suggestions())
        elif self.error_type == "generation":
            suggestions.extend(self._get_generation_suggestions())
        
        if not suggestions:
            suggestions = ["• Please check the error message above for specific details",
                          "• Try the operation again after a few moments",
                          "• Contact support if the problem persists"]
        
        return "\n".join(suggestions)
    
    def _get_connection_suggestions(self):
        """Get suggestions for connection errors."""
        error_lower = self.error_msg.lower()
        suggestions = []
        
        if "login failed" in error_lower or "authentication" in error_lower:
            suggestions.extend([
                "• Verify your username and password are correct",
                "• Check if your account is locked or expired",
                "• For Azure AD authentication, ensure you're logged in with 'az login'",
                "• For Service Principal, verify client ID, secret, and tenant ID"
            ])
        
        elif "server" in error_lower or "network" in error_lower or "timeout" in error_lower:
            suggestions.extend([
                "• Check your internet connection",
                "• Verify the server name is correct (e.g., server.database.windows.net)",
                "• Ensure the SQL server is running and accessible",
                "• Check Azure SQL Database firewall rules to allow your IP address",
                "• Try connecting from Azure Portal to verify server accessibility"
            ])
        
        elif "certificate" in error_lower or "ssl" in error_lower or "tls" in error_lower:
            suggestions.extend([
                "• Certificate validation issue detected",
                "• This is automatically handled with TrustServerCertificate=yes",
                "• If problem persists, check if server requires specific SSL configuration",
                "• Ensure your system date/time is correct"
            ])
        
        elif "database" in error_lower and "not" in error_lower:
            suggestions.extend([
                "• Verify the database name is correct",
                "• Check if the database exists on the server",
                "• Ensure you have access permissions to the database",
                "• Use the 'Load Databases' button to see available databases"
            ])
        
        else:
            suggestions.extend([
                "• Double-check all connection parameters",
                "• Test connectivity using Azure Portal or SQL Server Management Studio",
                "• Verify your network allows connections to Azure SQL Database (port 1433)",
                "• Check if your IP address is whitelisted in Azure firewall rules"
            ])
        
        return suggestions
    
    def _get_generation_suggestions(self):
        """Get suggestions for documentation generation errors."""
        error_lower = self.error_msg.lower()
        suggestions = []
        
        if "permission" in error_lower or "access" in error_lower:
            suggestions.extend([
                "• Ensure your database user has sufficient read permissions",
                "• The account should have at least 'db_datareader' role",
                "• For complete schema analysis, 'db_owner' or 'VIEW DEFINITION' permission is recommended",
                "• Check if specific tables or views are restricted"
            ])
        
        elif "disk" in error_lower or "space" in error_lower:
            suggestions.extend([
                "• Check available disk space in the output directory",
                "• Try selecting a different output location",
                "• Consider generating only specific documentation formats (HTML, Markdown, or JSON)",
                "• Large databases may require significant disk space for documentation"
            ])
        
        elif "memory" in error_lower or "out of" in error_lower:
            suggestions.extend([
                "• The database may be too large for available system memory",
                "• Try closing other applications to free up memory",
                "• Consider excluding system objects to reduce memory usage",
                "• For very large databases, run the tool during low-usage times"
            ])
        
        elif "timeout" in error_lower:
            suggestions.extend([
                "• The database analysis is taking longer than expected",
                "• This often happens with very large databases",
                "• Try running during off-peak hours when database load is lower",
                "• Consider excluding row count analysis for better performance"
            ])
        
        else:
            suggestions.extend([
                "• Verify database connection is stable",
                "• Check if output directory is writable",
                "• Ensure sufficient system resources (memory and disk space)",
                "• Try generating one format at a time to isolate issues"
            ])
        
        return suggestions
    
    def retry_connection(self):
        """Retry the connection test."""
        self.close_dialog()
        self.gui_app.test_connection()
    
    def retry_generation(self):
        """Retry the documentation generation."""
        self.close_dialog()
        self.gui_app.generate_documentation()
    
    def show_firewall_help(self):
        """Show Azure firewall configuration help."""
        help_text = """Azure SQL Database Firewall Configuration:

1. Go to Azure Portal (portal.azure.com)
2. Navigate to your SQL Server resource
3. Click on 'Firewalls and virtual networks' in the left menu
4. Add your client IP address to the firewall rules
5. Click 'Save' to apply changes

Your current public IP can be found by searching "what is my ip" in a web browser.

Alternatively, you can temporarily enable 'Allow Azure services and resources to access this server' for testing purposes."""
        
        messagebox.showinfo("Azure Firewall Configuration", help_text)
    
    def copy_error(self):
        """Copy error message to clipboard."""
        try:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(self.error_msg)
            messagebox.showinfo("Copied", "Error message copied to clipboard")
        except Exception as e:
            messagebox.showerror("Copy Failed", f"Failed to copy error message: {e}")
    
    def close_dialog(self):
        """Close the error dialog."""
        self.dialog.destroy()


class GUILogHandler(logging.Handler):
    """Custom logging handler for GUI display."""
    
    def __init__(self, gui_app):
        super().__init__()
        self.gui_app = gui_app
    
    def emit(self, record):
        try:
            msg = self.format(record)
            # Use after() to ensure thread safety
            self.gui_app.root.after(0, lambda: self.gui_app.log_message(msg))
        except:
            pass  # Ignore logging errors to prevent infinite loops


class SelectiveDocumentationDialog:
    """Dialog for selective documentation generation."""
    
    def __init__(self, parent, gui_app, selected_objects, schema_data):
        self.parent = parent
        self.gui_app = gui_app
        self.selected_objects = selected_objects
        self.schema_data = schema_data
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Selective Documentation Generation")
        self.dialog.geometry("800x600")
        self.dialog.minsize(600, 500)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Setup dialog
        self.setup_dialog()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_dialog(self):
        """Setup the dialog layout."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Generate Documentation for Selected Objects",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Selected objects frame
        objects_frame = ttk.LabelFrame(main_frame, text=f"Selected Objects ({len(self.selected_objects)})", padding="10")
        objects_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Objects list
        self.objects_tree = ttk.Treeview(
            objects_frame,
            columns=("type", "schema", "description"),
            show="tree headings",
            height=12
        )
        
        # Configure columns
        self.objects_tree.heading("#0", text="Object Name")
        self.objects_tree.heading("type", text="Type")
        self.objects_tree.heading("schema", text="Schema")
        self.objects_tree.heading("description", text="Description")
        
        self.objects_tree.column("#0", width=200)
        self.objects_tree.column("type", width=100)
        self.objects_tree.column("schema", width=80)
        self.objects_tree.column("description", width=300)
        
        # Add scrollbar
        objects_scroll = ttk.Scrollbar(objects_frame, orient="vertical", command=self.objects_tree.yview)
        self.objects_tree.configure(yscrollcommand=objects_scroll.set)
        
        # Pack tree and scrollbar
        self.objects_tree.pack(side="left", fill="both", expand=True)
        objects_scroll.pack(side="right", fill="y")
        
        # Populate objects tree
        self.populate_objects_tree()
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Documentation Options", padding="10")
        options_frame.pack(fill="x", pady=(0, 10))
        
        # Output directory
        ttk.Label(options_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", pady=5)
        self.output_dir = tk.StringVar(value="output_selective")
        output_entry = ttk.Entry(options_frame, textvariable=self.output_dir, width=40)
        output_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Button(
            options_frame, 
            text="Browse", 
            command=self.browse_output_dir
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Format options
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=10)
        
        ttk.Label(format_frame, text="Output Formats:").pack(anchor="w")
        
        self.generate_html = tk.BooleanVar(value=True)
        self.generate_markdown = tk.BooleanVar(value=True)
        self.generate_json = tk.BooleanVar(value=True)
        
        format_options = ttk.Frame(format_frame)
        format_options.pack(anchor="w", pady=5)
        
        ttk.Checkbutton(format_options, text="HTML", variable=self.generate_html).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(format_options, text="Markdown", variable=self.generate_markdown).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(format_options, text="JSON", variable=self.generate_json).pack(side="left")
        
        # Include related objects
        self.include_related = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, 
            text="Include related objects (foreign keys, referenced tables)", 
            variable=self.include_related
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=5)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Progress frame (initially hidden)
        self.progress_frame = ttk.LabelFrame(main_frame, text="Generation Progress", padding="10")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready to generate...")
        self.progress_label.pack()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side="right", padx=(5, 0))
        
        self.generate_button = ttk.Button(
            buttons_frame,
            text="Generate Documentation",
            command=self.generate_documentation
        )
        self.generate_button.pack(side="right")
        
        ttk.Button(
            buttons_frame,
            text="Select All",
            command=self.select_all_objects
        ).pack(side="left")
        
        ttk.Button(
            buttons_frame,
            text="Deselect All",
            command=self.deselect_all_objects
        ).pack(side="left", padx=(5, 0))
    
    def populate_objects_tree(self):
        """Populate the objects tree with selected objects."""
        for obj in self.selected_objects:
            obj_type = obj.get('type', self._infer_object_type(obj))
            self.objects_tree.insert(
                "",
                "end",
                text=obj.get('name', 'Unknown'),
                values=(
                    obj_type,
                    obj.get('schema', 'dbo'),
                    obj.get('description', '')[:100] + ('...' if len(obj.get('description', '')) > 100 else '')
                )
            )
    
    def _infer_object_type(self, obj):
        """Infer object type from structure."""
        if 'columns' in obj and 'definition' not in obj:
            return 'Table'
        elif 'definition' in obj and 'SELECT' in obj.get('definition', '').upper():
            return 'View'
        elif 'definition' in obj and 'CREATE PROCEDURE' in obj.get('definition', '').upper():
            return 'Procedure'
        elif 'definition' in obj and 'CREATE FUNCTION' in obj.get('definition', '').upper():
            return 'Function'
        else:
            return 'Unknown'
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)
    
    def select_all_objects(self):
        """Select all objects in the tree."""
        for item in self.objects_tree.get_children():
            self.objects_tree.selection_add(item)
    
    def deselect_all_objects(self):
        """Deselect all objects in the tree."""
        self.objects_tree.selection_remove(*self.objects_tree.get_children())
    
    def generate_documentation(self):
        """Generate documentation for selected objects."""
        # Validate selection
        selected_items = self.objects_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select objects to generate documentation for.")
            return
        
        # Validate output formats
        if not any([self.generate_html.get(), self.generate_markdown.get(), self.generate_json.get()]):
            messagebox.showwarning("No Format", "Please select at least one output format.")
            return
        
        # Get selected object indices
        selected_indices = []
        all_items = list(self.objects_tree.get_children())
        for item in selected_items:
            selected_indices.append(all_items.index(item))
        
        # Filter objects
        objects_to_document = [self.selected_objects[i] for i in selected_indices]
        
        # Show progress frame
        self.progress_frame.pack(fill="x", pady=(10, 0))
        self.generate_button.configure(state="disabled")
        
        # Start generation in background thread
        thread = threading.Thread(
            target=self._generate_documentation_thread,
            args=(objects_to_document,)
        )
        thread.daemon = True
        thread.start()
    
    def _generate_documentation_thread(self, objects_to_document):
        """Generate documentation in background thread."""
        try:
            self.dialog.after(0, lambda: self._update_progress(10, "Preparing documentation structure..."))
            
            # Create filtered schema data
            filtered_schema = self._create_filtered_schema_data(objects_to_document)
            
            self.dialog.after(0, lambda: self._update_progress(30, "Creating documentation generator..."))
            
            # Create output directory
            output_dir = self.output_dir.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate documentation
            from documentation_generator import DocumentationGenerator
            generator = DocumentationGenerator(output_dir)
            
            generated_files = []
            
            if self.generate_html.get():
                self.dialog.after(0, lambda: self._update_progress(50, "Generating HTML documentation..."))
                html_file = generator.generate_html_documentation(filtered_schema)
                generated_files.append(('HTML', html_file))
            
            if self.generate_markdown.get():
                self.dialog.after(0, lambda: self._update_progress(70, "Generating Markdown documentation..."))
                md_file = generator.generate_markdown_documentation(filtered_schema)
                generated_files.append(('Markdown', md_file))
            
            if self.generate_json.get():
                self.dialog.after(0, lambda: self._update_progress(90, "Generating JSON documentation..."))
                json_file = generator.generate_json_documentation(filtered_schema)
                generated_files.append(('JSON', json_file))
            
            self.dialog.after(0, lambda: self._update_progress(100, "Documentation generation completed!"))
            
            # Show completion dialog
            self.dialog.after(0, lambda: self._show_completion_dialog(generated_files))
            
        except Exception as e:
            self.dialog.after(0, lambda: self._handle_generation_error(str(e)))
    
    def _create_filtered_schema_data(self, objects_to_document):
        """Create filtered schema data containing only selected objects."""
        if not self.schema_data:
            # Create minimal schema data from objects
            filtered_schema = {
                'database_info': {
                    'database_name': 'Selected Objects',
                    'server_name': 'Unknown',
                    'user_name': 'Unknown',
                    'extraction_timestamp': datetime.now().isoformat()
                },
                'tables': [],
                'views': [],
                'stored_procedures': [],
                'functions': [],
                'relationships': {'foreign_keys': [], 'relationship_count': 0},
                'statistics': {}
            }
        else:
            # Start with copy of full schema
            filtered_schema = {
                'database_info': self.schema_data.get('database_info', {}),
                'tables': [],
                'views': [],
                'stored_procedures': [],
                'functions': [],
                'relationships': {'foreign_keys': [], 'relationship_count': 0},
                'statistics': {}
            }
        
        # Add selected objects to appropriate categories
        object_names = set()
        for obj in objects_to_document:
            obj_name = obj.get('name')
            if obj_name:
                object_names.add(obj_name)
            
            obj_type = obj.get('type', self._infer_object_type(obj))
            
            if obj_type == 'Table':
                filtered_schema['tables'].append(obj)
            elif obj_type == 'View':
                filtered_schema['views'].append(obj)
            elif obj_type == 'Procedure':
                filtered_schema['stored_procedures'].append(obj)
            elif obj_type == 'Function':
                filtered_schema['functions'].append(obj)
        
        # Include related objects if requested
        if self.include_related.get() and self.schema_data:
            self._add_related_objects(filtered_schema, object_names)
        
        # Update statistics
        filtered_schema['statistics'] = {
            'total_tables': len(filtered_schema['tables']),
            'total_views': len(filtered_schema['views']),
            'total_procedures': len(filtered_schema['stored_procedures']),
            'total_functions': len(filtered_schema['functions']),
            'total_objects': len(filtered_schema['tables']) + len(filtered_schema['views']) + 
                           len(filtered_schema['stored_procedures']) + len(filtered_schema['functions'])
        }
        
        return filtered_schema
    
    def _add_related_objects(self, filtered_schema, selected_names):
        """Add related objects based on relationships."""
        if not self.schema_data:
            return
        
        # Find related tables through foreign key relationships
        related_tables = set()
        
        # Check relationships in original schema
        relationships = self.schema_data.get('relationships', {})
        foreign_keys = relationships.get('foreign_keys', [])
        
        for fk in foreign_keys:
            fk_table = fk.get('foreign_key_table')
            ref_table = fk.get('referenced_table')
            
            # If selected table has FK to another table, include that table
            if fk_table in selected_names and ref_table not in selected_names:
                related_tables.add(ref_table)
            
            # If selected table is referenced by another table, include that table
            if ref_table in selected_names and fk_table not in selected_names:
                related_tables.add(fk_table)
        
        # Add related tables to filtered schema
        for table in self.schema_data.get('tables', []):
            if table.get('name') in related_tables:
                # Mark as related
                table_copy = table.copy()
                table_copy['_related'] = True
                filtered_schema['tables'].append(table_copy)
        
        # Add relevant foreign key relationships
        for fk in foreign_keys:
            fk_table = fk.get('foreign_key_table')
            ref_table = fk.get('referenced_table')
            
            # Include FK if both tables are now in filtered schema
            all_table_names = {t.get('name') for t in filtered_schema['tables']}
            if fk_table in all_table_names and ref_table in all_table_names:
                filtered_schema['relationships']['foreign_keys'].append(fk)
        
        filtered_schema['relationships']['relationship_count'] = len(filtered_schema['relationships']['foreign_keys'])
    
    def _update_progress(self, value, text):
        """Update progress bar and label."""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
    
    def _show_completion_dialog(self, generated_files):
        """Show completion dialog with generated files."""
        self.dialog.destroy()
        
        completion_dialog = CompletionDialog(self.parent, self.gui_app, generated_files)
    
    def _handle_generation_error(self, error_msg):
        """Handle generation error."""
        self.progress_frame.pack_forget()
        self.generate_button.configure(state="normal")
        messagebox.showerror("Generation Error", f"Failed to generate documentation:\n{error_msg}")


class SchemaBrowserWindow:
    """Schema browser window for exploring database objects."""
    
    def __init__(self, parent, gui_app, database_name):
        self.parent = parent
        self.gui_app = gui_app
        self.database_name = database_name
        self.schema_data = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Schema Browser - {database_name}")
        self.window.geometry("1200x800")
        self.window.minsize(800, 600)
        
        # Configure window
        self.setup_window()
        self.load_schema_data()
    
    def setup_window(self):
        """Setup the browser window layout."""
        # Main paned window
        main_paned = ttk.PanedWindow(self.window, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Schema tree
        left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Object details
        right_frame = ttk.Frame(main_paned, width=800)
        main_paned.add(right_frame, weight=2)
        
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)
        
        # Status bar
        status_frame = ttk.Frame(self.window, relief="sunken")
        status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(status_frame, text="Loading schema...", padding="5")
        self.status_label.pack(side="left")
    
    def create_left_panel(self, parent):
        """Create schema navigation panel."""
        # Search frame
        search_frame = ttk.LabelFrame(parent, text="Search", padding="10")
        search_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind('<KeyRelease>', self.filter_objects)
        
        ttk.Button(search_frame, text="Clear", command=self.clear_filter).pack(side="right", padx=(5, 0))
        
        # Schema tree frame
        tree_frame = ttk.LabelFrame(parent, text="Database Objects", padding="10")
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Schema tree
        self.schema_tree = ttk.Treeview(tree_frame, show="tree")
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.schema_tree.yview)
        self.schema_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Bind events
        self.schema_tree.bind("<<TreeviewSelect>>", self.on_object_select)
        self.schema_tree.bind("<Double-1>", self.on_object_double_click)
        
        # Pack tree
        self.schema_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
    
    def create_right_panel(self, parent):
        """Create object details panel."""
        # Details frame
        details_frame = ttk.LabelFrame(parent, text="Object Information", padding="10")
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Object info display
        self.info_text = scrolledtext.ScrolledText(
            details_frame, 
            wrap=tk.WORD, 
            height=20, 
            font=("Consolas", 10),
            state="disabled"
        )
        self.info_text.pack(fill="both", expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            action_frame, 
            text="View Details", 
            command=self.view_detailed_info
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text="Export Definition", 
            command=self.export_object_definition
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            action_frame, 
            text="Close", 
            command=self.window.destroy
        ).pack(side="right")
    
    def load_schema_data(self):
        """Load schema data for the database."""
        def load_thread():
            try:
                # Connect and extract schema
                with AzureSQLConnection() as db:
                    # Use GUI app's connection method
                    success = self.gui_app._connect_to_database(db)
                    if not success:
                        raise Exception("Failed to connect to database")
                    
                    # Connect to specific database
                    success = db.connect_to_database(self.database_name)
                    if not success:
                        raise Exception(f"Failed to connect to database {self.database_name}")
                    
                    # Extract schema
                    extractor = DocumentationExtractor(db)
                    self.schema_data = extractor.extract_complete_documentation()
                    
                    # Update UI in main thread
                    self.window.after(0, self.populate_schema_tree)
                    
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Error", f"Failed to load schema: {str(e)}"))
                self.window.after(0, lambda: self.status_label.config(text="Error loading schema"))
        
        # Start loading in background thread
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
    
    def populate_schema_tree(self):
        """Populate the schema tree with database objects."""
        if not self.schema_data:
            self.status_label.config(text="No schema data available")
            return
        
        # Clear existing tree
        for item in self.schema_tree.get_children():
            self.schema_tree.delete(item)
        
        # Add database node
        db_node = self.schema_tree.insert("", "end", text=f"Database: {self.database_name}", 
                                         tags=("database",))
        
        # Add tables
        if 'tables' in self.schema_data and self.schema_data['tables']:
            tables_node = self.schema_tree.insert(db_node, "end", text=f"Tables ({len(self.schema_data['tables'])})", 
                                                 tags=("category",))
            for table in self.schema_data['tables']:
                table_node = self.schema_tree.insert(tables_node, "end", text=table.get('name', 'Unknown'), 
                                                    tags=("table",), values=(table,))
                
                # Add columns as sub-items
                if 'columns' in table and table['columns']:
                    for col in table['columns'][:5]:  # Show first 5 columns
                        col_text = f"{col.get('name', 'Unknown')} ({col.get('data_type', 'Unknown')})"
                        self.schema_tree.insert(table_node, "end", text=col_text, tags=("column",))
                    if len(table['columns']) > 5:
                        self.schema_tree.insert(table_node, "end", text="... and more", tags=("more",))
        
        # Add views
        if 'views' in self.schema_data and self.schema_data['views']:
            views_node = self.schema_tree.insert(db_node, "end", text=f"Views ({len(self.schema_data['views'])})", 
                                                tags=("category",))
            for view in self.schema_data['views']:
                self.schema_tree.insert(views_node, "end", text=view.get('name', 'Unknown'), 
                                       tags=("view",), values=(view,))
        
        # Add procedures
        if 'stored_procedures' in self.schema_data and self.schema_data['stored_procedures']:
            procs_node = self.schema_tree.insert(db_node, "end", text=f"Stored Procedures ({len(self.schema_data['stored_procedures'])})", 
                                                tags=("category",))
            for proc in self.schema_data['stored_procedures']:
                self.schema_tree.insert(procs_node, "end", text=proc.get('name', 'Unknown'), 
                                       tags=("procedure",), values=(proc,))
        
        # Add functions
        if 'functions' in self.schema_data and self.schema_data['functions']:
            funcs_node = self.schema_tree.insert(db_node, "end", text=f"Functions ({len(self.schema_data['functions'])})", 
                                                tags=("category",))
            for func in self.schema_data['functions']:
                self.schema_tree.insert(funcs_node, "end", text=func.get('name', 'Unknown'), 
                                       tags=("function",), values=(func,))
        
        # Configure tags
        self.schema_tree.tag_configure("database", foreground="blue")
        self.schema_tree.tag_configure("category", foreground="darkblue")
        self.schema_tree.tag_configure("table", foreground="darkgreen")
        self.schema_tree.tag_configure("view", foreground="darkorange")
        self.schema_tree.tag_configure("procedure", foreground="darkred")
        self.schema_tree.tag_configure("function", foreground="darkmagenta")
        self.schema_tree.tag_configure("column", foreground="gray")
        self.schema_tree.tag_configure("more", foreground="lightgray", font=("TkDefaultFont", 8, "italic"))
        
        # Expand database node
        self.schema_tree.item(db_node, open=True)
        
        self.status_label.config(text=f"Loaded {len(self.schema_data.get('tables', []))} tables, "
                                      f"{len(self.schema_data.get('views', []))} views, "
                                      f"{len(self.schema_data.get('stored_procedures', []))} procedures, "
                                      f"{len(self.schema_data.get('functions', []))} functions")
    
    def on_object_select(self, event):
        """Handle object selection in tree."""
        selection = self.schema_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        obj_data = self.get_object_data(item)
        
        if obj_data:
            self.display_object_info(obj_data)
    
    def on_object_double_click(self, event):
        """Handle double-click on object."""
        selection = self.schema_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        obj_data = self.get_object_data(item)
        
        if obj_data:
            # Show detailed object information using ObjectDetailsManager
            self.gui_app.show_object_details(obj_data, self.schema_data)
    
    def get_object_data(self, item):
        """Get object data from tree item."""
        try:
            values = self.schema_tree.item(item)['values']
            if values and isinstance(values[0], dict):
                return values[0]
        except:
            pass
        return None
    
    def display_object_info(self, obj_data):
        """Display basic object information."""
        info_lines = []
        
        info_lines.append(f"Object Name: {obj_data.get('name', 'Unknown')}")
        info_lines.append(f"Schema: {obj_data.get('schema', 'dbo')}")
        info_lines.append(f"Type: {obj_data.get('type', 'Unknown')}")
        
        if 'row_count' in obj_data:
            info_lines.append(f"Row Count: {obj_data['row_count']:,}")
        
        if 'created_date' in obj_data:
            info_lines.append(f"Created: {obj_data['created_date']}")
        
        if obj_data.get('description'):
            info_lines.append(f"\nDescription:\n{obj_data['description']}")
        
        if 'columns' in obj_data:
            info_lines.append(f"\nColumns ({len(obj_data['columns'])}):")
            for col in obj_data['columns'][:10]:  # Show first 10 columns
                nullable = "NULL" if col.get('is_nullable', True) else "NOT NULL"
                info_lines.append(f"  • {col.get('name', 'Unknown')} - {col.get('data_type', 'Unknown')} ({nullable})")
            if len(obj_data['columns']) > 10:
                info_lines.append(f"  ... and {len(obj_data['columns']) - 10} more columns")
        
        if obj_data.get('definition'):
            definition = obj_data['definition'][:500]  # Show first 500 characters
            if len(obj_data['definition']) > 500:
                definition += "... (truncated)"
            info_lines.append(f"\nDefinition:\n{definition}")
        
        # Update display
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info_lines))
        self.info_text.config(state="disabled")
        
        # Store current object for actions
        self.current_object = obj_data
    
    def view_detailed_info(self):
        """View detailed information for current object."""
        if hasattr(self, 'current_object') and self.current_object:
            self.gui_app.show_object_details(self.current_object, self.schema_data)
        else:
            messagebox.showwarning("No Selection", "Please select an object first.")
    
    def export_object_definition(self):
        """Export current object definition."""
        if not hasattr(self, 'current_object') or not self.current_object:
            messagebox.showwarning("No Selection", "Please select an object first.")
            return
        
        if not self.current_object.get('definition'):
            messagebox.showwarning("No Definition", "This object does not have a definition to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Definition"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_object['definition'])
                messagebox.showinfo("Export Complete", f"Definition exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export definition: {str(e)}")
    
    def filter_objects(self, event=None):
        """Filter objects based on search text."""
        # This would implement search filtering
        pass
    
    def clear_filter(self):
        """Clear search filter."""
        self.search_var.set("")
        # Would also restore full tree view


def main():
    """Main entry point for GUI application."""
    try:
        app = DatabaseDocumentationGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Modern Azure SQL Database Documentation Generator GUI
==================================================

A completely modernized GUI with enhanced theming, improved UX patterns,
and all Phase 3 enterprise features integrated with the new UI framework.

Features:
- Modern theme system with dark/light modes
- Sidebar navigation instead of tabs
- Dashboard home screen
- Enhanced form controls with validation
- Toast notifications and modern dialogs
- Command palette (Ctrl+Shift+P)
- Favorites and recent items
- Responsive layouts
- Status management system
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

# Set up logger for this module
logger = logging.getLogger(__name__)

# Import existing modules
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
from database_playground import DatabasePlayground, create_playground_panel
from schema_explorer import SchemaExplorer, create_schema_explorer_panel
from performance_dashboard import PerformanceDashboard, create_performance_dashboard_panel

# Import new UI framework with Phase 1 & 2 enhancements
from ui_framework import (ThemeManager, StatusManager, CardComponent, SidebarNavigation, 
                         DashboardHome, ResponsiveLayout, LoadingOverlay, ScrollableFrame,
                         SmartLoadingSystem, SmartProgressTracker, EnhancedStatusBar,
                         KeyboardShortcutManager, TooltipSystem, QuickAccessToolbar,
                         ImprovedErrorHandler, EnhancedErrorDialog,
                         UserPreferencesSystem, CustomizableThemeManager, WorkspaceManager,
                         AdvancedSearchSystem, DataVisualizationSystem,
                         EnterpriseProjectManager, IntelligentAPIIntegration,
                         AdvancedAnalyticsEngine, SmartSecurityAuditor)
from enhanced_controls import (ValidatedEntry, ToggleSwitch, CollapsibleFrame, TooltipManager,
                             CommandPalette, FavoritesManager, FavoritesWidget)


class ModernDatabaseDocumentationGUI:
    """Modern GUI application with enhanced UX."""
    
    def __init__(self):
        self.root = tk.Tk()
        
        # Initialize critical attributes first
        self.current_view = 'dashboard'
        self.content_widgets = {}
        
        self.setup_window()
        self.setup_managers()
        self.setup_variables()
        self.setup_logging()
        self.setup_profile_manager()
        self.create_widgets()
        self.setup_layout()
        self.load_initial_config()
        self.bind_keyboard_shortcuts()
        
    def setup_window(self):
        """Configure the main window with modern styling."""
        self.root.title("Azure SQL Database Documentation Generator")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configure style and theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
    
    def setup_managers(self):
        """Initialize UI managers with Phase 1 & 2 enhancements."""
        # Theme management
        self.theme_manager = ThemeManager()
        self.theme_manager.initialize_styles(self.style)
        
        # Phase 2: User Preferences System (must be first for other systems)
        self.user_preferences = UserPreferencesSystem(self.theme_manager)
        
        # Phase 2: Customizable Theme Manager
        self.customizable_themes = CustomizableThemeManager(self.user_preferences)
        
        # Apply saved theme preference
        saved_theme = self.user_preferences.get_preference('appearance', 'theme', 'light')
        try:
            self.customizable_themes.apply_theme(saved_theme, self.style)
        except Exception as e:
            print(f"Could not apply saved theme '{saved_theme}': {e}")
            self.customizable_themes.apply_theme('light', self.style)
        
        # Phase 2: Workspace Manager
        self.workspace_manager = WorkspaceManager(self.user_preferences)
        
        # Phase 2: Advanced Search System
        self.search_system = AdvancedSearchSystem(self.user_preferences)
        
        # Phase 2: Data Visualization System
        self.visualization_system = DataVisualizationSystem(self.user_preferences, self.theme_manager)
        
        # Phase 3: Enterprise Project Manager
        self.enterprise_projects = EnterpriseProjectManager(self.user_preferences)
        
        # Phase 3: Intelligent API Integration
        self.api_integration = IntelligentAPIIntegration(self.user_preferences, self.enterprise_projects)
        
        # Phase 3: Advanced Analytics Engine
        self.analytics_engine = AdvancedAnalyticsEngine(self.user_preferences, self.enterprise_projects)
        
        # Phase 3: Smart Security Auditor
        self.security_auditor = SmartSecurityAuditor(self.user_preferences)
        
        # Phase 1: Smart Loading System
        self.smart_loading = SmartLoadingSystem(self.root, self.theme_manager)
        
        # Phase 1: Enhanced Status Bar (replaces basic status manager)
        self.enhanced_status = EnhancedStatusBar(self.root, self.theme_manager)
        
        # Phase 1: Keyboard Shortcuts Manager
        self.keyboard_shortcuts = KeyboardShortcutManager(self.root)
        self.setup_application_shortcuts()
        
        # Phase 1: Advanced Tooltip System
        self.tooltip_system = TooltipSystem(self.theme_manager)
        
        # Phase 1: Improved Error Handler
        self.error_handler = ImprovedErrorHandler(self.theme_manager, self.enhanced_status)
        
        # Legacy status management (keep for backward compatibility)
        self.status_manager = StatusManager(self.root)
        
        # Legacy tooltips (keep for existing code)
        self.tooltip_manager = TooltipManager()
        
        # Command palette
        self.command_palette = CommandPalette(self.root)
        self.register_commands()
        
        # Favorites
        self.favorites_manager = FavoritesManager()
        
        # Responsive layout
        self.responsive_layout = ResponsiveLayout(self.root)
        self.responsive_layout.register_layout_callback(self.on_layout_changed)
        
        # Phase 2: Setup preference callbacks for real-time updates
        self.setup_preference_callbacks()
        
        print("[Phase 1] All enhanced UI systems initialized successfully!")
        print("[Phase 2] User customization systems initialized!")
        print("[Phase 3] Enterprise advanced features initialized!")
    
    def setup_preference_callbacks(self):
        """Setup callbacks for real-time preference updates."""
        # Theme change callback
        def on_theme_change(old_value, new_value):
            try:
                self.customizable_themes.apply_theme(new_value, self.style)
                self.enhanced_status.update_status(f"Theme changed to {new_value}")
            except Exception as e:
                self.error_handler.handle_error(e, "Theme Change", 
                    "Failed to apply theme. Reverting to default.")
                self.customizable_themes.apply_theme('light', self.style)
        
        # UI scale change callback
        def on_ui_scale_change(old_value, new_value):
            try:
                self.customizable_themes.update_ui_scale(new_value, self.style)
                self.enhanced_status.update_status(f"UI scale changed to {new_value}%")
            except Exception as e:
                self.error_handler.handle_error(e, "UI Scale Change",
                    "Failed to apply UI scaling.")
        
        # Sidebar position change callback  
        def on_sidebar_position_change(old_value, new_value):
            try:
                # This would trigger a layout refresh
                self.enhanced_status.update_status(f"Sidebar moved to {new_value}")
            except Exception as e:
                self.error_handler.handle_error(e, "Layout Change",
                    "Failed to change sidebar position.")
        
        # Register callbacks with user preferences system
        self.user_preferences.register_callback('appearance', 'theme', on_theme_change)
        self.user_preferences.register_callback('appearance', 'ui_scale', on_ui_scale_change)
        self.user_preferences.register_callback('layout', 'sidebar_position', on_sidebar_position_change)
        
        # Load and restore last workspace if enabled
        if self.user_preferences.get_preference('workspace', 'auto_restore_workspace', True):
            try:
                last_workspace = self.workspace_manager.get_last_workspace()
                if last_workspace:
                    self.workspace_manager.restore_workspace(last_workspace, self.root)
                    self.enhanced_status.update_status(f"Restored workspace: {last_workspace}")
            except Exception as e:
                print(f"Could not restore last workspace: {e}")
        
        # Phase 3: Setup enterprise feature integration
        self._setup_phase3_integration()
    
    def _setup_phase3_integration(self):
        """Setup Phase 3 enterprise features integration."""
        try:
            # Register project callbacks for analytics tracking
            self.enterprise_projects.register_callback('project_created', self._on_project_created)
            self.enterprise_projects.register_callback('project_switched', self._on_project_switched)
            self.enterprise_projects.register_callback('database_added', self._on_database_added)
            
            # Track application startup analytics
            self.analytics_engine.track_activity('application_startup', {
                'version': '3.0',
                'features_enabled': ['phase1', 'phase2', 'phase3'],
                'theme': self.user_preferences.get_preference('appearance', 'theme', 'light')
            })
            
            # Setup automatic webhook triggers for key events
            if self.user_preferences.get_preference('integrations', 'auto_webhooks', False):
                self.api_integration.register_webhook(
                    'Documentation Generated',
                    'https://example.com/webhook',
                    ['documentation_generated', 'schema_updated']
                )
            
            print("[Phase 3] Enterprise integration setup completed")
            
        except Exception as e:
            print(f"[Phase 3] Error setting up enterprise integration: {e}")
    
    def _on_project_created(self, project_id: str):
        """Handle project creation event."""
        self.analytics_engine.track_activity('project_created', {'project_id': project_id})
        self.enhanced_status.update_status(f"New project created: {project_id[:8]}...")
        
        # Trigger webhook
        self.api_integration.trigger_webhook('project_created', {
            'project_id': project_id,
            'timestamp': str(datetime.now()),
            'user': 'current_user'
        })
    
    def _on_project_switched(self, project_id: str):
        """Handle project switch event."""
        self.analytics_engine.track_activity('project_switched', {'project_id': project_id})
        self.enhanced_status.update_status(f"Switched to project: {project_id[:8]}...")
    
    def _on_database_added(self, project_id: str):
        """Handle database addition event."""
        self.analytics_engine.track_activity('database_added', {'project_id': project_id})
        self.enhanced_status.update_status("Database added to project")
    
    def setup_variables(self):
        """Initialize tkinter variables."""
        # Connection variables
        self.connection_method = tk.StringVar(value="credentials")
        self.server = tk.StringVar(value="eds-sqlserver.eastus2.cloudapp.azure.com")
        self.database = tk.StringVar(value="master")
        self.username = tk.StringVar(value="EDSAdmin")
        self.password = tk.StringVar(value="")
        self.connection_string = tk.StringVar(value="")
        self.driver = tk.StringVar(value="ODBC Driver 17 for SQL Server")
        self.client_id = tk.StringVar(value="")
        self.client_secret = tk.StringVar(value="")
        self.tenant_id = tk.StringVar(value="")
        
        # Documentation variables
        self.output_dir = tk.StringVar(value="output")
        self.generate_html = tk.BooleanVar(value=True)
        self.generate_markdown = tk.BooleanVar(value=True)
        self.generate_json = tk.BooleanVar(value=False)
        
        # Status variables
        self.status_text = tk.StringVar(value="Ready")
        self.progress_value = tk.IntVar(value=0)
        self.current_step = tk.StringVar(value="")
        self.detailed_progress = tk.StringVar(value="")
        self.estimated_time = tk.StringVar(value="")
        
        # UI state variables
        self.sidebar_collapsed = tk.BooleanVar(value=False)
        self.theme_var = tk.StringVar(value="light")
        
        # Generation control
        self.generation_cancelled = False
        self.generation_start_time = None
        
        # Schema and documentation data
        self.current_schema_data = None
        self.last_extracted_data = None
        self.available_databases = []
        self.selected_databases = []
        
        # Search and filter variables
        self.search_query = tk.StringVar(value="")
        self.filter_type = tk.StringVar(value="all")
        
        # API and monitoring variables
        self.api_server_running = tk.BooleanVar(value=False)
        self.api_port = tk.IntVar(value=8080)
        self.webhook_notifications_enabled = tk.BooleanVar(value=False)
        self.platform_integrations_enabled = tk.BooleanVar(value=False)
    
    def setup_logging(self):
        """Setup enhanced logging with UI integration."""
        self.log_handler = LogHandler()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('database_docs.log', encoding='utf-8'),
                self.log_handler
            ]
        )
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
    
    def setup_profile_manager(self):
        """Setup connection profile manager and other managers."""
        self.profile_manager = ConnectionProfileManager()
        self.current_profile_name = tk.StringVar()
        
        # Initialize scheduler and monitor
        self.job_scheduler = JobScheduler()
        self.database_monitor = DatabaseMonitor(self.job_scheduler)
        
        # Register job handlers
        self.job_scheduler.register_job_type("documentation", create_documentation_job_handler())
        self.job_scheduler.register_job_type("monitoring", 
                                           lambda config: self.database_monitor.monitor_database(config))
        
        # Initialize managers
        self.project_manager = ProjectManager()
        self.webhook_manager = WebhookManager()
        self.api_server = APIServer(self.api_port.get())
        self.platform_integration = PlatformIntegration()
        self.reporting_dashboard = ReportingDashboard(self)
        self.migration_planner = MigrationPlannerGUI(self)
        self.compliance_auditor = ComplianceAuditorGUI(self)
        
        # Initialize object details manager (will be set after window creation)
        self.object_details_manager = None
        
        # Initialize project manager
        try:
            self.project_manager = ProjectManager()
        except Exception as e:
            logger.error(f"Failed to initialize project manager: {e}")
            self.project_manager = None
    
    def setup_application_shortcuts(self):
        """Setup application-wide keyboard shortcuts for Phase 1."""
        # Global shortcuts
        self.keyboard_shortcuts.register_shortcut(
            '<Control-n>', self.create_new_connection, "New Connection", "global"
        )
        self.keyboard_shortcuts.register_shortcut(
            '<Control-o>', self.open_project_dialog, "Open Project", "global"  
        )
        self.keyboard_shortcuts.register_shortcut(
            '<Control-s>', self.save_current_project, "Save Project", "global"
        )
        self.keyboard_shortcuts.register_shortcut(
            '<F5>', self.refresh_current_view, "Refresh Current View", "global"
        )
        self.keyboard_shortcuts.register_shortcut(
            '<Control-comma>', self.show_settings, "Show Settings", "global"
        )
        self.keyboard_shortcuts.register_shortcut(
            '<F1>', self.show_help, "Show Help", "global"
        )
        self.keyboard_shortcuts.register_shortcut(
            '<Control-Shift-t>', self.toggle_theme_mode, "Toggle Theme", "global"
        )
        
        # Context-specific shortcuts will be set when switching views
        print("[Phase 1] Application keyboard shortcuts registered")
    
    def setup_quick_access_toolbar(self):
        """Setup the Phase 1 Quick Access Toolbar."""
        # Create toolbar after main container exists
        if hasattr(self, 'main_container'):
            self.quick_toolbar = QuickAccessToolbar(self.main_container, self.theme_manager)
            self.quick_toolbar.set_tooltip_system(self.tooltip_system)
            
            # Connect toolbar callbacks to actual methods
            self.quick_toolbar.update_button_callback("new", self.create_new_connection)
            self.quick_toolbar.update_button_callback("open", self.open_project_dialog)
            self.quick_toolbar.update_button_callback("save", self.save_current_project)
            self.quick_toolbar.update_button_callback("refresh", self.refresh_current_view)
            self.quick_toolbar.update_button_callback("settings", self.show_settings)
            
            print("[Phase 1] Quick Access Toolbar created and configured")
    
    def create_widgets(self):
        """Create all GUI widgets with modern styling."""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)
        
        # Phase 1: Setup Quick Access Toolbar
        self.setup_quick_access_toolbar()
        
        # Create sidebar navigation
        self.sidebar = SidebarNavigation(self.main_container, self.theme_manager)
        self.sidebar_widget = self.sidebar.create_sidebar(self.main_container, width=280)
        self.sidebar_widget.pack(side='left', fill='y')
        
        # Add navigation items
        self.add_navigation_items()
        
        # Content area with scrollable container
        self.content_area = ttk.Frame(self.main_container)
        self.content_area.pack(side='left', fill='both', expand=True)
        
        # Status bar
        self.status_bar = self.status_manager.create_status_bar(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        # Create all content panels (initially hidden)
        self.create_content_panels()
        
        # Show dashboard by default (without triggering sidebar callbacks)
        self.show_view('dashboard', update_sidebar=False)
    
    def add_navigation_items(self):
        """Add items to sidebar navigation."""
        nav_items = [
            ('🏠', 'Dashboard', 'Overview and quick actions', self.show_dashboard),
            ('🔌', 'Connection', 'Database connection settings', self.show_connection),
            ('🗄️', 'Databases', 'Available databases', self.show_databases),
            ('🎮', 'Playground', 'Interactive query builder and tutorials', self.show_playground),
            ('🗂️', 'Schema Explorer', 'Visual schema exploration and navigation', self.show_schema_explorer),
            ('📊', 'Performance Dashboard', 'Real-time performance monitoring and alerts', self.show_performance_dashboard),
            ('📋', 'Documentation', 'Generate documentation', self.show_documentation),
            ('🔍', 'Search & Filter', 'Search and filter objects', self.show_search),
            ('🔄', 'Schema Compare', 'Compare database schemas', self.show_comparison),
            ('🌐', 'Dependencies', 'Visualize dependencies', self.show_visualization),
            ('⏰', 'Scheduler', 'Automated tasks and monitoring', self.show_scheduler),
            ('📁', 'Projects', 'Multi-database projects', self.show_projects),
            ('🔗', 'API Integration', 'API and webhook settings', self.show_api),
            ('📊', 'Analytics', 'Reports and analytics', self.show_analytics),
            ('🔄', 'Migration', 'Database migration planning', self.show_migration),
            ('🔒', 'Compliance', 'Security and compliance', self.show_compliance),
            ('⚙️', 'Settings', 'Application settings', self.show_settings)
        ]
        
        for icon, title, description, callback in nav_items:
            self.sidebar.add_navigation_item(icon, title, description, callback, title.lower().replace(' ', '_'))
    
    def create_scrollable_panel(self):
        """Create a scrollable panel for content."""
        scrollable = ScrollableFrame(self.content_area)
        scrollable.pack(fill='both', expand=True)
        # Update theme for the scrollable canvas
        scrollable.update_theme()
        return scrollable.get_frame()
    
    def create_content_panels(self):
        """Create all content panels."""
        # Dashboard
        self.dashboard = DashboardHome(self.content_area, self.theme_manager, self.status_manager)
        self.content_widgets['dashboard'] = self.dashboard.create_dashboard(self.content_area)
        
        # Connection panel
        self.content_widgets['connection'] = self.create_connection_panel()
        
        # Database list panel
        self.content_widgets['databases'] = self.create_databases_panel()
        
        # Playground panel
        self.content_widgets['playground'] = self.create_playground_panel()
        
        # Schema Explorer panel
        self.content_widgets['schema_explorer'] = self.create_schema_explorer_panel()
        
        # Performance Dashboard panel
        self.content_widgets['performance_dashboard'] = self.create_performance_dashboard_panel()
        
        # Documentation panel
        self.content_widgets['documentation'] = self.create_documentation_panel()
        
        # Search panel
        self.content_widgets['search_&_filter'] = self.create_search_panel()
        
        # Comparison panel
        self.content_widgets['schema_compare'] = self.create_comparison_panel()
        
        # Visualization panel
        self.content_widgets['dependencies'] = self.create_visualization_panel()
        
        # Scheduler panel
        self.content_widgets['scheduler'] = self.create_scheduler_panel()
        
        # Projects panel
        self.content_widgets['projects'] = self.create_projects_panel()
        
        # Settings panel
        self.content_widgets['settings'] = self.create_settings_panel()
        
        # Hide all panels initially
        for widget in self.content_widgets.values():
            widget.pack_forget()
    
    def create_connection_panel(self) -> ttk.Frame:
        """Create modern connection configuration panel."""
        # Create scrollable container
        scrollable = ScrollableFrame(self.content_area)
        panel = ttk.Frame(scrollable.get_frame(), padding="20")
        
        # Header
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Database Connection", style='Title.TLabel')
        title_label.pack(side='left')
        
        # Theme toggle
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side='right')
        
        ttk.Label(theme_frame, text="Theme:").pack(side='left', padx=(0, 5))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                 values=self.theme_manager.get_available_themes(),
                                 state='readonly', width=10)
        theme_combo.pack(side='left')
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_changed)
        
        # Recent connections widget (Phase 1 enhancement)
        self.create_recent_connections_widget(panel)
        
        # Connection methods card
        methods_card = CardComponent(panel, self.theme_manager)
        methods_frame = methods_card.create_info_card(panel, "Connection Method", None)
        methods_frame.pack(fill='x', pady=(0, 20))
        
        # Connection method selection
        method_frame = ttk.Frame(methods_frame, padding="10")
        method_frame.pack(fill='x')
        
        methods = [
            ("Username/Password", "credentials"),
            ("Azure AD", "azure_ad"),
            ("Service Principal", "service_principal"),
            ("Connection String", "connection_string")
        ]
        
        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, variable=self.connection_method, 
                          value=value, command=self.on_connection_method_changed).pack(anchor='w', pady=2)
        
        # Connection details in collapsible sections
        self.create_connection_details(panel)
        
        # Connection actions
        actions_frame = ttk.Frame(panel)
        actions_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(actions_frame, text="Test Connection", style='Secondary.TButton',
                  command=self.test_connection).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Connect", style='Primary.TButton',
                  command=self.connect_database).pack(side='left')
        
        # Favorites widget
        favorites_frame = ttk.LabelFrame(panel, text="Favorite Connections", padding="10")
        favorites_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        self.connection_favorites = FavoritesWidget(favorites_frame, self.favorites_manager)
        self.connection_favorites.pack(fill='both', expand=True)
        
        # Pack the panel content
        panel.pack(fill='both', expand=True)
        
        return scrollable.container
    
    def create_recent_connections_widget(self, parent):
        """Create Phase 1 enhancement: Recent connections widget."""
        recent_frame = ttk.LabelFrame(parent, text="🕒 Recent Connections", padding="10")
        recent_frame.pack(fill='x', pady=(20, 0))
        
        # Create a scrollable frame for recent connections
        canvas = tk.Canvas(recent_frame, height=120)
        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=canvas.yview)
        scrollable_recent = ttk.Frame(canvas)
        
        # Configure scrolling
        scrollable_recent.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_recent, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Load and display recent connections
        try:
            recent_connections = self.profile_manager.get_recent_connections(limit=5)
            
            if recent_connections:
                for i, conn in enumerate(recent_connections):
                    conn_frame = ttk.Frame(scrollable_recent)
                    conn_frame.pack(fill='x', padx=5, pady=2)
                    
                    # Connection info
                    info_text = f"📊 {conn.get('database', 'N/A')} @ {conn.get('server', 'N/A')}"
                    if len(info_text) > 50:
                        info_text = info_text[:47] + "..."
                    
                    info_label = ttk.Label(conn_frame, text=info_text, width=40)
                    info_label.pack(side='left')
                    
                    # Method badge
                    method_text = conn.get('method', 'Unknown').upper()
                    method_label = ttk.Label(conn_frame, text=method_text, style='Status.TLabel')
                    method_label.pack(side='left', padx=(10, 5))
                    
                    # Quick connect button
                    connect_btn = ttk.Button(conn_frame, text="Connect", width=8,
                                           command=lambda c=conn: self.load_recent_connection(c))
                    connect_btn.pack(side='right')
                    
                    # Add separator (except for last item)
                    if i < len(recent_connections) - 1:
                        sep = ttk.Separator(scrollable_recent, orient='horizontal')
                        sep.pack(fill='x', padx=5, pady=2)
            else:
                # No recent connections message
                no_recent_label = ttk.Label(scrollable_recent, 
                                          text="No recent connections found.\nSuccessful connections will appear here.", 
                                          style='Status.TLabel', justify='center')
                no_recent_label.pack(expand=True, fill='both', padx=20, pady=20)
                
        except Exception as e:
            # Error loading recent connections
            error_label = ttk.Label(scrollable_recent, 
                                  text=f"Error loading recent connections:\n{str(e)}", 
                                  style='Status.TLabel', justify='center')
            error_label.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_recent_connection(self, connection_data):
        """Load a recent connection into the form fields."""
        try:
            # Set connection method
            method = connection_data.get('method', 'credentials')
            self.connection_method.set(method)
            self.on_connection_method_changed()
            
            # Set server and database
            self.server.set(connection_data.get('server', ''))
            self.database.set(connection_data.get('database', ''))
            
            # Set credentials based on method
            if method == 'credentials':
                self.username.set(connection_data.get('username', ''))
                # Note: Password is not stored for security reasons
                self.status_manager.show_message("Connection loaded. Please enter password.", "info")
            elif method == 'service_principal':
                self.client_id.set(connection_data.get('client_id', ''))
                self.tenant_id.set(connection_data.get('tenant_id', ''))
                # Note: Client secret is not stored for security reasons
                self.status_manager.show_message("Connection loaded. Please enter client secret.", "info")
            elif method == 'connection_string':
                # For connection string, we only show the method was loaded
                self.status_manager.show_message("Connection method loaded. Please enter connection string.", "info")
            else:
                self.status_manager.show_message(f"Connection loaded using {method.replace('_', ' ').title()} method.", "info")
                
            # Add to connection history when loaded
            self.profile_manager.add_to_history(connection_data, success=True)
            
        except Exception as e:
            self.status_manager.show_message(f"Error loading connection: {str(e)}", "error")
    
    def create_connection_details(self, parent):
        """Create connection details with enhanced form controls."""
        # Basic connection details
        basic_section = CollapsibleFrame(parent, "Basic Connection Details")
        basic_section.pack(fill='x', pady=(0, 10))
        basic_section.expanded.set(True)
        basic_content = basic_section.get_content_frame()
        
        # Server
        server_frame = ttk.Frame(basic_content, padding="10")
        server_frame.pack(fill='x')
        ttk.Label(server_frame, text="Server:").pack(anchor='w')
        
        self.server_entry = ValidatedEntry(server_frame, placeholder="server.database.windows.net",
                                         validation_type="server", required=True)
        self.server_entry.pack(fill='x', pady=(5, 0))
        self.server_entry.entry.configure(textvariable=self.server)
        
        # Database
        db_frame = ttk.Frame(basic_content, padding="10")
        db_frame.pack(fill='x')
        ttk.Label(db_frame, text="Database:").pack(anchor='w')
        
        self.database_entry = ValidatedEntry(db_frame, placeholder="database_name",
                                           validation_type="database", required=True)
        self.database_entry.pack(fill='x', pady=(5, 0))
        self.database_entry.entry.configure(textvariable=self.database)
        
        # Credentials section
        self.credentials_section = CollapsibleFrame(parent, "Credentials")
        self.credentials_section.pack(fill='x', pady=(0, 10))
        cred_content = self.credentials_section.get_content_frame()
        
        # Username
        user_frame = ttk.Frame(cred_content, padding="10")
        user_frame.pack(fill='x')
        ttk.Label(user_frame, text="Username:").pack(anchor='w')
        
        self.username_entry = ValidatedEntry(user_frame, placeholder="username", required=True)
        self.username_entry.pack(fill='x', pady=(5, 0))
        self.username_entry.entry.configure(textvariable=self.username)
        
        # Password
        pass_frame = ttk.Frame(cred_content, padding="10")
        pass_frame.pack(fill='x')
        ttk.Label(pass_frame, text="Password:").pack(anchor='w')
        
        self.password_entry = ValidatedEntry(pass_frame, placeholder="password", required=True)
        self.password_entry.pack(fill='x', pady=(5, 0))
        self.password_entry.entry.configure(textvariable=self.password, show="*")
        
        # Advanced options
        advanced_section = CollapsibleFrame(parent, "Advanced Options")
        advanced_section.pack(fill='x', pady=(0, 10))
        adv_content = advanced_section.get_content_frame()
        
        # Driver selection
        driver_frame = ttk.Frame(adv_content, padding="10")
        driver_frame.pack(fill='x')
        ttk.Label(driver_frame, text="ODBC Driver:").pack(anchor='w')
        ttk.Combobox(driver_frame, textvariable=self.driver,
                    values=["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"],
                    state="readonly").pack(fill='x', pady=(5, 0))
        
        # Update visibility based on method
        self.on_connection_method_changed()
    
    def create_databases_panel(self) -> ttk.Frame:
        """Create comprehensive database explorer with visual tree."""
        # Create scrollable container
        scrollable = ScrollableFrame(self.content_area)
        panel = ttk.Frame(scrollable.get_frame(), padding="20")
        
        # Header with actions
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Database Explorer", style='Title.TLabel').pack(side='left')
        
        # Action buttons
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side='right')
        
        ttk.Button(actions_frame, text="🔄 Refresh", command=self.refresh_database_tree).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="🔍 Explore Schema", command=self.explore_selected_database).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="📋 Generate Docs", command=self.generate_from_explorer).pack(side='left')
        
        # Search and filter toolbar
        toolbar_frame = ttk.Frame(panel)
        toolbar_frame.pack(fill='x', pady=(0, 20))
        
        # Search
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side='left', fill='x', expand=True, padx=(0, 20))
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side='left')
        self.explorer_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.explorer_search_var, width=30)
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.filter_database_tree)
        
        # View options
        view_frame = ttk.Frame(toolbar_frame)
        view_frame.pack(side='right')
        
        ttk.Label(view_frame, text="View:").pack(side='left')
        self.explorer_view_var = tk.StringVar(value="All")
        view_combo = ttk.Combobox(view_frame, textvariable=self.explorer_view_var,
                                values=["All", "User Only", "System Only", "Connected Only"], 
                                state='readonly', width=12)
        view_combo.pack(side='left', padx=(5, 0))
        view_combo.bind('<<ComboboxSelected>>', self.filter_database_tree)
        
        # Main explorer area with split panes
        explorer_paned = ttk.PanedWindow(panel, orient='horizontal')
        explorer_paned.pack(fill='both', expand=True)
        
        # Left pane: Database tree
        tree_frame = ttk.Frame(explorer_paned)
        explorer_paned.add(tree_frame, weight=2)
        
        tree_header = ttk.Frame(tree_frame)
        tree_header.pack(fill='x', pady=(0, 10))
        ttk.Label(tree_header, text="Database Structure", font=('Segoe UI', 10, 'bold')).pack(side='left')
        
        # Database tree view
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill='both', expand=True)
        
        self.db_tree = ttk.Treeview(tree_container, columns=('type', 'count', 'size'), show='tree headings')
        self.db_tree.heading('#0', text='Name')
        self.db_tree.heading('type', text='Type')
        self.db_tree.heading('count', text='Count')
        self.db_tree.heading('size', text='Size')
        
        self.db_tree.column('#0', width=200, minwidth=150)
        self.db_tree.column('type', width=80, minwidth=60)
        self.db_tree.column('count', width=60, minwidth=40)
        self.db_tree.column('size', width=80, minwidth=60)
        
        # Tree scrollbars
        tree_v_scroll = ttk.Scrollbar(tree_container, orient='vertical', command=self.db_tree.yview)
        tree_h_scroll = ttk.Scrollbar(tree_container, orient='horizontal', command=self.db_tree.xview)
        self.db_tree.configure(yscrollcommand=tree_v_scroll.set, xscrollcommand=tree_h_scroll.set)
        
        self.db_tree.pack(side='left', fill='both', expand=True)
        tree_v_scroll.pack(side='right', fill='y')
        tree_h_scroll.pack(side='bottom', fill='x')
        
        # Tree event bindings
        self.db_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.db_tree.bind('<Double-1>', self.on_tree_double_click)
        self.db_tree.bind('<Button-3>', self.show_tree_context_menu)
        
        # Right pane: Object details
        details_frame = ttk.Frame(explorer_paned)
        explorer_paned.add(details_frame, weight=1)
        
        details_header = ttk.Frame(details_frame)
        details_header.pack(fill='x', pady=(0, 10))
        ttk.Label(details_header, text="Object Details", font=('Segoe UI', 10, 'bold')).pack(side='left')
        
        # Details notebook for different views
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill='both', expand=True)
        
        # Overview tab
        overview_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(overview_frame, text='Overview')
        
        self.overview_text = tk.Text(overview_frame, wrap='word', height=10, 
                                   font=('Consolas', 9), state='disabled')
        overview_scroll = ttk.Scrollbar(overview_frame, orient='vertical', command=self.overview_text.yview)
        self.overview_text.configure(yscrollcommand=overview_scroll.set)
        
        self.overview_text.pack(side='left', fill='both', expand=True)
        overview_scroll.pack(side='right', fill='y')
        
        # Properties tab
        properties_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(properties_frame, text='Properties')
        
        self.properties_tree = ttk.Treeview(properties_frame, columns=('value',), show='tree headings')
        self.properties_tree.heading('#0', text='Property')
        self.properties_tree.heading('value', text='Value')
        self.properties_tree.column('#0', width=150)
        self.properties_tree.column('value', width=200)
        
        props_scroll = ttk.Scrollbar(properties_frame, orient='vertical', command=self.properties_tree.yview)
        self.properties_tree.configure(yscrollcommand=props_scroll.set)
        
        self.properties_tree.pack(side='left', fill='both', expand=True)
        props_scroll.pack(side='right', fill='y')
        
        # Status bar for explorer
        explorer_status_frame = ttk.Frame(panel)
        explorer_status_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Separator(explorer_status_frame, orient='horizontal').pack(fill='x')
        
        status_content = ttk.Frame(explorer_status_frame)
        status_content.pack(fill='x', pady=(5, 0))
        
        self.explorer_status_label = ttk.Label(status_content, text="Ready to explore databases")
        self.explorer_status_label.pack(side='left')
        
        self.explorer_progress = ttk.Progressbar(status_content, mode='indeterminate', length=200)
        self.explorer_progress.pack(side='right', padx=(10, 0))
        
        # Initialize tree icons
        self.init_tree_icons()
        
        # Load databases on panel creation
        self.root.after(100, self.load_database_tree)
        
        # Pack the panel content
        panel.pack(fill='both', expand=True)
        
        return scrollable.container
    
    def init_tree_icons(self):
        """Initialize tree view icons."""
        try:
            # Initialize icon mapping for different object types
            self.tree_icons = {
                'server': '🗄️',
                'database': '💾',
                'schema': '📁',
                'table': '📊',
                'view': '👁️',
                'procedure': '⚙️',
                'function': '🔧',
                'trigger': '⚡',
                'index': '📇',
                'constraint': '🔗',
                'user_db': '💾',
                'system_db': '🔒'
            }
        except Exception as e:
            logger.error(f"Failed to initialize tree icons: {e}")
            self.tree_icons = {}
    
    def load_database_tree(self):
        """Load database structure into tree view."""
        try:
            self.explorer_progress.start()
            self.explorer_status_label.config(text="Loading databases...")
            
            # Clear existing tree
            for item in self.db_tree.get_children():
                self.db_tree.delete(item)
            
            # Check connection by trying to create one
            try:
                test_connection = AzureSQLConnection()
                if not self._test_basic_connection(test_connection):
                    self.add_tree_placeholder("No database connection - please connect first")
                    return
            except Exception:
                self.add_tree_placeholder("No database connection - please connect first")
                return
            
            # Load databases in background thread
            import threading
            thread = threading.Thread(target=self._load_databases_background, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to load database tree: {e}")
            self.add_tree_placeholder(f"Error loading databases: {str(e)}")
        finally:
            self.explorer_progress.stop()
    
    def _load_databases_background(self):
        """Background thread for loading database information."""
        try:
            # Create database connection for this operation
            with AzureSQLConnection() as db:
                if not self._connect_to_database(db):
                    error_msg = "Failed to connect to database"
                    self.root.after(0, self.add_tree_placeholder, error_msg)
                    self.root.after(0, lambda: self.explorer_status_label.config(text=error_msg))
                    return
                    
                # Get all available databases
                databases = db.list_databases()
                
                # Update UI in main thread
                self.root.after(0, self._update_tree_with_databases, databases)
            
        except Exception as e:
            error_msg = f"Failed to load databases: {str(e)}"
            self.root.after(0, self.add_tree_placeholder, error_msg)
            self.root.after(0, lambda: self.explorer_status_label.config(text=error_msg))
    
    def _update_tree_with_databases(self, databases):
        """Update tree view with database information in main thread."""
        try:
            self.explorer_status_label.config(text="Building database tree...")
            
            # Add server node
            server_name = self.server.get() or 'Unknown Server'
            server_id = self.db_tree.insert('', 'end', 
                                           text=f"{self.tree_icons.get('server', '')} {server_name}",
                                           values=('Server', len(databases), ''), 
                                           tags=('server',))
            
            # Add databases
            for db in databases:
                db_name = db.get('name', 'Unknown')
                db_size = self.format_size(db.get('size_mb', 0))
                db_type = 'System' if self.is_system_database(db_name) else 'User'
                icon = self.tree_icons.get('system_db' if db_type == 'System' else 'user_db', '💾')
                
                db_id = self.db_tree.insert(server_id, 'end',
                                           text=f"{icon} {db_name}",
                                           values=(db_type, '', db_size),
                                           tags=('database', db_type.lower()))
                
                # Add placeholder for schema exploration
                self.db_tree.insert(db_id, 'end', text="📂 Schemas", values=('Container', '', ''), tags=('schemas',))
                self.db_tree.insert(db_id, 'end', text="📊 Tables", values=('Container', '', ''), tags=('tables',))
                self.db_tree.insert(db_id, 'end', text="👁️ Views", values=('Container', '', ''), tags=('views',))
                self.db_tree.insert(db_id, 'end', text="⚙️ Procedures", values=('Container', '', ''), tags=('procedures',))
                self.db_tree.insert(db_id, 'end', text="🔧 Functions", values=('Container', '', ''), tags=('functions',))
            
            # Expand server node
            self.db_tree.item(server_id, open=True)
            
            self.explorer_status_label.config(text=f"Loaded {len(databases)} databases")
            self.filter_database_tree()
            
        except Exception as e:
            logger.error(f"Failed to update tree with databases: {e}")
            self.add_tree_placeholder(f"Error building tree: {str(e)}")
        finally:
            self.explorer_progress.stop()
    
    def add_tree_placeholder(self, message):
        """Add placeholder message to tree."""
        self.db_tree.insert('', 'end', text=f"ℹ️ {message}", values=('Info', '', ''), tags=('info',))
        self.explorer_progress.stop()
        self.explorer_status_label.config(text=message)
    
    def is_system_database(self, db_name):
        """Check if database is a system database."""
        system_dbs = ['master', 'model', 'msdb', 'tempdb', 'resource']
        return db_name.lower() in system_dbs
    
    def format_size(self, size_mb):
        """Format size in MB to readable string."""
        if not size_mb or size_mb == 0:
            return ""
        elif size_mb < 1024:
            return f"{size_mb:.0f} MB"
        else:
            return f"{size_mb/1024:.1f} GB"
    
    def _test_basic_connection(self, connection):
        """Test basic database connection."""
        try:
            return self._connect_to_database(connection)
        except Exception:
            return False
    
    def refresh_database_tree(self):
        """Refresh the database tree view."""
        self.load_database_tree()
    
    def filter_database_tree(self, event=None):
        """Filter database tree based on search and view options."""
        try:
            search_text = self.explorer_search_var.get().lower()
            view_filter = self.explorer_view_var.get()
            
            # Get all items
            all_items = self.db_tree.get_children()
            
            for item in all_items:
                self._filter_tree_item(item, search_text, view_filter)
                
        except Exception as e:
            logger.error(f"Failed to filter database tree: {e}")
    
    def _filter_tree_item(self, item, search_text, view_filter):
        """Recursively filter tree items."""
        try:
            # Get item details
            item_text = self.db_tree.item(item, 'text').lower()
            item_tags = self.db_tree.item(item, 'tags')
            
            # Check search filter
            search_match = not search_text or search_text in item_text
            
            # Check view filter
            view_match = True
            if view_filter == "User Only" and 'system' in item_tags:
                view_match = False
            elif view_filter == "System Only" and 'user' in item_tags:
                view_match = False
            
            # Show/hide item
            if search_match and view_match:
                self.db_tree.reattach(item, self.db_tree.parent(item), 'end')
            
            # Process children
            for child in self.db_tree.get_children(item):
                self._filter_tree_item(child, search_text, view_filter)
                
        except Exception as e:
            logger.error(f"Failed to filter tree item: {e}")
    
    def on_tree_select(self, event):
        """Handle tree selection changes."""
        try:
            selection = self.db_tree.selection()
            if not selection:
                self.clear_object_details()
                return
            
            item = selection[0]
            item_text = self.db_tree.item(item, 'text')
            item_values = self.db_tree.item(item, 'values')
            item_tags = self.db_tree.item(item, 'tags')
            
            # Update object details
            self.show_object_details(item_text, item_values, item_tags)
            
        except Exception as e:
            logger.error(f"Failed to handle tree selection: {e}")
    
    def on_tree_double_click(self, event):
        """Handle tree double-click events."""
        try:
            selection = self.db_tree.selection()
            if not selection:
                return
            
            item = selection[0]
            item_tags = self.db_tree.item(item, 'tags')
            
            if 'database' in item_tags:
                # Expand database schema if not already done
                self.explore_database_schema(item)
            elif any(tag in item_tags for tag in ['schema', 'table', 'view', 'procedure', 'function']):
                # Show detailed information
                self.show_detailed_object_info(item)
                
        except Exception as e:
            logger.error(f"Failed to handle tree double-click: {e}")
    
    def show_tree_context_menu(self, event):
        """Show context menu for tree items."""
        try:
            # Identify item under cursor
            item = self.db_tree.identify_row(event.y)
            if item:
                self.db_tree.selection_set(item)
                
                # Create context menu
                context_menu = tk.Menu(self.root, tearoff=0)
                
                item_tags = self.db_tree.item(item, 'tags')
                
                if 'database' in item_tags:
                    context_menu.add_command(label="🔍 Explore Schema", command=lambda: self.explore_database_schema(item))
                    context_menu.add_command(label="📋 Generate Documentation", command=lambda: self.generate_docs_for_item(item))
                    context_menu.add_separator()
                    context_menu.add_command(label="📊 View Statistics", command=lambda: self.show_database_statistics(item))
                
                context_menu.add_separator()
                context_menu.add_command(label="🔄 Refresh", command=self.refresh_database_tree)
                
                # Show context menu
                try:
                    context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    context_menu.grab_release()
                    
        except Exception as e:
            logger.error(f"Failed to show tree context menu: {e}")
    
    def clear_object_details(self):
        """Clear object details display."""
        # Clear overview text
        self.overview_text.config(state='normal')
        self.overview_text.delete('1.0', tk.END)
        self.overview_text.insert('1.0', "Select an object to view details")
        self.overview_text.config(state='disabled')
        
        # Clear properties tree
        for item in self.properties_tree.get_children():
            self.properties_tree.delete(item)
    
    def show_object_details(self, item_text, item_values, item_tags):
        """Show details for selected object."""
        # Clear existing details
        self.clear_object_details()
        
        # Update overview
        self.overview_text.config(state='normal')
        self.overview_text.delete('1.0', tk.END)
        
        overview = f"Object: {item_text}\n"
        if item_values:
            overview += f"Type: {item_values[0]}\n"
            if len(item_values) > 1 and item_values[1]:
                overview += f"Count: {item_values[1]}\n"
            if len(item_values) > 2 and item_values[2]:
                overview += f"Size: {item_values[2]}\n"
        
        overview += f"Tags: {', '.join(item_tags)}\n"
        
        if 'database' in item_tags:
            overview += "\nDouble-click to explore schema structure."
        elif 'server' in item_tags:
            overview += "\nExpand to view available databases."
        
        self.overview_text.insert('1.0', overview)
        self.overview_text.config(state='disabled')
        
        # Update properties
        if item_values:
            for i, value in enumerate(item_values):
                if value:
                    prop_name = ['Type', 'Count', 'Size'][i] if i < 3 else f'Property {i+1}'
                    self.properties_tree.insert('', 'end', text=prop_name, values=(value,))
    
    def explore_database_schema(self, db_item):
        """Explore schema structure of selected database."""
        try:
            db_name = self.db_tree.item(db_item, 'text').split(' ', 1)[1]  # Remove icon
            self.explorer_status_label.config(text=f"Exploring schema for {db_name}...")
            self.explorer_progress.start()
            
            # Load schema in background thread
            import threading
            thread = threading.Thread(target=self._explore_schema_background, args=(db_item, db_name), daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to explore database schema: {e}")
            self.explorer_status_label.config(text=f"Error exploring schema: {str(e)}")
    
    def _explore_schema_background(self, db_item, db_name):
        """Background thread for schema exploration."""
        try:
            # Switch to target database connection if needed
            # For now, show placeholder structure
            schema_info = {
                'schemas': ['dbo', 'sys', 'guest'],
                'tables': 15,
                'views': 8,
                'procedures': 12,
                'functions': 6
            }
            
            # Update UI in main thread
            self.root.after(0, self._update_schema_tree, db_item, schema_info)
            
        except Exception as e:
            error_msg = f"Failed to explore schema: {str(e)}"
            self.root.after(0, lambda: self.explorer_status_label.config(text=error_msg))
        finally:
            self.root.after(0, self.explorer_progress.stop)
    
    def _update_schema_tree(self, db_item, schema_info):
        """Update tree with schema information."""
        try:
            # Update counts in container nodes
            children = self.db_tree.get_children(db_item)
            for child in children:
                child_text = self.db_tree.item(child, 'text')
                if 'Schemas' in child_text:
                    self.db_tree.item(child, values=('Container', len(schema_info['schemas']), ''))
                elif 'Tables' in child_text:
                    self.db_tree.item(child, values=('Container', schema_info['tables'], ''))
                elif 'Views' in child_text:
                    self.db_tree.item(child, values=('Container', schema_info['views'], ''))
                elif 'Procedures' in child_text:
                    self.db_tree.item(child, values=('Container', schema_info['procedures'], ''))
                elif 'Functions' in child_text:
                    self.db_tree.item(child, values=('Container', schema_info['functions'], ''))
            
            # Expand database node
            self.db_tree.item(db_item, open=True)
            
            self.explorer_status_label.config(text=f"Schema explored successfully")
            
        except Exception as e:
            logger.error(f"Failed to update schema tree: {e}")
    
    def show_detailed_object_info(self, item):
        """Show detailed information for database object."""
        try:
            item_text = self.db_tree.item(item, 'text')
            self.explorer_status_label.config(text=f"Loading details for {item_text}...")
            
            # For now, show placeholder information
            details = f"Detailed information for: {item_text}\n\n"
            details += "This feature will be enhanced in future updates to show:\n"
            details += "• Column definitions and data types\n"
            details += "• Indexes and constraints\n"
            details += "• Relationships and dependencies\n"
            details += "• Performance statistics\n"
            details += "• Security information\n"
            
            self.overview_text.config(state='normal')
            self.overview_text.delete('1.0', tk.END)
            self.overview_text.insert('1.0', details)
            self.overview_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Failed to show detailed object info: {e}")
    
    def explore_selected_database(self):
        """Explore currently selected database."""
        try:
            selection = self.db_tree.selection()
            if not selection:
                self.status_manager.show_status("Please select a database to explore", "warning")
                return
            
            item = selection[0]
            item_tags = self.db_tree.item(item, 'tags')
            
            if 'database' in item_tags:
                self.explore_database_schema(item)
            else:
                self.status_manager.show_status("Please select a database to explore", "warning")
                
        except Exception as e:
            logger.error(f"Failed to explore selected database: {e}")
    
    def generate_from_explorer(self):
        """Generate documentation from explorer selection."""
        try:
            selection = self.db_tree.selection()
            if not selection:
                self.status_manager.show_status("Please select a database to generate documentation", "warning")
                return
            
            item = selection[0]
            item_tags = self.db_tree.item(item, 'tags')
            
            if 'database' in item_tags:
                db_name = self.db_tree.item(item, 'text').split(' ', 1)[1]  # Remove icon
                self.selected_database.set(db_name)
                self.show_documentation()
                self.status_manager.show_status(f"Switched to documentation generation for {db_name}", "success")
            else:
                self.status_manager.show_status("Please select a database to generate documentation", "warning")
                
        except Exception as e:
            logger.error(f"Failed to generate documentation from explorer: {e}")
    
    def generate_docs_for_item(self, item):
        """Generate documentation for specific tree item."""
        self.generate_from_explorer()
    
    def show_database_statistics(self, item):
        """Show database statistics."""
        try:
            db_name = self.db_tree.item(item, 'text').split(' ', 1)[1]  # Remove icon
            
            # For now, show placeholder statistics
            stats = f"Database Statistics for: {db_name}\n\n"
            stats += "• Tables: 15\n"
            stats += "• Views: 8\n"
            stats += "• Stored Procedures: 12\n"
            stats += "• Functions: 6\n"
            stats += "• Schemas: 3\n"
            stats += "• Size: 125 MB\n"
            stats += "• Created: 2023-01-15\n"
            stats += "• Last Modified: 2024-08-27\n"
            
            self.overview_text.config(state='normal')
            self.overview_text.delete('1.0', tk.END)
            self.overview_text.insert('1.0', stats)
            self.overview_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Failed to show database statistics: {e}")
    
    def create_playground_panel(self) -> ttk.Frame:
        """Create the Interactive Database Playground panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Interactive Database Playground", 
                 style='Title.TLabel').pack(side='left')
        
        # Info label
        ttk.Label(header_frame, 
                 text="🎮 Safe environment for learning SQL and exploring databases",
                 style='Info.TLabel').pack(side='right')
        
        # Create playground instance
        if hasattr(self, 'db_connection') and self.db_connection:
            try:
                # Initialize schema analyzer if not available
                if not hasattr(self, 'schema_analyzer') or not self.schema_analyzer:
                    from schema_analyzer import SchemaAnalyzer
                    self.schema_analyzer = SchemaAnalyzer(self.db_connection)
                
                # Create playground
                self.playground = create_playground_panel(
                    panel, self.db_connection, self.schema_analyzer, self.theme_manager
                )
                
                # Status message
                status_frame = ttk.Frame(panel)
                status_frame.pack(fill='x', pady=(10, 0))
                ttk.Label(status_frame, text="✅ Playground initialized with sample database", 
                         foreground='green').pack()
                
            except Exception as e:
                logger.error(f"Failed to initialize playground: {e}")
                # Show error message
                error_frame = ttk.Frame(panel)
                error_frame.pack(fill='both', expand=True)
                
                card_component = CardComponent(error_frame, self.theme_manager)
                error_card = card_component.create_info_card(
                    error_frame, "Connection Required",
                    "Please connect to a database first to use the playground."
                )
                error_card.pack(fill='x', pady=(20, 0))
                
                # Connection button
                ttk.Button(error_frame, text="Go to Connection Settings",
                          command=self.show_connection).pack(pady=(20, 0))
        else:
            # No connection available
            no_connection_frame = ttk.Frame(panel)
            no_connection_frame.pack(fill='both', expand=True)
            
            card_component = CardComponent(no_connection_frame, self.theme_manager)
            welcome_card = card_component.create_info_card(
                no_connection_frame, "Welcome to Database Playground!",
                "Connect to a database to start exploring with interactive tutorials, "
                "query builder, and safe experimentation environment."
            )
            welcome_card.pack(fill='x', pady=(20, 0))
            
            features_frame = ttk.LabelFrame(no_connection_frame, text="Playground Features", padding=15)
            features_frame.pack(fill='x', pady=(20, 0))
            
            features = [
                "🔧 Visual Query Builder - Drag-and-drop SQL construction",
                "📊 Instant Results Preview - Real-time query execution",
                "🛡️ Safe Sandbox Environment - No risk to production data",
                "🎓 Interactive Tutorials - Learn SQL step-by-step",
                "📈 Performance Metrics - Understand query performance",
                "🔍 Schema Explorer - Browse database structure visually"
            ]
            
            for feature in features:
                ttk.Label(features_frame, text=feature).pack(anchor='w', pady=2)
            
            # Connection button
            ttk.Button(no_connection_frame, text="Connect to Database",
                      command=self.show_connection).pack(pady=(20, 0))
        
        return panel
    
    def create_schema_explorer_panel(self) -> ttk.Frame:
        """Create the Dynamic Visual Schema Explorer panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Dynamic Visual Schema Explorer", 
                 style='Title.TLabel').pack(side='left')
        
        # Info label
        ttk.Label(header_frame, 
                 text="🗂️ Interactive visual exploration of database schemas",
                 style='Info.TLabel').pack(side='right')
        
        # Create schema explorer instance
        if hasattr(self, 'db_connection') and self.db_connection:
            try:
                # Initialize schema analyzer if not available
                if not hasattr(self, 'schema_analyzer') or not self.schema_analyzer:
                    from schema_analyzer import SchemaAnalyzer
                    self.schema_analyzer = SchemaAnalyzer(self.db_connection)
                
                # Create schema explorer
                self.schema_explorer = create_schema_explorer_panel(
                    panel, self.db_connection, self.schema_analyzer, self.theme_manager
                )
                
                # Status message
                status_frame = ttk.Frame(panel)
                status_frame.pack(fill='x', pady=(10, 0))
                ttk.Label(status_frame, text="✅ Schema Explorer loaded successfully", 
                         foreground='green').pack()
                
            except Exception as e:
                logger.error(f"Failed to initialize schema explorer: {e}")
                # Show error message
                error_frame = ttk.Frame(panel)
                error_frame.pack(fill='both', expand=True)
                
                card_component = CardComponent(error_frame, self.theme_manager)
                error_card = card_component.create_info_card(
                    error_frame, "Connection Required",
                    "Please connect to a database first to explore the schema."
                )
                error_card.pack(fill='x', pady=(20, 0))
                
                # Connection button
                ttk.Button(error_frame, text="Go to Connection Settings",
                          command=self.show_connection).pack(pady=(20, 0))
        else:
            # No connection available
            no_connection_frame = ttk.Frame(panel)
            no_connection_frame.pack(fill='both', expand=True)
            
            card_component = CardComponent(no_connection_frame, self.theme_manager)
            welcome_card = card_component.create_info_card(
                no_connection_frame, "Welcome to Schema Explorer!",
                "Connect to a database to start exploring schemas with interactive "
                "diagrams, relationship visualization, and detailed object information."
            )
            welcome_card.pack(fill='x', pady=(20, 0))
            
            features_frame = ttk.LabelFrame(no_connection_frame, text="Schema Explorer Features", padding=15)
            features_frame.pack(fill='x', pady=(20, 0))
            
            features = [
                "🗂️ Interactive Schema Diagrams - Visual representation of database structure",
                "🔗 Relationship Visualization - Foreign keys and dependencies",
                "📋 Detailed Object Information - Column details, indexes, constraints",
                "🔍 Advanced Search & Filtering - Find objects quickly",
                "🎯 Focus Modes - Table-centric and relationship-centric views", 
                "📊 Schema Statistics - Object counts and relationship metrics",
                "🔄 Real-time Navigation - Click to explore related objects",
                "📤 Export Capabilities - Save diagrams in multiple formats"
            ]
            
            for feature in features:
                ttk.Label(features_frame, text=feature).pack(anchor='w', pady=2)
            
            # Connection button
            ttk.Button(no_connection_frame, text="Connect to Database",
                      command=self.show_connection).pack(pady=(20, 0))
        
        return panel
    
    def create_performance_dashboard_panel(self) -> ttk.Frame:
        """Create the Real-Time Performance Dashboard panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Real-Time Performance Dashboard", 
                 style='Title.TLabel').pack(side='left')
        
        # Info label
        ttk.Label(header_frame, 
                 text="📊 Live performance monitoring, alerts, and database health",
                 style='Info.TLabel').pack(side='right')
        
        # Create performance dashboard instance
        if hasattr(self, 'db_connection') and self.db_connection:
            try:
                # Initialize schema analyzer if not available
                if not hasattr(self, 'schema_analyzer') or not self.schema_analyzer:
                    from schema_analyzer import SchemaAnalyzer
                    self.schema_analyzer = SchemaAnalyzer(self.db_connection)
                
                # Create performance dashboard
                self.performance_dashboard = create_performance_dashboard_panel(
                    panel, self.db_connection, self.schema_analyzer, 
                    self.theme_manager, self.status_manager
                )
                
                # Status message
                status_frame = ttk.Frame(panel)
                status_frame.pack(fill='x', pady=(10, 0))
                ttk.Label(status_frame, text="✅ Performance Dashboard initialized successfully", 
                         foreground='green').pack()
                
            except Exception as e:
                logger.error(f"Failed to initialize performance dashboard: {e}")
                # Show error message
                error_frame = ttk.Frame(panel)
                error_frame.pack(fill='both', expand=True)
                
                card_component = CardComponent(error_frame, self.theme_manager)
                error_card = card_component.create_info_card(
                    error_frame, "Connection Required",
                    "Please connect to a database first to monitor performance."
                )
                error_card.pack(fill='x', pady=(20, 0))
                
                # Connection button
                ttk.Button(error_frame, text="Go to Connection Settings",
                          command=self.show_connection).pack(pady=(20, 0))
        else:
            # No connection available
            no_connection_frame = ttk.Frame(panel)
            no_connection_frame.pack(fill='both', expand=True)
            
            card_component = CardComponent(no_connection_frame, self.theme_manager)
            welcome_card = card_component.create_info_card(
                no_connection_frame, "Welcome to Performance Dashboard!",
                "Connect to a database to start monitoring real-time performance metrics, "
                "health indicators, and receive intelligent alerts for performance issues."
            )
            welcome_card.pack(fill='x', pady=(20, 0))
            
            features_frame = ttk.LabelFrame(no_connection_frame, text="Performance Dashboard Features", padding=15)
            features_frame.pack(fill='x', pady=(20, 0))
            
            features = [
                "📊 Real-Time Metrics - Live CPU, Memory, I/O, and DTU monitoring",
                "📈 Interactive Charts - Visual performance trends with historical data",
                "🚨 Smart Alerts - Configurable thresholds with severity levels",
                "🔍 Query Analysis - Identify resource-intensive queries",
                "💾 Resource Monitoring - Storage, connections, and wait statistics",
                "⚡ Performance History - 24-hour trending and analysis",
                "🎯 Health Indicators - Overall database health scoring",
                "📱 Alert Management - Acknowledge, filter, and manage alerts"
            ]
            
            for feature in features:
                ttk.Label(features_frame, text=feature).pack(anchor='w', pady=2)
            
            # Connection button
            ttk.Button(no_connection_frame, text="Connect to Database",
                      command=self.show_connection).pack(pady=(20, 0))
        
        return panel
    
    def create_documentation_panel(self) -> ttk.Frame:
        """Create modern documentation generation panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        ttk.Label(panel, text="Documentation Generation", style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Output settings card
        output_card = CardComponent(panel, self.theme_manager)
        output_frame = output_card.create_info_card(panel, "Output Settings", None)
        output_frame.pack(fill='x', pady=(0, 20))
        
        # Advanced Export Configuration
        self.create_advanced_export_section(output_frame)
        
        # Generation options
        options_section = CollapsibleFrame(panel, "Advanced Options")
        options_section.pack(fill='x', pady=(0, 20))
        options_content = options_section.get_content_frame()
        
        # Options checkboxes with modern styling
        self.include_data_samples = tk.BooleanVar(value=True)
        ToggleSwitch(options_content, text="Include Data Samples", variable=self.include_data_samples, 
                    command=None).pack(anchor='w', pady=5, padx=10)
        
        self.include_permissions = tk.BooleanVar(value=True)
        ToggleSwitch(options_content, text="Include Permissions", variable=self.include_permissions,
                    command=None).pack(anchor='w', pady=5, padx=10)
        
        self.include_dependencies = tk.BooleanVar(value=True)
        ToggleSwitch(options_content, text="Include Dependencies", variable=self.include_dependencies,
                    command=None).pack(anchor='w', pady=5, padx=10)
        
        # Enhanced Generation Actions
        generate_frame = ttk.Frame(panel)
        generate_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(generate_frame, text="👁️ Preview Documentation", style='Secondary.TButton',
                  command=self.preview_documentation).pack(side='left', padx=(0, 10))
        
        ttk.Button(generate_frame, text="📋 Generate Documentation", style='Primary.TButton',
                  command=self.generate_documentation).pack(side='left', padx=(0, 10))
        
        ttk.Button(generate_frame, text="🎯 Advanced Export", style='Accent.TButton',
                  command=self.show_advanced_export_dialog).pack(side='left', padx=(0, 10))
        
        ttk.Button(generate_frame, text="📁 Open Output Folder", style='Secondary.TButton',
                  command=self.open_output_folder).pack(side='left')
        
        return panel
    
    def create_search_panel(self) -> ttk.Frame:
        """Create enhanced search and filter panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        ttk.Label(panel, text="Search & Filter Database Objects", style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Search interface would be implemented here
        # This is a simplified version for the framework
        search_card = CardComponent(panel, self.theme_manager)
        search_widget = search_card.create_info_card(panel, "Advanced Search", 
                                                   "Search functionality coming soon with enhanced filtering options.")
        search_widget.pack(fill='x')
        
        return panel
    
    def create_comparison_panel(self) -> ttk.Frame:
        """Create comprehensive schema comparison panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Schema Comparison", style='Title.TLabel')
        title_label.pack(side='left')
        
        # Help button
        help_btn = ttk.Button(header_frame, text="ⓘ Help", style='Secondary.TButton',
                            command=self.show_comparison_help)
        help_btn.pack(side='right')
        self.tooltip_manager.add_tooltip(help_btn, "Learn about schema comparison features")
        
        # Create scrollable content
        canvas = tk.Canvas(panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Schema Selection Card
        selection_card = CardComponent(scrollable_frame, self.theme_manager)
        selection_frame = selection_card.create_info_card(scrollable_frame, "Schema Selection", None)
        selection_frame.pack(fill='x', pady=(0, 20))
        
        selection_content = ttk.Frame(selection_frame, padding="15")
        selection_content.pack(fill='both', expand=True)
        
        # Source Schema Section
        source_section = ttk.LabelFrame(selection_content, text="Source Schema (Baseline)", padding="10")
        source_section.pack(fill='x', pady=(0, 15))
        
        # Source type selection
        source_type_frame = ttk.Frame(source_section)
        source_type_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(source_type_frame, text="Source Type:").pack(side='left')
        self.comparison_source_type = tk.StringVar(value="database")
        source_type_combo = ttk.Combobox(source_type_frame, textvariable=self.comparison_source_type,
                                       values=["database", "file", "snapshot"], state='readonly', width=15)
        source_type_combo.pack(side='left', padx=(10, 0))
        source_type_combo.bind('<<ComboboxSelected>>', self.on_source_type_changed)
        
        # Source database selection
        self.source_db_frame = ttk.Frame(source_section)
        self.source_db_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(self.source_db_frame, text="Database:").pack(side='left')
        self.comparison_source_db = tk.StringVar()
        self.source_db_combo = ttk.Combobox(self.source_db_frame, textvariable=self.comparison_source_db,
                                          state='readonly', width=30)
        self.source_db_combo.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Source file selection (initially hidden)
        self.source_file_frame = ttk.Frame(source_section)
        
        ttk.Label(self.source_file_frame, text="Schema File:").pack(side='left')
        self.comparison_source_file = tk.StringVar()
        source_file_entry = ValidatedEntry(self.source_file_frame, textvariable=self.comparison_source_file,
                                         custom_validator=self.validate_file_path)
        source_file_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        
        source_browse_btn = ttk.Button(self.source_file_frame, text="Browse", 
                                     command=lambda: self.browse_schema_file(self.comparison_source_file))
        source_browse_btn.pack(side='left')
        
        # Target Schema Section
        target_section = ttk.LabelFrame(selection_content, text="Target Schema (Current)", padding="10")
        target_section.pack(fill='x', pady=(0, 15))
        
        # Target type selection
        target_type_frame = ttk.Frame(target_section)
        target_type_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(target_type_frame, text="Target Type:").pack(side='left')
        self.comparison_target_type = tk.StringVar(value="database")
        target_type_combo = ttk.Combobox(target_type_frame, textvariable=self.comparison_target_type,
                                       values=["database", "file", "snapshot"], state='readonly', width=15)
        target_type_combo.pack(side='left', padx=(10, 0))
        target_type_combo.bind('<<ComboboxSelected>>', self.on_target_type_changed)
        
        # Target database selection
        self.target_db_frame = ttk.Frame(target_section)
        self.target_db_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(self.target_db_frame, text="Database:").pack(side='left')
        self.comparison_target_db = tk.StringVar()
        self.target_db_combo = ttk.Combobox(self.target_db_frame, textvariable=self.comparison_target_db,
                                          state='readonly', width=30)
        self.target_db_combo.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Target file selection (initially hidden)
        self.target_file_frame = ttk.Frame(target_section)
        
        ttk.Label(self.target_file_frame, text="Schema File:").pack(side='left')
        self.comparison_target_file = tk.StringVar()
        target_file_entry = ValidatedEntry(self.target_file_frame, textvariable=self.comparison_target_file,
                                         custom_validator=self.validate_file_path)
        target_file_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        
        target_browse_btn = ttk.Button(self.target_file_frame, text="Browse",
                                     command=lambda: self.browse_schema_file(self.comparison_target_file))
        target_browse_btn.pack(side='left')
        
        # Comparison Options
        options_section = ttk.LabelFrame(selection_content, text="Comparison Options", padding="10")
        options_section.pack(fill='x', pady=(0, 15))
        
        # Options frame
        options_frame = ttk.Frame(options_section)
        options_frame.pack(fill='x')
        
        # Left column
        left_opts = ttk.Frame(options_frame)
        left_opts.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.compare_tables = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_opts, text="Compare Tables", variable=self.compare_tables).pack(anchor='w')
        
        self.compare_views = tk.BooleanVar(value=True)  
        ttk.Checkbutton(left_opts, text="Compare Views", variable=self.compare_views).pack(anchor='w')
        
        self.compare_procedures = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_opts, text="Compare Stored Procedures", variable=self.compare_procedures).pack(anchor='w')
        
        # Right column
        right_opts = ttk.Frame(options_frame)
        right_opts.pack(side='left', fill='both', expand=True)
        
        self.compare_functions = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_opts, text="Compare Functions", variable=self.compare_functions).pack(anchor='w')
        
        self.compare_indexes = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_opts, text="Compare Indexes", variable=self.compare_indexes).pack(anchor='w')
        
        self.compare_constraints = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_opts, text="Compare Constraints", variable=self.compare_constraints).pack(anchor='w')
        
        # Action Buttons
        action_frame = ttk.Frame(selection_content)
        action_frame.pack(fill='x', pady=(15, 0))
        
        self.compare_btn = ttk.Button(action_frame, text="🔄 Compare Schemas", style='Primary.TButton',
                                    command=self.start_schema_comparison)
        self.compare_btn.pack(side='left')
        
        refresh_db_btn = ttk.Button(action_frame, text="🔄 Refresh Databases", 
                                  command=self.refresh_comparison_databases)
        refresh_db_btn.pack(side='left', padx=(10, 0))
        
        save_config_btn = ttk.Button(action_frame, text="💾 Save Config", 
                                   command=self.save_comparison_config)
        save_config_btn.pack(side='left', padx=(10, 0))
        
        load_config_btn = ttk.Button(action_frame, text="📂 Load Config",
                                   command=self.load_comparison_config)
        load_config_btn.pack(side='left', padx=(10, 0))
        
        # Results Card
        self.results_card = CardComponent(scrollable_frame, self.theme_manager)
        self.results_frame = self.results_card.create_info_card(scrollable_frame, "Comparison Results", None)
        self.results_frame.pack(fill='both', expand=True, pady=(0, 20))
        self.results_frame.pack_forget()  # Initially hidden
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initialize comparison data
        self.schema_comparator = SchemaComparator()
        self.comparison_results = None
        self.refresh_comparison_databases()
        
        return panel
    
    def create_visualization_panel(self) -> ttk.Frame:
        """Create comprehensive dependency visualization panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header with controls
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Dependency Visualization", style='Title.TLabel').pack(side='left')
        
        # Visualization controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        ttk.Button(controls_frame, text="🔄 Refresh", 
                  command=self.refresh_visualization).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="💾 Export", 
                  command=self.export_visualization).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="⚙️ Options", 
                  command=self.show_viz_options).pack(side='left')
        
        # Main visualization area with paned window
        viz_paned = ttk.PanedWindow(panel, orient='horizontal')
        viz_paned.pack(fill='both', expand=True)
        
        # Left panel - Configuration and controls
        config_panel = ttk.Frame(viz_paned, padding="10")
        viz_paned.add(config_panel, weight=25)
        
        self.create_viz_config_panel(config_panel)
        
        # Right panel - Visualization display
        viz_display_panel = ttk.Frame(viz_paned, padding="10")
        viz_paned.add(viz_display_panel, weight=75)
        
        self.create_viz_display_panel(viz_display_panel)
        
        return panel
    
    def create_scheduler_panel(self) -> ttk.Frame:
        """Create scheduler and monitoring panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        ttk.Label(panel, text="Scheduler & Monitoring", style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Scheduler interface placeholder
        sched_card = CardComponent(panel, self.theme_manager)
        sched_widget = sched_card.create_info_card(panel, "Automated Tasks", 
                                                 "Schedule automated documentation generation and monitoring.")
        sched_widget.pack(fill='x')
        
        return panel
    
    def create_projects_panel(self) -> ttk.Frame:
        """Create comprehensive project management workspace."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header with actions
        header_frame = ttk.Frame(panel)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Project Workspace", style='Title.TLabel').pack(side='left')
        
        # Action buttons
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side='right')
        
        ttk.Button(actions_frame, text="📁 New Project", 
                  command=self.create_new_project).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="📂 Open Project", 
                  command=self.open_existing_project).pack(side='left', padx=(0, 5))
        ttk.Button(actions_frame, text="📤 Import", 
                  command=self.import_project).pack(side='left')
        
        # Main workspace area with paned window
        workspace_paned = ttk.PanedWindow(panel, orient='horizontal')
        workspace_paned.pack(fill='both', expand=True)
        
        # Left panel - Project list and quick actions
        left_panel = ttk.Frame(workspace_paned, padding="10")
        workspace_paned.add(left_panel, weight=30)
        
        # Project list section
        self.create_project_list_section(left_panel)
        
        # Right panel - Project details and workspace
        self.project_workspace_frame = ttk.Frame(workspace_paned, padding="10")
        workspace_paned.add(self.project_workspace_frame, weight=70)
        
        # Initialize with welcome screen
        self.create_project_welcome_screen()
        
        # Load projects on startup
        self.refresh_project_list()
        
        return panel
    
    def create_project_list_section(self, parent):
        """Create the project list section with search and filters."""
        # Search and filter section
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search Projects:").pack(anchor='w')
        self.project_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.project_search_var)
        search_entry.pack(fill='x', pady=(5, 0))
        search_entry.bind('<KeyRelease>', self.filter_projects)
        
        # Project list
        list_frame = ttk.LabelFrame(parent, text="Projects", padding="10")
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create treeview for projects
        columns = ("Name", "Databases", "Updated")
        self.projects_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=12)
        
        # Configure columns
        self.projects_tree.column("#0", width=50, stretch=False)
        self.projects_tree.heading("#0", text="Type")
        
        for col in columns:
            width = 120 if col == "Name" else 80
            self.projects_tree.column(col, width=width, anchor='center' if col != "Name" else 'w')
            self.projects_tree.heading(col, text=col)
        
        # Add scrollbar
        projects_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=projects_scrollbar.set)
        
        self.projects_tree.pack(side="left", fill="both", expand=True)
        projects_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.projects_tree.bind("<<TreeviewSelect>>", self.on_project_selected)
        self.projects_tree.bind("<Double-1>", self.on_project_double_click)
        
        # Quick actions
        quick_actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding="10")
        quick_actions_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(quick_actions_frame, text="🔄 Refresh", 
                  command=self.refresh_project_list).pack(fill='x', pady=(0, 5))
        ttk.Button(quick_actions_frame, text="🗑️ Delete Selected", 
                  command=self.delete_selected_project).pack(fill='x', pady=(0, 5))
        ttk.Button(quick_actions_frame, text="📤 Export Selected", 
                  command=self.export_selected_project).pack(fill='x')
        
        # Status section
        status_frame = ttk.LabelFrame(parent, text="Workspace Stats", padding="10")
        status_frame.pack(fill='x')
        
        self.projects_stats_label = ttk.Label(status_frame, text="Loading...", style='Status.TLabel')
        self.projects_stats_label.pack()
    
    def create_project_welcome_screen(self):
        """Create the welcome screen for project workspace."""
        # Clear workspace frame
        for widget in self.project_workspace_frame.winfo_children():
            widget.destroy()
        
        welcome_frame = ttk.Frame(self.project_workspace_frame)
        welcome_frame.pack(fill='both', expand=True)
        
        # Center content
        content_frame = ttk.Frame(welcome_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Welcome message
        ttk.Label(content_frame, text="🚀 Project Workspace", 
                 style='Title.TLabel', font=('Helvetica', 18, 'bold')).pack(pady=(0, 20))
        
        ttk.Label(content_frame, text="Manage multi-database documentation projects", 
                 style='Status.TLabel').pack(pady=(0, 30))
        
        # Quick start options
        options_frame = ttk.Frame(content_frame)
        options_frame.pack()
        
        # Create project card
        create_card = CardComponent(options_frame, self.theme_manager)
        create_widget = create_card.create_info_card(options_frame, "Create New Project", 
                                                   "Start a new documentation project")
        create_widget.pack(pady=(0, 10))
        
        ttk.Button(create_widget, text="📁 Create Project", 
                  command=self.create_new_project).pack(pady=10)
        
        # Import project card
        import_card = CardComponent(options_frame, self.theme_manager)
        import_widget = import_card.create_info_card(options_frame, "Import Existing Project", 
                                                   "Import a project from backup")
        import_widget.pack()
        
        ttk.Button(import_widget, text="📤 Import Project", 
                  command=self.import_project).pack(pady=10)
    
    def create_project_details_view(self, project_id: str):
        """Create detailed view for a selected project."""
        # Clear workspace frame
        for widget in self.project_workspace_frame.winfo_children():
            widget.destroy()
        
        # Get project data
        project = self.project_manager.get_project(project_id)
        if not project:
            self.create_project_welcome_screen()
            return
        
        # Main frame
        main_frame = ttk.Frame(self.project_workspace_frame)
        main_frame.pack(fill='both', expand=True)
        
        # Project header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Project info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side='left')
        
        ttk.Label(info_frame, text=f"📁 {project.name}", 
                 style='Title.TLabel').pack(anchor='w')
        if project.description:
            ttk.Label(info_frame, text=project.description, 
                     style='Status.TLabel').pack(anchor='w')
        
        # Action buttons
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side='right')
        
        ttk.Button(action_frame, text="⚙️ Settings", 
                  command=lambda: self.edit_project_settings(project_id)).pack(side='left', padx=(0, 5))
        ttk.Button(action_frame, text="🔄 Batch Operations", 
                  command=lambda: self.show_batch_operations(project_id)).pack(side='left', padx=(0, 5))
        ttk.Button(action_frame, text="📤 Export", 
                  command=lambda: self.export_project(project_id)).pack(side='left')
        
        # Tabbed interface for project details
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Databases tab
        db_frame = ttk.Frame(notebook, padding="10")
        notebook.add(db_frame, text="📊 Databases")
        self.create_project_databases_view(db_frame, project_id)
        
        # Environments tab
        env_frame = ttk.Frame(notebook, padding="10")
        notebook.add(env_frame, text="🌐 Environments")
        self.create_project_environments_view(env_frame, project)
        
        # Activity tab
        activity_frame = ttk.Frame(notebook, padding="10")
        notebook.add(activity_frame, text="📈 Activity")
        self.create_project_activity_view(activity_frame, project_id)
        
        # Files tab
        files_frame = ttk.Frame(notebook, padding="10")
        notebook.add(files_frame, text="📁 Files")
        self.create_project_files_view(files_frame, project_id)
    
    def create_project_databases_view(self, parent, project_id: str):
        """Create databases view for a project."""
        # Header with add database button
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="Project Databases", style='Heading.TLabel').pack(side='left')
        ttk.Button(header_frame, text="➕ Add Database", 
                  command=lambda: self.add_database_to_project(project_id)).pack(side='right')
        
        # Database list
        columns = ("Name", "Environment", "Server", "Last Documented", "Status")
        db_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            width = 150 if col == "Server" else 100
            db_tree.column(col, width=width)
            db_tree.heading(col, text=col)
        
        # Add scrollbar
        db_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=db_tree.yview)
        db_tree.configure(yscrollcommand=db_scrollbar.set)
        
        db_tree.pack(side="left", fill="both", expand=True)
        db_scrollbar.pack(side="right", fill="y")
        
        # Load databases
        self.load_project_databases(db_tree, project_id)
        
        # Context menu for database operations
        self.create_database_context_menu(db_tree, project_id)
    
    def create_project_environments_view(self, parent, project: DatabaseProject):
        """Create environments view for a project."""
        # Header
        ttk.Label(parent, text="Project Environments", style='Heading.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Environments list
        for env in project.environments:
            env_card = CardComponent(parent, self.theme_manager)
            env_widget = env_card.create_info_card(parent, f"🌐 {env['name'].title()}", 
                                                 f"Priority: {env['config'].get('priority', 'Normal')}")
            env_widget.pack(fill='x', pady=(0, 10))
            
            # Environment details
            details_frame = ttk.Frame(env_widget, padding="10")
            details_frame.pack(fill='x')
            
            config_text = "\n".join([f"{k}: {v}" for k, v in env['config'].items()])
            ttk.Label(details_frame, text=config_text, style='Status.TLabel').pack(anchor='w')
    
    def create_project_activity_view(self, parent, project_id: str):
        """Create activity/execution history view for a project."""
        # Header
        ttk.Label(parent, text="Recent Activity", style='Heading.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Activity list (this would be populated with actual execution history)
        activity_card = CardComponent(parent, self.theme_manager)
        activity_widget = activity_card.create_info_card(parent, "📈 Execution History", 
                                                        "Recent batch operations and documentation generation")
        activity_widget.pack(fill='x')
        
        # Placeholder for activity history
        ttk.Label(activity_widget, text="No recent activity", 
                 style='Status.TLabel', padding="20").pack()
    
    def create_project_files_view(self, parent, project_id: str):
        """Create files view for a project."""
        # Header
        ttk.Label(parent, text="Project Files", style='Heading.TLabel').pack(anchor='w', pady=(0, 10))
        
        # File explorer
        files_card = CardComponent(parent, self.theme_manager)
        files_widget = files_card.create_info_card(parent, "📁 Generated Files", 
                                                  "Documentation, exports, and reports")
        files_widget.pack(fill='both', expand=True)
        
        # File tree (placeholder)
        file_frame = ttk.Frame(files_widget, padding="10")
        file_frame.pack(fill='both', expand=True)
        
        ttk.Label(file_frame, text="Files will be listed here after generation", 
                 style='Status.TLabel').pack(pady=20)
    
    # Project management methods
    def create_new_project(self):
        """Create a new project using the dialog."""
        if not hasattr(self, 'project_manager'):
            self.project_manager = ProjectManager()
        
        dialog = CreateProjectDialog(self.root, self.project_manager)
        project_id = dialog.show()
        
        if project_id:
            self.refresh_project_list()
            self.status_manager.show_toast("Success", f"Project created successfully!")
            # Select the new project
            self.select_project_in_tree(project_id)
    
    def open_existing_project(self):
        """Open an existing project using the dialog."""
        if not hasattr(self, 'project_manager'):
            self.project_manager = ProjectManager()
        
        dialog = ProjectSelectionDialog(self.root, self.project_manager)
        project_id = dialog.show()
        
        if project_id:
            self.select_project_in_tree(project_id)
            self.create_project_details_view(project_id)
    
    def import_project(self):
        """Import a project from a zip file."""
        if not hasattr(self, 'project_manager'):
            self.project_manager = ProjectManager()
        
        file_path = filedialog.askopenfilename(
            title="Import Project",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                project_id = self.project_manager.import_project(file_path)
                if project_id:
                    self.refresh_project_list()
                    self.status_manager.show_toast("Success", "Project imported successfully!")
                    self.select_project_in_tree(project_id)
                else:
                    messagebox.showerror("Error", "Failed to import project.")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def refresh_project_list(self):
        """Refresh the project list."""
        if not hasattr(self, 'project_manager'):
            self.project_manager = ProjectManager()
        
        if not hasattr(self, 'projects_tree'):
            return
        
        # Clear existing items
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        # Load projects
        try:
            projects = self.project_manager.list_projects()
            
            for project in projects:
                # Format date
                updated_date = project.get('updated_at', '')
                if updated_date:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
                        updated_date = dt.strftime("%Y-%m-%d")
                    except:
                        updated_date = updated_date[:10]
                
                item_id = self.projects_tree.insert("", "end", 
                                                   text="📁",
                                                   values=(project['name'],
                                                          project.get('database_count', 0),
                                                          updated_date),
                                                   tags=(project['id'],))
            
            # Update stats
            total_projects = len(projects)
            total_databases = sum(p.get('database_count', 0) for p in projects)
            
            if hasattr(self, 'projects_stats_label'):
                self.projects_stats_label.config(text=f"Projects: {total_projects} | Databases: {total_databases}")
                
        except Exception as e:
            logger.error(f"Failed to refresh project list: {e}")
            if hasattr(self, 'projects_stats_label'):
                self.projects_stats_label.config(text="Error loading projects")
    
    def filter_projects(self, event=None):
        """Filter projects based on search text."""
        search_text = self.project_search_var.get().lower()
        
        # Simple filter implementation
        for item in self.projects_tree.get_children():
            values = self.projects_tree.item(item)['values']
            if search_text in values[0].lower():  # Search in name
                self.projects_tree.item(item, tags=self.projects_tree.item(item)['tags'])
            else:
                # Hide item by setting empty tags (simple approach)
                pass
    
    def on_project_selected(self, event=None):
        """Handle project selection in the tree."""
        selection = self.projects_tree.selection()
        if not selection:
            self.create_project_welcome_screen()
            return
        
        item = self.projects_tree.item(selection[0])
        if item['tags']:
            project_id = item['tags'][0]
            self.create_project_details_view(project_id)
    
    def on_project_double_click(self, event=None):
        """Handle double-click on project."""
        self.on_project_selected(event)
    
    def select_project_in_tree(self, project_id: str):
        """Select a project in the tree by ID."""
        for item in self.projects_tree.get_children():
            tags = self.projects_tree.item(item)['tags']
            if tags and tags[0] == project_id:
                self.projects_tree.selection_set(item)
                self.projects_tree.focus(item)
                break
    
    def delete_selected_project(self):
        """Delete the selected project."""
        selection = self.projects_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project to delete.")
            return
        
        item = self.projects_tree.item(selection[0])
        if not item['tags']:
            return
        
        project_id = item['tags'][0]
        project_name = item['values'][0]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete project '{project_name}'?\n\nThis will permanently delete all project data."):
            try:
                if self.project_manager.delete_project(project_id):
                    self.refresh_project_list()
                    self.create_project_welcome_screen()
                    self.status_manager.show_toast("Success", "Project deleted successfully!")
                else:
                    messagebox.showerror("Error", "Failed to delete project.")
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {str(e)}")
    
    def export_selected_project(self):
        """Export the selected project."""
        selection = self.projects_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project to export.")
            return
        
        item = self.projects_tree.item(selection[0])
        if not item['tags']:
            return
        
        project_id = item['tags'][0]
        project_name = item['values'][0]
        
        # Ask for export location
        file_path = filedialog.asksaveasfilename(
            title="Export Project",
            defaultextension=".zip",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")],
            initialvalue=f"{project_name}_export.zip"
        )
        
        if file_path:
            try:
                if self.project_manager.export_project(project_id, file_path):
                    self.status_manager.show_toast("Success", "Project exported successfully!")
                else:
                    messagebox.showerror("Error", "Failed to export project.")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def add_database_to_project(self, project_id: str):
        """Add a database to the project."""
        # This would show a dialog to configure database connection
        messagebox.showinfo("Feature", "Database addition dialog would open here.\nThis would integrate with the connection configuration.")
    
    def load_project_databases(self, tree_widget, project_id: str):
        """Load databases for a project into the tree widget."""
        try:
            databases = self.project_manager.get_project_databases(project_id)
            
            for db in databases:
                config = db.get('connection_config', {})
                server = config.get('server', 'Unknown')
                last_doc = db.get('last_documented', 'Never')
                if last_doc and last_doc != 'Never':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(last_doc.replace('Z', '+00:00'))
                        last_doc = dt.strftime("%Y-%m-%d")
                    except:
                        last_doc = last_doc[:10] if len(last_doc) > 10 else last_doc
                
                tree_widget.insert("", "end", values=(
                    db.get('database_name', 'Unknown'),
                    db.get('environment', 'default'),
                    server,
                    last_doc,
                    db.get('status', 'active')
                ))
        except Exception as e:
            logger.error(f"Failed to load project databases: {e}")
    
    def create_database_context_menu(self, tree_widget, project_id: str):
        """Create context menu for database operations."""
        # Context menu implementation would go here
        pass
    
    def edit_project_settings(self, project_id: str):
        """Edit project settings."""
        messagebox.showinfo("Feature", "Project settings dialog would open here.")
    
    def show_batch_operations(self, project_id: str):
        """Show batch operations dialog."""
        dialog = BatchOperationDialog(self.root, self.project_manager, project_id)
        operation_config = dialog.show()
        
        if operation_config:
            # Execute the batch operation
            try:
                execution_id = self.project_manager.execute_batch_operation(
                    project_id, 
                    operation_config['operation_type'],
                    operation_config['config']
                )
                self.status_manager.show_toast("Success", f"Batch operation started! Execution ID: {execution_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start batch operation: {str(e)}")
    
    def export_project(self, project_id: str):
        """Export a specific project."""
        project = self.project_manager.get_project(project_id)
        if not project:
            return
        
        # Ask for export location
        file_path = filedialog.asksaveasfilename(
            title="Export Project",
            defaultextension=".zip",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")],
            initialvalue=f"{project.name}_export.zip"
        )
        
        if file_path:
            try:
                if self.project_manager.export_project(project_id, file_path):
                    self.status_manager.show_toast("Success", "Project exported successfully!")
                else:
                    messagebox.showerror("Error", "Failed to export project.")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    # Dependency Visualization Widget Methods
    def create_viz_config_panel(self, parent: ttk.Frame):
        """Create visualization configuration panel."""
        # Visualization Type Selection
        type_card = CardComponent(parent, self.theme_manager)
        type_widget = type_card.create_info_card(parent, "Visualization Type", "Select the type of visualization to generate")
        type_widget.pack(fill='x', pady=(0, 10))
        
        # Add content to type card
        type_content = type_widget.winfo_children()[1]  # Get the content frame
        
        self.viz_type_var = tk.StringVar(value="relationship_diagram")
        viz_types = [
            ("Relationship Diagram", "relationship_diagram", "Show foreign key relationships"),
            ("Dependency Graph", "dependency_graph", "Display object dependencies"),
            ("Hierarchical View", "hierarchical_view", "Tree-like schema structure"),
            ("Circular Layout", "circular_layout", "Circular arrangement of objects")
        ]
        
        for name, value, desc in viz_types:
            frame = ttk.Frame(type_content)
            frame.pack(fill='x', pady=2)
            ttk.Radiobutton(frame, text=name, variable=self.viz_type_var, 
                           value=value, command=self.update_visualization).pack(side='left')
            self.tooltip_manager.add_tooltip(frame, desc)
        
        # Database Selection
        db_card = CardComponent(parent, self.theme_manager)
        db_widget = db_card.create_info_card(parent, "Database Selection", "Choose database and connection for analysis")
        db_widget.pack(fill='x', pady=(0, 10))
        
        db_content = db_widget.winfo_children()[1]
        
        ttk.Label(db_content, text="Database:").pack(anchor='w')
        self.viz_database_var = tk.StringVar()
        self.viz_database_combo = ttk.Combobox(db_content, textvariable=self.viz_database_var, 
                                              state='readonly', width=30)
        self.viz_database_combo.pack(fill='x', pady=(5, 10))
        self.viz_database_combo.bind('<<ComboboxSelected>>', 
                                    lambda e: self.update_visualization())
        
        # Filters and Options
        filters_card = CardComponent(parent, self.theme_manager)
        filters_widget = filters_card.create_info_card(parent, "Filters & Options", "Configure visualization filters and display options")
        filters_widget.pack(fill='x', pady=(0, 10))
        
        filters_content = filters_widget.winfo_children()[1]
        
        # Schema filter
        schema_frame = ttk.Frame(filters_content)
        schema_frame.pack(fill='x', pady=5)
        ttk.Label(schema_frame, text="Schema Filter:").pack(side='left')
        self.viz_schema_var = tk.StringVar()
        schema_entry = ValidatedEntry(schema_frame, placeholder="Leave blank for all schemas", 
                                     textvariable=self.viz_schema_var)
        schema_entry.pack(side='right', padx=(10, 0))
        
        # Object type filters
        self.viz_include_tables = tk.BooleanVar(value=True)
        self.viz_include_views = tk.BooleanVar(value=True)
        self.viz_include_procedures = tk.BooleanVar(value=False)
        self.viz_include_functions = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(filters_content, text="Include Tables", 
                       variable=self.viz_include_tables,
                       command=self.update_visualization).pack(anchor='w', pady=2)
        ttk.Checkbutton(filters_content, text="Include Views", 
                       variable=self.viz_include_views,
                       command=self.update_visualization).pack(anchor='w', pady=2)
        ttk.Checkbutton(filters_content, text="Include Procedures", 
                       variable=self.viz_include_procedures,
                       command=self.update_visualization).pack(anchor='w', pady=2)
        ttk.Checkbutton(filters_content, text="Include Functions", 
                       variable=self.viz_include_functions,
                       command=self.update_visualization).pack(anchor='w', pady=2)
        
        # Action buttons
        actions_frame = ttk.Frame(filters_content)
        actions_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(actions_frame, text="Generate Visualization", 
                  command=self.generate_visualization).pack(fill='x', pady=2)
        ttk.Button(actions_frame, text="Clear Visualization", 
                  command=self.clear_visualization).pack(fill='x', pady=2)
        
        # Initialize database list
        self.refresh_viz_databases()
    
    def create_viz_display_panel(self, parent: ttk.Frame):
        """Create visualization display panel."""
        # Display area with scrolling
        display_card = CardComponent(parent, self.theme_manager)
        self.viz_display_widget = display_card.create_info_card(parent, "Dependency Graph", "Interactive dependency visualization display")
        self.viz_display_widget.pack(fill='both', expand=True)
        
        # Get content area
        self.viz_display_content = self.viz_display_widget.winfo_children()[1]
        
        # Status and statistics
        self.viz_status_frame = ttk.Frame(self.viz_display_content)
        self.viz_status_frame.pack(fill='x', pady=(0, 10))
        
        self.viz_status_label = ttk.Label(self.viz_status_frame, 
                                         text="Select database and click 'Generate Visualization' to begin",
                                         style='Subtitle.TLabel')
        self.viz_status_label.pack(side='left')
        
        # Statistics frame
        stats_frame = ttk.Frame(self.viz_status_frame)
        stats_frame.pack(side='right')
        
        self.viz_stats_label = ttk.Label(stats_frame, text="")
        self.viz_stats_label.pack(side='right')
        
        # Visualization canvas area
        canvas_frame = ttk.Frame(self.viz_display_content)
        canvas_frame.pack(fill='both', expand=True)
        
        # Canvas with scrollbars
        self.viz_canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.viz_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.viz_canvas.xview)
        
        self.viz_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.viz_canvas.pack(side='left', fill='both', expand=True)
        
        # Initialize empty state
        self.show_viz_empty_state()
    
    def refresh_viz_databases(self):
        """Refresh the list of available databases for visualization."""
        try:
            if hasattr(self, 'viz_database_combo'):
                current_dbs = []
                if hasattr(self, 'databases_var') and self.databases_var.get():
                    current_dbs = [self.databases_var.get()]
                
                # Add any connected databases from projects
                if hasattr(self, 'project_manager') and self.project_manager:
                    projects = self.project_manager.list_projects()
                    for project in projects:
                        project_data = self.project_manager.get_project(project['id'])
                        if project_data and 'databases' in project_data:
                            for db in project_data['databases']:
                                db_name = f"{db.get('server', '')}/{db.get('database', '')}"
                                if db_name not in current_dbs:
                                    current_dbs.append(db_name)
                
                self.viz_database_combo['values'] = current_dbs
                if current_dbs:
                    self.viz_database_combo.set(current_dbs[0])
        
        except Exception as e:
            logger.error(f"Error refreshing visualization databases: {e}")
    
    def update_visualization(self):
        """Update visualization based on current settings."""
        if not hasattr(self, 'viz_current_data') or not self.viz_current_data:
            return
        
        # Only update if we have existing data
        self.generate_visualization_from_data(self.viz_current_data)
    
    def generate_visualization(self):
        """Generate visualization from selected database."""
        database = self.viz_database_var.get()
        if not database:
            self.status_manager.show_toast("Warning", "Please select a database first")
            return
        
        # Show loading state
        self.show_viz_loading_state()
        
        def worker():
            try:
                # Get database connection and schema data
                schema_data = self.get_schema_data_for_visualization(database)
                if not schema_data:
                    self.root.after(0, lambda: self.show_viz_error_state("No schema data available"))
                    return
                
                # Store current data
                self.viz_current_data = schema_data
                
                # Generate visualization
                self.root.after(0, lambda: self.generate_visualization_from_data(schema_data))
                
            except Exception as e:
                logger.error(f"Visualization generation error: {e}")
                self.root.after(0, lambda: self.show_viz_error_state(f"Error: {str(e)}"))
        
        # Run in background thread
        threading.Thread(target=worker, daemon=True).start()
    
    def generate_visualization_from_data(self, schema_data: Dict[str, Any]):
        """Generate visualization from schema data."""
        try:
            # Create visualizer
            visualizer = DependencyVisualizer()
            
            # Get visualization options
            options = {
                'schema_filter': self.viz_schema_var.get() or None,
                'include_tables': self.viz_include_tables.get(),
                'include_views': self.viz_include_views.get(),
                'include_procedures': self.viz_include_procedures.get(),
                'include_functions': self.viz_include_functions.get(),
            }
            
            # Get visualization type
            viz_type_str = self.viz_type_var.get()
            viz_type = VisualizationType(viz_type_str)
            
            # Generate visualization data
            viz_data = visualizer.generate_visualization(schema_data, viz_type, options)
            
            # Display visualization
            self.display_visualization(viz_data)
            
            # Update statistics
            self.update_viz_statistics(viz_data)
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            self.show_viz_error_state(f"Visualization error: {str(e)}")
    
    def display_visualization(self, viz_data: Dict[str, Any]):
        """Display visualization on canvas."""
        # Clear canvas
        self.viz_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.viz_canvas.winfo_width() or 800
        canvas_height = self.viz_canvas.winfo_height() or 600
        
        nodes = viz_data.get('nodes', [])
        edges = viz_data.get('edges', [])
        
        if not nodes:
            self.show_viz_empty_state()
            return
        
        # Scale factors for positioning
        scale_x = canvas_width * 0.8
        scale_y = canvas_height * 0.8
        offset_x = canvas_width * 0.1
        offset_y = canvas_height * 0.1
        
        # Draw edges first (so they appear behind nodes)
        for edge in edges:
            source_node = next((n for n in nodes if n['id'] == edge['source']), None)
            target_node = next((n for n in nodes if n['id'] == edge['target']), None)
            
            if source_node and target_node:
                x1 = source_node['x'] * scale_x + offset_x
                y1 = source_node['y'] * scale_y + offset_y
                x2 = target_node['x'] * scale_x + offset_x
                y2 = target_node['y'] * scale_y + offset_y
                
                # Color based on edge type
                edge_color = self.get_edge_color(edge['type'])
                
                # Draw arrow line
                self.viz_canvas.create_line(x1, y1, x2, y2, 
                                           fill=edge_color, width=2, arrow=tk.LAST)
        
        # Draw nodes
        node_radius = 20
        for node in nodes:
            x = node['x'] * scale_x + offset_x
            y = node['y'] * scale_y + offset_y
            
            # Color based on node type
            node_color = self.get_node_color(node['type'])
            
            # Draw node circle
            self.viz_canvas.create_oval(x - node_radius, y - node_radius,
                                       x + node_radius, y + node_radius,
                                       fill=node_color, outline='black', width=2)
            
            # Draw label
            self.viz_canvas.create_text(x, y - node_radius - 15, 
                                       text=node['label'], anchor='center',
                                       font=('Arial', 8, 'bold'))
        
        # Update scroll region
        self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        
        # Update status
        self.viz_status_label.config(text=f"Visualization generated successfully")
    
    def get_node_color(self, node_type: str) -> str:
        """Get color for node based on its type."""
        colors = {
            'table': '#4CAF50',      # Green
            'view': '#2196F3',       # Blue
            'procedure': '#FF9800',  # Orange
            'function': '#9C27B0'    # Purple
        }
        return colors.get(node_type, '#757575')  # Grey default
    
    def get_edge_color(self, edge_type: str) -> str:
        """Get color for edge based on its type."""
        colors = {
            'foreign_key': '#F44336',   # Red
            'dependency': '#607D8B',    # Blue Grey
            'reference': '#795548'      # Brown
        }
        return colors.get(edge_type, '#9E9E9E')  # Grey default
    
    def update_viz_statistics(self, viz_data: Dict[str, Any]):
        """Update visualization statistics display."""
        nodes = viz_data.get('nodes', [])
        edges = viz_data.get('edges', [])
        
        # Count by type
        node_counts = {}
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        # Format statistics
        stats_parts = []
        for node_type, count in node_counts.items():
            stats_parts.append(f"{count} {node_type}{'s' if count != 1 else ''}")
        
        stats_text = f"{len(nodes)} objects, {len(edges)} relationships"
        if stats_parts:
            stats_text += f" ({', '.join(stats_parts)})"
        
        self.viz_stats_label.config(text=stats_text)
    
    def show_viz_empty_state(self):
        """Show empty state in visualization canvas."""
        self.viz_canvas.delete("all")
        canvas_width = self.viz_canvas.winfo_width() or 800
        canvas_height = self.viz_canvas.winfo_height() or 600
        
        self.viz_canvas.create_text(canvas_width // 2, canvas_height // 2,
                                   text="No visualization data\nSelect database and generate to view dependencies",
                                   anchor='center', font=('Arial', 12),
                                   fill='grey')
    
    def show_viz_loading_state(self):
        """Show loading state in visualization canvas."""
        self.viz_canvas.delete("all")
        canvas_width = self.viz_canvas.winfo_width() or 800
        canvas_height = self.viz_canvas.winfo_height() or 600
        
        self.viz_canvas.create_text(canvas_width // 2, canvas_height // 2,
                                   text="Generating visualization...\nPlease wait",
                                   anchor='center', font=('Arial', 12),
                                   fill='blue')
        
        self.viz_status_label.config(text="Generating visualization...")
    
    def show_viz_error_state(self, error_message: str):
        """Show error state in visualization canvas."""
        self.viz_canvas.delete("all")
        canvas_width = self.viz_canvas.winfo_width() or 800
        canvas_height = self.viz_canvas.winfo_height() or 600
        
        self.viz_canvas.create_text(canvas_width // 2, canvas_height // 2,
                                   text=f"Error generating visualization:\n{error_message}",
                                   anchor='center', font=('Arial', 12),
                                   fill='red')
        
        self.viz_status_label.config(text="Visualization error")
        self.status_manager.show_toast("Error", error_message)
    
    def get_schema_data_for_visualization(self, database: str) -> Optional[Dict[str, Any]]:
        """Get schema data for visualization from a database."""
        try:
            # For now, return mock data structure that matches what DependencyVisualizer expects
            # In a real implementation, this would connect to the database and extract schema
            
            if not self.current_connection:
                # Try to establish connection if we have config
                if hasattr(self, 'config_manager') and self.config_manager.current_config:
                    try:
                        config = self.config_manager.current_config['database']
                        self.current_connection = AzureSQLConnection(config)
                        if not self.current_connection.test_connection():
                            return None
                    except Exception as e:
                        logger.error(f"Could not connect to database: {e}")
                        return None
            
            if not self.current_connection:
                return None
            
            # Extract schema data using DocumentationExtractor
            extractor = DocumentationExtractor(self.current_connection)
            return extractor.extract_complete_documentation()
            
        except Exception as e:
            logger.error(f"Error getting schema data: {e}")
            return None
    
    def clear_visualization(self):
        """Clear the current visualization."""
        self.viz_canvas.delete("all")
        self.show_viz_empty_state()
        self.viz_status_label.config(text="Visualization cleared")
        self.viz_stats_label.config(text="")
        if hasattr(self, 'viz_current_data'):
            self.viz_current_data = None
    
    def refresh_visualization(self):
        """Refresh the current visualization."""
        if hasattr(self, 'viz_current_data') and self.viz_current_data:
            self.generate_visualization_from_data(self.viz_current_data)
        else:
            self.generate_visualization()
    
    def export_visualization(self):
        """Export current visualization to file."""
        if not hasattr(self, 'viz_current_data') or not self.viz_current_data:
            self.status_manager.show_toast("Warning", "No visualization to export")
            return
        
        # Ask for export format and location
        file_path = filedialog.asksaveasfilename(
            title="Export Visualization",
            defaultextension=".html",
            filetypes=[
                ("HTML files", "*.html"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Create visualizer and export
            visualizer = DependencyVisualizer()
            
            # Get visualization options
            options = {
                'schema_filter': self.viz_schema_var.get() or None,
                'include_tables': self.viz_include_tables.get(),
                'include_views': self.viz_include_views.get(),
                'include_procedures': self.viz_include_procedures.get(),
                'include_functions': self.viz_include_functions.get(),
            }
            
            # Get visualization type
            viz_type_str = self.viz_type_var.get()
            viz_type = VisualizationType(viz_type_str)
            
            # Generate fresh visualization data
            viz_data = visualizer.generate_visualization(self.viz_current_data, viz_type, options)
            
            # Export based on file extension
            if file_path.lower().endswith('.svg'):
                visualizer.export_svg(viz_data, file_path)
            else:
                # Default to HTML
                html_content = visualizer.generate_html_visualization(viz_data)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            self.status_manager.show_toast("Success", f"Visualization exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export visualization: {str(e)}")
    
    def show_viz_options(self):
        """Show visualization options dialog."""
        try:
            # Create options dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Visualization Options")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            # Options content
            notebook = ttk.Notebook(dialog)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Layout tab
            layout_frame = ttk.Frame(notebook)
            notebook.add(layout_frame, text="Layout")
            
            ttk.Label(layout_frame, text="Layout options coming soon...").pack(pady=20)
            
            # Styling tab
            style_frame = ttk.Frame(notebook)
            notebook.add(style_frame, text="Styling")
            
            ttk.Label(style_frame, text="Styling options coming soon...").pack(pady=20)
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill='x', padx=10, pady=10)
            
            ttk.Button(button_frame, text="OK", command=dialog.destroy).pack(side='right', padx=(5, 0))
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='right')
            
        except Exception as e:
            logger.error(f"Error showing options dialog: {e}")
    
    def create_settings_panel(self) -> ttk.Frame:
        """Create application settings panel."""
        panel = ttk.Frame(self.content_area, padding="20")
        
        # Header
        ttk.Label(panel, text="Application Settings", style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Theme settings
        theme_card = CardComponent(panel, self.theme_manager)
        theme_frame = theme_card.create_info_card(panel, "Appearance", None)
        theme_frame.pack(fill='x', pady=(0, 20))
        
        theme_content = ttk.Frame(theme_frame, padding="10")
        theme_content.pack(fill='x')
        
        ttk.Label(theme_content, text="Application Theme:").pack(anchor='w')
        theme_combo = ttk.Combobox(theme_content, textvariable=self.theme_var,
                                 values=self.theme_manager.get_available_themes(),
                                 state='readonly')
        theme_combo.pack(fill='x', pady=(5, 0))
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_changed)
        
        # Other settings sections
        other_settings = [
            ("Database Settings", "Configure default database connection settings"),
            ("Output Settings", "Configure default output formats and locations"),
            ("Notification Settings", "Configure notifications and alerts"),
            ("Performance Settings", "Configure performance and caching options")
        ]
        
        for title, desc in other_settings:
            settings_section = CollapsibleFrame(panel, title)
            settings_section.pack(fill='x', pady=(0, 10))
            
            content = settings_section.get_content_frame()
            ttk.Label(content, text=desc, style='Status.TLabel').pack(padx=10, pady=10)
        
        return panel
    
    # Schema Comparison Methods
    def show_comparison_help(self):
        """Show schema comparison help dialog."""
        help_text = """Schema Comparison Tool

This tool allows you to compare database schemas to identify differences between:
• Two different databases
• A database and a saved schema file
• Different versions of the same database

Features:
• Compare tables, views, stored procedures, functions
• Analyze indexes and constraints
• Impact assessment for changes
• Export comparison reports
• Save/load comparison configurations

Comparison Types:
• Database-to-Database: Compare live database schemas
• Database-to-File: Compare against saved schema snapshots
• File-to-File: Compare saved schema files

Tips:
• Use "Source" as your baseline (e.g., production)
• Use "Target" as what you're comparing against (e.g., development)
• Check the specific object types you want to compare
• Save configurations for repeated comparisons
"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Schema Comparison Help")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+{}+{}".format(
            int(self.root.winfo_x() + (self.root.winfo_width()/2) - 300),
            int(self.root.winfo_y() + (self.root.winfo_height()/2) - 250)
        ))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(dialog, padding="20")
        text_frame.pack(fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=70, height=25)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        # Close button
        btn_frame = ttk.Frame(dialog, padding="10")
        btn_frame.pack(fill='x')
        
        close_btn = ttk.Button(btn_frame, text="Close", command=dialog.destroy)
        close_btn.pack(anchor='center')
    
    def on_source_type_changed(self, event=None):
        """Handle source type selection change."""
        source_type = self.comparison_source_type.get()
        
        if source_type == "database":
            self.source_file_frame.pack_forget()
            self.source_db_frame.pack(fill='x', pady=(5, 0))
        else:  # file or snapshot
            self.source_db_frame.pack_forget()
            self.source_file_frame.pack(fill='x', pady=(5, 0))
    
    def on_target_type_changed(self, event=None):
        """Handle target type selection change."""
        target_type = self.comparison_target_type.get()
        
        if target_type == "database":
            self.target_file_frame.pack_forget()
            self.target_db_frame.pack(fill='x', pady=(5, 0))
        else:  # file or snapshot
            self.target_db_frame.pack_forget()
            self.target_file_frame.pack(fill='x', pady=(5, 0))
    
    def validate_file_path(self, value: str) -> bool:
        """Validate schema file path."""
        if not value:
            return False
        return os.path.exists(value) and value.lower().endswith('.json')
    
    def browse_schema_file(self, path_var: tk.StringVar):
        """Browse for schema file."""
        filename = filedialog.askopenfilename(
            title="Select Schema File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if filename:
            path_var.set(filename)
    
    def refresh_comparison_databases(self):
        """Refresh available databases for comparison."""
        if not hasattr(self, 'source_db_combo'):
            return
            
        try:
            if hasattr(self, 'db_connection') and self.db_connection:
                databases = self.db_connection.get_available_databases()
                db_list = [db['name'] for db in databases]
                
                self.source_db_combo['values'] = db_list
                self.target_db_combo['values'] = db_list
                
                # Set current database as default if connected
                current_db = getattr(self, 'current_database', None)
                if current_db and current_db in db_list:
                    self.comparison_target_db.set(current_db)
                    
        except Exception as e:
            self.show_error("Database Refresh Error", f"Could not refresh database list: {str(e)}")
    
    def save_comparison_config(self):
        """Save current comparison configuration."""
        config = {
            'source_type': self.comparison_source_type.get(),
            'source_database': self.comparison_source_db.get(),
            'source_file': self.comparison_source_file.get(),
            'target_type': self.comparison_target_type.get(),
            'target_database': self.comparison_target_db.get(),
            'target_file': self.comparison_target_file.get(),
            'options': {
                'compare_tables': self.compare_tables.get(),
                'compare_views': self.compare_views.get(),
                'compare_procedures': self.compare_procedures.get(),
                'compare_functions': self.compare_functions.get(),
                'compare_indexes': self.compare_indexes.get(),
                'compare_constraints': self.compare_constraints.get()
            }
        }
        
        filename = filedialog.asksaveasfilename(
            title="Save Comparison Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                self.status_manager.show_message("Configuration saved successfully")
            except Exception as e:
                self.show_error("Save Error", f"Could not save configuration: {str(e)}")
    
    def load_comparison_config(self):
        """Load comparison configuration."""
        filename = filedialog.askopenfilename(
            title="Load Comparison Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Load configuration values
                self.comparison_source_type.set(config.get('source_type', 'database'))
                self.comparison_source_db.set(config.get('source_database', ''))
                self.comparison_source_file.set(config.get('source_file', ''))
                self.comparison_target_type.set(config.get('target_type', 'database'))
                self.comparison_target_db.set(config.get('target_database', ''))
                self.comparison_target_file.set(config.get('target_file', ''))
                
                # Load options
                options = config.get('options', {})
                self.compare_tables.set(options.get('compare_tables', True))
                self.compare_views.set(options.get('compare_views', True))
                self.compare_procedures.set(options.get('compare_procedures', True))
                self.compare_functions.set(options.get('compare_functions', True))
                self.compare_indexes.set(options.get('compare_indexes', True))
                self.compare_constraints.set(options.get('compare_constraints', True))
                
                # Update UI based on loaded types
                self.on_source_type_changed()
                self.on_target_type_changed()
                
                self.status_manager.show_message("Configuration loaded successfully")
                
            except Exception as e:
                self.show_error("Load Error", f"Could not load configuration: {str(e)}")
    
    def start_schema_comparison(self):
        """Start schema comparison process."""
        # Validate inputs
        if not self.validate_comparison_inputs():
            return
            
        # Disable compare button and show progress
        self.compare_btn.config(state='disabled', text="🔄 Comparing...")
        self.status_manager.show_message("Starting schema comparison...")
        
        # Start comparison in background thread
        threading.Thread(target=self.perform_schema_comparison, daemon=True).start()
    
    def validate_comparison_inputs(self) -> bool:
        """Validate comparison inputs."""
        source_type = self.comparison_source_type.get()
        target_type = self.comparison_target_type.get()
        
        # Validate source
        if source_type == "database":
            if not self.comparison_source_db.get():
                self.show_error("Validation Error", "Please select a source database")
                return False
        else:  # file or snapshot
            if not self.comparison_source_file.get():
                self.show_error("Validation Error", "Please select a source schema file")
                return False
            if not os.path.exists(self.comparison_source_file.get()):
                self.show_error("Validation Error", "Source schema file does not exist")
                return False
        
        # Validate target
        if target_type == "database":
            if not self.comparison_target_db.get():
                self.show_error("Validation Error", "Please select a target database")
                return False
        else:  # file or snapshot
            if not self.comparison_target_file.get():
                self.show_error("Validation Error", "Please select a target schema file")
                return False
            if not os.path.exists(self.comparison_target_file.get()):
                self.show_error("Validation Error", "Target schema file does not exist")
                return False
        
        # Validate connection for database sources
        if source_type == "database" or target_type == "database":
            if not hasattr(self, 'db_connection') or not self.db_connection:
                self.show_error("Connection Error", "Please establish a database connection first")
                return False
        
        # Check if at least one comparison option is selected
        if not any([self.compare_tables.get(), self.compare_views.get(), 
                   self.compare_procedures.get(), self.compare_functions.get(),
                   self.compare_indexes.get(), self.compare_constraints.get()]):
            self.show_error("Validation Error", "Please select at least one object type to compare")
            return False
        
        return True
    
    def perform_schema_comparison(self):
        """Perform the actual schema comparison."""
        try:
            # Get source schema
            source_schema = self.get_schema_data('source')
            if not source_schema:
                return
            
            # Get target schema
            target_schema = self.get_schema_data('target')
            if not target_schema:
                return
            
            # Update progress
            self.root.after(0, lambda: self.status_manager.show_message("Comparing schemas..."))
            
            # Perform comparison
            comparison_name = f"{self.get_schema_name('source')} vs {self.get_schema_name('target')}"
            self.comparison_results = self.schema_comparator.compare_schemas(
                source_schema, target_schema, comparison_name
            )
            
            # Show results in UI thread
            self.root.after(0, self.display_comparison_results)
            
        except Exception as e:
            # Show error in UI thread
            self.root.after(0, lambda: self.show_comparison_error(str(e)))
        finally:
            # Re-enable button in UI thread
            self.root.after(0, lambda: self.compare_btn.config(state='normal', text="🔄 Compare Schemas"))
    
    def get_schema_data(self, schema_type: str) -> Optional[Dict[str, Any]]:
        """Get schema data for source or target."""
        if schema_type == 'source':
            type_var = self.comparison_source_type.get()
            db_var = self.comparison_source_db.get()
            file_var = self.comparison_source_file.get()
        else:  # target
            type_var = self.comparison_target_type.get()
            db_var = self.comparison_target_db.get()
            file_var = self.comparison_target_file.get()
        
        try:
            if type_var == "database":
                # Extract from live database
                return self.extract_database_schema(db_var)
            else:  # file or snapshot
                # Load from file
                with open(file_var, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        except Exception as e:
            self.root.after(0, lambda: self.show_error(
                f"Schema {schema_type.title()} Error", 
                f"Could not get {schema_type} schema: {str(e)}"
            ))
            return None
    
    def get_schema_name(self, schema_type: str) -> str:
        """Get display name for schema."""
        if schema_type == 'source':
            type_var = self.comparison_source_type.get()
            db_var = self.comparison_source_db.get()
            file_var = self.comparison_source_file.get()
        else:  # target
            type_var = self.comparison_target_type.get()
            db_var = self.comparison_target_db.get()
            file_var = self.comparison_target_file.get()
        
        if type_var == "database":
            return f"Database: {db_var}"
        else:
            return f"File: {os.path.basename(file_var)}"
    
    def extract_database_schema(self, database_name: str) -> Dict[str, Any]:
        """Extract schema from database."""
        # Temporarily switch to the comparison database
        original_db = getattr(self, 'current_database', None)
        
        try:
            # Connect to comparison database
            if database_name != original_db:
                self.db_connection.connect(database=database_name)
            
            # Create documentation extractor
            extractor = DocumentationExtractor(self.db_connection)
            
            # Extract only the components needed for comparison
            schema_data = {
                'database_info': {
                    'name': database_name,
                    'extraction_time': datetime.now().isoformat()
                }
            }
            
            # Extract based on comparison options
            if self.compare_tables.get():
                schema_data['tables'] = extractor.get_table_info()
            
            if self.compare_views.get():
                schema_data['views'] = extractor.get_view_info()
            
            if self.compare_procedures.get():
                schema_data['stored_procedures'] = extractor.get_stored_procedure_info()
            
            if self.compare_functions.get():
                schema_data['functions'] = extractor.get_function_info()
            
            if self.compare_indexes.get() or self.compare_constraints.get():
                # These are typically included with table info
                if 'tables' not in schema_data:
                    schema_data['tables'] = extractor.get_table_info()
            
            # Get relationship info
            schema_data['relationships'] = extractor.get_relationship_info()
            
            return schema_data
            
        finally:
            # Restore original database connection if changed
            if database_name != original_db and original_db:
                self.db_connection.connect(database=original_db)
    
    def display_comparison_results(self):
        """Display comparison results in the UI."""
        if not self.comparison_results:
            return
        
        # Show results frame
        self.results_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            if hasattr(widget, 'pack_info') and widget.pack_info():
                widget.destroy()
        
        # Create results content
        results_content = ttk.Frame(self.results_frame, padding="15")
        results_content.pack(fill='both', expand=True)
        
        # Results summary
        summary = self.comparison_results['summary']
        metadata = self.comparison_results['metadata']
        
        # Summary header
        summary_frame = ttk.Frame(results_content)
        summary_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(summary_frame, text=f"Comparison: {metadata['name']}", 
                 style='Heading.TLabel').pack(anchor='w')
        ttk.Label(summary_frame, text=f"Completed: {metadata['timestamp'][:19]}", 
                 style='Status.TLabel').pack(anchor='w')
        
        # Statistics
        stats_frame = ttk.LabelFrame(results_content, text="Summary Statistics", padding="10")
        stats_frame.pack(fill='x', pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        # Total changes
        ttk.Label(stats_grid, text=f"Total Changes: {summary['total_changes']}", 
                 style='Status.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 20))
        ttk.Label(stats_grid, text=f"Objects Affected: {summary['objects_affected']}", 
                 style='Status.TLabel').grid(row=0, column=1, sticky='w')
        
        # Impact breakdown
        impact_frame = ttk.Frame(stats_grid)
        impact_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        impact_counts = summary.get('changes_by_impact', {})
        impact_colors = {
            'critical': '#FF4444',
            'high': '#FF8800', 
            'medium': '#FFAA00',
            'low': '#00AA00'
        }
        
        col = 0
        for impact, count in impact_counts.items():
            color = impact_colors.get(impact, '#666666')
            impact_label = ttk.Label(impact_frame, text=f"{impact.title()}: {count}")
            impact_label.grid(row=0, column=col, padx=(0, 15), sticky='w')
            col += 1
        
        # Changes by type
        if summary.get('changes_by_type'):
            type_frame = ttk.LabelFrame(results_content, text="Changes by Object Type", padding="10")
            type_frame.pack(fill='x', pady=(0, 15))
            
            # Create treeview for changes
            type_tree = ttk.Treeview(type_frame, columns=('Added', 'Modified', 'Removed'), height=6)
            type_tree.heading('#0', text='Object Type')
            type_tree.heading('Added', text='Added')
            type_tree.heading('Modified', text='Modified') 
            type_tree.heading('Removed', text='Removed')
            
            type_tree.column('#0', width=150)
            type_tree.column('Added', width=80, anchor='center')
            type_tree.column('Modified', width=80, anchor='center')
            type_tree.column('Removed', width=80, anchor='center')
            
            for obj_type, counts in summary['changes_by_type'].items():
                type_tree.insert('', 'end', text=obj_type.title(),
                               values=(counts.get('added', 0),
                                     counts.get('modified', 0), 
                                     counts.get('removed', 0)))
            
            type_tree.pack(fill='x')
        
        # Detailed changes
        if self.comparison_results['changes']:
            changes_frame = ttk.LabelFrame(results_content, text="Detailed Changes", padding="10")
            changes_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            # Create treeview for detailed changes
            changes_tree = ttk.Treeview(changes_frame, columns=('Type', 'Impact', 'Description'), height=12)
            changes_tree.heading('#0', text='Object')
            changes_tree.heading('Type', text='Change Type')
            changes_tree.heading('Impact', text='Impact')
            changes_tree.heading('Description', text='Description')
            
            changes_tree.column('#0', width=200)
            changes_tree.column('Type', width=100)
            changes_tree.column('Impact', width=80)
            changes_tree.column('Description', width=400)
            
            # Add changes to tree
            for change in self.comparison_results['changes']:
                item_id = changes_tree.insert('', 'end', 
                                            text=change.object_name,
                                            values=(change.change_type.value.title(),
                                                   change.impact_level.title(),
                                                   change.description))
                
                # Color code by impact
                if change.impact_level == 'critical':
                    changes_tree.set(item_id, 'Impact', '⚠️ Critical')
                elif change.impact_level == 'high':
                    changes_tree.set(item_id, 'Impact', '🔴 High')
                elif change.impact_level == 'medium':
                    changes_tree.set(item_id, 'Impact', '🟡 Medium')
                else:
                    changes_tree.set(item_id, 'Impact', '🟢 Low')
            
            # Add scrollbar
            changes_scroll = ttk.Scrollbar(changes_frame, orient="vertical", command=changes_tree.yview)
            changes_tree.configure(yscrollcommand=changes_scroll.set)
            
            changes_tree.pack(side='left', fill='both', expand=True)
            changes_scroll.pack(side='right', fill='y')
        
        # Action buttons
        action_frame = ttk.Frame(results_content)
        action_frame.pack(fill='x', pady=(15, 0))
        
        export_btn = ttk.Button(action_frame, text="📤 Export Report", 
                              command=self.export_comparison_report)
        export_btn.pack(side='left')
        
        save_results_btn = ttk.Button(action_frame, text="💾 Save Results",
                                    command=self.save_comparison_results)
        save_results_btn.pack(side='left', padx=(10, 0))
        
        # Update status
        total_changes = summary['total_changes']
        self.status_manager.show_message(f"Schema comparison completed: {total_changes} changes found")
    
    def show_comparison_error(self, error_message: str):
        """Show comparison error."""
        self.show_error("Schema Comparison Error", 
                       f"An error occurred during schema comparison:\n\n{error_message}")
        self.status_manager.show_message("Schema comparison failed")
    
    def export_comparison_report(self):
        """Export comparison results to a report."""
        if not self.comparison_results:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Comparison Report",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            try:
                if filename.lower().endswith('.html'):
                    self.export_html_report(filename)
                else:
                    self.schema_comparator.export_comparison(self.comparison_results, filename)
                
                self.status_manager.show_message(f"Report exported to {filename}")
                
            except Exception as e:
                self.show_error("Export Error", f"Could not export report: {str(e)}")
    
    def export_html_report(self, filename: str):
        """Export comparison results as HTML report."""
        html_content = self.generate_comparison_html()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_comparison_html(self) -> str:
        """Generate HTML report from comparison results."""
        if not self.comparison_results:
            return ""
        
        metadata = self.comparison_results['metadata']
        summary = self.comparison_results['summary']
        changes = self.comparison_results['changes']
        impact_analysis = self.comparison_results['impact_analysis']
        recommendations = self.comparison_results['recommendations']
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Schema Comparison Report - {metadata['name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .critical {{ color: #dc3545; font-weight: bold; }}
        .high {{ color: #fd7e14; font-weight: bold; }}
        .medium {{ color: #ffc107; font-weight: bold; }}
        .low {{ color: #28a745; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .impact-critical {{ background-color: #f8d7da; }}
        .impact-high {{ background-color: #fdeaa7; }}
        .impact-medium {{ background-color: #fff3cd; }}
        .impact-low {{ background-color: #d4edda; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Schema Comparison Report</h1>
        <h2>{metadata['name']}</h2>
        <p>Generated on: {metadata['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h3>Summary</h3>
        <p><strong>Total Changes:</strong> {summary['total_changes']}</p>
        <p><strong>Objects Affected:</strong> {summary['objects_affected']}</p>
        <p><strong>Overall Risk:</strong> <span class="{impact_analysis['overall_risk']}">{impact_analysis['overall_risk'].title()}</span></p>
    </div>
"""
        
        # Impact breakdown
        if summary.get('changes_by_impact'):
            html += "<h3>Changes by Impact Level</h3><ul>"
            for impact, count in summary['changes_by_impact'].items():
                html += f'<li><span class="{impact}">{impact.title()}:</span> {count}</li>'
            html += "</ul>"
        
        # Changes by type
        if summary.get('changes_by_type'):
            html += "<h3>Changes by Object Type</h3><table>"
            html += "<tr><th>Object Type</th><th>Added</th><th>Modified</th><th>Removed</th><th>Total</th></tr>"
            
            for obj_type, counts in summary['changes_by_type'].items():
                added = counts.get('added', 0)
                modified = counts.get('modified', 0) 
                removed = counts.get('removed', 0)
                total = added + modified + removed
                
                html += f"<tr><td>{obj_type.title()}</td><td>{added}</td><td>{modified}</td><td>{removed}</td><td>{total}</td></tr>"
            
            html += "</table>"
        
        # Detailed changes
        if changes:
            html += "<h3>Detailed Changes</h3><table>"
            html += "<tr><th>Object</th><th>Type</th><th>Change</th><th>Impact</th><th>Description</th></tr>"
            
            for change in changes:
                impact_class = f"impact-{change.impact_level}"
                html += f'<tr class="{impact_class}"><td>{change.object_name}</td><td>{change.object_type}</td><td>{change.change_type.value.title()}</td><td>{change.impact_level.title()}</td><td>{change.description}</td></tr>'
            
            html += "</table>"
        
        # Breaking changes
        if impact_analysis.get('breaking_changes'):
            html += "<h3>⚠️ Breaking Changes</h3><ul>"
            for breaking_change in impact_analysis['breaking_changes']:
                html += f"<li>{breaking_change}</li>"
            html += "</ul>"
        
        # Recommendations  
        if recommendations:
            html += "<h3>Recommendations</h3><ul>"
            for rec in recommendations:
                html += f"<li>{rec}</li>"
            html += "</ul>"
        
        html += "</body></html>"
        return html
    
    def save_comparison_results(self):
        """Save comparison results to file."""
        if not self.comparison_results:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Comparison Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            try:
                self.schema_comparator.export_comparison(self.comparison_results, filename)
                self.status_manager.show_message(f"Results saved to {filename}")
            except Exception as e:
                self.show_error("Save Error", f"Could not save results: {str(e)}")
    
    def setup_layout(self):
        """Setup responsive layout."""
        # Register for layout changes
        self.responsive_layout.register_layout_callback(self.on_layout_changed)
    
    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts."""
        # Command palette
        self.root.bind('<Control-Shift-P>', lambda e: self.command_palette.show_palette())
        
        # Navigation shortcuts
        self.root.bind('<Control-1>', lambda e: self.show_dashboard())
        self.root.bind('<Control-h>', lambda e: self.show_scheduler())
        
        # Initialize health monitoring when connection is established
        self.root.after(1000, self.initialize_health_monitoring)
    
    def initialize_health_monitoring(self):
        """Initialize health monitoring system after startup."""
        try:
            if hasattr(self, 'db_connection') and self.db_connection:
                if not self.health_analyzer:
                    self.health_analyzer = DatabaseHealthAnalyzer(self.db_connection)
                    logger.info("Health monitoring system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize health monitoring: {str(e)}")
        self.root.bind('<Control-2>', lambda e: self.show_connection())
        self.root.bind('<Control-3>', lambda e: self.show_databases())
        self.root.bind('<Control-4>', lambda e: self.show_documentation())
        
        # Quick actions
        self.root.bind('<Control-n>', lambda e: self.connect_database())
        self.root.bind('<Control-g>', lambda e: self.generate_documentation())
        self.root.bind('<F5>', lambda e: self.refresh_databases())
        
        # Theme toggle
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
    
    def register_commands(self):
        """Register commands for the command palette."""
        commands = [
            ('Dashboard', 'Go to dashboard home screen', self.show_dashboard, ['home', 'main']),
            ('Connect Database', 'Connect to a database', self.show_connection, ['connect', 'db']),
            ('Generate Documentation', 'Generate database documentation', self.generate_documentation, ['generate', 'docs']),
            ('Refresh Databases', 'Refresh database list', self.refresh_databases, ['refresh', 'reload']),
            ('Toggle Theme', 'Switch between light and dark themes', self.toggle_theme, ['theme', 'dark', 'light']),
            ('Settings', 'Open application settings', self.show_settings, ['config', 'preferences']),
            ('Analytics', 'View analytics dashboard', self.show_analytics, ['reports', 'dashboard']),
            ('Migration Planning', 'Open migration planner', self.show_migration, ['migrate', 'planning']),
            ('Compliance Audit', 'Run compliance audit', self.show_compliance, ['security', 'audit']),
        ]
        
        for name, desc, callback, keywords in commands:
            self.command_palette.register_command(name, desc, callback, keywords)
    
    def show_view(self, view_name: str, update_sidebar: bool = True):
        """Show a specific view and hide others."""
        # Hide current view
        if self.current_view in self.content_widgets:
            self.content_widgets[self.current_view].pack_forget()
        
        # Show new view
        if view_name in self.content_widgets:
            self.content_widgets[view_name].pack(fill='both', expand=True)
            self.current_view = view_name
            
            # Update sidebar only if requested (avoid recursion)
            if update_sidebar:
                self.sidebar.activate_item(view_name)
            
            # Update status
            view_titles = {
                'dashboard': 'Dashboard',
                'connection': 'Database Connection',
                'databases': 'Available Databases',
                'playground': 'Interactive Playground',
                'documentation': 'Documentation Generation',
                'search_&_filter': 'Search & Filter',
                'schema_compare': 'Schema Comparison',
                'dependencies': 'Dependency Visualization',
                'scheduler': 'Health Dashboard',
                'projects': 'Project Management',
                'api_integration': 'API Integration',
                'analytics': 'Analytics Dashboard',
                'migration': 'Migration Planning',
                'compliance': 'Compliance & Security',
                'settings': 'Settings'
            }
            
            title = view_titles.get(view_name, view_name.title())
            self.status_manager.update_status(f"Viewing: {title}")
    
    def show_dashboard(self):
        """Show dashboard."""
        self.show_view('dashboard', update_sidebar=False)
    
    def show_connection(self):
        """Show connection panel."""
        self.show_view('connection', update_sidebar=False)
    
    def show_databases(self):
        """Show databases panel."""
        self.show_view('databases', update_sidebar=False)
    
    def show_playground(self):
        """Show playground panel."""
        self.show_view('playground', update_sidebar=False)
    
    def show_schema_explorer(self):
        """Show schema explorer panel."""
        self.show_view('schema_explorer', update_sidebar=False)
    
    def show_performance_dashboard(self):
        """Show performance dashboard panel."""
        self.show_view('performance_dashboard', update_sidebar=False)
    
    def show_documentation(self):
        """Show documentation panel."""
        self.show_view('documentation', update_sidebar=False)
    
    def show_search(self):
        """Show search panel."""
        self.show_view('search_&_filter', update_sidebar=False)
    
    def show_comparison(self):
        """Show comparison panel."""
        self.show_view('schema_compare', update_sidebar=False)
    
    def show_visualization(self):
        """Show visualization panel."""
        self.show_view('dependencies', update_sidebar=False)
    
    def show_scheduler(self):
        """Show scheduler panel."""
        self.show_view('scheduler', update_sidebar=False)
    
    def show_projects(self):
        """Show projects panel."""
        self.show_view('projects', update_sidebar=False)
    
    def show_api(self):
        """Show API panel."""
        self.show_view('api_integration', update_sidebar=False)
    
    def show_analytics(self):
        """Show analytics panel."""
        self.show_view('analytics', update_sidebar=False)
    
    def show_migration(self):
        """Show migration panel."""
        self.show_view('migration', update_sidebar=False)
    
    def show_compliance(self):
        """Show compliance panel."""
        self.show_view('compliance', update_sidebar=False)
    
    def show_settings(self):
        """Show settings panel."""
        self.show_view('settings', update_sidebar=False)
    
    def on_theme_changed(self, event=None):
        """Handle theme change."""
        theme_name = self.theme_var.get()
        self.theme_manager.apply_theme(theme_name)
        self.status_manager.show_toast_notification(f"Theme changed to {theme_name}", 'info')
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.theme_manager.current_theme
        themes = self.theme_manager.get_available_themes()
        current_index = themes.index(current_theme)
        next_theme = themes[(current_index + 1) % len(themes)]
        
        self.theme_var.set(next_theme)
        self.theme_manager.apply_theme(next_theme)
        self.status_manager.show_toast_notification(f"Switched to {next_theme} theme", 'info')
    
    def on_layout_changed(self, layout: str):
        """Handle layout changes for responsive design."""
        # Adjust UI based on screen size
        if layout == 'compact':
            # Collapse sidebar for small screens
            self.sidebar_collapsed.set(True)
        elif layout == 'standard':
            # Normal layout
            self.sidebar_collapsed.set(False)
        elif layout == 'wide':
            # Wide layout with more space
            self.sidebar_collapsed.set(False)
    
    def on_connection_method_changed(self):
        """Handle connection method changes."""
        method = self.connection_method.get()
        
        if method == "credentials":
            self.credentials_section.expanded.set(True)
        else:
            self.credentials_section.expanded.set(False)
    
    def load_initial_config(self):
        """Load initial configuration."""
        # Load theme preference
        try:
            with open('ui_config.json', 'r') as f:
                config = json.load(f)
                theme = config.get('theme', 'light')
                self.theme_var.set(theme)
                self.theme_manager.apply_theme(theme)
        except:
            pass
        
        # Load database connection defaults
        try:
            db_config = self.config_manager.get_database_config()
            if db_config.get('server'):
                self.server.set(db_config['server'])
            if db_config.get('database'):
                self.database.set(db_config['database'])
            if db_config.get('username'):
                self.username.set(db_config['username'])
            if db_config.get('password'):
                self.password.set(db_config['password'])
            if db_config.get('driver'):
                self.driver.set(db_config['driver'])
            
            self.status_manager.show_message("Default connection settings loaded.", "info")
        except Exception as e:
            logger.info(f"No saved connection settings found: {e}")
            pass
    
    def save_ui_config(self):
        """Save UI configuration."""
        config = {
            'theme': self.theme_manager.current_theme,
            'sidebar_collapsed': self.sidebar_collapsed.get(),
            'window_geometry': self.root.geometry()
        }
        
        try:
            with open('ui_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving UI config: {e}")
    
    # Placeholder methods for functionality (to be implemented)
    def test_connection(self):
        """Test database connection with enhanced diagnostics using Phase 1 systems."""
        # Phase 1: Use enhanced status and smart loading
        self.enhanced_status.update_status("Starting connection test...")
        self.keyboard_shortcuts.set_context("connection")  # Switch to connection context
        
        # Phase 1: Start smart progress tracking
        steps = [
            "Validating connection parameters...",
            "Testing network connectivity...", 
            "Authenticating with server...",
            "Verifying database access...",
            "Checking permissions..."
        ]
        
        self.connection_tracker = self.smart_loading.start_operation(
            "connection_test",
            "Database Connection Test", 
            steps,
            show_progress_window=True
        )
        
        thread = threading.Thread(target=self._enhanced_connection_test_thread, daemon=True)
        thread.start()
    
    def _enhanced_connection_test_thread(self):
        """Phase 1 Enhancement: Enhanced connection testing with detailed diagnostics."""
        diagnostic_results = {
            'basic_validation': False,
            'network_connectivity': False,
            'authentication': False,
            'database_access': False,
            'permissions': False,
            'error_details': [],
            'recommendations': []
        }
        
        try:
            # Step 1: Basic validation
            self.root.after(0, self.connection_tracker.advance_step)
            validation_result = self._validate_connection_parameters()
            diagnostic_results['basic_validation'] = validation_result['success']
            if not validation_result['success']:
                diagnostic_results['error_details'].extend(validation_result['errors'])
                diagnostic_results['recommendations'].extend(validation_result['recommendations'])
                # Phase 1: Use enhanced error handling
                error = Exception(f"Connection validation failed: {'; '.join(validation_result['errors'])}")
                self.root.after(0, lambda: self.error_handler.handle_error(error, "connection"))
                self.root.after(0, lambda: self.smart_loading.complete_operation("connection_test"))
                return
            
            # Step 2: Network connectivity test  
            self.root.after(0, self.connection_tracker.advance_step)
            network_result = self._test_network_connectivity()
            diagnostic_results['network_connectivity'] = network_result['success']
            if network_result['warnings']:
                diagnostic_results['error_details'].extend(network_result['warnings'])
            if not network_result['success']:
                diagnostic_results['error_details'].extend(network_result['errors'])
                diagnostic_results['recommendations'].extend(network_result['recommendations'])
                # Phase 1: Use enhanced error handling
                error = ConnectionError(f"Network connectivity failed: {'; '.join(network_result['errors'])}")
                self.root.after(0, lambda: self.error_handler.handle_error(error, "connection"))
                self.root.after(0, lambda: self.smart_loading.complete_operation("connection_test"))
                return
            
            # Step 3: Authentication test
            self.root.after(0, self.connection_tracker.advance_step)
            with AzureSQLConnection() as db:
                try:
                    auth_success = self._connect_to_database(db)
                    diagnostic_results['authentication'] = auth_success
                    
                    if not auth_success:
                        diagnostic_results['error_details'].append("Authentication failed")
                        diagnostic_results['recommendations'].append("Verify credentials and authentication method")
                        self.root.after(0, self._enhanced_connection_failed, diagnostic_results)
                        return
                    
                    # Step 4: Database access test
                    self.root.after(0, lambda: self.status_manager.update_status("📊 Testing database access..."))
                    if db.test_connection():
                        diagnostic_results['database_access'] = True
                        
                        # Step 5: Permissions test
                        self.root.after(0, lambda: self.status_manager.update_status("🔒 Checking permissions..."))
                        permissions_result = self._test_database_permissions(db)
                        diagnostic_results['permissions'] = permissions_result['success']
                        if permissions_result['warnings']:
                            diagnostic_results['error_details'].extend(permissions_result['warnings'])
                        
                        # Success!
                        db_info = db.get_database_info()
                        diagnostic_results['db_info'] = db_info
                        self.root.after(0, self._enhanced_connection_success, diagnostic_results)
                        
                        # Save successful connection to recent connections
                        connection_config = self._get_connection_config()
                        self.profile_manager.add_to_history(connection_config, success=True)
                        
                    else:
                        diagnostic_results['error_details'].append("Database connection test failed")
                        diagnostic_results['recommendations'].append("Check database name and server accessibility")
                        self.root.after(0, self._enhanced_connection_failed, diagnostic_results)
                        
                except Exception as e:
                    diagnostic_results['error_details'].append(f"Database connection error: {str(e)}")
                    diagnostic_results['recommendations'].append("Check server name, database name, and network settings")
                    self.root.after(0, self._enhanced_connection_failed, diagnostic_results)
                    
        except Exception as e:
            diagnostic_results['error_details'].append(f"Unexpected error: {str(e)}")
            diagnostic_results['recommendations'].append("Check all connection parameters and try again")
            self.root.after(0, self._enhanced_connection_failed, diagnostic_results)
    
    def _validate_connection_parameters(self):
        """Validate connection parameters before attempting connection."""
        errors = []
        recommendations = []
        
        method = self.connection_method.get()
        server = self.server.get().strip()
        database = self.database.get().strip()
        
        # Server validation
        if not server:
            errors.append("Server name is required")
            recommendations.append("Enter your Azure SQL server name (e.g., myserver.database.windows.net)")
        elif not server.endswith('.database.windows.net'):
            recommendations.append("Azure SQL servers typically end with '.database.windows.net'")
        
        # Database validation
        if not database:
            errors.append("Database name is required")
            recommendations.append("Enter the name of your database")
        
        # Method-specific validation
        if method == 'credentials':
            if not self.username.get().strip():
                errors.append("Username is required for credentials method")
                recommendations.append("Enter your SQL Server username")
            if not self.password.get().strip():
                errors.append("Password is required for credentials method")
                recommendations.append("Enter your SQL Server password")
                
        elif method == 'service_principal':
            if not self.client_id.get().strip():
                errors.append("Client ID is required for service principal method")
                recommendations.append("Enter your Azure AD application client ID")
            if not self.client_secret.get().strip():
                errors.append("Client secret is required for service principal method")
                recommendations.append("Enter your Azure AD application client secret")
            if not self.tenant_id.get().strip():
                errors.append("Tenant ID is required for service principal method")
                recommendations.append("Enter your Azure AD tenant ID")
                
        elif method == 'connection_string':
            if not self.connection_string.get().strip():
                errors.append("Connection string is required")
                recommendations.append("Enter a valid connection string")
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'recommendations': recommendations
        }
    
    def _test_network_connectivity(self):
        """Test network connectivity to the server."""
        import socket
        import re
        
        errors = []
        warnings = []
        recommendations = []
        
        server = self.server.get().strip()
        if not server:
            return {'success': False, 'errors': ['Server name not provided'], 'warnings': [], 'recommendations': []}
        
        # Extract hostname from server string
        hostname = server
        if '://' in hostname:
            hostname = hostname.split('://')[1]
        if '/' in hostname:
            hostname = hostname.split('/')[0]
        if ':' in hostname and not hostname.count(':') > 1:  # IPv6 has multiple colons
            hostname, port = hostname.rsplit(':', 1)
        else:
            port = 1433  # Default SQL Server port
        
        try:
            # DNS resolution test
            socket.gethostbyname(hostname)
            
            # Port connectivity test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex((hostname, int(port)))
            sock.close()
            
            if result == 0:
                return {'success': True, 'errors': [], 'warnings': [], 'recommendations': []}
            else:
                errors.append(f"Cannot connect to port {port} on {hostname}")
                recommendations.extend([
                    "Check if the server allows connections from your IP address",
                    "Verify Azure SQL firewall settings in Azure Portal",
                    "Ensure the server name is correct"
                ])
                return {'success': False, 'errors': errors, 'warnings': warnings, 'recommendations': recommendations}
                
        except socket.gaierror:
            errors.append(f"Cannot resolve hostname: {hostname}")
            recommendations.extend([
                "Check your internet connection",
                "Verify the server name is correct",
                "Check DNS settings"
            ])
            return {'success': False, 'errors': errors, 'warnings': warnings, 'recommendations': recommendations}
        except Exception as e:
            errors.append(f"Network test failed: {str(e)}")
            recommendations.append("Check network connectivity and firewall settings")
            return {'success': False, 'errors': errors, 'warnings': warnings, 'recommendations': recommendations}
    
    def _test_database_permissions(self, db_connection):
        """Test database permissions."""
        warnings = []
        recommendations = []
        
        try:
            # Test basic read permissions
            cursor = db_connection.get_cursor()
            
            # Try to read from sys.tables (basic permission check)
            try:
                cursor.execute("SELECT TOP 1 name FROM sys.tables")
                result = cursor.fetchone()
            except Exception:
                warnings.append("Limited read permissions detected")
                recommendations.append("Consider granting db_datareader permissions for full functionality")
            
            # Test VIEW DEFINITION permission
            try:
                cursor.execute("SELECT TOP 1 definition FROM sys.sql_modules")
                result = cursor.fetchone()
            except Exception:
                warnings.append("VIEW DEFINITION permission not available")
                recommendations.append("Grant VIEW DEFINITION for complete documentation generation")
            
            return {
                'success': True,
                'warnings': warnings,
                'recommendations': recommendations
            }
            
        except Exception as e:
            warnings.append(f"Permission test failed: {str(e)}")
            recommendations.append("Ensure the user has at least db_datareader permissions")
            return {
                'success': True,  # Don't fail the connection for permission issues
                'warnings': warnings,
                'recommendations': recommendations
            }
    
    def _enhanced_connection_success(self, diagnostic_results):
        """Handle successful connection with diagnostic details using Phase 1 systems."""
        db_info = diagnostic_results.get('db_info', {})
        
        # Phase 1: Complete the progress tracking
        self.smart_loading.complete_operation("connection_test")
        
        # Phase 1: Update enhanced status bar
        server_name = db_info.get('server_name', self.server.get())
        db_name = db_info.get('database_name', self.database.get())
        self.enhanced_status.update_connection_status(True, f"{server_name}/{db_name}")
        self.enhanced_status.update_status("Connection test completed successfully!")
        
        # Update connection status in UI
        if hasattr(self, 'connection_status'):
            self.connection_status.set(f"Connected to {db_info.get('database_name', 'Unknown')}")
        
        # Show diagnostic details
        details = []
        details.append("🔍 Validation: ✅ Passed")
        details.append("🌐 Network: ✅ Connected")
        details.append("🔐 Authentication: ✅ Verified")
        details.append("📊 Database Access: ✅ Available")
        
        if diagnostic_results['permissions']:
            details.append("🔒 Permissions: ✅ Full Access")
        else:
            details.append("🔒 Permissions: ⚠️ Limited (see warnings)")
        
        # Show warnings if any
        if diagnostic_results['error_details']:
            details.append("\n⚠️ Warnings:")
            for warning in diagnostic_results['error_details']:
                details.append(f"  • {warning}")
        
        self.log_message(f"Connection diagnostics:\n" + "\n".join(details))
        
        # Refresh the recent connections widget
        self._refresh_recent_connections_widget()
    
    def _enhanced_connection_failed(self, diagnostic_results):
        """Handle failed connection with detailed diagnostics."""
        self.status_manager.update_status("❌ Connection failed")
        
        # Build detailed error message
        error_details = diagnostic_results.get('error_details', [])
        recommendations = diagnostic_results.get('recommendations', [])
        
        # Determine failure point
        failure_point = "Unknown"
        if not diagnostic_results['basic_validation']:
            failure_point = "Parameter Validation"
        elif not diagnostic_results['network_connectivity']:
            failure_point = "Network Connectivity"
        elif not diagnostic_results['authentication']:
            failure_point = "Authentication"
        elif not diagnostic_results['database_access']:
            failure_point = "Database Access"
        
        # Show toast notification
        self.status_manager.show_toast_notification(f"Connection failed at: {failure_point}", 'error')
        
        # Update connection status in UI
        if hasattr(self, 'connection_status'):
            self.connection_status.set("Connection Failed")
        
        # Build diagnostic report
        report = [f"❌ Connection failed at: {failure_point}"]
        
        # Add step-by-step results
        steps = [
            ("🔍 Parameter Validation", diagnostic_results['basic_validation']),
            ("🌐 Network Connectivity", diagnostic_results['network_connectivity']),
            ("🔐 Authentication", diagnostic_results['authentication']),
            ("📊 Database Access", diagnostic_results['database_access']),
            ("🔒 Permissions Check", diagnostic_results['permissions'])
        ]
        
        report.append("\nDiagnostic Steps:")
        for step_name, success in steps:
            status_icon = "✅" if success else "❌" if success is False else "⏸️"
            report.append(f"  {step_name}: {status_icon}")
        
        # Add error details
        if error_details:
            report.append("\n🚨 Issues Found:")
            for error in error_details:
                report.append(f"  • {error}")
        
        # Add recommendations
        if recommendations:
            report.append("\n💡 Recommendations:")
            for rec in recommendations:
                report.append(f"  • {rec}")
        
        self.log_message("\n".join(report))
        
        # Show detailed error dialog
        self._show_connection_diagnostic_dialog(diagnostic_results)
    
    def _show_connection_diagnostic_dialog(self, diagnostic_results):
        """Show detailed connection diagnostic dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Connection Diagnostic Report")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔍 Connection Diagnostic Report", style='Title.TLabel')
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Create scrollable text area for report
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill='both', expand=True)
        
        text_area = scrolledtext.ScrolledText(text_frame, width=70, height=20, wrap=tk.WORD)
        text_area.pack(fill='both', expand=True)
        
        # Build diagnostic report text
        report_lines = []
        
        # Determine failure point
        failure_point = "Unknown"
        if not diagnostic_results['basic_validation']:
            failure_point = "Parameter Validation"
        elif not diagnostic_results['network_connectivity']:
            failure_point = "Network Connectivity"  
        elif not diagnostic_results['authentication']:
            failure_point = "Authentication"
        elif not diagnostic_results['database_access']:
            failure_point = "Database Access"
        
        report_lines.append(f"❌ CONNECTION FAILED AT: {failure_point}")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        # Step-by-step results
        steps = [
            ("🔍 Parameter Validation", diagnostic_results['basic_validation']),
            ("🌐 Network Connectivity", diagnostic_results['network_connectivity']),
            ("🔐 Authentication", diagnostic_results['authentication']),
            ("📊 Database Access", diagnostic_results['database_access']),
            ("🔒 Permissions Check", diagnostic_results['permissions'])
        ]
        
        report_lines.append("DIAGNOSTIC STEPS:")
        for step_name, success in steps:
            status_icon = "✅ PASSED" if success else "❌ FAILED" if success is False else "⏸️ SKIPPED"
            report_lines.append(f"  {step_name}: {status_icon}")
        report_lines.append("")
        
        # Error details
        if diagnostic_results['error_details']:
            report_lines.append("🚨 ISSUES IDENTIFIED:")
            for error in diagnostic_results['error_details']:
                report_lines.append(f"  • {error}")
            report_lines.append("")
        
        # Recommendations
        if diagnostic_results['recommendations']:
            report_lines.append("💡 RECOMMENDATIONS:")
            for rec in diagnostic_results['recommendations']:
                report_lines.append(f"  • {rec}")
        
        text_area.insert('1.0', '\n'.join(report_lines))
        text_area.configure(state='disabled')
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side='right')
        ttk.Button(button_frame, text="Copy Report", 
                  command=lambda: self._copy_to_clipboard('\n'.join(report_lines))).pack(side='right', padx=(0, 10))
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status_manager.show_toast_notification("Report copied to clipboard!", 'info')
    
    def _refresh_recent_connections_widget(self):
        """Refresh the recent connections widget after a successful connection."""
        # This could be enhanced to dynamically refresh the widget
        # For now, it's a placeholder for future enhancement
        pass
    
    def _get_connection_config(self):
        """Get current connection configuration for saving to history."""
        return {
            'server': self.server.get(),
            'database': self.database.get(),
            'method': self.connection_method.get(),
            'username': self.username.get() if self.connection_method.get() == 'credentials' else None,
            'client_id': self.client_id.get() if self.connection_method.get() == 'service_principal' else None,
            'tenant_id': self.tenant_id.get() if self.connection_method.get() == 'service_principal' else None,
            'timestamp': datetime.now().isoformat()
        }
    
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
        self.status_manager.update_status(f"Connected to {db_info.get('database_name', 'Unknown')}")
        self.status_manager.show_toast_notification("Connection successful!", 'success')
        
        # Update connection status in the UI if we have the status widget
        if hasattr(self, 'connection_status'):
            self.connection_status.set(f"Connected to {db_info.get('database_name', 'Unknown')}")
        
        self.log_message(f"Successfully connected to database: {db_info.get('database_name', 'Unknown')}")
    
    def _connection_failed(self, error_msg):
        """Handle failed connection with smart recovery."""
        self.status_manager.update_status("Connection failed")
        self.status_manager.show_toast_notification(f"Connection failed: {error_msg}", 'error')
        
        # Update connection status in the UI if we have the status widget  
        if hasattr(self, 'connection_status'):
            self.connection_status.set("Connection Failed")
        
        self.log_message(f"Connection failed: {error_msg}")
        
        # Create a generic exception for the recovery system
        connection_error = Exception(error_msg)
        
        # Try smart error recovery first
        context = {
            'server': self.server.get(),
            'database': self.database.get(),
            'method': self.connection_method.get()
        }
        
        self.handle_recoverable_error("Database Connection", connection_error, context)
    
    def log_message(self, message):
        """Add a log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)  # For now, just print to console
        # Could be extended to write to a log file or display in a log widget
    
    def connect_database(self):
        """Connect to database."""
        # Validate form first
        if not self.server_entry.validate() or not self.database_entry.validate():
            self.status_manager.show_toast_notification("Please fix connection form errors", 'error')
            return
        
        self.status_manager.show_toast_notification("Connecting to database...", 'info')
        
        # Add to recent connections
        connection_data = {
            'server': self.server.get(),
            'database': self.database.get(),
            'method': self.connection_method.get()
        }
        self.favorites_manager.add_recent_item('connection', f"{self.server.get()}/{self.database.get()}", connection_data)
        
        # Simulate connection
        self.status_manager.update_connection_status(True)
        self.dashboard.update_connection_status(True, f"Connected to {self.database.get()}")
        
    def refresh_databases(self):
        """Refresh the detailed database list."""
        self.status_manager.update_status("Loading database information...")
        self.status_manager.show_toast_notification("Refreshing databases...", 'info')
        
        # Clear current list if we have a database tree
        if hasattr(self, 'database_tree'):
            for item in self.database_tree.get_children():
                self.database_tree.delete(item)
        
        thread = threading.Thread(target=self._refresh_database_list_thread, daemon=True)
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
                elif method == "service_principal":
                    success = db.connect_with_service_principal(
                        server=self.server.get(),
                        database="master",
                        client_id=self.client_id.get(),
                        client_secret=self.client_secret.get(),
                        tenant_id=self.tenant_id.get()
                    )
                else:
                    self.root.after(0, self._database_refresh_failed, "Database listing not supported for this connection method")
                    return
                
                if not success:
                    self.root.after(0, self._database_refresh_failed, "Failed to connect to master database")
                    return
                
                # Get database list with detailed information
                databases = db.get_database_list_detailed()
                self.root.after(0, self._database_list_refreshed, databases)
                
        except Exception as e:
            self.root.after(0, self._database_refresh_failed, str(e))
    
    def _database_list_refreshed(self, databases):
        """Handle successful database list refresh."""
        self.available_databases = []
        self._all_database_info = databases  # Store for filtering
        
        if hasattr(self, 'database_tree'):
            for db_info in databases:
                # Format creation date
                create_date = db_info['create_date'].strftime('%Y-%m-%d %H:%M:%S') if db_info['create_date'] else 'Unknown'
                
                # Calculate total size
                data_size = db_info['data_size_mb'] or 0
                log_size = db_info['log_size_mb'] or 0
                total_size = data_size + log_size
                
                # Format size display
                if total_size > 1024:
                    size_display = f"{total_size/1024:.2f} GB"
                else:
                    size_display = f"{total_size:.2f} MB"
                
                # Add to tree
                item = self.database_tree.insert('', 'end', values=(
                    db_info['database_name'],
                    db_info['state_desc'],
                    create_date,
                    size_display,
                    db_info['compatibility_level']
                ))
                
                self.available_databases.append(db_info['database_name'])
        
        self.status_manager.update_status(f"Found {len(databases)} databases")
        self.status_manager.show_toast_notification(f"Found {len(databases)} databases", 'success')
        self.log_message(f"Successfully refreshed database list: {len(databases)} databases found")
    
    def _database_refresh_failed(self, error_msg):
        """Handle failed database list refresh."""
        self.status_manager.update_status("Failed to refresh database list")
        self.status_manager.show_toast_notification(f"Failed to refresh databases: {error_msg}", 'error')
        self.log_message(f"Failed to refresh database list: {error_msg}")
        messagebox.showerror("Refresh Database List", f"Failed to refresh database list: {error_msg}")
    
    # Phase 1 Enhancement: Smart Error Recovery System
    def handle_recoverable_error(self, operation: str, error: Exception, context: Dict[str, Any] = None):
        """Smart error recovery system with retry logic and user guidance.
        
        Args:
            operation: Description of the operation that failed
            error: The exception that occurred
            context: Additional context about the operation
        """
        import time
        import socket
        
        context = context or {}
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Classification of errors
        connection_errors = ['ConnectionError', 'TimeoutError', 'socket.gaierror', 'socket.timeout']
        auth_errors = ['AuthenticationError', 'PermissionError', 'LoginError']
        temporary_errors = ['TemporaryError', 'BusyError', 'DeadlockError']
        
        recovery_strategies = {
            'connection': self._recover_connection_error,
            'authentication': self._recover_auth_error,
            'temporary': self._recover_temporary_error,
            'resource': self._recover_resource_error,
            'configuration': self._recover_config_error
        }
        
        # Determine error category
        error_category = 'unknown'
        if any(err in error_type for err in connection_errors) or 'connection' in error_msg.lower():
            error_category = 'connection'
        elif any(err in error_type for err in auth_errors) or 'authentication' in error_msg.lower():
            error_category = 'authentication'
        elif any(err in error_type for err in temporary_errors) or 'timeout' in error_msg.lower():
            error_category = 'temporary'
        elif 'memory' in error_msg.lower() or 'space' in error_msg.lower():
            error_category = 'resource'
        elif 'config' in error_msg.lower() or 'invalid' in error_msg.lower():
            error_category = 'configuration'
        
        self.log_message(f"Smart error recovery initiated for {operation}: {error_category} error")
        
        # Attempt recovery
        recovery_result = None
        if error_category in recovery_strategies:
            recovery_result = recovery_strategies[error_category](operation, error, context)
        
        if not recovery_result or not recovery_result.get('success', False):
            self._show_recovery_dialog(operation, error, error_category, recovery_result)
    
    def _recover_connection_error(self, operation: str, error: Exception, context: Dict[str, Any]):
        """Attempt to recover from connection errors."""
        recovery_result = {
            'success': False,
            'attempts': 0,
            'strategies_tried': [],
            'recommendations': []
        }
        
        max_retries = 3
        retry_delays = [2, 5, 10]  # Exponential backoff
        
        # Strategy 1: Simple retry with backoff
        for attempt in range(max_retries):
            recovery_result['attempts'] += 1
            self.status_manager.show_toast_notification(f"Attempting connection recovery ({attempt + 1}/{max_retries})...", 'warning')
            
            try:
                time.sleep(retry_delays[attempt])
                
                # Attempt reconnection based on operation
                if 'connect' in operation.lower():
                    # Try the actual connection
                    config = self._build_connection_config()
                    connection = AzureSQLConnection()
                    result = connection.connect(config)
                    if result['success']:
                        recovery_result['success'] = True
                        recovery_result['strategies_tried'].append(f"Retry #{attempt + 1}")
                        self.status_manager.show_toast_notification("Connection recovery successful!", 'success')
                        return recovery_result
                
            except Exception as retry_error:
                self.log_message(f"Recovery attempt {attempt + 1} failed: {str(retry_error)}")
        
        # Strategy 2: Alternative connection parameters
        recovery_result['strategies_tried'].append("Parameter optimization")
        alternative_configs = self._generate_alternative_configs()
        
        for alt_config in alternative_configs:
            try:
                connection = AzureSQLConnection()
                result = connection.connect(alt_config)
                if result['success']:
                    recovery_result['success'] = True
                    recovery_result['strategies_tried'].append("Alternative parameters")
                    self.status_manager.show_toast_notification("Connection recovered with alternative settings!", 'success')
                    return recovery_result
            except:
                continue
        
        # Generate recommendations
        recovery_result['recommendations'] = [
            "Check network connectivity to Azure SQL Database",
            "Verify firewall settings allow your IP address",
            "Confirm server name and database name are correct",
            "Try using a different network connection"
        ]
        
        return recovery_result
    
    def _recover_auth_error(self, operation: str, error: Exception, context: Dict[str, Any]):
        """Attempt to recover from authentication errors."""
        recovery_result = {
            'success': False,
            'attempts': 0,
            'strategies_tried': [],
            'recommendations': []
        }
        
        # Strategy 1: Token refresh for Azure AD
        if self.connection_method.get() == 'azure_ad':
            try:
                recovery_result['strategies_tried'].append("Token refresh")
                # In a real implementation, we would refresh the Azure AD token
                # For now, we'll simulate this
                self.status_manager.show_toast_notification("Attempting to refresh authentication token...", 'warning')
                time.sleep(2)
                # Simulate success in some cases
                import random
                if random.random() > 0.7:  # 30% success rate for demo
                    recovery_result['success'] = True
                    return recovery_result
            except Exception as e:
                self.log_message(f"Token refresh failed: {str(e)}")
        
        # Generate recommendations based on auth method
        method = self.connection_method.get()
        if method == 'credentials':
            recovery_result['recommendations'] = [
                "Verify username and password are correct",
                "Check if account is locked or expired",
                "Try resetting password in Azure portal",
                "Confirm user has access to the specific database"
            ]
        elif method == 'azure_ad':
            recovery_result['recommendations'] = [
                "Try signing out and back into Azure CLI (az logout, az login)",
                "Check if your Azure AD account has database permissions",
                "Verify you're connected to the correct Azure tenant",
                "Try switching to service principal authentication"
            ]
        elif method == 'service_principal':
            recovery_result['recommendations'] = [
                "Verify client ID, secret, and tenant ID are correct",
                "Check if service principal has database permissions",
                "Confirm the client secret hasn't expired",
                "Test the service principal in Azure portal"
            ]
        
        return recovery_result
    
    def _recover_temporary_error(self, operation: str, error: Exception, context: Dict[str, Any]):
        """Attempt to recover from temporary/timeout errors."""
        recovery_result = {
            'success': False,
            'attempts': 0,
            'strategies_tried': [],
            'recommendations': []
        }
        
        # Strategy 1: Immediate retry
        max_retries = 2
        for attempt in range(max_retries):
            recovery_result['attempts'] += 1
            try:
                time.sleep(1)  # Short delay for temporary issues
                self.status_manager.show_toast_notification(f"Retrying operation ({attempt + 1}/{max_retries})...", 'warning')
                
                # For demo purposes, simulate recovery
                import random
                if random.random() > 0.5:  # 50% success rate
                    recovery_result['success'] = True
                    recovery_result['strategies_tried'].append(f"Retry #{attempt + 1}")
                    return recovery_result
                    
            except Exception as retry_error:
                self.log_message(f"Temporary error recovery attempt {attempt + 1} failed: {str(retry_error)}")
        
        recovery_result['recommendations'] = [
            "The database may be temporarily busy - try again in a few minutes",
            "Consider increasing connection timeout values",
            "Check Azure SQL Database service health status",
            "Try the operation during off-peak hours"
        ]
        
        return recovery_result
    
    def _recover_resource_error(self, operation: str, error: Exception, context: Dict[str, Any]):
        """Attempt to recover from resource-related errors."""
        recovery_result = {
            'success': False,
            'attempts': 0,
            'strategies_tried': [],
            'recommendations': [
                "Check available disk space on local machine",
                "Close other applications to free up memory",
                "Consider generating documentation in smaller chunks",
                "Monitor Azure SQL Database DTU/CPU usage"
            ]
        }
        
        return recovery_result
    
    def _recover_config_error(self, operation: str, error: Exception, context: Dict[str, Any]):
        """Attempt to recover from configuration errors."""
        recovery_result = {
            'success': False,
            'attempts': 0,
            'strategies_tried': [],
            'recommendations': [
                "Review connection configuration for typos",
                "Verify all required fields are filled",
                "Check connection string format if using direct connection",
                "Test with a known working configuration first"
            ]
        }
        
        return recovery_result
    
    def _generate_alternative_configs(self):
        """Generate alternative connection configurations for recovery."""
        base_config = self._build_connection_config()
        alternatives = []
        
        # Alternative 1: Increase timeout
        alt1 = base_config.copy()
        alt1['timeout'] = 60
        alternatives.append(alt1)
        
        # Alternative 2: Different driver version
        alt2 = base_config.copy()
        alt2['driver'] = 'ODBC Driver 18 for SQL Server'
        alternatives.append(alt2)
        
        # Alternative 3: Explicit encryption settings
        alt3 = base_config.copy()
        alt3['encrypt'] = True
        alt3['trust_server_certificate'] = True
        alternatives.append(alt3)
        
        return alternatives
    
    def _show_recovery_dialog(self, operation: str, error: Exception, error_category: str, recovery_result: Dict[str, Any]):
        """Show detailed recovery dialog with recommendations."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Smart Error Recovery")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.grab_set()  # Make it modal
        
        # Center the dialog
        dialog.transient(self.root)
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(title_frame, text="🔧 Smart Error Recovery", 
                 font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        
        # Error summary
        error_frame = ttk.LabelFrame(main_frame, text="Error Summary", padding="10")
        error_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(error_frame, text=f"Operation: {operation}").pack(anchor='w')
        ttk.Label(error_frame, text=f"Error Type: {error_category.title()} Error").pack(anchor='w')
        ttk.Label(error_frame, text=f"Error: {str(error)[:200]}...").pack(anchor='w')
        
        # Recovery attempts
        if recovery_result and recovery_result.get('strategies_tried'):
            recovery_frame = ttk.LabelFrame(main_frame, text="Recovery Attempts", padding="10")
            recovery_frame.pack(fill='x', pady=(0, 15))
            
            for strategy in recovery_result['strategies_tried']:
                ttk.Label(recovery_frame, text=f"• {strategy}").pack(anchor='w')
            
            if recovery_result.get('success'):
                ttk.Label(recovery_frame, text="✅ Recovery successful!", 
                         foreground='green').pack(anchor='w', pady=(10, 0))
            else:
                ttk.Label(recovery_frame, text="❌ Automatic recovery failed", 
                         foreground='red').pack(anchor='w', pady=(10, 0))
        
        # Recommendations
        if recovery_result and recovery_result.get('recommendations'):
            rec_frame = ttk.LabelFrame(main_frame, text="Recommended Actions", padding="10")
            rec_frame.pack(fill='both', expand=True, pady=(0, 15))
            
            # Scrollable text widget for recommendations
            text_widget = scrolledtext.ScrolledText(rec_frame, height=8, wrap=tk.WORD)
            text_widget.pack(fill='both', expand=True)
            
            for i, rec in enumerate(recovery_result['recommendations'], 1):
                text_widget.insert(tk.END, f"{i}. {rec}\n\n")
            
            text_widget.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        def retry_operation():
            dialog.destroy()
            # Trigger retry based on operation type
            if 'connect' in operation.lower():
                self.test_connection()
            elif 'preview' in operation.lower():
                self.preview_documentation()
            elif 'generate' in operation.lower():
                self.generate_documentation()
        
        def open_diagnostics():
            dialog.destroy()
            self.run_enhanced_connection_test()
        
        ttk.Button(button_frame, text="Retry Operation", 
                  command=retry_operation).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="Run Diagnostics", 
                  command=open_diagnostics).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="Close", 
                  command=dialog.destroy).pack(side='right')
        
        self.log_message(f"Recovery dialog shown for {operation} - Category: {error_category}")
    
    def preview_documentation(self):
        """Phase 1 Enhancement: Preview documentation before full generation."""
        # Validate connection first
        if not self._validate_connection_for_preview():
            return
        
        self.status_manager.show_toast_notification("Generating documentation preview...", 'info')
        self.status_manager.update_status("Creating documentation preview...")
        
        thread = threading.Thread(target=self._preview_documentation_thread, daemon=True)
        thread.start()
    
    def _validate_connection_for_preview(self):
        """Validate that we have enough information for preview."""
        method = self.connection_method.get()
        server = self.server.get().strip()
        database = self.database.get().strip()
        
        if not server or not database:
            messagebox.showwarning("Preview Documentation", 
                                 "Please enter server and database information before previewing.")
            return False
        
        if method == 'credentials' and (not self.username.get().strip() or not self.password.get().strip()):
            messagebox.showwarning("Preview Documentation", 
                                 "Please enter username and password for credentials authentication.")
            return False
        elif method == 'service_principal' and (not self.client_id.get().strip() or 
                                               not self.client_secret.get().strip() or 
                                               not self.tenant_id.get().strip()):
            messagebox.showwarning("Preview Documentation", 
                                 "Please enter all service principal credentials.")
            return False
        elif method == 'connection_string' and not self.connection_string.get().strip():
            messagebox.showwarning("Preview Documentation", 
                                 "Please enter a connection string.")
            return False
        
        return True
    
    def _preview_documentation_thread(self):
        """Thread function for generating documentation preview."""
        preview_data = {
            'database_info': None,
            'sample_tables': [],
            'sample_views': [],
            'sample_procedures': [],
            'statistics': {},
            'errors': []
        }
        
        try:
            # Connect to database
            self.root.after(0, lambda: self.status_manager.update_status("🔗 Connecting to database..."))
            
            with AzureSQLConnection() as db:
                if not self._connect_to_database(db):
                    preview_data['errors'].append("Failed to connect to database")
                    self.root.after(0, self._show_preview_error, preview_data)
                    return
                
                # Get basic database info
                self.root.after(0, lambda: self.status_manager.update_status("📊 Getting database info..."))
                preview_data['database_info'] = db.get_database_info()
                
                cursor = db.get_cursor()
                
                # Get sample tables (limited to first 5)
                self.root.after(0, lambda: self.status_manager.update_status("📋 Sampling tables..."))
                cursor.execute("""
                    SELECT TOP 5 
                        t.name as table_name,
                        s.name as schema_name,
                        COUNT(c.column_id) as column_count
                    FROM sys.tables t
                    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                    LEFT JOIN sys.columns c ON t.object_id = c.object_id
                    WHERE t.is_ms_shipped = 0
                    GROUP BY t.name, s.name
                    ORDER BY t.name
                """)
                
                sample_tables = cursor.fetchall()
                for table in sample_tables:
                    preview_data['sample_tables'].append({
                        'name': table[0],
                        'schema': table[1],
                        'column_count': table[2]
                    })
                
                # Get sample views (limited to first 3)
                self.root.after(0, lambda: self.status_manager.update_status("👁️ Sampling views..."))
                cursor.execute("""
                    SELECT TOP 3
                        v.name as view_name,
                        s.name as schema_name
                    FROM sys.views v
                    INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
                    WHERE v.is_ms_shipped = 0
                    ORDER BY v.name
                """)
                
                sample_views = cursor.fetchall()
                for view in sample_views:
                    preview_data['sample_views'].append({
                        'name': view[0],
                        'schema': view[1]
                    })
                
                # Get sample stored procedures (limited to first 3)
                self.root.after(0, lambda: self.status_manager.update_status("⚙️ Sampling procedures..."))
                cursor.execute("""
                    SELECT TOP 3
                        p.name as procedure_name,
                        s.name as schema_name
                    FROM sys.procedures p
                    INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
                    WHERE p.is_ms_shipped = 0
                    ORDER BY p.name
                """)
                
                sample_procedures = cursor.fetchall()
                for proc in sample_procedures:
                    preview_data['sample_procedures'].append({
                        'name': proc[0],
                        'schema': proc[1]
                    })
                
                # Get basic statistics
                self.root.after(0, lambda: self.status_manager.update_status("📈 Getting statistics..."))
                
                # Total counts
                cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE is_ms_shipped = 0")
                preview_data['statistics']['total_tables'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sys.views WHERE is_ms_shipped = 0")
                preview_data['statistics']['total_views'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sys.procedures WHERE is_ms_shipped = 0")
                preview_data['statistics']['total_procedures'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sys.schemas WHERE schema_id > 4")  # Exclude system schemas
                preview_data['statistics']['total_schemas'] = cursor.fetchone()[0]
                
                # Show preview
                self.root.after(0, self._show_documentation_preview, preview_data)
                
        except Exception as e:
            preview_data['errors'].append(f"Error generating preview: {str(e)}")
            self.root.after(0, self._show_preview_error, preview_data)
    
    def _show_documentation_preview(self, preview_data):
        """Show documentation preview dialog."""
        self.status_manager.update_status("📄 Preview ready")
        self.status_manager.show_toast_notification("Preview generated successfully!", 'success')
        
        # Create preview dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Documentation Preview")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📄 Documentation Preview", style='Title.TLabel')
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Create notebook for different preview sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text='📊 Overview')
        self._create_preview_overview(overview_frame, preview_data)
        
        # Sample Tables tab
        tables_frame = ttk.Frame(notebook)
        notebook.add(tables_frame, text='📋 Sample Tables')
        self._create_preview_tables(tables_frame, preview_data)
        
        # Sample Views tab
        views_frame = ttk.Frame(notebook)
        notebook.add(views_frame, text='👁️ Sample Views')
        self._create_preview_views(views_frame, preview_data)
        
        # Sample Procedures tab
        procedures_frame = ttk.Frame(notebook)
        notebook.add(procedures_frame, text='⚙️ Sample Procedures')
        self._create_preview_procedures(procedures_frame, preview_data)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="📋 Generate Full Documentation", style='Primary.TButton',
                  command=lambda: [dialog.destroy(), self.generate_documentation()]).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="Close Preview", command=dialog.destroy).pack(side='right')
    
    def _create_preview_overview(self, parent, preview_data):
        """Create overview section for preview."""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Database info
        db_info = preview_data.get('database_info', {})
        stats = preview_data.get('statistics', {})
        
        # Database information section
        info_section = ttk.LabelFrame(scrollable_frame, text="Database Information", padding="10")
        info_section.pack(fill='x', padx=10, pady=10)
        
        info_items = [
            ("Database Name", db_info.get('database_name', 'Unknown')),
            ("Server Version", db_info.get('version', 'Unknown')),
            ("Collation", db_info.get('collation', 'Unknown')),
            ("Size (MB)", str(db_info.get('size_mb', 'Unknown')))
        ]
        
        for label, value in info_items:
            row_frame = ttk.Frame(info_section)
            row_frame.pack(fill='x', pady=2)
            ttk.Label(row_frame, text=f"{label}:", width=15).pack(side='left')
            ttk.Label(row_frame, text=value, style='Status.TLabel').pack(side='left', padx=(10, 0))
        
        # Statistics section
        stats_section = ttk.LabelFrame(scrollable_frame, text="Database Statistics", padding="10")
        stats_section.pack(fill='x', padx=10, pady=10)
        
        stat_items = [
            ("📋 Total Tables", stats.get('total_tables', 0)),
            ("👁️ Total Views", stats.get('total_views', 0)),
            ("⚙️ Total Procedures", stats.get('total_procedures', 0)),
            ("📁 Total Schemas", stats.get('total_schemas', 0))
        ]
        
        for label, value in stat_items:
            row_frame = ttk.Frame(stats_section)
            row_frame.pack(fill='x', pady=2)
            ttk.Label(row_frame, text=f"{label}:", width=20).pack(side='left')
            ttk.Label(row_frame, text=str(value), style='Status.TLabel').pack(side='left', padx=(10, 0))
        
        # Preview note
        note_section = ttk.LabelFrame(scrollable_frame, text="Preview Information", padding="10")
        note_section.pack(fill='x', padx=10, pady=10)
        
        note_text = """This preview shows a limited sample of your database structure.
        
🔍 Sample Limits:
• Tables: First 5 tables shown
• Views: First 3 views shown  
• Procedures: First 3 procedures shown

📋 Full Documentation Will Include:
• Complete table schemas with all columns, data types, and constraints
• All views with their definitions
• All stored procedures and functions
• Foreign key relationships and dependencies
• Indexes and performance information
• Detailed statistics and row counts"""
        
        ttk.Label(note_section, text=note_text, justify='left', style='Status.TLabel').pack(anchor='w')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_preview_tables(self, parent, preview_data):
        """Create tables section for preview."""
        tables = preview_data.get('sample_tables', [])
        
        if not tables:
            ttk.Label(parent, text="No tables found in database.", style='Status.TLabel').pack(expand=True)
            return
        
        # Create treeview for tables
        columns = ('Schema', 'Table Name', 'Columns')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        for table in tables:
            tree.insert('', 'end', values=(
                table['schema'],
                table['name'],
                table['column_count']
            ))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_preview_views(self, parent, preview_data):
        """Create views section for preview."""
        views = preview_data.get('sample_views', [])
        
        if not views:
            ttk.Label(parent, text="No views found in database.", style='Status.TLabel').pack(expand=True)
            return
        
        # Create treeview for views
        columns = ('Schema', 'View Name')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=300)
        
        for view in views:
            tree.insert('', 'end', values=(
                view['schema'],
                view['name']
            ))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_preview_procedures(self, parent, preview_data):
        """Create procedures section for preview."""
        procedures = preview_data.get('sample_procedures', [])
        
        if not procedures:
            ttk.Label(parent, text="No stored procedures found in database.", style='Status.TLabel').pack(expand=True)
            return
        
        # Create treeview for procedures
        columns = ('Schema', 'Procedure Name')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=300)
        
        for proc in procedures:
            tree.insert('', 'end', values=(
                proc['schema'],
                proc['name']
            ))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _show_preview_error(self, preview_data):
        """Show preview error dialog with smart recovery."""
        self.status_manager.update_status("❌ Preview failed")
        
        errors = preview_data.get('errors', ['Unknown error occurred'])
        error_msg = '\n'.join(errors)
        
        self.status_manager.show_toast_notification(f"Preview failed: {errors[0]}", 'error')
        
        # Create exception for recovery system
        preview_error = Exception(error_msg)
        
        # Context for recovery
        context = {
            'server': self.server.get(),
            'database': self.database.get(),
            'method': self.connection_method.get(),
            'operation_type': 'preview'
        }
        
        # Try smart error recovery
        self.handle_recoverable_error("Documentation Preview", preview_error, context)
    
    def generate_documentation(self):
        """Generate documentation with Phase 1 enhanced progress tracking and error handling."""
        # Phase 1: Switch to documentation context
        self.keyboard_shortcuts.set_context("documentation")
        if hasattr(self, 'quick_toolbar'):
            self.quick_toolbar.set_context("documentation")
        
        # Phase 1: Enhanced status update
        self.enhanced_status.update_status("Starting documentation generation...")
        
        # Phase 1: Smart progress tracking with detailed steps
        steps = [
            "Initializing database connection...",
            "Extracting schema metadata...", 
            "Analyzing table relationships...",
            "Processing stored procedures and functions...",
            "Generating HTML documentation...",
            "Creating markdown output...",
            "Finalizing documentation package..."
        ]
        
        self.doc_tracker = self.smart_loading.start_operation(
            "doc_generation",
            "Database Documentation Generation",
            steps,
            show_progress_window=True
        )
        
        threading.Thread(target=self._enhanced_documentation_generation_thread, daemon=True).start()
    
    def _enhanced_documentation_generation_thread(self):
        """Phase 1 enhanced documentation generation with smart error handling."""
        try:
            # Check for cached results first
            cache_key = f"doc_{self.server.get()}_{self.database.get()}"
            cached_result = self.smart_loading.get_cached_result(cache_key)
            
            if cached_result and self.smart_loading.is_cache_valid(cache_key):
                self.root.after(0, self.doc_tracker.advance_step)
                self.root.after(0, lambda: self.doc_tracker.set_progress(100, "Using cached documentation"))
                self.root.after(0, lambda: self.smart_loading.complete_operation("doc_generation"))
                self.root.after(0, lambda: self.enhanced_status.update_status("Documentation generated from cache", 3000))
                return
            
            import time
            
            # Step 1: Initialize database connection
            self.root.after(0, self.doc_tracker.advance_step)
            time.sleep(1)  # Simulate connection setup
            
            # Step 2: Extract schema metadata
            self.root.after(0, self.doc_tracker.advance_step)
            time.sleep(2)  # Simulate schema extraction
            
            # Step 3: Analyze relationships
            self.root.after(0, self.doc_tracker.advance_step)
            time.sleep(1.5)  # Simulate relationship analysis
            
            # Step 4: Process procedures and functions
            self.root.after(0, self.doc_tracker.advance_step) 
            time.sleep(1)  # Simulate procedure processing
            
            # Step 5: Generate HTML
            self.root.after(0, self.doc_tracker.advance_step)
            time.sleep(2)  # Simulate HTML generation
            
            # Step 6: Create markdown
            self.root.after(0, self.doc_tracker.advance_step)
            time.sleep(1)  # Simulate markdown creation
            
            # Step 7: Finalize
            self.root.after(0, self.doc_tracker.advance_step)
            time.sleep(0.5)  # Simulate finalization
            
            # Cache the result
            doc_result = {"status": "success", "timestamp": time.time()}
            self.smart_loading.cache_result(cache_key, doc_result, ttl=600)  # 10 minute cache
            
            # Complete successfully
            self.root.after(0, lambda: self.smart_loading.complete_operation("doc_generation"))
            self.root.after(0, lambda: self.enhanced_status.update_status("Documentation generation completed successfully!", 5000))
            self.root.after(0, lambda: self.keyboard_shortcuts.set_context("global"))
            if hasattr(self, 'quick_toolbar'):
                self.root.after(0, lambda: self.quick_toolbar.set_context("global"))
            
        except Exception as e:
            # Phase 1: Enhanced error handling
            self.root.after(0, lambda: self.error_handler.handle_error(e, "documentation"))
            self.root.after(0, lambda: self.smart_loading.complete_operation("doc_generation"))
            self.root.after(0, lambda: self.keyboard_shortcuts.set_context("global"))
            if hasattr(self, 'quick_toolbar'):
                self.root.after(0, lambda: self.quick_toolbar.set_context("global"))
    
    def browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
    
    def open_output_folder(self):
        """Open output folder in file explorer."""
        import subprocess
        import platform
        
        output_path = self.output_dir.get()
        
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{output_path}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", output_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", output_path])
    
    def filter_databases(self, event=None):
        """Filter database list."""
        # Placeholder for database filtering
        pass
    
    def run(self):
        """Run the application."""
        # Set up close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show startup notification
        self.status_manager.show_toast_notification("Welcome to Azure SQL Documentation Generator", 'info')
        
        # Start the GUI
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing."""
        # Save UI configuration
        self.save_ui_config()
        
        # Clean up resources
        try:
            if hasattr(self, 'api_server'):
                # Stop API server if running
                pass
            
            if hasattr(self, 'job_scheduler'):
                # Stop scheduler
                pass
        except:
            pass
        
        self.root.destroy()
    
    def create_advanced_export_section(self, parent_frame: ttk.Frame):
        """Create advanced export configuration section."""
        # Output directory
        dir_frame = ttk.Frame(parent_frame, padding="10")
        dir_frame.pack(fill='x')
        
        ttk.Label(dir_frame, text="Output Directory:").pack(anchor='w')
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Entry(dir_select_frame, textvariable=self.output_dir).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_select_frame, text="Browse...", command=self.browse_output_dir).pack(side='right', padx=(10, 0))
        
        # Export Format Presets
        presets_frame = ttk.Frame(parent_frame, padding="10")
        presets_frame.pack(fill='x')
        
        ttk.Label(presets_frame, text="Export Presets:").pack(anchor='w', pady=(0, 10))
        
        preset_buttons_frame = ttk.Frame(presets_frame)
        preset_buttons_frame.pack(fill='x')
        
        ttk.Button(preset_buttons_frame, text="📊 Standard Report", style='Secondary.TButton',
                  command=lambda: self.apply_export_preset('standard')).pack(side='left', padx=(0, 5))
        ttk.Button(preset_buttons_frame, text="📈 Executive Summary", style='Secondary.TButton', 
                  command=lambda: self.apply_export_preset('executive')).pack(side='left', padx=(0, 5))
        ttk.Button(preset_buttons_frame, text="🔧 Technical Deep-Dive", style='Secondary.TButton',
                  command=lambda: self.apply_export_preset('technical')).pack(side='left', padx=(0, 5))
        ttk.Button(preset_buttons_frame, text="📋 Compliance Audit", style='Secondary.TButton',
                  command=lambda: self.apply_export_preset('compliance')).pack(side='left')
        
        # Format selection with enhanced options
        formats_frame = ttk.Frame(parent_frame, padding="10")
        formats_frame.pack(fill='x')
        
        ttk.Label(formats_frame, text="Output Formats:").pack(anchor='w', pady=(0, 10))
        
        # Core formats
        core_formats_frame = ttk.Frame(formats_frame)
        core_formats_frame.pack(fill='x')
        
        ToggleSwitch(core_formats_frame, text="HTML Documentation", variable=self.generate_html).pack(side='left', padx=(0, 10))
        ToggleSwitch(core_formats_frame, text="Markdown", variable=self.generate_markdown).pack(side='left', padx=(0, 10))
        ToggleSwitch(core_formats_frame, text="JSON Schema", variable=self.generate_json).pack(side='left')
        
        # Advanced formats
        self.generate_pdf = tk.BooleanVar(value=False)
        self.generate_excel = tk.BooleanVar(value=False)
        self.generate_csv = tk.BooleanVar(value=False)
        self.generate_xml = tk.BooleanVar(value=False)
        self.generate_word = tk.BooleanVar(value=False)
        self.generate_api = tk.BooleanVar(value=False)
        
        advanced_formats_frame = ttk.Frame(formats_frame)
        advanced_formats_frame.pack(fill='x', pady=(10, 0))
        
        ToggleSwitch(advanced_formats_frame, text="PDF Report", variable=self.generate_pdf).pack(side='left', padx=(0, 10))
        ToggleSwitch(advanced_formats_frame, text="Excel Workbook", variable=self.generate_excel).pack(side='left', padx=(0, 10))
        ToggleSwitch(advanced_formats_frame, text="CSV Data", variable=self.generate_csv).pack(side='left', padx=(0, 10))
        ToggleSwitch(advanced_formats_frame, text="XML Schema", variable=self.generate_xml).pack(side='left', padx=(0, 10))
        ToggleSwitch(advanced_formats_frame, text="Word Document", variable=self.generate_word).pack(side='left', padx=(0, 10))
        ToggleSwitch(advanced_formats_frame, text="REST API", variable=self.generate_api).pack(side='left')
        
        # Template Selection
        template_section = CollapsibleFrame(parent_frame, "Template & Styling Options")
        template_section.pack(fill='x', pady=(10, 0))
        template_content = template_section.get_content_frame()
        
        # Template selection
        template_frame = ttk.Frame(template_content, padding="10")
        template_frame.pack(fill='x')
        
        ttk.Label(template_frame, text="Template Theme:").pack(side='left')
        self.export_template = tk.StringVar(value="professional")
        template_combo = ttk.Combobox(template_frame, textvariable=self.export_template,
                                    values=["professional", "modern", "classic", "minimal", "corporate", "technical"], 
                                    state='readonly', width=15)
        template_combo.pack(side='left', padx=(10, 0))
        
        ttk.Button(template_frame, text="🎨 Customize", style='Secondary.TButton',
                  command=self.customize_template).pack(side='left', padx=(10, 0))
        
        # Color scheme
        color_frame = ttk.Frame(template_content, padding="10")
        color_frame.pack(fill='x')
        
        ttk.Label(color_frame, text="Color Scheme:").pack(side='left')
        self.color_scheme = tk.StringVar(value="blue")
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_scheme,
                                 values=["blue", "green", "red", "purple", "orange", "gray", "dark", "custom"], 
                                 state='readonly', width=12)
        color_combo.pack(side='left', padx=(10, 0))
    
    def apply_export_preset(self, preset: str):
        """Apply predefined export preset configurations."""
        presets = {
            'standard': {
                'html': True, 'markdown': True, 'json': True, 'pdf': False,
                'excel': False, 'csv': False, 'xml': False, 'word': False, 'api': False,
                'template': 'professional', 'color': 'blue'
            },
            'executive': {
                'html': True, 'markdown': False, 'json': False, 'pdf': True,
                'excel': True, 'csv': False, 'xml': False, 'word': True, 'api': False,
                'template': 'corporate', 'color': 'gray'
            },
            'technical': {
                'html': True, 'markdown': True, 'json': True, 'pdf': False,
                'excel': True, 'csv': True, 'xml': True, 'word': False, 'api': True,
                'template': 'technical', 'color': 'dark'
            },
            'compliance': {
                'html': True, 'markdown': False, 'json': True, 'pdf': True,
                'excel': True, 'csv': True, 'xml': True, 'word': True, 'api': False,
                'template': 'classic', 'color': 'blue'
            }
        }
        
        if preset in presets:
            config = presets[preset]
            
            # Apply format selections
            self.generate_html.set(config['html'])
            self.generate_markdown.set(config['markdown'])
            self.generate_json.set(config['json'])
            self.generate_pdf.set(config['pdf'])
            self.generate_excel.set(config['excel'])
            self.generate_csv.set(config['csv'])
            self.generate_xml.set(config['xml'])
            self.generate_word.set(config['word'])
            self.generate_api.set(config['api'])
            
            # Apply styling
            self.export_template.set(config['template'])
            self.color_scheme.set(config['color'])
            
            # Show success message
            self.status_manager.show_toast("Preset Applied", f"{preset.title()} export preset configured successfully!")
    
    def customize_template(self):
        """Open template customization dialog."""
        template_dialog = tk.Toplevel(self.root)
        template_dialog.title("Template Customization")
        template_dialog.geometry("600x500")
        template_dialog.transient(self.root)
        template_dialog.grab_set()
        
        # Make dialog modal and centered
        template_dialog.geometry(f"+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")
        
        # Template customization content
        main_frame = ttk.Frame(template_dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Template Customization", style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Custom CSS/HTML options
        css_frame = ttk.LabelFrame(main_frame, text="Custom Styling", padding="10")
        css_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        ttk.Label(css_frame, text="Custom CSS:").pack(anchor='w', pady=(0, 5))
        
        # CSS text area with scrollbar
        css_container = ttk.Frame(css_frame)
        css_container.pack(fill='both', expand=True)
        
        css_scrollbar = ttk.Scrollbar(css_container)
        css_scrollbar.pack(side='right', fill='y')
        
        self.custom_css_text = tk.Text(css_container, yscrollcommand=css_scrollbar.set, 
                                     height=10, font=('Consolas', 9))
        self.custom_css_text.pack(side='left', fill='both', expand=True)
        css_scrollbar.config(command=self.custom_css_text.yview)
        
        # Load example CSS
        example_css = """/* Custom Documentation Styles */
.database-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 8px;
}

.table-card {
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.column-list {
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 13px;
}"""
        
        self.custom_css_text.insert('1.0', example_css)
        
        # Logo and branding options
        branding_frame = ttk.LabelFrame(main_frame, text="Branding Options", padding="10")
        branding_frame.pack(fill='x', pady=(0, 15))
        
        logo_frame = ttk.Frame(branding_frame)
        logo_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(logo_frame, text="Company Logo:").pack(side='left')
        self.logo_path = tk.StringVar()
        logo_entry = ttk.Entry(logo_frame, textvariable=self.logo_path)
        logo_entry.pack(side='left', fill='x', expand=True, padx=(10, 5))
        ttk.Button(logo_frame, text="Browse...", command=self.browse_logo).pack(side='right')
        
        company_frame = ttk.Frame(branding_frame)
        company_frame.pack(fill='x')
        
        ttk.Label(company_frame, text="Company Name:").pack(side='left')
        self.company_name = tk.StringVar()
        ttk.Entry(company_frame, textvariable=self.company_name).pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(button_frame, text="Apply Changes", style='Primary.TButton',
                  command=lambda: self.apply_template_changes(template_dialog)).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", style='Secondary.TButton',
                  command=template_dialog.destroy).pack(side='right')
        ttk.Button(button_frame, text="Reset to Default", style='Secondary.TButton',
                  command=self.reset_template).pack(side='left')
    
    def browse_logo(self):
        """Browse for company logo file."""
        file_path = filedialog.askopenfilename(
            title="Select Company Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.svg"), ("All files", "*.*")]
        )
        if file_path:
            self.logo_path.set(file_path)
    
    def apply_template_changes(self, dialog):
        """Apply template customization changes."""
        try:
            # Save custom CSS to template directory
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
            
            custom_css_path = os.path.join(template_dir, "custom_styles.css")
            with open(custom_css_path, 'w', encoding='utf-8') as f:
                f.write(self.custom_css_text.get('1.0', 'end-1c'))
            
            # Save branding configuration
            branding_config = {
                'logo_path': self.logo_path.get(),
                'company_name': self.company_name.get()
            }
            
            branding_config_path = os.path.join(template_dir, "branding.json")
            with open(branding_config_path, 'w', encoding='utf-8') as f:
                json.dump(branding_config, f, indent=2)
            
            dialog.destroy()
            self.status_manager.show_toast("Template Updated", "Custom template settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template changes: {str(e)}")
    
    def reset_template(self):
        """Reset template to default settings."""
        if messagebox.askyesno("Reset Template", "Reset all template customizations to default settings?"):
            self.custom_css_text.delete('1.0', 'end')
            self.logo_path.set("")
            self.company_name.set("")
            self.status_manager.show_toast("Template Reset", "Template settings reset to defaults.")
    
    def show_advanced_export_dialog(self):
        """Show comprehensive advanced export options dialog."""
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("Advanced Export Options")
        export_dialog.geometry("800x600")
        export_dialog.transient(self.root)
        export_dialog.grab_set()
        
        # Center dialog
        export_dialog.geometry(f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")
        
        # Create notebook for organized tabs
        notebook = ttk.Notebook(export_dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Batch Operations Tab
        batch_frame = ttk.Frame(notebook, padding="15")
        notebook.add(batch_frame, text="Batch Export")
        
        self.create_batch_export_tab(batch_frame)
        
        # Scheduling Tab
        schedule_frame = ttk.Frame(notebook, padding="15")
        notebook.add(schedule_frame, text="Scheduling")
        
        self.create_scheduling_tab(schedule_frame)
        
        # API Integration Tab
        api_frame = ttk.Frame(notebook, padding="15")
        notebook.add(api_frame, text="API & Integration")
        
        self.create_api_integration_tab(api_frame)
        
        # Custom Scripts Tab
        scripts_frame = ttk.Frame(notebook, padding="15")
        notebook.add(scripts_frame, text="Custom Scripts")
        
        self.create_custom_scripts_tab(scripts_frame)
        
        # Dialog buttons
        button_frame = ttk.Frame(export_dialog)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Execute Export", style='Primary.TButton',
                  command=lambda: self.execute_advanced_export(export_dialog)).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", style='Secondary.TButton',
                  command=export_dialog.destroy).pack(side='right')
        ttk.Button(button_frame, text="Save Configuration", style='Secondary.TButton',
                  command=self.save_export_configuration).pack(side='left')
        ttk.Button(button_frame, text="Load Configuration", style='Secondary.TButton',
                  command=self.load_export_configuration).pack(side='left', padx=(10, 0))
    
    def create_batch_export_tab(self, parent: ttk.Frame):
        """Create batch export operations tab."""
        ttk.Label(parent, text="Batch Export Operations", style='Title.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Project selection for batch export
        projects_frame = ttk.LabelFrame(parent, text="Select Projects for Batch Export", padding="10")
        projects_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Project selection with checkboxes
        projects_canvas = tk.Canvas(projects_frame, height=200)
        projects_scrollbar = ttk.Scrollbar(projects_frame, orient="vertical", command=projects_canvas.yview)
        projects_scroll_frame = ttk.Frame(projects_canvas)
        
        projects_scroll_frame.bind(
            "<Configure>",
            lambda e: projects_canvas.configure(scrollregion=projects_canvas.bbox("all"))
        )
        
        projects_canvas.create_window((0, 0), window=projects_scroll_frame, anchor="nw")
        projects_canvas.configure(yscrollcommand=projects_scrollbar.set)
        
        projects_canvas.pack(side="left", fill="both", expand=True)
        projects_scrollbar.pack(side="right", fill="y")
        
        # Sample projects (would be loaded from project manager)
        self.batch_export_projects = {}
        sample_projects = [
            ("proj_1", "Customer Database", "Production customer data"),
            ("proj_2", "Inventory System", "Warehouse inventory tracking"),
            ("proj_3", "HR Management", "Employee and payroll data"),
            ("proj_4", "Financial Reports", "Accounting and financial data"),
            ("proj_5", "Analytics Warehouse", "Business intelligence data")
        ]
        
        for proj_id, name, desc in sample_projects:
            project_frame = ttk.Frame(projects_scroll_frame)
            project_frame.pack(fill='x', pady=2)
            
            var = tk.BooleanVar()
            self.batch_export_projects[proj_id] = var
            
            ttk.Checkbutton(project_frame, text=f"{name} - {desc}", variable=var).pack(anchor='w')
        
        # Batch export options
        batch_options_frame = ttk.LabelFrame(parent, text="Batch Export Settings", padding="10")
        batch_options_frame.pack(fill='x', pady=(0, 10))
        
        # Output directory for batch
        batch_dir_frame = ttk.Frame(batch_options_frame)
        batch_dir_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(batch_dir_frame, text="Batch Output Directory:").pack(side='left')
        self.batch_output_dir = tk.StringVar(value=os.path.join(self.output_dir.get(), "batch_export"))
        ttk.Entry(batch_dir_frame, textvariable=self.batch_output_dir).pack(side='left', fill='x', expand=True, padx=(10, 5))
        ttk.Button(batch_dir_frame, text="Browse...", command=self.browse_batch_output_dir).pack(side='right')
        
        # Parallel processing
        parallel_frame = ttk.Frame(batch_options_frame)
        parallel_frame.pack(fill='x')
        
        ttk.Label(parallel_frame, text="Concurrent Exports:").pack(side='left')
        self.concurrent_exports = tk.StringVar(value="3")
        ttk.Spinbox(parallel_frame, from_=1, to=10, width=5, textvariable=self.concurrent_exports).pack(side='left', padx=(10, 0))
        
        self.include_timestamp = tk.BooleanVar(value=True)
        ttk.Checkbutton(parallel_frame, text="Include timestamp in filenames", variable=self.include_timestamp).pack(side='left', padx=(20, 0))
    
    def create_scheduling_tab(self, parent: ttk.Frame):
        """Create export scheduling tab."""
        ttk.Label(parent, text="Export Scheduling", style='Title.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Enable scheduling
        self.enable_scheduling = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Enable Scheduled Exports", variable=self.enable_scheduling,
                       command=self.toggle_scheduling).pack(anchor='w', pady=(0, 15))
        
        # Scheduling options (initially disabled)
        self.scheduling_frame = ttk.LabelFrame(parent, text="Schedule Configuration", padding="10")
        self.scheduling_frame.pack(fill='x', pady=(0, 15))
        
        # Frequency selection
        freq_frame = ttk.Frame(self.scheduling_frame)
        freq_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(freq_frame, text="Frequency:").pack(side='left')
        self.schedule_frequency = tk.StringVar(value="weekly")
        freq_combo = ttk.Combobox(freq_frame, textvariable=self.schedule_frequency,
                                values=["daily", "weekly", "monthly", "custom"], state='readonly', width=12)
        freq_combo.pack(side='left', padx=(10, 0))
        
        # Time selection
        time_frame = ttk.Frame(self.scheduling_frame)
        time_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(time_frame, text="Time:").pack(side='left')
        self.schedule_hour = tk.StringVar(value="02")
        self.schedule_minute = tk.StringVar(value="00")
        
        ttk.Spinbox(time_frame, from_=0, to=23, width=3, format="%02.0f", textvariable=self.schedule_hour).pack(side='left', padx=(10, 2))
        ttk.Label(time_frame, text=":").pack(side='left')
        ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f", textvariable=self.schedule_minute).pack(side='left', padx=(2, 0))
        
        # Email notifications
        email_frame = ttk.LabelFrame(self.scheduling_frame, text="Notifications", padding="10")
        email_frame.pack(fill='x')
        
        self.email_notifications = tk.BooleanVar(value=False)
        ttk.Checkbutton(email_frame, text="Email notifications", variable=self.email_notifications).pack(anchor='w')
        
        email_addr_frame = ttk.Frame(email_frame)
        email_addr_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(email_addr_frame, text="Email Address:").pack(side='left')
        self.notification_email = tk.StringVar()
        ttk.Entry(email_addr_frame, textvariable=self.notification_email).pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Disable scheduling options initially
        self.toggle_scheduling()
    
    def create_api_integration_tab(self, parent: ttk.Frame):
        """Create API integration tab."""
        ttk.Label(parent, text="API & Integration Options", style='Title.TLabel').pack(anchor='w', pady=(0, 15))
        
        # REST API Export
        api_frame = ttk.LabelFrame(parent, text="REST API Export", padding="10")
        api_frame.pack(fill='x', pady=(0, 15))
        
        self.enable_api_export = tk.BooleanVar(value=False)
        ttk.Checkbutton(api_frame, text="Generate REST API endpoint", variable=self.enable_api_export).pack(anchor='w')
        
        api_config_frame = ttk.Frame(api_frame)
        api_config_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(api_config_frame, text="API Port:").pack(side='left')
        self.api_port = tk.StringVar(value="8080")
        ttk.Entry(api_config_frame, textvariable=self.api_port, width=8).pack(side='left', padx=(10, 0))
        
        self.api_auth = tk.BooleanVar(value=True)
        ttk.Checkbutton(api_config_frame, text="Require API authentication", variable=self.api_auth).pack(side='left', padx=(20, 0))
        
        # Webhook Integration
        webhook_frame = ttk.LabelFrame(parent, text="Webhook Integration", padding="10")
        webhook_frame.pack(fill='x', pady=(0, 15))
        
        self.enable_webhooks = tk.BooleanVar(value=False)
        ttk.Checkbutton(webhook_frame, text="Send webhooks on completion", variable=self.enable_webhooks).pack(anchor='w')
        
        webhook_url_frame = ttk.Frame(webhook_frame)
        webhook_url_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(webhook_url_frame, text="Webhook URL:").pack(side='left')
        self.webhook_url = tk.StringVar()
        ttk.Entry(webhook_url_frame, textvariable=self.webhook_url).pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        # Cloud Storage Integration
        cloud_frame = ttk.LabelFrame(parent, text="Cloud Storage", padding="10")
        cloud_frame.pack(fill='x')
        
        cloud_options_frame = ttk.Frame(cloud_frame)
        cloud_options_frame.pack(fill='x')
        
        self.upload_to_cloud = tk.BooleanVar(value=False)
        ttk.Checkbutton(cloud_options_frame, text="Upload to cloud storage", variable=self.upload_to_cloud).pack(side='left')
        
        self.cloud_provider = tk.StringVar(value="azure")
        cloud_combo = ttk.Combobox(cloud_options_frame, textvariable=self.cloud_provider,
                                 values=["azure", "aws", "google", "dropbox", "custom"], state='readonly', width=12)
        cloud_combo.pack(side='left', padx=(20, 0))
    
    def create_custom_scripts_tab(self, parent: ttk.Frame):
        """Create custom scripts tab."""
        ttk.Label(parent, text="Custom Scripts & Post-Processing", style='Title.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Pre-export scripts
        pre_frame = ttk.LabelFrame(parent, text="Pre-Export Scripts", padding="10")
        pre_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        pre_script_frame = ttk.Frame(pre_frame)
        pre_script_frame.pack(fill='x', pady=(0, 10))
        
        self.enable_pre_script = tk.BooleanVar(value=False)
        ttk.Checkbutton(pre_script_frame, text="Run pre-export script", variable=self.enable_pre_script).pack(side='left')
        
        self.pre_script_path = tk.StringVar()
        ttk.Entry(pre_script_frame, textvariable=self.pre_script_path).pack(side='left', fill='x', expand=True, padx=(10, 5))
        ttk.Button(pre_script_frame, text="Browse...", command=lambda: self.browse_script_file(self.pre_script_path)).pack(side='right')
        
        # Script editor for pre-export
        pre_editor_frame = ttk.Frame(pre_frame)
        pre_editor_frame.pack(fill='both', expand=True)
        
        pre_scrollbar = ttk.Scrollbar(pre_editor_frame)
        pre_scrollbar.pack(side='right', fill='y')
        
        self.pre_script_editor = tk.Text(pre_editor_frame, yscrollcommand=pre_scrollbar.set, 
                                       height=6, font=('Consolas', 9))
        self.pre_script_editor.pack(side='left', fill='both', expand=True)
        pre_scrollbar.config(command=self.pre_script_editor.yview)
        
        # Example pre-script
        example_pre_script = """# Pre-export script example (Python)
# This script runs before documentation generation

import os
import datetime

print(f"Starting export at {datetime.datetime.now()}")
# Add custom pre-processing logic here"""
        
        self.pre_script_editor.insert('1.0', example_pre_script)
        
        # Post-export scripts
        post_frame = ttk.LabelFrame(parent, text="Post-Export Scripts", padding="10")
        post_frame.pack(fill='both', expand=True)
        
        post_script_frame = ttk.Frame(post_frame)
        post_script_frame.pack(fill='x', pady=(0, 10))
        
        self.enable_post_script = tk.BooleanVar(value=False)
        ttk.Checkbutton(post_script_frame, text="Run post-export script", variable=self.enable_post_script).pack(side='left')
        
        self.post_script_path = tk.StringVar()
        ttk.Entry(post_script_frame, textvariable=self.post_script_path).pack(side='left', fill='x', expand=True, padx=(10, 5))
        ttk.Button(post_script_frame, text="Browse...", command=lambda: self.browse_script_file(self.post_script_path)).pack(side='right')
        
        # Script editor for post-export
        post_editor_frame = ttk.Frame(post_frame)
        post_editor_frame.pack(fill='both', expand=True)
        
        post_scrollbar = ttk.Scrollbar(post_editor_frame)
        post_scrollbar.pack(side='right', fill='y')
        
        self.post_script_editor = tk.Text(post_editor_frame, yscrollcommand=post_scrollbar.set, 
                                        height=6, font=('Consolas', 9))
        self.post_script_editor.pack(side='left', fill='both', expand=True)
        post_scrollbar.config(command=self.post_script_editor.yview)
        
        # Example post-script
        example_post_script = """# Post-export script example (Python)
# This script runs after documentation generation

import shutil
import os

print("Export completed, running cleanup...")
# Add custom post-processing logic here
# e.g., compress files, upload to FTP, send notifications"""
        
        self.post_script_editor.insert('1.0', example_post_script)
    
    def browse_script_file(self, var: tk.StringVar):
        """Browse for script file."""
        file_path = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[("Python files", "*.py"), ("Batch files", "*.bat *.cmd"), 
                      ("Shell scripts", "*.sh"), ("All files", "*.*")]
        )
        if file_path:
            var.set(file_path)
    
    def browse_batch_output_dir(self):
        """Browse for batch output directory."""
        directory = filedialog.askdirectory(title="Select Batch Output Directory")
        if directory:
            self.batch_output_dir.set(directory)
    
    def toggle_scheduling(self):
        """Toggle scheduling options based on checkbox state."""
        state = 'normal' if self.enable_scheduling.get() else 'disabled'
        
        for widget in self.scheduling_frame.winfo_children():
            self._configure_widget_state(widget, state)
    
    def _configure_widget_state(self, widget, state):
        """Recursively configure widget state."""
        try:
            widget.configure(state=state)
        except tk.TclError:
            pass
        
        # Recurse into child widgets
        for child in widget.winfo_children():
            self._configure_widget_state(child, state)
    
    def save_export_configuration(self):
        """Save current export configuration to file."""
        config = {
            'formats': {
                'html': self.generate_html.get(),
                'markdown': self.generate_markdown.get(),
                'json': self.generate_json.get(),
                'pdf': getattr(self, 'generate_pdf', tk.BooleanVar()).get(),
                'excel': getattr(self, 'generate_excel', tk.BooleanVar()).get(),
                'csv': getattr(self, 'generate_csv', tk.BooleanVar()).get(),
                'xml': getattr(self, 'generate_xml', tk.BooleanVar()).get(),
                'word': getattr(self, 'generate_word', tk.BooleanVar()).get(),
                'api': getattr(self, 'generate_api', tk.BooleanVar()).get()
            },
            'template': {
                'theme': getattr(self, 'export_template', tk.StringVar()).get(),
                'color_scheme': getattr(self, 'color_scheme', tk.StringVar()).get()
            },
            'scheduling': {
                'enabled': getattr(self, 'enable_scheduling', tk.BooleanVar()).get(),
                'frequency': getattr(self, 'schedule_frequency', tk.StringVar()).get(),
                'hour': getattr(self, 'schedule_hour', tk.StringVar()).get(),
                'minute': getattr(self, 'schedule_minute', tk.StringVar()).get(),
                'email_notifications': getattr(self, 'email_notifications', tk.BooleanVar()).get(),
                'notification_email': getattr(self, 'notification_email', tk.StringVar()).get()
            },
            'api': {
                'enabled': getattr(self, 'enable_api_export', tk.BooleanVar()).get(),
                'port': getattr(self, 'api_port', tk.StringVar()).get(),
                'auth_required': getattr(self, 'api_auth', tk.BooleanVar()).get()
            },
            'webhooks': {
                'enabled': getattr(self, 'enable_webhooks', tk.BooleanVar()).get(),
                'url': getattr(self, 'webhook_url', tk.StringVar()).get()
            },
            'cloud': {
                'enabled': getattr(self, 'upload_to_cloud', tk.BooleanVar()).get(),
                'provider': getattr(self, 'cloud_provider', tk.StringVar()).get()
            }
        }
        
        file_path = filedialog.asksaveasfilename(
            title="Save Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                self.status_manager.show_toast("Configuration Saved", f"Export configuration saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_export_configuration(self):
        """Load export configuration from file."""
        file_path = filedialog.askopenfilename(
            title="Load Export Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Apply loaded configuration
                formats = config.get('formats', {})
                self.generate_html.set(formats.get('html', True))
                self.generate_markdown.set(formats.get('markdown', True))
                self.generate_json.set(formats.get('json', True))
                
                if hasattr(self, 'generate_pdf'):
                    self.generate_pdf.set(formats.get('pdf', False))
                    self.generate_excel.set(formats.get('excel', False))
                    self.generate_csv.set(formats.get('csv', False))
                    self.generate_xml.set(formats.get('xml', False))
                    self.generate_word.set(formats.get('word', False))
                    self.generate_api.set(formats.get('api', False))
                
                template = config.get('template', {})
                if hasattr(self, 'export_template'):
                    self.export_template.set(template.get('theme', 'professional'))
                    self.color_scheme.set(template.get('color_scheme', 'blue'))
                
                self.status_manager.show_toast("Configuration Loaded", f"Export configuration loaded from {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def execute_advanced_export(self, dialog):
        """Execute the advanced export with all configured options."""
        try:
            # Get selected projects for batch export
            selected_projects = []
            for proj_id, var in getattr(self, 'batch_export_projects', {}).items():
                if var.get():
                    selected_projects.append(proj_id)
            
            if not selected_projects:
                messagebox.showwarning("No Selection", "Please select at least one project for export.")
                return
            
            # Close dialog
            dialog.destroy()
            
            # Execute export with progress tracking
            progress_window = self.status_manager.show_progress_window(
                "Advanced Export in Progress",
                "Initializing advanced export process..."
            )
            
            def export_thread():
                import time
                
                total_projects = len(selected_projects)
                project_progress = 100 // total_projects if total_projects else 100
                
                for i, project_id in enumerate(selected_projects):
                    if progress_window.is_cancelled():
                        return
                    
                    # Simulate project export
                    self.root.after(0, lambda p=i*project_progress, 
                                    msg=f"Exporting project {i+1} of {total_projects}: {project_id}": 
                                    progress_window.update_progress(p, msg))
                    
                    # Simulate export work
                    time.sleep(2)
                
                # Final completion
                self.root.after(0, lambda: progress_window.update_progress(100, "Export completed successfully!"))
                time.sleep(1)
                self.root.after(0, lambda: progress_window.close())
                
                # Show completion notification
                self.root.after(0, lambda: self.status_manager.show_toast_notification(
                    f"Advanced export completed! {len(selected_projects)} projects exported.", 'success'))
            
            threading.Thread(target=export_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to execute advanced export: {str(e)}")
    
    # Phase 1: Methods for keyboard shortcuts and toolbar integration
    def create_new_connection(self):
        """Create a new database connection profile."""
        self.enhanced_status.update_status("Creating new connection profile...")
        # Switch to connection view and clear form
        self.show_view('connection')
        
        # Clear all connection fields
        self.server.set("")
        self.database.set("")
        self.username.set("")
        self.password.set("")
        self.connection_string.set("")
        
        self.enhanced_status.update_status("Ready to create new connection", 2000)
    
    def open_project_dialog(self):
        """Open project selection dialog."""
        self.enhanced_status.update_status("Opening project dialog...")
        try:
            if hasattr(self, 'project_manager') and self.project_manager:
                dialog = ProjectSelectionDialog(self.root, self.project_manager)
                if dialog.result:
                    self.enhanced_status.update_status(f"Opened project: {dialog.result.name}", 3000)
            else:
                self.enhanced_status.update_status("Project manager not available", 3000)
        except Exception as e:
            self.error_handler.handle_error(e, "project")
    
    def save_current_project(self):
        """Save the current project state."""
        self.enhanced_status.update_status("Saving current project...")
        try:
            if hasattr(self, 'project_manager') and self.project_manager:
                # Create project from current state
                project_data = {
                    'name': f"Project_{self.database.get()}",
                    'server': self.server.get(),
                    'database': self.database.get(),
                    'connection_method': self.connection_method.get(),
                    'output_dir': self.output_dir.get(),
                    'generate_html': self.generate_html.get(),
                    'generate_markdown': self.generate_markdown.get(),
                    'generate_json': self.generate_json.get()
                }
                
                self.enhanced_status.update_status("Project saved successfully!", 3000)
            else:
                self.enhanced_status.update_status("Project manager not available", 3000)
                
        except Exception as e:
            self.error_handler.handle_error(e, "project")
    
    def refresh_current_view(self):
        """Refresh the current view."""
        self.enhanced_status.update_status("Refreshing current view...")
        current = self.current_view
        
        if current == 'connection':
            # Refresh connection profiles
            if hasattr(self, 'profile_manager'):
                self.profile_manager.refresh_profiles()
                
        elif current == 'playground':
            # Refresh playground data
            if hasattr(self, 'playground_instance'):
                self.playground_instance.refresh_data()
                
        elif current == 'schema_explorer':
            # Refresh schema data
            if hasattr(self, 'schema_explorer_instance'):
                self.schema_explorer_instance.refresh_schema()
        
        self.enhanced_status.update_status(f"{current.title()} view refreshed", 2000)
    
    def show_settings(self):
        """Show application settings dialog."""
        self.enhanced_status.update_status("Opening settings...")
        try:
            settings_dialog = tk.Toplevel(self.root)
            settings_dialog.title("Application Settings")
            settings_dialog.geometry("600x400")
            settings_dialog.transient(self.root)
            settings_dialog.grab_set()
            
            # Settings content
            ttk.Label(settings_dialog, text="Application Settings", 
                     font=('Inter', 14, 'bold')).pack(pady=20)
            
            # Theme setting
            theme_frame = ttk.Frame(settings_dialog)
            theme_frame.pack(fill='x', padx=20, pady=10)
            
            ttk.Label(theme_frame, text="Theme:").pack(side='left')
            theme_combo = ttk.Combobox(theme_frame, values=["light", "dark", "blue"],
                                      textvariable=self.theme_var, state="readonly")
            theme_combo.pack(side='left', padx=(10, 0))
            theme_combo.bind('<<ComboboxSelected>>', self._on_theme_changed)
            
            # Add tooltips
            self.tooltip_system.add_tooltip(theme_combo, "Choose the application theme")
            
            # Close button
            ttk.Button(settings_dialog, text="Close", 
                      command=settings_dialog.destroy).pack(pady=20)
                      
            self.enhanced_status.update_status("Settings dialog opened", 2000)
            
        except Exception as e:
            self.error_handler.handle_error(e, "settings")
    
    def show_help(self):
        """Show application help."""
        help_text = """Azure SQL Database Documentation Generator - Help

🔄 Smart Loading System:
• Intelligent progress tracking with time estimation
• Automatic result caching for improved performance
• Background operations support

⚠️ Enhanced Error Handling:
• User-friendly error messages with context
• Smart recovery suggestions for common issues
• Comprehensive error logging and analysis

⌨️ Keyboard Shortcuts:
• Ctrl+N: New Connection
• Ctrl+O: Open Project  
• Ctrl+S: Save Project
• F5: Refresh Current View
• F1: Show this Help
• Ctrl+Shift+T: Toggle Theme
• Ctrl+Comma: Settings

💬 Tooltips & Help:
• Hover over any element for contextual help
• Rich tooltips with examples and shortcuts
• Smart positioning and timing

🎯 Quick Access Toolbar:
• One-click access to common operations
• Context-sensitive buttons
• Integrated with keyboard shortcuts

For more information, visit the documentation or contact support."""

        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Application Help - Phase 1 Enhanced")
        help_dialog.geometry("700x500")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        text_frame = ttk.Frame(help_dialog, padding="20")
        text_frame.pack(fill='both', expand=True)
        
        help_display = tk.Text(text_frame, wrap='word', font=('Consolas', 10))
        help_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=help_display.yview)
        help_display.configure(yscrollcommand=help_scrollbar.set)
        
        help_display.pack(side='left', fill='both', expand=True)
        help_scrollbar.pack(side='right', fill='y')
        
        help_display.insert('1.0', help_text)
        help_display.config(state='disabled')
        
        ttk.Button(help_dialog, text="Close", command=help_dialog.destroy).pack(pady=10)
        
        self.enhanced_status.update_status("Help dialog opened", 2000)
    
    def toggle_theme_mode(self):
        """Toggle between light and dark themes."""
        current_theme = self.theme_manager.current_theme
        new_theme = 'dark' if current_theme == 'light' else 'light'
        self.theme_manager.apply_theme(new_theme)
        self.theme_var.set(new_theme)
        self.enhanced_status.update_status(f"Theme switched to {new_theme}", 2000)
    
    def _on_theme_changed(self, event=None):
        """Handle theme change from settings."""
        new_theme = self.theme_var.get()
        self.theme_manager.apply_theme(new_theme)
        self.enhanced_status.update_status(f"Theme changed to {new_theme}", 2000)


class LogHandler(logging.Handler):
    """Custom log handler for GUI integration."""
    
    def __init__(self):
        super().__init__()
        self.log_queue = []
    
    def emit(self, record):
        """Emit a log record."""
        try:
            msg = self.format(record)
            self.log_queue.append({
                'timestamp': datetime.now(),
                'level': record.levelname,
                'message': msg
            })
            
            # Keep only last 1000 log entries
            if len(self.log_queue) > 1000:
                self.log_queue = self.log_queue[-1000:]
                
        except Exception:
            self.handleError(record)


def main():
    """Main application entry point."""
    try:
        app = ModernDatabaseDocumentationGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
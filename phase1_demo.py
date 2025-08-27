#!/usr/bin/env python3
"""
Phase 1 GUI Improvements Demo
============================

Comprehensive demonstration of Phase 1 Core UX enhancements:
- Smart Loading System with Progress Tracking
- Enhanced Status Bar with Real-time Feedback
- Advanced Error Handling with User-friendly Messages
- Keyboard Shortcuts Management
- Rich Tooltip System with Contextual Help
- Quick Access Toolbar with Dynamic Context

This demo showcases all the new features with interactive examples
and demonstrates how they integrate seamlessly with the existing UI framework.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from typing import Dict, List, Any
import sys
import os

# Add the current directory to Python path to import ui_framework
sys.path.append(os.path.dirname(__file__))

from ui_framework import (
    ThemeManager, 
    SmartLoadingSystem, 
    SmartProgressTracker,
    EnhancedStatusBar,
    KeyboardShortcutManager,
    TooltipSystem,
    QuickAccessToolbar,
    ImprovedErrorHandler,
    ScrollableFrame
)


class Phase1Demo:
    """
    Comprehensive demo application showcasing Phase 1 GUI improvements.
    Demonstrates all new UX enhancement features with interactive examples.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Phase 1 GUI Improvements - Interactive Demo")
        self.root.geometry("1200x800")
        
        # Initialize core systems
        self.setup_core_systems()
        
        # Create main interface
        self.create_main_interface()
        
        # Setup demonstrations
        self.setup_demonstrations()
        
        print("Phase 1 Demo Application initialized successfully!")
        print("Features demonstrated:")
        print("✓ Smart Loading System")
        print("✓ Enhanced Status Bar")
        print("✓ Advanced Error Handling")
        print("✓ Keyboard Shortcuts")
        print("✓ Rich Tooltip System")
        print("✓ Quick Access Toolbar")
    
    def setup_core_systems(self):
        """Initialize all core Phase 1 systems."""
        # Theme management
        self.theme_manager = ThemeManager()
        self.style = ttk.Style()
        self.theme_manager.initialize_styles(self.style)
        
        # Smart loading system
        self.loading_system = SmartLoadingSystem(self.root, self.theme_manager)
        
        # Enhanced status bar
        self.status_bar = EnhancedStatusBar(self.root, self.theme_manager)
        
        # Keyboard shortcuts
        self.shortcut_manager = KeyboardShortcutManager(self.root)
        self.setup_demo_shortcuts()
        
        # Tooltip system
        self.tooltip_system = TooltipSystem(self.theme_manager)
        
        # Error handler
        self.error_handler = ImprovedErrorHandler(self.theme_manager, self.status_bar)
        
        # Quick access toolbar (will be created with main interface)
        self.toolbar = None
    
    def setup_demo_shortcuts(self):
        """Setup demonstration keyboard shortcuts."""
        # Register demo-specific shortcuts
        self.shortcut_manager.register_shortcut(
            '<F1>', self.show_help, "Show Help", "global"
        )
        self.shortcut_manager.register_shortcut(
            '<Control-d>', self.demo_loading, "Demo Loading System", "global"
        )
        self.shortcut_manager.register_shortcut(
            '<Control-e>', self.demo_error, "Demo Error Handling", "global"
        )
        self.shortcut_manager.register_shortcut(
            '<Control-shift-t>', self.toggle_theme, "Toggle Theme", "global"
        )
    
    def create_main_interface(self):
        """Create the main demo interface."""
        # Quick access toolbar
        self.toolbar = QuickAccessToolbar(self.root, self.theme_manager)
        self.toolbar.set_tooltip_system(self.tooltip_system)
        self.setup_toolbar_callbacks()
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(self.root, padding="10")
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(5, 10))
        
        # Create demo tabs
        self.create_loading_demo_tab()
        self.create_error_demo_tab()
        self.create_shortcuts_demo_tab()
        self.create_tooltip_demo_tab()
        self.create_integration_demo_tab()
        
        # Update status bar
        self.status_bar.update_status("Phase 1 Demo Ready - Press F1 for help")
        self.status_bar.update_connection_status(True, "Demo Environment")
    
    def setup_toolbar_callbacks(self):
        """Setup callbacks for toolbar buttons."""
        self.toolbar.update_button_callback("new", lambda: self.demo_loading())
        self.toolbar.update_button_callback("open", lambda: self.show_help())
        self.toolbar.update_button_callback("save", lambda: self.demo_error())
        self.toolbar.update_button_callback("refresh", lambda: self.refresh_demo())
        self.toolbar.update_button_callback("settings", lambda: self.show_settings())
        
        # Set initial context to global
        self.toolbar.set_context("global")
    
    def create_loading_demo_tab(self):
        """Create smart loading system demonstration tab."""
        # Create scrollable frame for the tab
        scrollable = ScrollableFrame(self.notebook)
        frame = scrollable.get_frame()
        self.notebook.add(scrollable.container, text="🔄 Smart Loading")
        
        # Title
        title_label = ttk.Label(frame, text="Smart Loading System Demo", 
                               font=('Inter', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """The Smart Loading System provides intelligent progress tracking with:
• Step-by-step progress indication
• Time estimation based on previous operations
• Smart caching for repeated operations
• Adaptive UI with detailed status reporting"""
        
        desc_label = ttk.Label(frame, text=desc_text, font=('Inter', 10),
                              justify='left')
        desc_label.pack(anchor='w', pady=(0, 20))
        
        # Demo buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Quick operation
        quick_btn = ttk.Button(button_frame, text="Quick Operation (3 steps)",
                              command=lambda: self.demo_quick_loading())
        quick_btn.pack(side='left', padx=(0, 10))
        
        self.tooltip_system.add_tooltip(
            quick_btn, 
            "Demonstrates a quick 3-step operation with progress tracking",
            rich_content={'shortcut': 'Ctrl+D', 'example': 'Database connection test'}
        )
        
        # Complex operation
        complex_btn = ttk.Button(button_frame, text="Complex Operation (8 steps)",
                                command=lambda: self.demo_complex_loading())
        complex_btn.pack(side='left', padx=(0, 10))
        
        self.tooltip_system.add_tooltip(
            complex_btn,
            "Shows detailed progress tracking for complex multi-step operations",
            rich_content={'example': 'Full schema analysis with documentation generation'}
        )
        
        # Background operation
        bg_btn = ttk.Button(button_frame, text="Background Operation",
                           command=lambda: self.demo_background_loading())
        bg_btn.pack(side='left', padx=(0, 10))
        
        self.tooltip_system.add_tooltip(
            bg_btn,
            "Demonstrates background processing with status updates"
        )
        
        # Cached operation
        cache_btn = ttk.Button(button_frame, text="Test Caching",
                              command=lambda: self.demo_cached_operation())
        cache_btn.pack(side='left')
        
        self.tooltip_system.add_tooltip(
            cache_btn,
            "Shows smart caching - first run will be slow, subsequent runs will be instant"
        )
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Operation Results", padding="10")
        results_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.loading_results = tk.Text(results_frame, height=8, wrap='word', 
                                      font=('Consolas', 9), state='disabled')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", 
                                 command=self.loading_results.yview)
        self.loading_results.configure(yscrollcommand=scrollbar.set)
        
        self.loading_results.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_error_demo_tab(self):
        """Create error handling demonstration tab."""
        scrollable = ScrollableFrame(self.notebook)
        frame = scrollable.get_frame()
        self.notebook.add(scrollable.container, text="⚠️ Error Handling")
        
        # Title
        title_label = ttk.Label(frame, text="Advanced Error Handling Demo", 
                               font=('Inter', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """The Improved Error Handler provides:
• User-friendly error messages with context
• Recovery suggestions based on error type
• Comprehensive error logging and analysis
• Beautiful error dialogs with technical details"""
        
        desc_label = ttk.Label(frame, text=desc_text, font=('Inter', 10),
                              justify='left')
        desc_label.pack(anchor='w', pady=(0, 20))
        
        # Error type demos
        error_frame = ttk.LabelFrame(frame, text="Error Type Demonstrations", padding="10")
        error_frame.pack(fill='x', pady=(0, 20))
        
        # Connection errors
        conn_frame = ttk.Frame(error_frame)
        conn_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(conn_frame, text="Connection Errors:", font=('Inter', 10, 'bold')).pack(anchor='w')
        
        btn_frame1 = ttk.Frame(conn_frame)
        btn_frame1.pack(fill='x', pady=(5, 0))
        
        ttk.Button(btn_frame1, text="Timeout Error",
                  command=lambda: self.demo_error_type('connection', 'timeout')).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame1, text="Auth Error",
                  command=lambda: self.demo_error_type('connection', 'auth')).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame1, text="Server Not Found",
                  command=lambda: self.demo_error_type('connection', 'server')).pack(side='left', padx=(0, 5))
        
        # SQL errors
        sql_frame = ttk.Frame(error_frame)
        sql_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(sql_frame, text="SQL Errors:", font=('Inter', 10, 'bold')).pack(anchor='w')
        
        btn_frame2 = ttk.Frame(sql_frame)
        btn_frame2.pack(fill='x', pady=(5, 0))
        
        ttk.Button(btn_frame2, text="Syntax Error",
                  command=lambda: self.demo_error_type('sql', 'syntax')).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame2, text="Table Not Found",
                  command=lambda: self.demo_error_type('sql', 'table')).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame2, text="Permission Denied",
                  command=lambda: self.demo_error_type('sql', 'permission')).pack(side='left', padx=(0, 5))
        
        # System errors
        sys_frame = ttk.Frame(error_frame)
        sys_frame.pack(fill='x')
        ttk.Label(sys_frame, text="System Errors:", font=('Inter', 10, 'bold')).pack(anchor='w')
        
        btn_frame3 = ttk.Frame(sys_frame)
        btn_frame3.pack(fill='x', pady=(5, 0))
        
        ttk.Button(btn_frame3, text="File Not Found",
                  command=lambda: self.demo_error_type('file', 'not_found')).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame3, text="Memory Error",
                  command=lambda: self.demo_error_type('system', 'memory')).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame3, text="Generic Error",
                  command=lambda: self.demo_error_type('system', 'generic')).pack(side='left', padx=(0, 5))
        
        # Error log
        log_frame = ttk.LabelFrame(frame, text="Error Log", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        self.error_log = tk.Text(log_frame, height=6, wrap='word', 
                                font=('Consolas', 9), state='disabled')
        error_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", 
                                       command=self.error_log.yview)
        self.error_log.configure(yscrollcommand=error_scrollbar.set)
        
        self.error_log.pack(side='left', fill='both', expand=True)
        error_scrollbar.pack(side='right', fill='y')
    
    def create_shortcuts_demo_tab(self):
        """Create keyboard shortcuts demonstration tab."""
        scrollable = ScrollableFrame(self.notebook)
        frame = scrollable.get_frame()
        self.notebook.add(scrollable.container, text="⌨️ Shortcuts")
        
        # Title
        title_label = ttk.Label(frame, text="Keyboard Shortcuts System Demo", 
                               font=('Inter', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Context switcher
        context_frame = ttk.LabelFrame(frame, text="Context Management", padding="10")
        context_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(context_frame, text="Current Context:", font=('Inter', 10, 'bold')).pack(anchor='w')
        
        self.context_var = tk.StringVar(value="global")
        context_combo = ttk.Combobox(context_frame, textvariable=self.context_var,
                                    values=["global", "connection", "documentation", "playground"],
                                    state="readonly")
        context_combo.pack(anchor='w', pady=(5, 0))
        context_combo.bind('<<ComboboxSelected>>', self.change_shortcut_context)
        
        self.tooltip_system.add_tooltip(
            context_combo,
            "Different contexts provide different keyboard shortcuts",
            rich_content={'example': 'Connection context adds Ctrl+Enter for testing'}
        )
        
        # Shortcuts display
        shortcuts_frame = ttk.LabelFrame(frame, text="Active Shortcuts", padding="10")
        shortcuts_frame.pack(fill='both', expand=True)
        
        self.shortcuts_text = tk.Text(shortcuts_frame, wrap='word', 
                                     font=('Consolas', 9), state='disabled')
        shortcuts_scrollbar = ttk.Scrollbar(shortcuts_frame, orient="vertical",
                                           command=self.shortcuts_text.yview)
        self.shortcuts_text.configure(yscrollcommand=shortcuts_scrollbar.set)
        
        self.shortcuts_text.pack(side='left', fill='both', expand=True)
        shortcuts_scrollbar.pack(side='right', fill='y')
        
        # Update shortcuts display
        self.update_shortcuts_display()
    
    def create_tooltip_demo_tab(self):
        """Create tooltip system demonstration tab."""
        scrollable = ScrollableFrame(self.notebook)
        frame = scrollable.get_frame()
        self.notebook.add(scrollable.container, text="💬 Tooltips")
        
        # Title
        title_label = ttk.Label(frame, text="Advanced Tooltip System Demo", 
                               font=('Inter', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Basic tooltips section
        basic_frame = ttk.LabelFrame(frame, text="Basic Tooltips", padding="10")
        basic_frame.pack(fill='x', pady=(0, 15))
        
        basic_btn1 = ttk.Button(basic_frame, text="Simple Tooltip")
        basic_btn1.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(basic_btn1, "This is a simple tooltip with basic information")
        
        basic_btn2 = ttk.Button(basic_frame, text="Positioned Tooltip")
        basic_btn2.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(basic_btn2, "This tooltip appears at the top", position="top")
        
        # Rich content tooltips
        rich_frame = ttk.LabelFrame(frame, text="Rich Content Tooltips", padding="10")
        rich_frame.pack(fill='x', pady=(0, 15))
        
        rich_btn1 = ttk.Button(rich_frame, text="With Shortcut")
        rich_btn1.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(
            rich_btn1, 
            "Execute SQL query in the playground",
            rich_content={'shortcut': 'F9 or Ctrl+Enter'}
        )
        
        rich_btn2 = ttk.Button(rich_frame, text="With Example")
        rich_btn2.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(
            rich_btn2,
            "Generate database documentation",
            rich_content={'example': 'SELECT * FROM sys.tables'}
        )
        
        rich_btn3 = ttk.Button(rich_frame, text="Full Rich Content")
        rich_btn3.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(
            rich_btn3,
            "Connect to Azure SQL Database with various authentication methods",
            rich_content={
                'shortcut': 'Ctrl+Shift+C',
                'example': 'Server: server.database.windows.net\\nDatabase: mydb'
            }
        )
        
        # Interactive tooltips
        interactive_frame = ttk.LabelFrame(frame, text="Interactive Elements", padding="10")
        interactive_frame.pack(fill='x', pady=(0, 15))
        
        # Entry with tooltip
        ttk.Label(interactive_frame, text="Server Name:").pack(anchor='w')
        server_entry = ttk.Entry(interactive_frame, width=40)
        server_entry.pack(anchor='w', pady=(2, 10))
        self.tooltip_system.add_tooltip(
            server_entry,
            "Enter the full server name including domain",
            rich_content={'example': 'myserver.database.windows.net'}
        )
        
        # Combobox with tooltip
        ttk.Label(interactive_frame, text="Authentication Method:").pack(anchor='w')
        auth_combo = ttk.Combobox(interactive_frame, 
                                 values=["SQL Server", "Windows", "Azure AD"],
                                 state="readonly", width=37)
        auth_combo.pack(anchor='w', pady=(2, 0))
        self.tooltip_system.add_tooltip(
            auth_combo,
            "Choose the authentication method for database connection",
            rich_content={
                'shortcut': 'Alt+Down to expand',
                'example': 'SQL Server for username/password\\nWindows for integrated auth'
            }
        )
        
        # Tooltip customization
        custom_frame = ttk.LabelFrame(frame, text="Tooltip Customization Demo", padding="10")
        custom_frame.pack(fill='both', expand=True)
        
        ttk.Label(custom_frame, text="Hover over these elements to see different tooltip behaviors:",
                 font=('Inter', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Different delay times
        delay_frame = ttk.Frame(custom_frame)
        delay_frame.pack(fill='x', pady=(0, 10))
        
        delay_btn1 = ttk.Button(delay_frame, text="Fast (100ms)")
        delay_btn1.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(delay_btn1, "Fast appearing tooltip", delay=100)
        
        delay_btn2 = ttk.Button(delay_frame, text="Normal (500ms)")
        delay_btn2.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(delay_btn2, "Normal timing tooltip", delay=500)
        
        delay_btn3 = ttk.Button(delay_frame, text="Slow (1000ms)")
        delay_btn3.pack(side='left', padx=(0, 10))
        self.tooltip_system.add_tooltip(delay_btn3, "Slow appearing tooltip", delay=1000)
    
    def create_integration_demo_tab(self):
        """Create system integration demonstration tab."""
        scrollable = ScrollableFrame(self.notebook)
        frame = scrollable.get_frame()
        self.notebook.add(scrollable.container, text="🔗 Integration")
        
        # Title
        title_label = ttk.Label(frame, text="System Integration Demo", 
                               font=('Inter', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """This tab demonstrates how all Phase 1 systems work together:
• Quick Access Toolbar adapts to different contexts
• Status Bar provides real-time feedback during operations
• Error Handler integrates with all systems for consistent UX
• Keyboard shortcuts work across all components
• Tooltips provide contextual help everywhere"""
        
        desc_label = ttk.Label(frame, text=desc_text, font=('Inter', 10),
                              justify='left')
        desc_label.pack(anchor='w', pady=(0, 20))
        
        # Integrated workflow demo
        workflow_frame = ttk.LabelFrame(frame, text="Integrated Workflow Demo", padding="10")
        workflow_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(workflow_frame, text="Simulate Complete Database Documentation Workflow:",
                 font=('Inter', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        workflow_btn = ttk.Button(workflow_frame, text="🚀 Start Full Workflow Demo",
                                 command=self.demo_full_workflow)
        workflow_btn.pack(anchor='w')
        
        self.tooltip_system.add_tooltip(
            workflow_btn,
            "Demonstrates complete integration of all Phase 1 systems",
            rich_content={
                'shortcut': 'Ctrl+Shift+W',
                'example': 'Connection → Schema Analysis → Documentation Generation'
            }
        )
        
        # Context switching demo
        context_demo_frame = ttk.LabelFrame(frame, text="Context Switching Demo", padding="10")
        context_demo_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(context_demo_frame, text="Switch between different application contexts:",
                 font=('Inter', 10, 'bold')).pack(anchor='w', pady=(0, 10))
        
        context_buttons = ttk.Frame(context_demo_frame)
        context_buttons.pack(fill='x')
        
        for context in ['connection', 'documentation', 'playground']:
            btn = ttk.Button(context_buttons, text=f"{context.title()} Context",
                            command=lambda c=context: self.switch_demo_context(c))
            btn.pack(side='left', padx=(0, 10))
            
            self.tooltip_system.add_tooltip(
                btn,
                f"Switch to {context} context - updates toolbar, shortcuts, and status",
                rich_content={'example': f'Context-specific buttons and shortcuts for {context}'}
            )
        
        # System status
        status_frame = ttk.LabelFrame(frame, text="System Status", padding="10")
        status_frame.pack(fill='both', expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, wrap='word',
                                  font=('Consolas', 9), state='disabled')
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical",
                                        command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side='left', fill='both', expand=True)
        status_scrollbar.pack(side='right', fill='y')
        
        self.update_system_status()
    
    def setup_demonstrations(self):
        """Setup interactive demonstrations."""
        # Register additional shortcuts for workflow demo
        self.shortcut_manager.register_shortcut(
            '<Control-Shift-w>', self.demo_full_workflow, "Full Workflow Demo", "global"
        )
        
        # Start periodic status updates
        self.root.after(1000, self.periodic_status_update)
    
    # Demo Methods
    def demo_quick_loading(self):
        """Demo quick 3-step operation."""
        steps = [
            "Connecting to database...",
            "Validating credentials...",
            "Loading schema information..."
        ]
        
        tracker = self.loading_system.start_operation(
            "quick_demo",
            "Quick Database Connection",
            steps
        )
        
        def simulate_work():
            try:
                for i in range(len(steps)):
                    time.sleep(random.uniform(0.5, 1.5))  # Simulate work
                    self.root.after(0, tracker.advance_step)
                
                # Complete operation
                self.root.after(0, lambda: self.loading_system.complete_operation("quick_demo"))
                self.root.after(0, lambda: self.log_loading_result("Quick operation completed successfully!"))
                
            except Exception as e:
                self.root.after(0, lambda: tracker.error(str(e)))
        
        threading.Thread(target=simulate_work, daemon=True).start()
    
    def demo_complex_loading(self):
        """Demo complex 8-step operation."""
        steps = [
            "Initializing connection pool...",
            "Analyzing database structure...",
            "Scanning tables and views...",
            "Extracting relationships...",
            "Processing stored procedures...",
            "Generating documentation...",
            "Applying formatting...",
            "Finalizing output..."
        ]
        
        tracker = self.loading_system.start_operation(
            "complex_demo",
            "Full Schema Documentation Generation",
            steps
        )
        
        def simulate_complex_work():
            try:
                for i in range(len(steps)):
                    # Variable work time based on step complexity
                    if i in [1, 2, 5]:  # Complex steps
                        time.sleep(random.uniform(1.0, 2.5))
                    else:
                        time.sleep(random.uniform(0.3, 1.0))
                    
                    self.root.after(0, tracker.advance_step)
                
                self.root.after(0, lambda: self.loading_system.complete_operation("complex_demo"))
                self.root.after(0, lambda: self.log_loading_result("Complex operation completed with detailed progress tracking!"))
                
            except Exception as e:
                self.root.after(0, lambda: tracker.error(str(e)))
        
        threading.Thread(target=simulate_complex_work, daemon=True).start()
    
    def demo_background_loading(self):
        """Demo background operation without progress window."""
        tracker = self.loading_system.start_operation(
            "background_demo",
            "Background Data Sync",
            ["Synchronizing data in background..."],
            show_progress_window=False
        )
        
        self.status_bar.update_status("Background operation started...")
        
        def background_work():
            try:
                for i in range(5):
                    time.sleep(1)
                    self.root.after(0, lambda i=i: self.status_bar.update_status(f"Background progress: {(i+1)*20}%"))
                
                self.root.after(0, lambda: self.loading_system.complete_operation("background_demo"))
                self.root.after(0, lambda: self.status_bar.update_status("Background operation completed", 3000))
                self.root.after(0, lambda: self.log_loading_result("Background operation completed silently!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.update_status(f"Background error: {e}", 5000))
        
        threading.Thread(target=background_work, daemon=True).start()
    
    def demo_cached_operation(self):
        """Demo caching system."""
        cache_key = "demo_cached_data"
        
        # Check cache first
        cached_result = self.loading_system.get_cached_result(cache_key)
        
        if cached_result and self.loading_system.is_cache_valid(cache_key):
            self.log_loading_result("⚡ Cache hit! Instant result from cached operation.")
            return
        
        # Simulate expensive operation
        steps = ["Fetching data...", "Processing results...", "Caching for future use..."]
        tracker = self.loading_system.start_operation(
            "cache_demo",
            "Expensive Operation (First Run)",
            steps
        )
        
        def expensive_work():
            try:
                result_data = []
                
                for i, step in enumerate(steps):
                    time.sleep(random.uniform(1.0, 2.0))  # Expensive work
                    result_data.append(f"Step {i+1} result")
                    self.root.after(0, tracker.advance_step)
                
                # Cache the result
                self.loading_system.cache_result(cache_key, result_data, ttl=30)  # 30 second cache
                
                self.root.after(0, lambda: self.loading_system.complete_operation("cache_demo"))
                self.root.after(0, lambda: self.log_loading_result("🐌 First run completed (slow). Try again within 30 seconds for cached result!"))
                
            except Exception as e:
                self.root.after(0, lambda: tracker.error(str(e)))
        
        threading.Thread(target=expensive_work, daemon=True).start()
    
    def demo_error_type(self, category: str, error_type: str):
        """Demo specific error type."""
        error_messages = {
            'connection': {
                'timeout': "Connection timeout after 30 seconds",
                'auth': "Login failed for user 'demo_user'",
                'server': "Could not resolve server name 'nonexistent.server.com'"
            },
            'sql': {
                'syntax': "Incorrect syntax near 'SELCT'",
                'table': "Invalid object name 'NonExistentTable'",
                'permission': "SELECT permission denied on object 'SecureTable'"
            },
            'file': {
                'not_found': "Could not find file 'C:\\nonexistent\\file.txt'"
            },
            'system': {
                'memory': "Out of memory error",
                'generic': "An unexpected system error occurred"
            }
        }
        
        # Create appropriate exception type
        error_msg = error_messages.get(category, {}).get(error_type, "Generic error message")
        
        if category == 'connection':
            if error_type == 'timeout':
                error = TimeoutError(error_msg)
            elif error_type == 'auth':
                error = PermissionError(error_msg)
            else:
                error = ConnectionError(error_msg)
        elif category == 'file':
            error = FileNotFoundError(error_msg)
        elif category == 'system' and error_type == 'memory':
            error = MemoryError(error_msg)
        else:
            error = Exception(error_msg)
        
        # Handle the error
        error_info = self.error_handler.handle_error(error, context=category)
        
        # Log to demo
        self.log_error_result(f"Handled {category}_{error_type} error: {error_info['user_message']}")
    
    def demo_full_workflow(self):
        """Demo complete integrated workflow."""
        self.status_bar.update_status("Starting full workflow demo...")
        
        # Switch to connection context
        self.toolbar.set_context("connection")
        self.shortcut_manager.set_context("connection")
        self.update_system_status("Context switched to: Connection")
        
        def workflow_steps():
            try:
                # Phase 1: Connection
                self.root.after(0, lambda: self.status_bar.update_status("Phase 1: Establishing connection..."))
                time.sleep(1.5)
                
                # Phase 2: Schema Analysis
                self.root.after(0, lambda: self.status_bar.update_status("Phase 2: Analyzing schema..."))
                self.root.after(0, lambda: self.toolbar.set_context("playground"))
                self.root.after(0, lambda: self.shortcut_manager.set_context("playground"))
                time.sleep(2.0)
                
                # Phase 3: Documentation
                self.root.after(0, lambda: self.status_bar.update_status("Phase 3: Generating documentation..."))
                self.root.after(0, lambda: self.toolbar.set_context("documentation"))
                self.root.after(0, lambda: self.shortcut_manager.set_context("documentation"))
                time.sleep(1.8)
                
                # Complete
                self.root.after(0, lambda: self.status_bar.update_status("Workflow completed successfully!", 3000))
                self.root.after(0, lambda: self.update_system_status("Full workflow demo completed - all systems integrated"))
                self.root.after(0, lambda: self.toolbar.set_context("global"))
                self.root.after(0, lambda: self.shortcut_manager.set_context("global"))
                
            except Exception as e:
                self.root.after(0, lambda: self.error_handler.handle_error(e, "workflow"))
        
        threading.Thread(target=workflow_steps, daemon=True).start()
    
    def switch_demo_context(self, context: str):
        """Switch demonstration context."""
        self.toolbar.set_context(context)
        self.shortcut_manager.set_context(context)
        self.status_bar.update_status(f"Switched to {context} context", 2000)
        self.update_system_status(f"Context changed to: {context}")
        self.update_shortcuts_display()
    
    # Helper methods
    def log_loading_result(self, message: str):
        """Log loading operation result."""
        self.loading_results.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        self.loading_results.insert('end', f"[{timestamp}] {message}\n")
        self.loading_results.see('end')
        self.loading_results.config(state='disabled')
    
    def log_error_result(self, message: str):
        """Log error handling result."""
        self.error_log.config(state='normal')
        timestamp = time.strftime("%H:%M:%S")
        self.error_log.insert('end', f"[{timestamp}] {message}\n")
        self.error_log.see('end')
        self.error_log.config(state='disabled')
    
    def update_system_status(self, message: str = None):
        """Update system status display."""
        self.status_text.config(state='normal')
        
        if message:
            timestamp = time.strftime("%H:%M:%S")
            self.status_text.insert('end', f"[{timestamp}] {message}\n")
            self.status_text.see('end')
        
        self.status_text.config(state='disabled')
    
    def change_shortcut_context(self, event):
        """Handle shortcut context change."""
        context = self.context_var.get()
        self.shortcut_manager.set_context(context)
        self.update_shortcuts_display()
        self.status_bar.update_status(f"Shortcuts context: {context}", 2000)
    
    def update_shortcuts_display(self):
        """Update the shortcuts display."""
        context = self.shortcut_manager.current_context
        help_text = self.shortcut_manager.get_shortcuts_help(context)
        
        self.shortcuts_text.config(state='normal')
        self.shortcuts_text.delete('1.0', 'end')
        self.shortcuts_text.insert('1.0', help_text)
        self.shortcuts_text.config(state='disabled')
    
    def periodic_status_update(self):
        """Periodic status bar updates."""
        # Update memory info if available
        try:
            import psutil
            memory = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent()
            self.status_bar.memory_var.set(f"Memory: {memory:.1f}%, CPU: {cpu:.1f}%")
        except ImportError:
            pass
        
        # Schedule next update
        self.root.after(5000, self.periodic_status_update)
    
    # Action methods for toolbar and shortcuts
    def show_help(self):
        """Show help information."""
        help_text = """Phase 1 GUI Improvements Demo - Help

🔄 Smart Loading System:
• Intelligent progress tracking with time estimation
• Smart caching for repeated operations
• Background operation support

⚠️ Advanced Error Handling:
• User-friendly error messages
• Context-specific recovery suggestions
• Comprehensive error logging

⌨️ Keyboard Shortcuts:
• Context-aware shortcut management
• Customizable key bindings
• F1: Show this help
• Ctrl+D: Demo loading system
• Ctrl+E: Demo error handling
• Ctrl+Shift+T: Toggle theme

💬 Rich Tooltips:
• Contextual help with examples
• Smart positioning and timing
• Rich content support

🔗 System Integration:
• All systems work together seamlessly
• Context-aware UI adaptation
• Real-time status feedback

Try the different tabs to explore each feature!"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Phase 1 Demo - Help")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        text_frame = ttk.Frame(dialog, padding="20")
        text_frame.pack(fill='both', expand=True)
        
        help_display = tk.Text(text_frame, wrap='word', font=('Consolas', 10))
        help_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=help_display.yview)
        help_display.configure(yscrollcommand=help_scrollbar.set)
        
        help_display.pack(side='left', fill='both', expand=True)
        help_scrollbar.pack(side='right', fill='y')
        
        help_display.insert('1.0', help_text)
        help_display.config(state='disabled')
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 300
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        dialog.geometry(f"+{x}+{y}")
    
    def demo_loading(self):
        """Shortcut for loading demo."""
        self.demo_quick_loading()
    
    def demo_error(self):
        """Shortcut for error demo."""
        self.demo_error_type('system', 'generic')
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current = self.theme_manager.current_theme
        new_theme = 'dark' if current == 'light' else 'light'
        self.theme_manager.apply_theme(new_theme)
        self.status_bar.update_status(f"Theme switched to {new_theme}", 2000)
    
    def refresh_demo(self):
        """Refresh demo state."""
        self.status_bar.update_status("Demo refreshed - all systems reset", 2000)
        
        # Clear logs
        self.loading_results.config(state='normal')
        self.loading_results.delete('1.0', 'end')
        self.loading_results.config(state='disabled')
        
        self.error_log.config(state='normal')
        self.error_log.delete('1.0', 'end')
        self.error_log.config(state='disabled')
        
        self.update_system_status("Demo state refreshed")
    
    def show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo("Settings", "Settings dialog would open here.\n\nThis demonstrates the toolbar integration!")
    
    def run(self):
        """Run the demo application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nDemo application closed.")


if __name__ == "__main__":
    print("Starting Phase 1 GUI Improvements Demo...")
    print("=" * 50)
    
    try:
        demo = Phase1Demo()
        demo.run()
    except Exception as e:
        print(f"Error starting demo: {e}")
        import traceback
        traceback.print_exc()
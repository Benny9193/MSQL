#!/usr/bin/env python3
"""
Modern UI Demonstration Script
============================

A comprehensive demonstration of all the modern UI features and components
implemented in the Azure SQL Database Documentation Generator.

Run this script to see all the enhanced UI components in action.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

# Import the UI framework components
from ui_framework import (ThemeManager, StatusManager, CardComponent, 
                         DashboardHome, LoadingOverlay)
from enhanced_controls import (ValidatedEntry, ToggleSwitch, CollapsibleFrame, 
                             TooltipManager, CommandPalette, FavoritesManager, FavoritesWidget)


class ModernUIDemo:
    """Demonstration of all modern UI components."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modern UI Framework Demo")
        self.root.geometry("1200x800")
        
        self.setup_demo()
    
    def setup_demo(self):
        """Setup the demonstration interface."""
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.status_manager = StatusManager(self.root)
        self.tooltip_manager = TooltipManager()
        self.favorites_manager = FavoritesManager()
        
        # Initialize styles
        style = ttk.Style()
        style.theme_use('clam')
        self.theme_manager.initialize_styles(style)
        
        # Create main layout
        self.create_demo_layout()
        
        # Setup command palette
        self.command_palette = CommandPalette(self.root)
        self.register_demo_commands()
        
        # Add some demo favorites
        self.add_demo_favorites()
    
    def create_demo_layout(self):
        """Create the demo layout."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_container, text="Modern UI Framework Demo", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Theme selection
        theme_frame = ttk.Frame(main_container)
        theme_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(theme_frame, text="Select Theme:", font=('Arial', 12, 'bold')).pack(side='left')
        
        self.theme_var = tk.StringVar(value="light")
        for theme in self.theme_manager.get_available_themes():
            ttk.Radiobutton(theme_frame, text=theme.title(), variable=self.theme_var, 
                          value=theme, command=self.change_theme).pack(side='left', padx=10)
        
        # Create notebook for different demos
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True)
        
        # Demo tabs
        self.create_controls_demo(notebook)
        self.create_cards_demo(notebook)
        self.create_notifications_demo(notebook)
        self.create_forms_demo(notebook)
        self.create_favorites_demo(notebook)
        
        # Status bar
        status_bar = self.status_manager.create_status_bar(self.root)
        status_bar.pack(side='bottom', fill='x')
        
        # Show welcome message
        self.status_manager.show_toast_notification("Welcome to the Modern UI Demo!", 'info')
    
    def create_controls_demo(self, notebook):
        """Create enhanced controls demonstration."""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Enhanced Controls")
        
        # Section title
        ttk.Label(frame, text="Enhanced Form Controls", style='Heading.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Toggle switches
        toggle_section = ttk.LabelFrame(frame, text="Toggle Switches", padding="15")
        toggle_section.pack(fill='x', pady=(0, 15))
        
        self.notifications_enabled = tk.BooleanVar(value=True)
        self.dark_mode_enabled = tk.BooleanVar(value=False)
        self.auto_save_enabled = tk.BooleanVar(value=True)
        
        ToggleSwitch(toggle_section, text="Enable Notifications", 
                    variable=self.notifications_enabled, command=self.on_toggle_changed).pack(anchor='w', pady=5)
        ToggleSwitch(toggle_section, text="Dark Mode", 
                    variable=self.dark_mode_enabled, command=self.toggle_dark_mode).pack(anchor='w', pady=5)
        ToggleSwitch(toggle_section, text="Auto Save", 
                    variable=self.auto_save_enabled, command=self.on_toggle_changed).pack(anchor='w', pady=5)
        
        # Collapsible sections
        collapsible_section = ttk.LabelFrame(frame, text="Collapsible Sections", padding="15")
        collapsible_section.pack(fill='x', pady=(0, 15))
        
        # Create collapsible frames
        for i, (title, content) in enumerate([
            ("Database Settings", "Configure your database connection parameters here."),
            ("Advanced Options", "Additional settings for power users."),
            ("Help & Documentation", "Access help resources and documentation.")
        ]):
            collapsible = CollapsibleFrame(collapsible_section, title)
            collapsible.pack(fill='x', pady=5)
            
            # Add content
            content_frame = collapsible.get_content_frame()
            ttk.Label(content_frame, text=content).pack(padx=10, pady=10)
            
            if i == 0:  # Expand first section by default
                collapsible.expanded.set(True)
        
        # Command palette info
        cmd_section = ttk.LabelFrame(frame, text="Command Palette", padding="15")
        cmd_section.pack(fill='x')
        
        ttk.Label(cmd_section, text="Press Ctrl+Shift+P to open the command palette", 
                 font=('Arial', 12)).pack()
        ttk.Label(cmd_section, text="Search and execute any command quickly!", 
                 style='Status.TLabel').pack()
    
    def create_cards_demo(self, notebook):
        """Create card components demonstration."""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Card Components")
        
        # Section title
        ttk.Label(frame, text="Modern Card Components", style='Heading.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Metric cards
        metrics_frame = ttk.LabelFrame(frame, text="Metric Cards", padding="15")
        metrics_frame.pack(fill='x', pady=(0, 15))
        
        metrics_container = ttk.Frame(metrics_frame)
        metrics_container.pack(fill='x')
        
        card_component = CardComponent(metrics_container, self.theme_manager)
        
        # Create metric cards
        metrics = [
            ("127", "Total Databases", "+12%", "success"),
            ("45", "Active Connections", "-3%", "warning"),
            ("98.5%", "Uptime", "+0.2%", "success"),
            ("2.3s", "Avg Response", "+0.1s", "danger")
        ]
        
        for i, (value, label, trend, color) in enumerate(metrics):
            card = card_component.create_metric_card(metrics_container, value, label, trend, color)
            card.pack(side='left', fill='x', expand=True, padx=5 if i > 0 else 0)
        
        # Info cards
        info_frame = ttk.LabelFrame(frame, text="Information Cards", padding="15")
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Sample info cards
        actions = [
            {'text': 'View Details', 'command': lambda: self.show_demo_message("Details viewed!"), 'style': 'Primary.TButton'},
            {'text': 'Edit', 'command': lambda: self.show_demo_message("Edit mode activated!"), 'style': 'Secondary.TButton'}
        ]
        
        info_card = card_component.create_info_card(info_frame, "Database Connection Status",
                                                  "Currently connected to ProductionDB with 15 active sessions.", actions)
        info_card.pack(fill='x', pady=5)
        
        # Status cards
        status_frame = ttk.LabelFrame(frame, text="Status Cards", padding="15")
        status_frame.pack(fill='x')
        
        statuses = [
            ("API Server", "online", ["Port 8080 open", "3 active connections"]),
            ("Database Monitor", "active", ["Checking every 30 seconds", "Last check: 2 minutes ago"]),
            ("Scheduler", "pending", ["5 jobs queued", "Next run: in 15 minutes"])
        ]
        
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill='x')
        
        for i, (title, status, details) in enumerate(statuses):
            status_card = card_component.create_status_card(status_container, title, status, details)
            status_card.pack(side='left', fill='x', expand=True, padx=5 if i > 0 else 0)
    
    def create_notifications_demo(self, notebook):
        """Create notifications demonstration."""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Notifications & Dialogs")
        
        # Section title
        ttk.Label(frame, text="Status & Notification System", style='Heading.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Toast notifications
        toast_section = ttk.LabelFrame(frame, text="Toast Notifications", padding="15")
        toast_section.pack(fill='x', pady=(0, 15))
        
        toast_buttons_frame = ttk.Frame(toast_section)
        toast_buttons_frame.pack(fill='x')
        
        toast_types = [
            ("Info", "info", "This is an info message"),
            ("Success", "success", "Operation completed successfully!"),
            ("Warning", "warning", "Please check your input"),
            ("Error", "error", "An error occurred")
        ]
        
        for text, type_name, message in toast_types:
            ttk.Button(toast_buttons_frame, text=f"Show {text}",
                      command=lambda t=type_name, m=message: self.status_manager.show_toast_notification(m, t)).pack(side='left', padx=5)
        
        # Progress windows
        progress_section = ttk.LabelFrame(frame, text="Progress Windows", padding="15")
        progress_section.pack(fill='x', pady=(0, 15))
        
        ttk.Button(progress_section, text="Show Progress Window",
                  command=self.show_progress_demo).pack()
        
        # Confirmation dialogs
        dialog_section = ttk.LabelFrame(frame, text="Modern Dialogs", padding="15")
        dialog_section.pack(fill='x')
        
        ttk.Button(dialog_section, text="Show Confirmation Dialog",
                  command=self.show_confirmation_demo).pack()
    
    def create_forms_demo(self, notebook):
        """Create form validation demonstration."""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Form Validation")
        
        # Section title
        ttk.Label(frame, text="Enhanced Form Controls with Validation", style='Heading.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Form section
        form_section = ttk.LabelFrame(frame, text="Validated Form Fields", padding="15")
        form_section.pack(fill='x')
        
        # Email field
        ttk.Label(form_section, text="Email Address:").pack(anchor='w', pady=(10, 0))
        self.email_entry = ValidatedEntry(form_section, placeholder="Enter your email address",
                                        validation_type="email", required=True)
        self.email_entry.pack(fill='x', pady=(5, 10))
        
        # Server field
        ttk.Label(form_section, text="Server Name:").pack(anchor='w')
        self.server_entry = ValidatedEntry(form_section, placeholder="server.database.windows.net",
                                         validation_type="server", required=True)
        self.server_entry.pack(fill='x', pady=(5, 10))
        
        # Database field
        ttk.Label(form_section, text="Database Name:").pack(anchor='w')
        self.db_entry = ValidatedEntry(form_section, placeholder="database_name",
                                     validation_type="database", required=True)
        self.db_entry.pack(fill='x', pady=(5, 10))
        
        # Custom validation field
        ttk.Label(form_section, text="Custom Validation (Must contain 'test'):").pack(anchor='w')
        self.custom_entry = ValidatedEntry(form_section, placeholder="Enter text containing 'test'",
                                         custom_validator=lambda x: ("test" in x.lower(), "Text must contain 'test'"),
                                         required=True)
        self.custom_entry.pack(fill='x', pady=(5, 10))
        
        # Validation button
        ttk.Button(form_section, text="Validate All Fields",
                  command=self.validate_demo_form).pack(pady=10)
    
    def create_favorites_demo(self, notebook):
        """Create favorites demonstration."""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Favorites & Bookmarks")
        
        # Section title
        ttk.Label(frame, text="Favorites Management System", style='Heading.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Favorites widget
        favorites_section = ttk.LabelFrame(frame, text="Saved Favorites", padding="10")
        favorites_section.pack(fill='both', expand=True, pady=(0, 15))
        
        favorites_widget = FavoritesWidget(favorites_section, self.favorites_manager)
        favorites_widget.pack(fill='both', expand=True)
        
        # Add favorite button
        actions_frame = ttk.Frame(frame)
        actions_frame.pack(fill='x')
        
        ttk.Button(actions_frame, text="Add Sample Favorite",
                  command=self.add_sample_favorite).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text="Clear All Favorites",
                  command=self.clear_favorites).pack(side='left')
    
    def change_theme(self):
        """Change the application theme."""
        theme_name = self.theme_var.get()
        self.theme_manager.apply_theme(theme_name)
        self.status_manager.show_toast_notification(f"Theme changed to {theme_name}", 'info')
    
    def on_toggle_changed(self):
        """Handle toggle switch changes."""
        if self.notifications_enabled.get():
            self.status_manager.show_toast_notification("Notifications enabled", 'success')
        
        if self.auto_save_enabled.get():
            self.status_manager.show_toast_notification("Auto-save enabled", 'info')
    
    def toggle_dark_mode(self):
        """Toggle dark mode."""
        if self.dark_mode_enabled.get():
            self.theme_var.set('dark')
            self.theme_manager.apply_theme('dark')
            self.status_manager.show_toast_notification("Dark mode enabled", 'info')
        else:
            self.theme_var.set('light')
            self.theme_manager.apply_theme('light')
            self.status_manager.show_toast_notification("Light mode enabled", 'info')
    
    def show_demo_message(self, message: str):
        """Show a demo message."""
        self.status_manager.show_toast_notification(message, 'success')
    
    def show_progress_demo(self):
        """Show progress window demo."""
        progress_window = self.status_manager.show_progress_window(
            "Demo Operation",
            "Demonstrating progress window functionality..."
        )
        
        def progress_thread():
            stages = [
                ("Initializing demo", 20),
                ("Processing data", 40),
                ("Applying changes", 60),
                ("Updating display", 80),
                ("Finalizing", 100)
            ]
            
            for stage, percent in stages:
                if progress_window.is_cancelled():
                    return
                
                self.root.after(0, lambda s=stage, p=percent: 
                               progress_window.update_progress(p, "Demo Operation", s))
                time.sleep(1)
            
            self.root.after(0, lambda: progress_window.close())
            self.root.after(0, lambda: self.status_manager.show_toast_notification(
                "Demo operation completed!", 'success'))
        
        threading.Thread(target=progress_thread, daemon=True).start()
    
    def show_confirmation_demo(self):
        """Show confirmation dialog demo."""
        def on_confirmed():
            self.status_manager.show_toast_notification("Action confirmed!", 'success')
        
        self.status_manager.show_confirmation_dialog(
            "Confirmation Demo",
            "This is a modern confirmation dialog. Do you want to proceed?",
            on_confirmed
        )
    
    def validate_demo_form(self):
        """Validate all form fields."""
        fields = [self.email_entry, self.server_entry, self.db_entry, self.custom_entry]
        all_valid = all(field.validate() for field in fields)
        
        if all_valid:
            self.status_manager.show_toast_notification("All fields are valid!", 'success')
        else:
            self.status_manager.show_toast_notification("Please fix form errors", 'error')
    
    def add_demo_favorites(self):
        """Add demo favorites."""
        demo_favorites = [
            ('connection', 'Production Database', {'server': 'prod-server.com', 'database': 'MainDB'}),
            ('connection', 'Development Database', {'server': 'dev-server.com', 'database': 'DevDB'}),
            ('database', 'Analytics DB', {'server': 'analytics.com', 'database': 'Analytics'}),
            ('report', 'Monthly Report', {'type': 'monthly', 'format': 'html'}),
            ('object', 'Users Table', {'table': 'Users', 'schema': 'dbo'})
        ]
        
        for fav_type, name, data in demo_favorites:
            self.favorites_manager.add_favorite(fav_type, name, data)
    
    def add_sample_favorite(self):
        """Add a sample favorite."""
        import random
        
        sample_names = ['Test Connection', 'Demo Database', 'Sample Report', 'Example Table']
        name = f"{random.choice(sample_names)} {random.randint(1, 100)}"
        
        self.favorites_manager.add_favorite('connection', name, {'demo': True, 'timestamp': time.time()})
        self.status_manager.show_toast_notification(f"Added favorite: {name}", 'success')
    
    def clear_favorites(self):
        """Clear all favorites."""
        def on_confirmed():
            # This would clear favorites in a real implementation
            self.status_manager.show_toast_notification("Favorites cleared!", 'info')
        
        self.status_manager.show_confirmation_dialog(
            "Clear Favorites",
            "Are you sure you want to clear all favorites?",
            on_confirmed
        )
    
    def register_demo_commands(self):
        """Register demo commands for command palette."""
        commands = [
            ('Show Info Toast', 'Show an info notification', 
             lambda: self.status_manager.show_toast_notification("Info from command palette!", 'info'), 
             ['info', 'notification']),
            ('Show Success Toast', 'Show a success notification', 
             lambda: self.status_manager.show_toast_notification("Success from command palette!", 'success'), 
             ['success', 'notification']),
            ('Switch to Dark Theme', 'Switch to dark theme', 
             lambda: (self.theme_var.set('dark'), self.theme_manager.apply_theme('dark')), 
             ['dark', 'theme']),
            ('Switch to Light Theme', 'Switch to light theme', 
             lambda: (self.theme_var.set('light'), self.theme_manager.apply_theme('light')), 
             ['light', 'theme']),
            ('Show Progress Demo', 'Demonstrate progress window', 
             self.show_progress_demo, ['progress', 'demo']),
            ('Validate Form', 'Validate all form fields', 
             self.validate_demo_form, ['validate', 'form']),
        ]
        
        for name, desc, callback, keywords in commands:
            self.command_palette.register_command(name, desc, callback, keywords)
    
    def run(self):
        """Run the demo application."""
        # Add demo instructions
        instructions = """
Modern UI Demo Instructions:
• Try different themes using the radio buttons
• Test toggle switches and collapsible sections
• Click buttons to see toast notifications
• Press Ctrl+Shift+P for the command palette
• Validate form fields by entering different values
• View the favorites system in the last tab

Keyboard Shortcuts:
• Ctrl+Shift+P: Command Palette
• Ctrl+T: Toggle Theme (in full app)
        """
        
        self.status_manager.update_status("Demo ready - explore all features!")
        print(instructions)
        
        self.root.mainloop()


if __name__ == "__main__":
    demo = ModernUIDemo()
    demo.run()
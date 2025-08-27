#!/usr/bin/env python3
"""
Modern UI Demo - Showcase for Sleek and Modernized UI Elements
=============================================================

A demonstration application showcasing the modernized UI framework with:
- Sleek color schemes and typography
- Smooth animations and transitions  
- Modern card layouts and spacing
- Interactive elements with visual feedback
- Contemporary design patterns
"""

import tkinter as tk
from tkinter import ttk
import time
from ui_framework import (
    ThemeManager, StatusManager, CardComponent, 
    ToastNotification, ModernDialog, ScrollableFrame
)

class ModernUIDemo:
    """Demo application showcasing modernized UI elements."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_theme()
        self.create_interface()
        
    def setup_window(self):
        """Setup main window with modern styling."""
        self.root.title("Modern UI Demo - Azure SQL Database Documentation Generator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
    def setup_theme(self):
        """Initialize theme manager and status system."""
        self.theme_manager = ThemeManager()
        self.theme_manager.initialize_styles(ttk.Style())
        
        self.status_manager = StatusManager(self.root)
        
        # Create card component
        self.card_component = CardComponent(self.root, self.theme_manager)
        
    def create_interface(self):
        """Create the demo interface."""
        # Main container with modern styling
        main_container = ttk.Frame(self.root, style='TFrame', padding="24")
        main_container.pack(fill='both', expand=True)
        
        # Header section
        self.create_header(main_container)
        
        # Content area with tabs
        self.create_content_area(main_container)
        
        # Status bar
        status_bar = self.status_manager.create_status_bar(self.root)
        status_bar.pack(side='bottom', fill='x')
        
        # Set initial status
        self.status_manager.update_status("Modern UI Demo Ready")
        
    def create_header(self, parent):
        """Create modern header section."""
        header_frame = ttk.Frame(parent, style='TFrame')
        header_frame.pack(fill='x', pady=(0, 24))
        
        # Title with modern typography
        title_label = ttk.Label(header_frame, text="Modern UI Showcase", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
        # Theme toggle button
        theme_frame = ttk.Frame(header_frame, style='TFrame')
        theme_frame.pack(side='right')
        
        ttk.Button(theme_frame, text="Switch to Dark", 
                  command=self.toggle_theme, 
                  style='Secondary.TButton').pack(side='right', padx=(8, 0))
        
        ttk.Button(theme_frame, text="Show Toast", 
                  command=lambda: self.show_sample_toast('info'),
                  style='Primary.TButton').pack(side='right')
        
    def create_content_area(self, parent):
        """Create tabbed content area."""
        # Modern notebook with sleek tabs
        notebook = ttk.Notebook(parent, style='TNotebook')
        notebook.pack(fill='both', expand=True)
        
        # Typography Tab
        self.create_typography_tab(notebook)
        
        # Cards Tab
        self.create_cards_tab(notebook)
        
        # Interactive Elements Tab
        self.create_interactive_tab(notebook)
        
        # Forms Tab
        self.create_forms_tab(notebook)
        
        # Scrollable Content Tab
        self.create_scrollable_tab(notebook)
        
    def create_typography_tab(self, notebook):
        """Create typography showcase tab."""
        tab_frame = ttk.Frame(notebook, style='TFrame', padding="24")
        notebook.add(tab_frame, text="Typography")
        
        # Typography samples
        typography_samples = [
            ("Title Style", "Title.TLabel", "Large heading for major sections"),
            ("Heading Style", "Heading.TLabel", "Section headings"),
            ("Subheading Style", "Subheading.TLabel", "Subsection headings"),
            ("Body Style", "Body.TLabel", "Regular body text content"),
            ("Caption Style", "Caption.TLabel", "Small descriptive text"),
        ]
        
        for text, style, description in typography_samples:
            sample_frame = ttk.Frame(tab_frame, style='Card.TFrame', padding="16")
            sample_frame.pack(fill='x', pady=(0, 16))
            
            ttk.Label(sample_frame, text=text, style=style).pack(anchor='w')
            ttk.Label(sample_frame, text=f"Style: {style}", 
                     style='Caption.TLabel').pack(anchor='w', pady=(4, 0))
            ttk.Label(sample_frame, text=description, 
                     style='Body.TLabel').pack(anchor='w', pady=(2, 0))
    
    def create_cards_tab(self, notebook):
        """Create card components showcase tab."""
        tab_frame = ttk.Frame(notebook, style='TFrame', padding="24")
        notebook.add(tab_frame, text="Cards & Metrics")
        
        # Metrics row
        metrics_frame = ttk.Frame(tab_frame, style='TFrame')
        metrics_frame.pack(fill='x', pady=(0, 24))
        
        metrics_data = [
            ("1,247", "Total Databases", "+12%", "success"),
            ("98.5%", "Uptime", "+0.3%", "success"),
            ("42ms", "Avg Response", "-5ms", "info"),
            ("3", "Active Issues", "-2", "warning"),
        ]
        
        for i, (value, label, trend, color) in enumerate(metrics_data):
            metric_card = self.card_component.create_metric_card(
                metrics_frame, value, label, trend, color
            )
            metric_card.pack(side='left', fill='both', expand=True, 
                           padx=(0, 16) if i < len(metrics_data)-1 else (0, 0))
        
        # Info cards
        info_frame = ttk.Frame(tab_frame, style='TFrame')
        info_frame.pack(fill='x', pady=(0, 24))
        
        # Feature card
        feature_card = self.card_component.create_info_card(
            info_frame,
            title="Modern Design System",
            content="Built with contemporary UI patterns, consistent spacing, and intuitive interactions. Features smooth animations, modern typography, and accessible color schemes.",
            actions=[
                {"text": "Learn More", "command": lambda: self.show_sample_toast('info'), "style": "Primary.TButton"},
                {"text": "Docs", "command": lambda: self.show_sample_toast('success'), "style": "Ghost.TButton"}
            ]
        )
        feature_card.pack(side='left', fill='both', expand=True, padx=(0, 16))
        
        # Status card
        status_card = self.card_component.create_status_card(
            info_frame,
            title="System Status",
            status="online",
            details=["All services operational", "Last update: 2 minutes ago"]
        )
        status_card.pack(side='right', fill='both', expand=True)
    
    def create_interactive_tab(self, notebook):
        """Create interactive elements tab."""
        tab_frame = ttk.Frame(notebook, style='TFrame', padding="24")
        notebook.add(tab_frame, text="Interactive Elements")
        
        # Button showcase
        buttons_frame = ttk.LabelFrame(tab_frame, text="Modern Buttons", 
                                     style='TLabelFrame', padding="20")
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        button_row1 = ttk.Frame(buttons_frame, style='TFrame')
        button_row1.pack(fill='x', pady=(0, 12))
        
        ttk.Button(button_row1, text="Primary Action", 
                  style='Primary.TButton',
                  command=lambda: self.show_sample_toast('success')).pack(side='left', padx=(0, 12))
        
        ttk.Button(button_row1, text="Secondary", 
                  style='Secondary.TButton',
                  command=lambda: self.show_sample_toast('info')).pack(side='left', padx=(0, 12))
        
        ttk.Button(button_row1, text="Success", 
                  style='Success.TButton',
                  command=lambda: self.show_sample_toast('success')).pack(side='left', padx=(0, 12))
        
        button_row2 = ttk.Frame(buttons_frame, style='TFrame')
        button_row2.pack(fill='x')
        
        ttk.Button(button_row2, text="Warning", 
                  style='Warning.TButton',
                  command=lambda: self.show_sample_toast('warning')).pack(side='left', padx=(0, 12))
        
        ttk.Button(button_row2, text="Danger", 
                  style='Danger.TButton',
                  command=lambda: self.show_sample_toast('error')).pack(side='left', padx=(0, 12))
        
        ttk.Button(button_row2, text="Ghost", 
                  style='Ghost.TButton',
                  command=lambda: self.show_sample_toast('info')).pack(side='left', padx=(0, 12))
        
        # Dialogs section
        dialogs_frame = ttk.LabelFrame(tab_frame, text="Modern Dialogs", 
                                     style='TLabelFrame', padding="20")
        dialogs_frame.pack(fill='x')
        
        dialog_buttons = ttk.Frame(dialogs_frame, style='TFrame')
        dialog_buttons.pack()
        
        ttk.Button(dialog_buttons, text="Info Dialog", 
                  command=lambda: self.show_sample_dialog('info')).pack(side='left', padx=(0, 12))
        
        ttk.Button(dialog_buttons, text="Warning Dialog", 
                  command=lambda: self.show_sample_dialog('warning')).pack(side='left', padx=(0, 12))
        
        ttk.Button(dialog_buttons, text="Question Dialog", 
                  command=lambda: self.show_sample_dialog('question')).pack(side='left')
    
    def create_forms_tab(self, notebook):
        """Create modern form elements tab."""
        tab_frame = ttk.Frame(notebook, style='TFrame', padding="24")
        notebook.add(tab_frame, text="Form Elements")
        
        form_frame = ttk.LabelFrame(tab_frame, text="Modern Form Design", 
                                  style='TLabelFrame', padding="24")
        form_frame.pack(fill='x')
        
        # Form fields with modern styling
        fields_frame = ttk.Frame(form_frame, style='TFrame')
        fields_frame.pack(fill='x', pady=(0, 16))
        
        # Name field
        name_frame = ttk.Frame(fields_frame, style='TFrame')
        name_frame.pack(fill='x', pady=(0, 16))
        ttk.Label(name_frame, text="Name", style='Body.TLabel').pack(anchor='w', pady=(0, 4))
        name_entry = ttk.Entry(name_frame, style='TEntry', font=('Inter', 9))
        name_entry.pack(fill='x')
        name_entry.insert(0, "Modern UI Framework")
        
        # Email field  
        email_frame = ttk.Frame(fields_frame, style='TFrame')
        email_frame.pack(fill='x', pady=(0, 16))
        ttk.Label(email_frame, text="Description", style='Body.TLabel').pack(anchor='w', pady=(0, 4))
        desc_entry = ttk.Entry(email_frame, style='TEntry', font=('Inter', 9))
        desc_entry.pack(fill='x')
        desc_entry.insert(0, "Sleek and intuitive database management interface")
        
        # Dropdown
        dropdown_frame = ttk.Frame(fields_frame, style='TFrame')
        dropdown_frame.pack(fill='x', pady=(0, 16))
        ttk.Label(dropdown_frame, text="Theme", style='Body.TLabel').pack(anchor='w', pady=(0, 4))
        theme_var = tk.StringVar(value="Light")
        theme_combo = ttk.Combobox(dropdown_frame, textvariable=theme_var, 
                                 values=["Light", "Dark", "Auto"], 
                                 style='TCombobox', font=('Inter', 9))
        theme_combo.pack(fill='x')
        
        # Form actions
        actions_frame = ttk.Frame(form_frame, style='TFrame')
        actions_frame.pack(fill='x', pady=(16, 0))
        
        ttk.Button(actions_frame, text="Save Changes", 
                  style='Primary.TButton',
                  command=lambda: self.status_manager.show_message("Changes saved successfully!", "success")).pack(side='right', padx=(12, 0))
        
        ttk.Button(actions_frame, text="Reset", 
                  style='Secondary.TButton',
                  command=lambda: self.status_manager.show_message("Form reset", "info")).pack(side='right')
    
    def create_scrollable_tab(self, notebook):
        """Create scrollable content demonstration tab."""
        # Create scrollable container for the tab content
        scrollable = ScrollableFrame(notebook)
        scrollable_frame = scrollable.get_frame()
        
        # Add tab to notebook
        notebook.add(scrollable.container, text="Scrollable Content")
        
        # Create extensive content to demonstrate scrolling
        content_container = ttk.Frame(scrollable_frame, padding="24")
        content_container.pack(fill='both', expand=True)
        
        # Header
        ttk.Label(content_container, text="Scrollable Content Demo", 
                 style='Title.TLabel').pack(anchor='w', pady=(0, 16))
        
        ttk.Label(content_container, 
                 text="This tab demonstrates scrollable content areas that adapt to any screen size. Use your mouse wheel or scrollbars to navigate.", 
                 style='Body.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create multiple sections to force scrolling
        sections = [
            ("Database Connections", "Manage and configure database connections with various authentication methods."),
            ("Schema Analysis", "Explore database schemas with interactive visualizations and detailed object information."),
            ("Documentation Generation", "Create comprehensive database documentation in multiple formats including HTML, Markdown, and JSON."),
            ("Performance Monitoring", "Monitor real-time database performance metrics with customizable dashboards and alerts."),
            ("Query Optimization", "Analyze and optimize database queries for better performance and resource utilization."),
            ("Security Compliance", "Audit database security settings and ensure compliance with industry standards."),
            ("Migration Planning", "Plan and execute database migrations with detailed analysis and risk assessment."),
            ("Backup Management", "Schedule and manage database backups with automated verification and recovery testing."),
            ("User Management", "Manage database users, roles, and permissions with comprehensive access control."),
            ("Data Analysis", "Perform advanced data analysis with built-in statistical tools and visualization."),
        ]
        
        for i, (title, description) in enumerate(sections):
            # Create section card
            section_card = self.card_component.create_info_card(
                content_container,
                title=title,
                content=description,
                actions=[
                    {"text": "Configure", "command": lambda t=title: self.status_manager.show_message(f"Configuring {t}", "info"), "style": "Primary.TButton"},
                    {"text": "Learn More", "command": lambda t=title: self.status_manager.show_message(f"More info about {t}", "success"), "style": "Ghost.TButton"}
                ]
            )
            section_card.pack(fill='x', pady=(0, 16))
            
            # Add some form elements to make it more realistic
            if i % 3 == 0:  # Every third section gets a form
                form_frame = ttk.LabelFrame(content_container, text=f"{title} Settings", 
                                          padding="16")
                form_frame.pack(fill='x', pady=(0, 16))
                
                # Add form fields
                field_frame = ttk.Frame(form_frame)
                field_frame.pack(fill='x', pady=(0, 8))
                
                ttk.Label(field_frame, text="Configuration Name:", style='Body.TLabel').pack(anchor='w')
                entry = ttk.Entry(field_frame, style='TEntry')
                entry.pack(fill='x', pady=(4, 8))
                entry.insert(0, f"{title} Configuration")
                
                ttk.Label(field_frame, text="Options:", style='Body.TLabel').pack(anchor='w')
                options_frame = ttk.Frame(field_frame)
                options_frame.pack(fill='x', pady=4)
                
                # Add checkboxes
                for j, option in enumerate(["Enable notifications", "Auto-refresh", "Advanced mode"]):
                    var = tk.BooleanVar(value=j == 0)  # First option checked
                    ttk.Checkbutton(options_frame, text=option, variable=var, 
                                  style='TCheckbutton').pack(anchor='w', pady=2)
        
        # Add footer
        footer_frame = ttk.Frame(content_container, padding="20")
        footer_frame.pack(fill='x', pady=20)
        
        ttk.Label(footer_frame, text="End of scrollable content", 
                 style='Caption.TLabel').pack(anchor='w')
        
        # Add scroll controls
        controls_frame = ttk.Frame(footer_frame)
        controls_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(controls_frame, text="Scroll to Top", 
                  style='Secondary.TButton',
                  command=scrollable.scroll_to_top).pack(side='left', padx=(0, 10))
        
        ttk.Button(controls_frame, text="Scroll to Bottom", 
                  style='Secondary.TButton',
                  command=scrollable.scroll_to_bottom).pack(side='left')
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.theme_manager.current_theme
        new_theme = 'dark' if current_theme == 'light' else 'light'
        self.theme_manager.apply_theme(new_theme)
        self.status_manager.show_message(f"Switched to {new_theme.title()} theme", "info")
    
    def show_sample_toast(self, toast_type):
        """Show sample toast notification."""
        messages = {
            'info': "This is an informational message with modern styling",
            'success': "Operation completed successfully with smooth animations",
            'warning': "Please review the highlighted items before continuing", 
            'error': "An error occurred - please check your inputs and try again"
        }
        
        self.status_manager.show_message(messages[toast_type], toast_type, 4000)
    
    def show_sample_dialog(self, dialog_type):
        """Show sample modern dialog."""
        messages = {
            'info': "This is a modern information dialog with sleek styling and improved user experience.",
            'warning': "This action cannot be undone. Are you sure you want to continue?",
            'question': "Would you like to save your changes before closing?"
        }
        
        buttons = {
            'info': ['OK'],
            'warning': ['Continue', 'Cancel'],
            'question': ['Save', 'Don\'t Save', 'Cancel']
        }
        
        dialog = ModernDialog(self.root, f"{dialog_type.title()} Dialog", 
                            messages[dialog_type], dialog_type, buttons[dialog_type])
        result = dialog.show()
        
        if result:
            self.status_manager.show_message(f"Dialog result: {result}", "info")
    
    def run(self):
        """Run the demo application."""
        print("Starting Modern UI Demo...")
        print("Features:")
        print("• Sleek color schemes and modern typography")
        print("• Smooth animations and transitions")
        print("• Contemporary card layouts and spacing") 
        print("• Interactive elements with visual feedback")
        print("• Modern form controls and buttons")
        print()
        
        self.root.mainloop()

def main():
    """Main entry point."""
    demo = ModernUIDemo()
    demo.run()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Modern UI Framework for Azure SQL Database Documentation Generator
================================================================

A comprehensive UI framework providing modern theming, enhanced controls,
responsive layouts, and improved user experience components.

Features:
- Theme management system with light/dark modes
- Enhanced form controls with validation
- Modern layout components (cards, panels, etc.)
- Responsive design patterns
- Status and notification system
- Interactive components and animations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
import threading
import time


class ThemeManager:
    """Manages application themes and styling."""
    
    def __init__(self):
        self.current_theme = 'light'
        self.themes = self._load_themes()
        self.style = None
        self.theme_change_callbacks = []
    
    def _load_themes(self) -> Dict[str, Dict[str, str]]:
        """Load modern theme definitions with sleek colors and improved hierarchy."""
        return {
            'light': {
                'primary': '#1a1a1a',
                'primary_light': '#2d2d30',
                'secondary': '#007acc',
                'secondary_light': '#1890ff',
                'success': '#00c851',
                'success_light': '#00e676',
                'warning': '#ff9800',
                'warning_light': '#ffb74d',
                'danger': '#f44336',
                'danger_light': '#ff7043',
                'info': '#2196f3',
                'info_light': '#42a5f5',
                'background': '#fafbfc',
                'background_secondary': '#f6f8fa',
                'surface': '#ffffff',
                'surface_secondary': '#f8f9fa',
                'surface_elevated': '#ffffff',
                'text': '#1a1a1a',
                'text_secondary': '#586069',
                'text_muted': '#8b949e',
                'text_disabled': '#d0d7de',
                'border': '#d1d9e0',
                'border_light': '#e1e8ed',
                'border_focus': '#007acc',
                'shadow': 'rgba(0, 0, 0, 0.04)',
                'shadow_elevated': 'rgba(0, 0, 0, 0.08)',
                'shadow_modal': 'rgba(0, 0, 0, 0.16)',
                'accent': '#007acc',
                'accent_light': '#e3f2fd',
                'hover': 'rgba(0, 122, 204, 0.08)',
                'active': 'rgba(0, 122, 204, 0.12)',
                'selection': 'rgba(0, 122, 204, 0.15)'
            },
            'dark': {
                'primary': '#f0f6ff',
                'primary_light': '#ffffff',
                'secondary': '#58a6ff',
                'secondary_light': '#79c0ff',
                'success': '#3fb950',
                'success_light': '#56d364',
                'warning': '#d29922',
                'warning_light': '#e3b341',
                'danger': '#f85149',
                'danger_light': '#ff7b72',
                'info': '#58a6ff',
                'info_light': '#79c0ff',
                'background': '#0d1117',
                'background_secondary': '#161b22',
                'surface': '#21262d',
                'surface_secondary': '#30363d',
                'surface_elevated': '#262c36',
                'text': '#f0f6ff',
                'text_secondary': '#8b949e',
                'text_muted': '#6e7681',
                'text_disabled': '#484f58',
                'border': '#30363d',
                'border_light': '#21262d',
                'border_focus': '#58a6ff',
                'shadow': 'rgba(0, 0, 0, 0.25)',
                'shadow_elevated': 'rgba(0, 0, 0, 0.35)',
                'shadow_modal': 'rgba(0, 0, 0, 0.45)',
                'accent': '#58a6ff',
                'accent_light': '#1c2128',
                'hover': 'rgba(88, 166, 255, 0.12)',
                'active': 'rgba(88, 166, 255, 0.16)',
                'selection': 'rgba(88, 166, 255, 0.20)'
            },
            'blue': {
                'primary': '#0d47a1',
                'primary_light': '#1565c0',
                'secondary': '#1976d2',
                'secondary_light': '#42a5f5',
                'success': '#388e3c',
                'success_light': '#66bb6a',
                'warning': '#f57c00',
                'warning_light': '#ffb74d',
                'danger': '#d32f2f',
                'danger_light': '#ef5350',
                'info': '#0288d1',
                'info_light': '#29b6f6',
                'background': '#f5f5f5',
                'background_secondary': '#eeeeee',
                'surface': '#ffffff',
                'surface_secondary': '#fafafa',
                'text': '#212121',
                'text_secondary': '#757575',
                'text_muted': '#bdbdbd',
                'border': '#e0e0e0',
                'border_light': '#eeeeee',
                'shadow': '#00000020',
                'accent': '#2196f3'
            }
        }
    
    def initialize_styles(self, style: ttk.Style):
        """Initialize ttk styles with current theme."""
        self.style = style
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the application."""
        if theme_name not in self.themes:
            return False
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        if self.style:
            self._configure_ttk_styles(theme)
        
        # Notify callbacks
        for callback in self.theme_change_callbacks:
            try:
                callback(theme_name, theme)
            except Exception as e:
                print(f"Theme callback error: {e}")
        
        return True
    
    def _configure_ttk_styles(self, theme: Dict[str, str]):
        """Configure modern ttk styles with sleek design and improved spacing."""
        style = self.style
        
        # Modern base styles with improved spacing
        style.configure('TFrame', 
                       background=theme['background'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('TLabel', 
                       background=theme['background'], 
                       foreground=theme['text'],
                       font=('Inter', 9),
                       padding=(2, 4))
        
        # Modern button style with hover effects
        style.configure('TButton', 
                       background=theme['surface'],
                       foreground=theme['text'],
                       font=('Inter', 9, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       borderwidth=1,
                       focuscolor='none')
        
        style.map('TButton',
                 background=[('active', theme['hover']),
                           ('pressed', theme['active'])],
                 foreground=[('active', theme['text']),
                           ('pressed', theme['text'])],
                 relief=[('pressed', 'flat')])
        
        # Sleek entry fields
        style.configure('TEntry', 
                       background=theme['surface'],
                       foreground=theme['text'],
                       font=('Inter', 9),
                       padding=(12, 8),
                       relief='flat',
                       borderwidth=1,
                       insertcolor=theme['text'],
                       focuscolor=theme['accent'])
        
        style.map('TEntry',
                 background=[('focus', theme['surface_elevated'])],
                 bordercolor=[('focus', theme['border_focus'])])
        
        # Modern text widget
        style.configure('TText', 
                       background=theme['surface'],
                       foreground=theme['text'],
                       font=('Consolas', 9),
                       padding=(12, 8),
                       relief='flat',
                       borderwidth=1)
        
        # Sleek combobox
        style.configure('TCombobox', 
                       background=theme['surface'],
                       foreground=theme['text'],
                       font=('Inter', 9),
                       padding=(12, 8),
                       relief='flat',
                       borderwidth=1)
        
        # Modern notebook tabs
        style.configure('TNotebook', 
                       background=theme['background'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('TNotebook.Tab', 
                       background=theme['surface_secondary'],
                       foreground=theme['text_secondary'],
                       font=('Inter', 9, 'normal'),
                       padding=(16, 12),
                       relief='flat')
        
        style.map('TNotebook.Tab',
                 background=[('selected', theme['surface']),
                           ('active', theme['hover'])],
                 foreground=[('selected', theme['text']),
                           ('active', theme['text'])])
        
        # Modern label frame
        style.configure('TLabelFrame', 
                       background=theme['background'],
                       foreground=theme['text'],
                       font=('Inter', 10, 'bold'),
                       relief='flat',
                       borderwidth=0)
        
        # Sleek treeview
        style.configure('Treeview', 
                       background=theme['surface'],
                       foreground=theme['text'],
                       font=('Inter', 9),
                       relief='flat',
                       borderwidth=0,
                       rowheight=28)
        
        style.configure('Treeview.Heading', 
                       background=theme['surface_secondary'],
                       foreground=theme['text'],
                       font=('Inter', 9, 'bold'),
                       relief='flat',
                       borderwidth=0)
        
        style.map('Treeview',
                 background=[('selected', theme['selection'])],
                 foreground=[('selected', theme['text'])])
        
        # Modern typography styles
        style.configure('Title.TLabel', 
                       background=theme['background'],
                       foreground=theme['primary'],
                       font=('Inter', 24, 'bold'),
                       padding=(0, 8))
        
        style.configure('Heading.TLabel',
                       background=theme['background'],
                       foreground=theme['text'],
                       font=('Inter', 18, 'bold'),
                       padding=(0, 6))
        
        style.configure('Subheading.TLabel',
                       background=theme['background'],
                       foreground=theme['text_secondary'],
                       font=('Inter', 12, 'bold'),
                       padding=(0, 4))
        
        style.configure('Body.TLabel',
                       background=theme['background'],
                       foreground=theme['text'],
                       font=('Inter', 9),
                       padding=(0, 2))
        
        style.configure('Caption.TLabel',
                       background=theme['background'],
                       foreground=theme['text_muted'],
                       font=('Inter', 8),
                       padding=(0, 1))
        
        # Status and state styles
        style.configure('Status.TLabel',
                       background=theme['background'],
                       foreground=theme['accent'],
                       font=('Inter', 9, 'bold'))
        
        style.configure('Success.TLabel',
                       background=theme['background'],
                       foreground=theme['success'],
                       font=('Inter', 9, 'bold'))
        
        style.configure('Warning.TLabel',
                       background=theme['background'],
                       foreground=theme['warning'],
                       font=('Inter', 9, 'bold'))
        
        style.configure('Error.TLabel',
                       background=theme['background'],
                       foreground=theme['danger'],
                       font=('Inter', 9, 'bold'))
        
        # Modern card styles with subtle shadows (simulated with borders)
        style.configure('Card.TFrame',
                       background=theme['surface_elevated'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('CardHeader.TFrame',
                       background=theme['surface_elevated'],
                       relief='flat')
        
        style.configure('CardCompact.TFrame',
                       background=theme['surface'],
                       relief='flat',
                       borderwidth=0)
        
        # Modern button variants with improved styling
        style.configure('Primary.TButton',
                       background=theme['accent'],
                       foreground='white',
                       font=('Inter', 9, 'bold'),
                       padding=(20, 10),
                       relief='flat',
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', theme['secondary_light']),
                           ('pressed', theme['secondary'])])
        
        style.configure('Secondary.TButton',
                       background=theme['surface_secondary'],
                       foreground=theme['text'],
                       font=('Inter', 9, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       focuscolor='none')
        
        style.map('Secondary.TButton',
                 background=[('active', theme['hover']),
                           ('pressed', theme['active'])])
        
        style.configure('Success.TButton',
                       background=theme['success'],
                       foreground='white',
                       font=('Inter', 9, 'bold'),
                       padding=(16, 8),
                       relief='flat',
                       focuscolor='none')
        
        style.map('Success.TButton',
                 background=[('active', theme['success_light'])])
        
        style.configure('Warning.TButton',
                       background=theme['warning'],
                       foreground='white',
                       font=('Inter', 9, 'bold'),
                       padding=(16, 8),
                       relief='flat',
                       focuscolor='none')
        
        style.map('Warning.TButton',
                 background=[('active', theme['warning_light'])])
        
        style.configure('Danger.TButton',
                       background=theme['danger'],
                       foreground='white',
                       font=('Inter', 9, 'bold'),
                       padding=(16, 8),
                       relief='flat',
                       focuscolor='none')
        
        style.map('Danger.TButton',
                 background=[('active', theme['danger_light'])])
        
        style.configure('Ghost.TButton',
                       background=theme['background'],
                       foreground=theme['accent'],
                       font=('Inter', 9, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       borderwidth=1,
                       focuscolor='none')
        
        style.map('Ghost.TButton',
                 background=[('active', theme['accent_light']),
                           ('pressed', theme['hover'])])
        
        # Modern sidebar with cleaner styling
        style.configure('Sidebar.TFrame',
                       background=theme['surface'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('SidebarItem.TFrame',
                       background=theme['surface'],
                       relief='flat')
        
        style.configure('SidebarItemActive.TFrame',
                       background=theme['accent_light'],
                       relief='flat')
        
        style.configure('SidebarItem.TLabel',
                       background=theme['surface'],
                       foreground=theme['text_secondary'],
                       font=('Inter', 9, 'normal'),
                       padding=(16, 12))
        
        style.configure('SidebarItemActive.TLabel',
                       background=theme['accent_light'],
                       foreground=theme['accent'],
                       font=('Inter', 9, 'bold'),
                       padding=(16, 12))
        
        # Modern progress bar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=theme['accent'],
                       troughcolor=theme['surface_secondary'],
                       relief='flat',
                       borderwidth=0)
        
        # Status bar styling
        style.configure('StatusBar.TFrame',
                       background=theme['surface_secondary'],
                       relief='flat',
                       borderwidth=0)
        
        # Toolbar styling
        style.configure('Toolbar.TFrame',
                       background=theme['surface_elevated'],
                       relief='flat',
                       borderwidth=0)
    
    def get_color(self, color_name: str) -> str:
        """Get a color from the current theme."""
        return self.themes[self.current_theme].get(color_name, '#000000')
    
    def register_theme_callback(self, callback: Callable):
        """Register a callback for theme changes."""
        self.theme_change_callbacks.append(callback)
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return list(self.themes.keys())


class StatusManager:
    """Manages status notifications and user feedback."""
    
    def __init__(self, parent):
        self.parent = parent
        self.toast_queue = []
        self.active_toasts = []
        self.status_bar = None
        self.progress_windows = {}
    
    def create_status_bar(self, parent) -> ttk.Frame:
        """Create application status bar."""
        self.status_bar = ttk.Frame(parent, style='StatusBar.TFrame', height=25)
        
        # Status text
        self.status_text = ttk.Label(self.status_bar, text="Ready", style='Status.TLabel')
        self.status_text.pack(side='left', padx=5)
        
        # Progress indicator
        self.status_progress = ttk.Progressbar(self.status_bar, mode='indeterminate', length=100)
        
        # Connection status
        self.connection_status = ttk.Label(self.status_bar, text="●", foreground='red')
        self.connection_status.pack(side='right', padx=5)
        
        return self.status_bar
    
    def show_toast_notification(self, message: str, type: str = 'info', duration: int = 3000):
        """Show a toast notification."""
        toast = ToastNotification(self.parent, message, type, duration)
        self.active_toasts.append(toast)
        
        # Auto-remove after duration
        def remove_toast():
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
        
        self.parent.after(duration, remove_toast)
    
    def show_message(self, message: str, type: str = 'info', duration: int = 3000):
        """Show a message notification (alias for show_toast_notification)."""
        self.show_toast_notification(message, type, duration)
    
    def update_status(self, text: str, show_progress: bool = False):
        """Update status bar text."""
        if self.status_bar:
            self.status_text.config(text=text)
            
            if show_progress:
                self.status_progress.pack(side='left', padx=5)
                self.status_progress.start()
            else:
                self.status_progress.stop()
                self.status_progress.pack_forget()
    
    def update_connection_status(self, connected: bool):
        """Update connection status indicator."""
        if self.connection_status:
            color = 'green' if connected else 'red'
            self.connection_status.config(foreground=color)
    
    def show_confirmation_dialog(self, title: str, message: str, callback: Callable = None) -> bool:
        """Show modern confirmation dialog."""
        dialog = ModernDialog(self.parent, title, message, 'question', ['Yes', 'No'])
        result = dialog.show()
        
        if callback and result == 'Yes':
            callback()
        
        return result == 'Yes'
    
    def show_progress_window(self, title: str, message: str, task_id: str = None) -> 'ProgressWindow':
        """Show progress window for long operations."""
        if not task_id:
            task_id = f"task_{len(self.progress_windows)}"
        
        progress_window = ProgressWindow(self.parent, title, message)
        self.progress_windows[task_id] = progress_window
        
        return progress_window
    
    def close_progress_window(self, task_id: str):
        """Close a progress window."""
        if task_id in self.progress_windows:
            self.progress_windows[task_id].close()
            del self.progress_windows[task_id]


class ToastNotification:
    """Modern toast notification with sleek design and smooth animations."""
    
    def __init__(self, parent, message: str, type: str, duration: int):
        self.parent = parent
        self.type = type
        self.duration = duration
        self.is_closing = False
        
        # Create toast window
        self.toast = tk.Toplevel(parent)
        self.toast.withdraw()  # Hide initially
        self.toast.overrideredirect(True)
        self.toast.attributes('-topmost', True)
        
        # Modern type styles with better colors
        type_styles = {
            'info': {'bg': '#e3f2fd', 'fg': '#0d47a1', 'accent': '#2196f3', 'icon': 'ℹ'},
            'success': {'bg': '#e8f5e8', 'fg': '#2e7d32', 'accent': '#4caf50', 'icon': '✓'},
            'warning': {'bg': '#fff8e1', 'fg': '#e65100', 'accent': '#ff9800', 'icon': '⚠'},
            'error': {'bg': '#ffebee', 'fg': '#c62828', 'accent': '#f44336', 'icon': '✗'}
        }
        
        style = type_styles.get(type, type_styles['info'])
        
        # Create modern container with rounded appearance
        self.toast.configure(bg='white')
        
        # Main container with padding for shadow effect
        container = tk.Frame(self.toast, bg='white')
        container.pack(fill='both', expand=True, padx=4, pady=4)
        
        # Inner frame with modern styling
        main_frame = tk.Frame(container, bg='white', relief='flat')
        main_frame.pack(fill='both', expand=True)
        
        # Accent bar on the left
        accent_bar = tk.Frame(main_frame, bg=style['accent'], width=4)
        accent_bar.pack(side='left', fill='y')
        accent_bar.pack_propagate(False)
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg='white')
        content_frame.pack(side='left', fill='both', expand=True, padx=(16, 12), pady=12)
        
        # Header with icon and type
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 4))
        
        # Type icon with modern styling
        icon_label = tk.Label(header_frame, text=style['icon'], font=('Inter', 14, 'bold'),
                             fg=style['accent'], bg='white')
        icon_label.pack(side='left', padx=(0, 8))
        
        # Type label
        type_label = tk.Label(header_frame, text=type.title(), font=('Inter', 9, 'bold'),
                             fg=style['fg'], bg='white')
        type_label.pack(side='left')
        
        # Message with better typography
        msg_label = tk.Label(content_frame, text=message, font=('Inter', 9),
                           fg=style['fg'], bg='white', wraplength=280, justify='left')
        msg_label.pack(fill='both', expand=True, pady=(2, 0))
        
        # Close button with modern design
        close_frame = tk.Frame(main_frame, bg='white')
        close_frame.pack(side='right', padx=(0, 8), pady=8)
        
        close_btn = tk.Label(close_frame, text='×', font=('Inter', 12, 'bold'),
                           fg='#8b949e', bg='white', cursor='hand2',
                           padx=8, pady=4)
        close_btn.pack()
        close_btn.bind('<Button-1>', lambda e: self.close())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=style['accent'], bg='#f6f8fa'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg='#8b949e', bg='white'))
        
        # Position and show with smooth animations
        self.position_toast()
        self.animate_in()
        
        # Auto-close after duration
        self.toast.after(duration, self.close)
    
    def position_toast(self):
        """Position toast in top-right corner with better spacing."""
        self.toast.update_idletasks()
        width = max(360, self.toast.winfo_reqwidth())  # Minimum width for consistency
        height = self.toast.winfo_reqheight()
        
        # Position in top-right corner with margin
        screen_width = self.toast.winfo_screenwidth()
        x = screen_width - width - 24
        y = 24
        
        # Stack multiple toasts
        try:
            if hasattr(self.parent, 'status_manager') and hasattr(self.parent.status_manager, 'active_toasts'):
                stack_offset = len(self.parent.status_manager.active_toasts) * (height + 12)
                y += stack_offset
        except AttributeError:
            pass
        
        self.toast.geometry(f"{width}x{height}+{x}+{y}")
    
    def animate_in(self):
        """Smooth slide-in and fade-in animation."""
        self.toast.attributes('-alpha', 0.0)
        
        # Get final position
        final_x = int(self.toast.geometry().split('+')[1])
        start_x = final_x + 50  # Start 50px to the right
        
        # Set initial position
        geometry_parts = self.toast.geometry().split('+')
        geometry_parts[1] = str(start_x)
        self.toast.geometry('+'.join(geometry_parts))
        
        self.toast.deiconify()  # Show the window
        self.slide_and_fade_in(start_x, final_x, 0.0)
    
    def slide_and_fade_in(self, current_x: int, final_x: int, alpha: float):
        """Slide and fade animation step."""
        if alpha < 1.0 and current_x > final_x:
            # Update alpha
            self.toast.attributes('-alpha', alpha)
            
            # Update position
            geometry_parts = self.toast.geometry().split('+')
            geometry_parts[1] = str(current_x)
            self.toast.geometry('+'.join(geometry_parts))
            
            # Continue animation
            next_alpha = min(1.0, alpha + 0.15)
            next_x = max(final_x, current_x - 8)
            self.toast.after(30, lambda: self.slide_and_fade_in(next_x, final_x, next_alpha))
        else:
            # Ensure final state
            self.toast.attributes('-alpha', 1.0)
            geometry_parts = self.toast.geometry().split('+')
            geometry_parts[1] = str(final_x)
            self.toast.geometry('+'.join(geometry_parts))
    
    def close(self):
        """Close the toast with fade-out animation."""
        if self.is_closing:
            return
            
        self.is_closing = True
        self.fade_out(1.0)
    
    def fade_out(self, alpha: float):
        """Smooth fade-out animation."""
        if alpha > 0.0:
            self.toast.attributes('-alpha', alpha)
            self.toast.after(30, lambda: self.fade_out(alpha - 0.15))
        else:
            try:
                self.toast.destroy()
            except:
                pass


class ModernDialog:
    """Modern dialog with custom styling."""
    
    def __init__(self, parent, title: str, message: str, dialog_type: str = 'info', buttons: List[str] = None):
        self.parent = parent
        self.result = None
        
        if buttons is None:
            buttons = ['OK']
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_rootx() + (parent.winfo_width() // 2) - 200)
        y = (parent.winfo_rooty() + (parent.winfo_height() // 2) - 100)
        self.dialog.geometry(f"400x200+{x}+{y}")
        
        self.create_content(message, dialog_type, buttons)
    
    def create_content(self, message: str, dialog_type: str, buttons: List[str]):
        """Create dialog content."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Icon and message frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='x', pady=(0, 20))
        
        # Icon
        icons = {'info': 'ℹ', 'question': '?', 'warning': '⚠', 'error': '✗'}
        icon_colors = {'info': '#17a2b8', 'question': '#6f42c1', 'warning': '#ffc107', 'error': '#dc3545'}
        
        icon = icons.get(dialog_type, 'ℹ')
        color = icon_colors.get(dialog_type, '#17a2b8')
        
        icon_label = tk.Label(content_frame, text=icon, font=('Arial', 24, 'bold'),
                             fg=color, bg=main_frame['background'])
        icon_label.pack(side='left', padx=(0, 15))
        
        # Message
        msg_label = tk.Label(content_frame, text=message, font=('Arial', 11),
                           wraplength=300, justify='left', bg=main_frame['background'])
        msg_label.pack(side='left', fill='both', expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x')
        
        for i, button_text in enumerate(buttons):
            style = 'Primary.TButton' if i == 0 else 'TButton'
            btn = ttk.Button(button_frame, text=button_text, style=style,
                           command=lambda text=button_text: self.button_clicked(text))
            btn.pack(side='right', padx=(10, 0) if i > 0 else 0)
    
    def button_clicked(self, button_text: str):
        """Handle button click."""
        self.result = button_text
        self.dialog.destroy()
    
    def show(self) -> str:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


class ProgressWindow:
    """Modern progress window."""
    
    def __init__(self, parent, title: str, message: str):
        self.parent = parent
        self.cancelled = False
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self.window.update_idletasks()
        x = (parent.winfo_rootx() + (parent.winfo_width() // 2) - 200)
        y = (parent.winfo_rooty() + (parent.winfo_height() // 2) - 100)
        self.window.geometry(f"400x150+{x}+{y}")
        
        self.create_content(message)
    
    def create_content(self, message: str):
        """Create progress window content."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Message
        self.message_label = ttk.Label(main_frame, text=message, font=('Arial', 11))
        self.message_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', style='Modern.Horizontal.TProgressbar')
        self.progress.pack(fill='x', pady=(0, 15))
        self.progress.start()
        
        # Details label
        self.details_label = ttk.Label(main_frame, text="", font=('Arial', 9), style='Status.TLabel')
        self.details_label.pack(pady=(0, 15))
        
        # Cancel button
        self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack()
    
    def update_progress(self, percent: int = None, message: str = None, details: str = None):
        """Update progress information."""
        if percent is not None:
            self.progress.config(mode='determinate')
            self.progress['value'] = percent
        
        if message:
            self.message_label.config(text=message)
        
        if details:
            self.details_label.config(text=details)
        
        self.window.update()
    
    def cancel(self):
        """Cancel the operation."""
        self.cancelled = True
        self.close()
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.cancelled
    
    def close(self):
        """Close the progress window."""
        try:
            self.progress.stop()
            self.window.destroy()
        except:
            pass


class CardComponent:
    """Modern card component for displaying information."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
    
    def create_info_card(self, parent, title: str, content: str, actions: List[Dict] = None) -> ttk.Frame:
        """Create an information card."""
        card = ttk.Frame(parent, style='Card.TFrame', padding="15")
        
        # Header
        if title:
            header = ttk.Frame(card, style='CardHeader.TFrame', padding="10")
            header.pack(fill='x', pady=(0, 10))
            
            title_label = ttk.Label(header, text=title, style='Heading.TLabel')
            title_label.pack(side='left')
        
        # Content
        if content:
            content_label = ttk.Label(card, text=content, wraplength=300)
            content_label.pack(fill='x', pady=(0, 10))
        
        # Actions
        if actions:
            action_frame = ttk.Frame(card)
            action_frame.pack(fill='x')
            
            for action in actions:
                btn = ttk.Button(action_frame, 
                               text=action.get('text', 'Action'),
                               command=action.get('command'),
                               style=action.get('style', 'TButton'))
                btn.pack(side='right', padx=(10, 0))
        
        return card
    
    def create_metric_card(self, parent, value: str, label: str, trend: str = None, color: str = None) -> ttk.Frame:
        """Create a modern metric display card with sleek styling."""
        card = ttk.Frame(parent, style='Card.TFrame', padding="24")
        
        # Value with modern typography
        value_style = 'Title.TLabel'
        if color:
            # Create custom style for colored metrics with modern colors
            style_name = f'Metric{color.title()}.TLabel'
            self.theme_manager.style.configure(style_name,
                                             background=self.theme_manager.get_color('surface_elevated'),
                                             foreground=self.theme_manager.get_color(color),
                                             font=('Inter', 32, 'bold'))
            value_style = style_name
        
        value_label = ttk.Label(card, text=value, style=value_style)
        value_label.pack(pady=(0, 8))
        
        # Label with better spacing
        label_label = ttk.Label(card, text=label, style='Body.TLabel')
        label_label.pack(pady=(0, 4))
        
        # Trend with modern indicators
        if trend:
            trend_frame = ttk.Frame(card, style='Card.TFrame')
            trend_frame.pack(pady=(8, 0), fill='x')
            
            # Trend icon
            trend_icon = '▲' if trend.startswith('+') else '▼' if trend.startswith('-') else '●'
            trend_color = 'success' if trend.startswith('+') else 'danger' if trend.startswith('-') else 'text_muted'
            
            icon_label = ttk.Label(trend_frame, text=trend_icon, 
                                  style=f'{trend_color.title()}.TLabel' if trend_color != 'text_muted' else 'Caption.TLabel')
            icon_label.pack(side='left', padx=(0, 6))
            
            trend_label = ttk.Label(trend_frame, text=trend, 
                                  style=f'{trend_color.title()}.TLabel' if trend_color != 'text_muted' else 'Caption.TLabel')
            trend_label.pack(side='left')
        
        return card
    
    def create_status_card(self, parent, title: str, status: str, details: List[str] = None) -> ttk.Frame:
        """Create a status display card."""
        card = ttk.Frame(parent, style='Card.TFrame', padding="15")
        
        # Header with status indicator
        header = ttk.Frame(card)
        header.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(header, text=title, style='Heading.TLabel')
        title_label.pack(side='left')
        
        # Status indicator
        status_colors = {
            'online': 'success', 'connected': 'success', 'active': 'success',
            'offline': 'danger', 'disconnected': 'danger', 'inactive': 'danger',
            'warning': 'warning', 'pending': 'warning'
        }
        
        status_color = status_colors.get(status.lower(), 'text_secondary')
        status_indicator = ttk.Label(header, text='●', 
                                   style=f'{status_color.title()}.TLabel' if status_color != 'text_secondary' else 'Status.TLabel')
        status_indicator.pack(side='right')
        
        status_label = ttk.Label(header, text=status.title(), 
                               style=f'{status_color.title()}.TLabel' if status_color != 'text_secondary' else 'Status.TLabel')
        status_label.pack(side='right', padx=(0, 5))
        
        # Details
        if details:
            for detail in details:
                detail_label = ttk.Label(card, text=f"• {detail}", style='Status.TLabel')
                detail_label.pack(anchor='w')
        
        return card


class SidebarNavigation:
    """Modern sidebar navigation component."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.active_item = None
        self.navigation_items = []
        self.callbacks = {}
        
    def create_sidebar(self, parent, width: int = 250) -> ttk.Frame:
        """Create sidebar navigation."""
        self.sidebar = ttk.Frame(parent, style='Sidebar.TFrame', width=width)
        self.sidebar.pack_propagate(False)
        
        # Header
        header = ttk.Frame(self.sidebar, style='Sidebar.TFrame', padding="20 15")
        header.pack(fill='x')
        
        # Logo/Title
        title_label = ttk.Label(header, text="SQL Documentation", style='Heading.TLabel')
        title_label.pack()
        
        # Navigation items container
        self.nav_container = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        self.nav_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        return self.sidebar
    
    def add_navigation_item(self, icon: str, title: str, description: str, callback: Callable, item_id: str = None):
        """Add a navigation item."""
        if not item_id:
            item_id = title.lower().replace(' ', '_')
        
        # Create item frame
        item_frame = ttk.Frame(self.nav_container, style='SidebarItem.TFrame', padding="10")
        item_frame.pack(fill='x', pady=(0, 5))
        
        # Icon
        icon_label = ttk.Label(item_frame, text=icon, font=('Arial', 14))
        icon_label.pack(side='left', padx=(0, 10))
        
        # Text container
        text_frame = ttk.Frame(item_frame, style='SidebarItem.TFrame')
        text_frame.pack(side='left', fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(text_frame, text=title, font=('Arial', 10, 'bold'))
        title_label.pack(anchor='w')
        
        # Description
        desc_label = ttk.Label(text_frame, text=description, font=('Arial', 8), style='Status.TLabel')
        desc_label.pack(anchor='w')
        
        # Click binding
        def on_click(event=None):
            self.activate_item(item_id, callback)
        
        # Bind click to all elements
        for widget in [item_frame, icon_label, text_frame, title_label, desc_label]:
            widget.bind('<Button-1>', on_click)
            widget.configure(cursor='hand2')
        
        # Store item reference
        self.navigation_items.append({
            'id': item_id,
            'frame': item_frame,
            'callback': callback
        })
        
        self.callbacks[item_id] = callback
    
    def activate_item(self, item_id: str, callback: Callable = None):
        """Activate a navigation item."""
        # Deactivate current item
        if self.active_item:
            for item in self.navigation_items:
                if item['id'] == self.active_item:
                    item['frame'].configure(style='SidebarItem.TFrame')
                    break
        
        # Activate new item
        self.active_item = item_id
        for item in self.navigation_items:
            if item['id'] == item_id:
                item['frame'].configure(style='SidebarItemActive.TFrame')
                break
        
        # Execute callback
        if callback:
            callback()
        elif item_id in self.callbacks:
            self.callbacks[item_id]()
    
    def get_active_item(self) -> str:
        """Get the currently active item ID."""
        return self.active_item


class EnhancedTreeview:
    """Enhanced Treeview with sorting, filtering, and customization."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.sort_reverse = {}
        self.filters = {}
        
    def create_enhanced_treeview(self, parent, columns: List[str], show_tree: bool = False) -> Dict[str, Any]:
        """Create enhanced treeview with toolbar."""
        container = ttk.Frame(parent)
        
        # Toolbar
        toolbar = self.create_toolbar(container)
        toolbar.pack(fill='x', pady=(0, 5))
        
        # Treeview frame
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree' if show_tree else 'headings')
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(tree, c))
            tree.column(col, width=100)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack elements
        tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        return {
            'container': container,
            'toolbar': toolbar,
            'treeview': tree,
            'v_scrollbar': v_scroll,
            'h_scrollbar': h_scroll
        }
    
    def create_toolbar(self, parent) -> ttk.Frame:
        """Create toolbar with filter and search controls."""
        toolbar = ttk.Frame(parent, style='Toolbar.TFrame')
        
        # Search
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side='left', padx=(0, 10))
        
        ttk.Label(search_frame, text="🔍").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # Filter dropdown
        filter_frame = ttk.Frame(toolbar)
        filter_frame.pack(side='left', padx=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side='left')
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                  values=['All', 'Active', 'Inactive'], width=10, state='readonly')
        filter_combo.pack(side='left', padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
        filter_combo.set('All')
        
        # Actions
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side='right')
        
        ttk.Button(action_frame, text="Export", command=self.export_data).pack(side='right', padx=(5, 0))
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side='right')
        
        return toolbar
    
    def sort_by_column(self, tree: ttk.Treeview, col: str):
        """Sort treeview by column."""
        items = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Determine sort order
        reverse = self.sort_reverse.get(col, False)
        self.sort_reverse[col] = not reverse
        
        # Sort items
        try:
            # Try numeric sort first
            items.sort(key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else float('inf'), reverse=reverse)
        except:
            # Fall back to string sort
            items.sort(key=lambda x: x[0].lower(), reverse=reverse)
        
        # Rearrange items
        for index, (val, child) in enumerate(items):
            tree.move(child, '', index)
        
        # Update column heading to show sort direction
        for column in tree['columns']:
            tree.heading(column, text=column)
        
        arrow = ' ▲' if not reverse else ' ▼'
        tree.heading(col, text=col + arrow)
    
    def on_search_changed(self, event=None):
        """Handle search text change."""
        # This would filter the treeview based on search text
        pass
    
    def on_filter_changed(self, event=None):
        """Handle filter change."""
        # This would apply the selected filter
        pass
    
    def export_data(self):
        """Export treeview data."""
        # This would export the current treeview data
        pass
    
    def refresh_data(self):
        """Refresh treeview data."""
        # This would refresh the treeview contents
        pass


class DashboardHome:
    """Dashboard home screen with overview and quick actions."""
    
    def __init__(self, parent, theme_manager: ThemeManager, status_manager: StatusManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.status_manager = status_manager
        self.metrics = {}
        
    def create_dashboard(self, parent) -> ttk.Frame:
        """Create dashboard home screen."""
        dashboard = ttk.Frame(parent, padding="20")
        
        # Welcome header
        header_frame = ttk.Frame(dashboard)
        header_frame.pack(fill='x', pady=(0, 20))
        
        welcome_label = ttk.Label(header_frame, 
                                text="Azure SQL Database Documentation Generator",
                                style='Title.TLabel')
        welcome_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                 text="Enterprise Database Documentation & Management Platform",
                                 style='Subheading.TLabel')
        subtitle_label.pack()
        
        # Metrics row
        metrics_frame = ttk.Frame(dashboard)
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        self.create_metrics_cards(metrics_frame)
        
        # Main content area with two columns
        content_frame = ttk.Frame(dashboard)
        content_frame.pack(fill='both', expand=True)
        
        # Left column - Recent activity
        left_column = ttk.Frame(content_frame)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.create_recent_activity(left_column)
        self.create_system_status(left_column)
        
        # Right column - Quick actions
        right_column = ttk.Frame(content_frame, width=300)
        right_column.pack(side='right', fill='y')
        right_column.pack_propagate(False)
        
        self.create_quick_actions(right_column)
        self.create_connection_status(right_column)
        
        return dashboard
    
    def create_metrics_cards(self, parent):
        """Create metrics display cards."""
        card_component = CardComponent(parent, self.theme_manager)
        
        metrics = [
            {'value': '0', 'label': 'Databases Documented', 'key': 'databases'},
            {'value': '0', 'label': 'Reports Generated', 'key': 'reports'},
            {'value': '0%', 'label': 'Avg Compliance Score', 'key': 'compliance'},
            {'value': '0', 'label': 'Active Projects', 'key': 'projects'}
        ]
        
        for i, metric in enumerate(metrics):
            card = card_component.create_metric_card(parent, 
                                                   metric['value'], 
                                                   metric['label'],
                                                   color='secondary')
            card.pack(side='left', fill='x', expand=True, padx=5 if i > 0 else 0)
            
            # Store reference for updates
            self.metrics[metric['key']] = card.winfo_children()[0]  # Value label
    
    def create_recent_activity(self, parent):
        """Create recent activity feed."""
        activity_frame = ttk.LabelFrame(parent, text="Recent Activity", padding="15")
        activity_frame.pack(fill='x', pady=(0, 20))
        
        # Activity list
        self.activity_listbox = tk.Listbox(activity_frame, height=6, 
                                         bg=self.theme_manager.get_color('surface'),
                                         fg=self.theme_manager.get_color('text'),
                                         font=('Arial', 9))
        self.activity_listbox.pack(fill='x')
        
        # Add some sample activities
        activities = [
            "🔌 Connected to database 'ProductionDB'",
            "📋 Generated documentation for 15 tables",
            "🔍 Completed compliance audit - 85% score",
            "📊 Analytics report exported",
            "⏰ Scheduled backup job created"
        ]
        
        for activity in activities:
            self.activity_listbox.insert(tk.END, activity)
    
    def create_system_status(self, parent):
        """Create system status display."""
        status_frame = ttk.LabelFrame(parent, text="System Status", padding="15")
        status_frame.pack(fill='x')
        
        card_component = CardComponent(parent, self.theme_manager)
        
        # Database connection status
        db_status = card_component.create_status_card(status_frame,
                                                    "Database Connection",
                                                    "disconnected",
                                                    ["No active connections"])
        db_status.pack(fill='x', pady=(0, 10))
        
        # Background services
        services_status = card_component.create_status_card(status_frame,
                                                          "Background Services",
                                                          "active",
                                                          ["Scheduler running", "Monitor active"])
        services_status.pack(fill='x')
    
    def create_quick_actions(self, parent):
        """Create quick actions panel."""
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding="15")
        actions_frame.pack(fill='x', pady=(0, 20))
        
        actions = [
            ('🔌', 'Connect to Database', 'Connect to a new database', None),
            ('📋', 'Generate Documentation', 'Create database documentation', None),
            ('🔍', 'Run Compliance Audit', 'Check security compliance', None),
            ('📊', 'View Analytics', 'See usage analytics', None),
            ('⚙️', 'Settings', 'Configure application', None)
        ]
        
        for icon, title, description, callback in actions:
            action_frame = ttk.Frame(actions_frame)
            action_frame.pack(fill='x', pady=(0, 10))
            
            # Icon
            icon_label = ttk.Label(action_frame, text=icon, font=('Arial', 16))
            icon_label.pack(side='left', padx=(0, 10))
            
            # Text
            text_frame = ttk.Frame(action_frame)
            text_frame.pack(side='left', fill='both', expand=True)
            
            title_label = ttk.Label(text_frame, text=title, font=('Arial', 10, 'bold'))
            title_label.pack(anchor='w')
            
            desc_label = ttk.Label(text_frame, text=description, font=('Arial', 8), style='Status.TLabel')
            desc_label.pack(anchor='w')
            
            # Make clickable
            for widget in [action_frame, icon_label, text_frame, title_label, desc_label]:
                widget.configure(cursor='hand2')
                widget.bind('<Button-1>', lambda e, cb=callback: cb() if cb else None)
    
    def create_connection_status(self, parent):
        """Create connection status widget."""
        conn_frame = ttk.LabelFrame(parent, text="Connection Status", padding="15")
        conn_frame.pack(fill='x')
        
        # Status indicator
        status_frame = ttk.Frame(conn_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        self.conn_indicator = ttk.Label(status_frame, text="●", foreground='red', font=('Arial', 14))
        self.conn_indicator.pack(side='left')
        
        self.conn_label = ttk.Label(status_frame, text="Not Connected", style='Status.TLabel')
        self.conn_label.pack(side='left', padx=(5, 0))
        
        # Connection details
        self.conn_details = ttk.Label(conn_frame, text="No active database connection", 
                                    font=('Arial', 9), style='Status.TLabel')
        self.conn_details.pack(fill='x')
    
    def update_metric(self, key: str, value: str, trend: str = None):
        """Update a metric value."""
        if key in self.metrics:
            self.metrics[key].config(text=value)
    
    def add_activity(self, activity: str):
        """Add a new activity to the feed."""
        self.activity_listbox.insert(0, f"{datetime.now().strftime('%H:%M')} - {activity}")
        
        # Keep only last 10 items
        while self.activity_listbox.size() > 10:
            self.activity_listbox.delete(tk.END)
    
    def update_connection_status(self, connected: bool, details: str = None):
        """Update connection status display."""
        if connected:
            self.conn_indicator.config(foreground='green')
            self.conn_label.config(text="Connected")
            if details:
                self.conn_details.config(text=details)
        else:
            self.conn_indicator.config(foreground='red')
            self.conn_label.config(text="Not Connected")
            self.conn_details.config(text="No active database connection")


class ResponsiveLayout:
    """Responsive layout manager for different screen sizes."""
    
    def __init__(self, parent):
        self.parent = parent
        self.breakpoints = {'small': 800, 'medium': 1200, 'large': 1600}
        self.current_layout = None
        self.layout_callbacks = []
        
        # Bind to window resize
        parent.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event=None):
        """Handle window resize events."""
        if event and event.widget == self.parent:
            width = self.parent.winfo_width()
            new_layout = self.determine_layout(width)
            
            if new_layout != self.current_layout:
                self.current_layout = new_layout
                self.apply_layout(new_layout)
    
    def determine_layout(self, width: int) -> str:
        """Determine layout based on width."""
        if width < self.breakpoints['small']:
            return 'compact'
        elif width < self.breakpoints['medium']:
            return 'standard'
        else:
            return 'wide'
    
    def apply_layout(self, layout: str):
        """Apply the specified layout."""
        for callback in self.layout_callbacks:
            try:
                callback(layout)
            except Exception as e:
                print(f"Layout callback error: {e}")
    
    def register_layout_callback(self, callback: Callable):
        """Register a callback for layout changes."""
        self.layout_callbacks.append(callback)


# Enhanced form controls
class EnhancedEntry(ttk.Entry):
    """Enhanced entry widget with placeholder and validation."""
    
    def __init__(self, parent, placeholder: str = "", validate_func: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.validate_func = validate_func
        self.default_fg = self['foreground'] if 'foreground' in self else None
        self.placeholder_active = False
        
        if placeholder:
            self.show_placeholder()
        
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)
        self.bind('<KeyRelease>', self.on_key_release)
    
    def show_placeholder(self):
        """Show placeholder text."""
        if not self.get():
            self.placeholder_active = True
            self.insert(0, self.placeholder)
            self.config(foreground='grey')
    
    def hide_placeholder(self):
        """Hide placeholder text."""
        if self.placeholder_active:
            self.placeholder_active = False
            self.delete(0, tk.END)
            if self.default_fg:
                self.config(foreground=self.default_fg)
    
    def on_focus_in(self, event):
        """Handle focus in event."""
        self.hide_placeholder()
    
    def on_focus_out(self, event):
        """Handle focus out event."""
        if not self.get():
            self.show_placeholder()
        elif self.validate_func:
            self.validate_input()
    
    def on_key_release(self, event):
        """Handle key release for real-time validation."""
        if not self.placeholder_active and self.validate_func:
            self.validate_input()
    
    def validate_input(self) -> bool:
        """Validate input using provided function."""
        if self.validate_func and not self.placeholder_active:
            is_valid = self.validate_func(self.get())
            
            if is_valid:
                self.config(background='white')
                return True
            else:
                self.config(background='#ffebee')
                return False
        return True
    
    def get(self):
        """Get entry value, excluding placeholder."""
        value = super().get()
        return '' if self.placeholder_active else value


class ScrollableFrame:
    """Scrollable frame widget that can contain any content and adapt to different screen sizes."""
    
    def __init__(self, parent, **kwargs):
        """Create a scrollable frame with vertical and horizontal scrollbars."""
        self.parent = parent
        
        # Create main container
        self.container = ttk.Frame(parent, **kwargs)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(self.container, highlightthickness=0, bd=0, relief='flat')
        
        # Create scrollbars
        self.scrollbar_v = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollbar_h = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        
        # Create the actual scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrollbars
        self.canvas.configure(
            yscrollcommand=self.scrollbar_v.set,
            xscrollcommand=self.scrollbar_h.set
        )
        
        # Pack scrollbars and canvas
        self.scrollbar_v.pack(side="right", fill="y")
        self.scrollbar_h.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Configure canvas to expand frame width to canvas width
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Apply theme colors
        self.update_theme()
        
        # Enable mouse wheel scrolling
        self.bind_mousewheel()
    
    def pack(self, **kwargs):
        """Pack the scrollable frame container."""
        self.container.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        """Grid the scrollable frame container."""
        self.container.grid(**kwargs)
        return self
    
    def place(self, **kwargs):
        """Place the scrollable frame container."""
        self.container.place(**kwargs)
        return self
    
    def _on_canvas_configure(self, event):
        """Configure scroll region and frame width on canvas resize."""
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Make the frame fill the canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def bind_mousewheel(self):
        """Enable mouse wheel scrolling when mouse is over the canvas."""
        def _on_mousewheel(event):
            try:
                # Windows and macOS
                if event.delta:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                # Linux
                elif event.num == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.canvas.yview_scroll(1, "units")
            except tk.TclError:
                pass  # Widget may have been destroyed
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self.canvas.bind_all("<Button-4>", _on_mousewheel)
            self.canvas.bind_all("<Button-5>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def update_theme(self):
        """Update canvas colors to match current theme."""
        try:
            # Get background color from ttk theme
            bg_color = self.parent.tk.call('ttk::style', 'lookup', 'TFrame', '-background')
            self.canvas.configure(bg=bg_color)
        except (tk.TclError, AttributeError):
            # Fallback to default light background
            self.canvas.configure(bg='#fafbfc')
    
    def scroll_to_top(self):
        """Scroll to the top of the content."""
        self.canvas.yview_moveto(0)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the content."""
        self.canvas.yview_moveto(1)
    
    def scroll_to_position(self, fraction):
        """Scroll to a specific position (0.0 = top, 1.0 = bottom)."""
        self.canvas.yview_moveto(fraction)
    
    def get_frame(self):
        """Get the inner scrollable frame for adding widgets."""
        return self.scrollable_frame
    
    def configure_canvas(self, **kwargs):
        """Configure the canvas widget."""
        self.canvas.configure(**kwargs)
    
    def show_scrollbars(self, vertical=True, horizontal=True):
        """Show or hide scrollbars."""
        if vertical:
            self.scrollbar_v.pack(side="right", fill="y")
        else:
            self.scrollbar_v.pack_forget()
        
        if horizontal:
            self.scrollbar_h.pack(side="bottom", fill="x")
        else:
            self.scrollbar_h.pack_forget()


class SmartLoadingSystem:
    """
    Advanced loading system with progress tracking, smart caching, and progressive enhancement.
    Provides multiple loading indicators and progress tracking for different operations.
    """
    
    def __init__(self, parent, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.active_operations = {}
        self.cache = {}
        self.progress_windows = {}
        
    def start_operation(self, operation_id: str, title: str, steps: List[str] = None, 
                       show_progress_window: bool = True) -> 'SmartProgressTracker':
        """Start a tracked operation with optional progress window."""
        tracker = SmartProgressTracker(
            operation_id=operation_id,
            title=title,
            steps=steps or ["Processing..."],
            parent=self.parent,
            theme_manager=self.theme_manager,
            show_window=show_progress_window
        )
        
        self.active_operations[operation_id] = tracker
        return tracker
    
    def complete_operation(self, operation_id: str):
        """Complete and cleanup an operation."""
        if operation_id in self.active_operations:
            tracker = self.active_operations[operation_id]
            tracker.complete()
            del self.active_operations[operation_id]
    
    def get_cached_result(self, cache_key: str):
        """Get cached result if available."""
        return self.cache.get(cache_key)
    
    def cache_result(self, cache_key: str, result: Any, ttl: int = 300):
        """Cache result with TTL."""
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'ttl': ttl
        }
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_item = self.cache[cache_key]
        return (time.time() - cached_item['timestamp']) < cached_item['ttl']


class SmartProgressTracker:
    """
    Smart progress tracker with adaptive UI and detailed status reporting.
    Provides step-by-step progress indication with estimated completion times.
    """
    
    def __init__(self, operation_id: str, title: str, steps: List[str], 
                 parent, theme_manager: ThemeManager, show_window: bool = True):
        self.operation_id = operation_id
        self.title = title
        self.steps = steps
        self.current_step = 0
        self.parent = parent
        self.theme_manager = theme_manager
        self.start_time = time.time()
        self.step_times = []
        self.window = None
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value=steps[0] if steps else "Starting...")
        self.time_var = tk.StringVar(value="Estimating...")
        
        if show_window:
            self.create_progress_window()
    
    def create_progress_window(self):
        """Create modern progress window with detailed information."""
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry("500x200")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(self.parent)
        self.window.grab_set()
        
        theme = self.theme_manager.themes[self.theme_manager.current_theme]
        self.window.configure(bg=theme['background'])
        
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=self.title, 
                               font=('Inter', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Current step status
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                     font=('Inter', 10))
        self.status_label.pack(anchor='w', pady=(0, 5))
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.progress_var,
                                           length=400, 
                                           mode='determinate')
        self.progress_bar.pack(fill='x')
        
        # Time and step info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x')
        
        # Step counter
        self.step_label = ttk.Label(info_frame, 
                                   text=f"Step 1 of {len(self.steps)}",
                                   font=('Inter', 9))
        self.step_label.pack(side='left')
        
        # Time estimation
        self.time_label = ttk.Label(info_frame, textvariable=self.time_var,
                                   font=('Inter', 9))
        self.time_label.pack(side='right')
        
        # Center window on parent
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 250
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 100
        self.window.geometry(f"+{x}+{y}")
    
    def advance_step(self, custom_message: str = None):
        """Advance to next step with optional custom message."""
        step_end_time = time.time()
        if self.current_step > 0:
            step_duration = step_end_time - (self.start_time + sum(self.step_times))
            self.step_times.append(step_duration)
        
        self.current_step += 1
        
        if self.current_step <= len(self.steps):
            # Update progress
            progress = (self.current_step / len(self.steps)) * 100
            self.progress_var.set(progress)
            
            # Update status message
            if custom_message:
                self.status_var.set(custom_message)
            elif self.current_step <= len(self.steps):
                self.status_var.set(self.steps[self.current_step - 1])
            
            # Update step counter
            if self.window:
                self.step_label.config(text=f"Step {self.current_step} of {len(self.steps)}")
            
            # Update time estimation
            self.update_time_estimation()
            
            if self.window:
                self.window.update()
    
    def update_time_estimation(self):
        """Update estimated completion time."""
        if not self.step_times or self.current_step >= len(self.steps):
            return
        
        avg_step_time = sum(self.step_times) / len(self.step_times)
        remaining_steps = len(self.steps) - self.current_step
        estimated_remaining = avg_step_time * remaining_steps
        
        if estimated_remaining < 60:
            time_text = f"~{int(estimated_remaining)}s remaining"
        else:
            minutes = int(estimated_remaining // 60)
            seconds = int(estimated_remaining % 60)
            time_text = f"~{minutes}m {seconds}s remaining"
        
        self.time_var.set(time_text)
    
    def set_progress(self, percentage: float, message: str = None):
        """Set progress percentage directly."""
        self.progress_var.set(percentage)
        if message:
            self.status_var.set(message)
        if self.window:
            self.window.update()
    
    def complete(self):
        """Complete the operation and close window."""
        self.progress_var.set(100)
        self.status_var.set("Completed!")
        
        if self.window:
            self.window.after(1000, self.window.destroy)
    
    def error(self, message: str):
        """Handle operation error."""
        self.status_var.set(f"Error: {message}")
        if self.window:
            # Change progress bar color to indicate error
            style = ttk.Style()
            style.configure("Error.Horizontal.TProgressbar", 
                          background='red')
            self.progress_bar.configure(style="Error.Horizontal.TProgressbar")


class EnhancedStatusBar:
    """
    Enhanced status bar with multiple indicators, animations, and contextual information.
    Provides detailed status feedback and operation monitoring.
    """
    
    def __init__(self, parent, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.status_frame = None
        self.status_var = tk.StringVar(value="Ready")
        self.connection_var = tk.StringVar(value="Disconnected")
        self.operation_var = tk.StringVar(value="")
        self.memory_var = tk.StringVar(value="")
        self.create_status_bar()
        
    def create_status_bar(self) -> ttk.Frame:
        """Create comprehensive status bar with multiple indicators."""
        self.status_frame = ttk.Frame(self.parent)
        self.status_frame.pack(side='bottom', fill='x', padx=2, pady=2)
        
        # Left section - main status
        left_frame = ttk.Frame(self.status_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        self.status_label = ttk.Label(left_frame, textvariable=self.status_var,
                                     font=('Inter', 9))
        self.status_label.pack(side='left', padx=(5, 15))
        
        # Connection indicator
        conn_frame = ttk.Frame(left_frame)
        conn_frame.pack(side='left', padx=(0, 15))
        
        self.conn_dot = tk.Label(conn_frame, text="●", foreground="red", 
                                font=('Arial', 12))
        self.conn_dot.pack(side='left')
        
        self.conn_label = ttk.Label(conn_frame, textvariable=self.connection_var,
                                   font=('Inter', 9))
        self.conn_label.pack(side='left', padx=(3, 0))
        
        # Right section - system info
        right_frame = ttk.Frame(self.status_frame)
        right_frame.pack(side='right')
        
        # Memory usage
        self.memory_label = ttk.Label(right_frame, textvariable=self.memory_var,
                                     font=('Inter', 9))
        self.memory_label.pack(side='right', padx=(15, 5))
        
        # Time
        self.time_label = ttk.Label(right_frame, text="", font=('Inter', 9))
        self.time_label.pack(side='right', padx=(15, 0))
        
        # Start time updates
        self.update_time()
        self.update_memory()
        
        return self.status_frame
    
    def update_status(self, message: str, duration: int = 0):
        """Update main status message."""
        self.status_var.set(message)
        
        if duration > 0:
            self.parent.after(duration, lambda: self.status_var.set("Ready"))
    
    def update_connection_status(self, connected: bool, server: str = ""):
        """Update connection status with visual indicator."""
        if connected:
            self.connection_var.set(f"Connected {f'to {server}' if server else ''}")
            self.conn_dot.config(foreground="green")
        else:
            self.connection_var.set("Disconnected")
            self.conn_dot.config(foreground="red")
    
    def update_operation_status(self, operation: str):
        """Update current operation indicator."""
        self.operation_var.set(operation)
    
    def update_time(self):
        """Update time display."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.parent.after(1000, self.update_time)
    
    def update_memory(self):
        """Update memory usage display."""
        try:
            import psutil
            memory_percent = psutil.virtual_memory().percent
            self.memory_var.set(f"Memory: {memory_percent:.1f}%")
        except ImportError:
            self.memory_var.set("Memory: N/A")
        
        self.parent.after(5000, self.update_memory)  # Update every 5 seconds


class KeyboardShortcutManager:
    """
    Advanced keyboard shortcuts manager with contextual bindings and user customization.
    Provides intelligent keyboard navigation and accessibility features.
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.shortcuts = {}
        self.context_shortcuts = {}
        self.current_context = "global"
        self.setup_default_shortcuts()
    
    def setup_default_shortcuts(self):
        """Setup commonly used keyboard shortcuts."""
        default_shortcuts = {
            'global': {
                '<Control-n>': ('new_connection', 'New Connection'),
                '<Control-o>': ('open_project', 'Open Project'),
                '<Control-s>': ('save_project', 'Save Project'),
                '<Control-q>': ('quit_app', 'Quit Application'),
                '<F5>': ('refresh_data', 'Refresh Data'),
                '<Control-t>': ('toggle_theme', 'Toggle Theme'),
                '<Control-comma>': ('open_settings', 'Open Settings'),
                '<Control-question>': ('show_help', 'Show Help'),
                '<Control-Shift-d>': ('toggle_debug', 'Toggle Debug Mode')
            },
            'connection': {
                '<Control-Return>': ('test_connection', 'Test Connection'),
                '<Control-Shift-Return>': ('connect', 'Connect to Database')
            },
            'documentation': {
                '<Control-g>': ('generate_docs', 'Generate Documentation'),
                '<Control-p>': ('preview_docs', 'Preview Documentation'),
                '<Control-e>': ('export_docs', 'Export Documentation')
            },
            'playground': {
                '<F9>': ('execute_query', 'Execute Query'),
                '<Control-Return>': ('execute_query', 'Execute Query'),
                '<Control-Shift-c>': ('clear_results', 'Clear Results'),
                '<Control-l>': ('format_sql', 'Format SQL Query')
            }
        }
        
        for context, shortcuts in default_shortcuts.items():
            self.context_shortcuts[context] = shortcuts
    
    def register_shortcut(self, key_combination: str, callback: Callable, 
                         description: str = "", context: str = "global"):
        """Register a keyboard shortcut with callback."""
        if context not in self.context_shortcuts:
            self.context_shortcuts[context] = {}
        
        self.context_shortcuts[context][key_combination] = (callback, description)
        
        # Bind to current window if it's the active context
        if context == self.current_context or context == "global":
            try:
                self.parent.bind_all(key_combination, lambda event: callback())
            except Exception as e:
                print(f"Failed to bind shortcut {key_combination}: {e}")
    
    def set_context(self, context: str):
        """Change keyboard shortcut context."""
        # Unbind previous context shortcuts
        self._unbind_context_shortcuts(self.current_context)
        
        self.current_context = context
        
        # Bind new context shortcuts
        self._bind_context_shortcuts(context)
        # Always bind global shortcuts
        self._bind_context_shortcuts("global")
    
    def _bind_context_shortcuts(self, context: str):
        """Bind shortcuts for specific context."""
        if context in self.context_shortcuts:
            for key, (callback, desc) in self.context_shortcuts[context].items():
                try:
                    if callable(callback):
                        self.parent.bind_all(key, lambda event, cb=callback: cb())
                except Exception as e:
                    print(f"Failed to bind shortcut {key}: {e}")
    
    def _unbind_context_shortcuts(self, context: str):
        """Unbind shortcuts for specific context."""
        if context in self.context_shortcuts:
            for key in self.context_shortcuts[context].keys():
                try:
                    self.parent.unbind_all(key)
                except Exception:
                    pass  # Ignore unbinding errors
    
    def get_shortcuts_help(self, context: str = None) -> str:
        """Get help text for keyboard shortcuts."""
        if context is None:
            context = self.current_context
        
        help_text = f"Keyboard Shortcuts - {context.title()} Context:\n\n"
        
        # Add global shortcuts
        if "global" in self.context_shortcuts:
            help_text += "Global Shortcuts:\n"
            for key, (_, desc) in self.context_shortcuts["global"].items():
                help_text += f"  {key.replace('<', '').replace('>', '').replace('Control', 'Ctrl')}: {desc}\n"
            help_text += "\n"
        
        # Add context-specific shortcuts
        if context != "global" and context in self.context_shortcuts:
            help_text += f"{context.title()} Shortcuts:\n"
            for key, (_, desc) in self.context_shortcuts[context].items():
                help_text += f"  {key.replace('<', '').replace('>', '').replace('Control', 'Ctrl')}: {desc}\n"
        
        return help_text


class TooltipSystem:
    """
    Advanced tooltip system with rich content, positioning, and timing controls.
    Provides contextual help and information throughout the application.
    """
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.tooltips = {}
        self.active_tooltip = None
        self.delay = 500  # ms before showing tooltip
        self.fade_duration = 200  # ms for fade animation
    
    def add_tooltip(self, widget, text: str, rich_content: dict = None, 
                   position: str = "auto", delay: int = None):
        """Add tooltip to a widget with optional rich content."""
        tooltip = AdvancedTooltip(
            widget=widget,
            text=text,
            rich_content=rich_content,
            position=position,
            theme_manager=self.theme_manager,
            delay=delay or self.delay,
            fade_duration=self.fade_duration
        )
        
        self.tooltips[id(widget)] = tooltip
        return tooltip
    
    def remove_tooltip(self, widget):
        """Remove tooltip from widget."""
        widget_id = id(widget)
        if widget_id in self.tooltips:
            self.tooltips[widget_id].destroy()
            del self.tooltips[widget_id]
    
    def hide_all_tooltips(self):
        """Hide all active tooltips."""
        for tooltip in self.tooltips.values():
            tooltip.hide()


class AdvancedTooltip:
    """
    Individual tooltip with rich content support and smart positioning.
    """
    
    def __init__(self, widget, text: str, rich_content: dict = None,
                 position: str = "auto", theme_manager: ThemeManager = None,
                 delay: int = 500, fade_duration: int = 200):
        self.widget = widget
        self.text = text
        self.rich_content = rich_content or {}
        self.position = position
        self.theme_manager = theme_manager
        self.delay = delay
        self.fade_duration = fade_duration
        self.tooltip_window = None
        self.show_timer = None
        self.hide_timer = None
        
        self.setup_bindings()
    
    def setup_bindings(self):
        """Setup mouse events for tooltip display."""
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event):
        """Handle mouse enter event."""
        self.cancel_hide_timer()
        self.show_timer = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event):
        """Handle mouse leave event."""
        self.cancel_show_timer()
        self.hide_tooltip()
    
    def on_motion(self, event):
        """Handle mouse motion to update tooltip position."""
        if self.tooltip_window:
            self.position_tooltip(event)
    
    def show_tooltip(self):
        """Show the tooltip window."""
        if self.tooltip_window:
            return
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_attributes("-topmost", True)
        
        # Get theme colors
        theme = self.theme_manager.themes[self.theme_manager.current_theme] if self.theme_manager else {}
        bg_color = theme.get('surface_elevated', '#ffffff')
        text_color = theme.get('text', '#000000')
        border_color = theme.get('border', '#cccccc')
        
        # Configure tooltip appearance
        self.tooltip_window.configure(bg=bg_color, relief='solid', bd=1)
        
        # Create content
        self.create_tooltip_content(bg_color, text_color, border_color)
        
        # Position tooltip
        self.position_tooltip()
        
        # Fade in animation
        self.fade_in()
    
    def create_tooltip_content(self, bg_color: str, text_color: str, border_color: str):
        """Create the tooltip content with rich formatting."""
        main_frame = tk.Frame(self.tooltip_window, bg=bg_color, padx=8, pady=6)
        main_frame.pack()
        
        # Main text
        text_label = tk.Label(
            main_frame, 
            text=self.text,
            bg=bg_color,
            fg=text_color,
            font=('Inter', 9),
            justify='left',
            wraplength=300
        )
        text_label.pack(anchor='w')
        
        # Rich content (shortcuts, examples, etc.)
        if self.rich_content:
            if 'shortcut' in self.rich_content:
                shortcut_frame = tk.Frame(main_frame, bg=bg_color)
                shortcut_frame.pack(fill='x', pady=(4, 0))
                
                tk.Label(
                    shortcut_frame,
                    text=f"Shortcut: {self.rich_content['shortcut']}",
                    bg=bg_color,
                    fg=text_color,
                    font=('Inter', 8, 'italic')
                ).pack(anchor='w')
            
            if 'example' in self.rich_content:
                example_frame = tk.Frame(main_frame, bg=bg_color)
                example_frame.pack(fill='x', pady=(4, 0))
                
                tk.Label(
                    example_frame,
                    text=f"Example: {self.rich_content['example']}",
                    bg=bg_color,
                    fg=text_color,
                    font=('Consolas', 8),
                    wraplength=280
                ).pack(anchor='w')
    
    def position_tooltip(self, event=None):
        """Position tooltip near the widget."""
        if not self.tooltip_window:
            return
        
        # Get widget position
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()
        
        # Update tooltip size
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()
        
        # Calculate position
        if self.position == "bottom" or self.position == "auto":
            x = widget_x + (widget_width // 2) - (tooltip_width // 2)
            y = widget_y + widget_height + 5
        elif self.position == "top":
            x = widget_x + (widget_width // 2) - (tooltip_width // 2)
            y = widget_y - tooltip_height - 5
        elif self.position == "right":
            x = widget_x + widget_width + 5
            y = widget_y + (widget_height // 2) - (tooltip_height // 2)
        else:  # left
            x = widget_x - tooltip_width - 5
            y = widget_y + (widget_height // 2) - (tooltip_height // 2)
        
        # Ensure tooltip stays on screen
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        if x < 0:
            x = 10
        if y + tooltip_height > screen_height:
            y = widget_y - tooltip_height - 5
        if y < 0:
            y = widget_y + widget_height + 5
        
        self.tooltip_window.wm_geometry(f"+{int(x)}+{int(y)}")
    
    def fade_in(self):
        """Animate tooltip fade in."""
        try:
            self.tooltip_window.wm_attributes("-alpha", 0.0)
            self.animate_fade(0.0, 1.0, 50)
        except Exception:
            pass  # Fallback if alpha not supported
    
    def animate_fade(self, current_alpha: float, target_alpha: float, step_ms: int):
        """Animate alpha transition."""
        try:
            if abs(current_alpha - target_alpha) < 0.05:
                self.tooltip_window.wm_attributes("-alpha", target_alpha)
                return
            
            next_alpha = current_alpha + (target_alpha - current_alpha) * 0.2
            self.tooltip_window.wm_attributes("-alpha", next_alpha)
            
            self.tooltip_window.after(step_ms, 
                                     lambda: self.animate_fade(next_alpha, target_alpha, step_ms))
        except Exception:
            pass
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        self.cancel_show_timer()
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def cancel_show_timer(self):
        """Cancel the show timer."""
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None
    
    def cancel_hide_timer(self):
        """Cancel the hide timer."""
        if self.hide_timer:
            self.widget.after_cancel(self.hide_timer)
            self.hide_timer = None
    
    def destroy(self):
        """Clean up tooltip resources."""
        self.cancel_show_timer()
        self.cancel_hide_timer()
        self.hide_tooltip()
        
        # Remove bindings
        try:
            self.widget.unbind("<Enter>")
            self.widget.unbind("<Leave>")
            self.widget.unbind("<Motion>")
        except Exception:
            pass


class QuickAccessToolbar:
    """
    Quick access toolbar with customizable buttons for frequent operations.
    Provides one-click access to commonly used features and dynamic context-based actions.
    """
    
    def __init__(self, parent, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.toolbar_frame = None
        self.buttons = {}
        self.separators = []
        self.current_context = "global"
        self.context_buttons = {}
        self.tooltip_system = None
        self.create_toolbar()
        self.setup_default_buttons()
    
    def create_toolbar(self):
        """Create the main toolbar container."""
        self.toolbar_frame = ttk.Frame(self.parent)
        self.toolbar_frame.pack(side='top', fill='x', padx=5, pady=2)
        
        # Left section - main actions
        self.left_frame = ttk.Frame(self.toolbar_frame)
        self.left_frame.pack(side='left', padx=(0, 10))
        
        # Right section - context actions
        self.right_frame = ttk.Frame(self.toolbar_frame)
        self.right_frame.pack(side='right')
        
        return self.toolbar_frame
    
    def setup_default_buttons(self):
        """Setup default toolbar buttons."""
        # Main action buttons (always visible)
        self.add_button("new", "New Connection", self._placeholder_callback,
                       icon="🔗", tooltip="Create a new database connection")
        self.add_button("open", "Open", self._placeholder_callback,
                       icon="📁", tooltip="Open existing project or connection")
        self.add_button("save", "Save", self._placeholder_callback,
                       icon="💾", tooltip="Save current project")
        
        self.add_separator()
        
        self.add_button("refresh", "Refresh", self._placeholder_callback,
                       icon="🔄", tooltip="Refresh current data")
        self.add_button("settings", "Settings", self._placeholder_callback,
                       icon="⚙️", tooltip="Open application settings")
        
        # Context-specific buttons (shown/hidden based on current context)
        self.context_buttons = {
            'connection': [
                {"id": "test_conn", "text": "Test", "callback": self._placeholder_callback,
                 "icon": "🔍", "tooltip": "Test database connection"},
                {"id": "connect", "text": "Connect", "callback": self._placeholder_callback,
                 "icon": "🔌", "tooltip": "Connect to database"}
            ],
            'documentation': [
                {"id": "generate", "text": "Generate", "callback": self._placeholder_callback,
                 "icon": "📄", "tooltip": "Generate documentation"},
                {"id": "preview", "text": "Preview", "callback": self._placeholder_callback,
                 "icon": "👁️", "tooltip": "Preview documentation"},
                {"id": "export", "text": "Export", "callback": self._placeholder_callback,
                 "icon": "📤", "tooltip": "Export documentation"}
            ],
            'playground': [
                {"id": "execute", "text": "Execute", "callback": self._placeholder_callback,
                 "icon": "▶️", "tooltip": "Execute SQL query"},
                {"id": "clear", "text": "Clear", "callback": self._placeholder_callback,
                 "icon": "🗑️", "tooltip": "Clear query results"},
                {"id": "format", "text": "Format", "callback": self._placeholder_callback,
                 "icon": "✨", "tooltip": "Format SQL query"}
            ]
        }
    
    def add_button(self, button_id: str, text: str, callback: Callable,
                   icon: str = "", tooltip: str = "", context: str = "global"):
        """Add a button to the toolbar."""
        # Choose parent frame based on context
        parent_frame = self.left_frame if context == "global" else self.right_frame
        
        # Create button with modern styling
        if icon:
            button_text = f"{icon} {text}"
        else:
            button_text = text
        
        button = ttk.Button(parent_frame, text=button_text, command=callback)
        button.pack(side='left', padx=2)
        
        self.buttons[button_id] = {
            'widget': button,
            'callback': callback,
            'context': context,
            'tooltip': tooltip
        }
        
        # Add tooltip if provided and tooltip system is available
        if tooltip and self.tooltip_system:
            self.tooltip_system.add_tooltip(button, tooltip)
        
        return button
    
    def add_separator(self):
        """Add a visual separator between button groups."""
        separator = ttk.Separator(self.left_frame, orient='vertical')
        separator.pack(side='left', padx=8, pady=2, fill='y')
        self.separators.append(separator)
        return separator
    
    def set_context(self, context: str):
        """Change toolbar context and show/hide relevant buttons."""
        self.current_context = context
        
        # Hide all context buttons first
        for ctx_buttons in self.context_buttons.values():
            for btn_info in ctx_buttons:
                btn_id = btn_info['id']
                if btn_id in self.buttons:
                    self.buttons[btn_id]['widget'].pack_forget()
        
        # Show buttons for current context
        if context in self.context_buttons:
            # Add separator if we have context buttons
            if self.context_buttons[context]:
                self.add_separator()
            
            for btn_info in self.context_buttons[context]:
                if btn_info['id'] not in self.buttons:
                    # Create new context button
                    self.add_button(
                        btn_info['id'],
                        btn_info['text'],
                        btn_info['callback'],
                        btn_info.get('icon', ''),
                        btn_info.get('tooltip', ''),
                        context
                    )
                else:
                    # Show existing button
                    self.buttons[btn_info['id']]['widget'].pack(side='left', padx=2)
    
    def set_tooltip_system(self, tooltip_system: TooltipSystem):
        """Set the tooltip system for toolbar buttons."""
        self.tooltip_system = tooltip_system
        
        # Add tooltips to existing buttons
        for button_id, button_info in self.buttons.items():
            if button_info['tooltip']:
                self.tooltip_system.add_tooltip(button_info['widget'], button_info['tooltip'])
    
    def update_button_callback(self, button_id: str, callback: Callable):
        """Update the callback for a specific button."""
        if button_id in self.buttons:
            self.buttons[button_id]['callback'] = callback
            self.buttons[button_id]['widget'].configure(command=callback)
    
    def enable_button(self, button_id: str, enabled: bool = True):
        """Enable or disable a specific button."""
        if button_id in self.buttons:
            state = 'normal' if enabled else 'disabled'
            self.buttons[button_id]['widget'].configure(state=state)
    
    def _placeholder_callback(self):
        """Placeholder callback for buttons without assigned functions."""
        pass


class ImprovedErrorHandler:
    """
    Advanced error handling system with user-friendly messages, error recovery suggestions,
    and comprehensive logging. Provides graceful error handling throughout the application.
    """
    
    def __init__(self, theme_manager: ThemeManager, status_manager: StatusManager = None):
        self.theme_manager = theme_manager
        self.status_manager = status_manager
        self.error_log = []
        self.error_patterns = self._setup_error_patterns()
        self.recovery_suggestions = self._setup_recovery_suggestions()
    
    def _setup_error_patterns(self) -> Dict[str, Dict[str, str]]:
        """Setup common error patterns and their user-friendly messages."""
        return {
            'connection': {
                'timeout': "Connection timed out. The server may be unavailable or overloaded.",
                'authentication': "Authentication failed. Please check your username and password.",
                'server_not_found': "Server not found. Please verify the server address.",
                'network': "Network error. Please check your internet connection.",
                'permission': "Permission denied. You may not have access to this resource.",
                'database_not_found': "Database not found. Please verify the database name."
            },
            'sql': {
                'syntax_error': "SQL syntax error. Please check your query syntax.",
                'table_not_found': "Table or view not found. Please verify the object name.",
                'column_not_found': "Column not found. Please check the column name.",
                'permission_denied': "Insufficient permissions to execute this query.",
                'timeout': "Query execution timed out. The query may be too complex."
            },
            'file': {
                'not_found': "File not found. Please check the file path.",
                'permission_denied': "Permission denied. You may not have access to this file.",
                'disk_full': "Disk space full. Please free up space and try again.",
                'invalid_format': "Invalid file format. Please select a valid file."
            },
            'system': {
                'memory_error': "Out of memory. Please close other applications and try again.",
                'disk_error': "Disk error. Please check your disk space and permissions.",
                'general': "An unexpected error occurred. Please try again."
            }
        }
    
    def _setup_recovery_suggestions(self) -> Dict[str, List[str]]:
        """Setup recovery suggestions for different error types."""
        return {
            'connection_timeout': [
                "Check your network connection",
                "Verify the server is running and accessible",
                "Try increasing the connection timeout in settings",
                "Contact your database administrator if the problem persists"
            ],
            'authentication_failed': [
                "Double-check your username and password",
                "Ensure your account has the necessary permissions",
                "Try using Windows Authentication if available",
                "Contact your administrator to reset your password"
            ],
            'sql_syntax_error': [
                "Review your SQL syntax for typos",
                "Use the built-in SQL formatter to check syntax",
                "Consult SQL documentation for proper syntax",
                "Try executing parts of the query to isolate the error"
            ],
            'general_error': [
                "Try the operation again",
                "Check the application logs for more details",
                "Restart the application if the problem persists",
                "Contact support if the issue continues"
            ]
        }
    
    def handle_error(self, error: Exception, context: str = "general", 
                    show_dialog: bool = True, log_error: bool = True) -> Dict[str, Any]:
        """
        Handle an error with user-friendly messaging and recovery suggestions.
        
        Returns error information including user message and suggestions.
        """
        error_info = self._analyze_error(error, context)
        
        if log_error:
            self._log_error(error_info)
        
        if show_dialog:
            self._show_error_dialog(error_info)
        
        if self.status_manager:
            self.status_manager.update_status(f"Error: {error_info['user_message']}", duration=5000)
        
        return error_info
    
    def _analyze_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Analyze error and determine user-friendly message and suggestions."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Determine error category and specific type
        category, specific_type = self._categorize_error(error_str, error_type, context)
        
        # Get user-friendly message
        user_message = self._get_user_message(category, specific_type, error_str)
        
        # Get recovery suggestions
        suggestions = self._get_recovery_suggestions(category, specific_type)
        
        return {
            'original_error': error,
            'error_type': error_type,
            'context': context,
            'category': category,
            'specific_type': specific_type,
            'user_message': user_message,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat(),
            'technical_details': str(error)
        }
    
    def _categorize_error(self, error_str: str, error_type: str, context: str) -> tuple:
        """Categorize the error based on context and error message."""
        # Connection-related errors
        if context in ['connection', 'database'] or 'connection' in error_str:
            if 'timeout' in error_str:
                return 'connection', 'timeout'
            elif 'authentication' in error_str or 'login' in error_str:
                return 'connection', 'authentication'
            elif 'server' in error_str and 'not found' in error_str:
                return 'connection', 'server_not_found'
            elif 'network' in error_str:
                return 'connection', 'network'
            elif 'permission' in error_str or 'access' in error_str:
                return 'connection', 'permission'
            elif 'database' in error_str and 'not found' in error_str:
                return 'connection', 'database_not_found'
        
        # SQL-related errors
        elif context == 'sql' or 'sql' in error_str:
            if 'syntax' in error_str:
                return 'sql', 'syntax_error'
            elif 'table' in error_str or 'view' in error_str:
                return 'sql', 'table_not_found'
            elif 'column' in error_str:
                return 'sql', 'column_not_found'
            elif 'permission' in error_str:
                return 'sql', 'permission_denied'
            elif 'timeout' in error_str:
                return 'sql', 'timeout'
        
        # File-related errors
        elif 'file' in error_str or error_type in ['FileNotFoundError', 'PermissionError']:
            if 'not found' in error_str or error_type == 'FileNotFoundError':
                return 'file', 'not_found'
            elif 'permission' in error_str or error_type == 'PermissionError':
                return 'file', 'permission_denied'
            elif 'space' in error_str or 'disk full' in error_str:
                return 'file', 'disk_full'
            elif 'format' in error_str:
                return 'file', 'invalid_format'
        
        # System-related errors
        elif error_type in ['MemoryError', 'OutOfMemoryError']:
            return 'system', 'memory_error'
        elif 'disk' in error_str:
            return 'system', 'disk_error'
        
        return 'system', 'general'
    
    def _get_user_message(self, category: str, specific_type: str, error_str: str) -> str:
        """Get user-friendly error message."""
        if category in self.error_patterns and specific_type in self.error_patterns[category]:
            return self.error_patterns[category][specific_type]
        
        # Fallback to generic message
        return f"An error occurred: {error_str[:100]}{'...' if len(error_str) > 100 else ''}"
    
    def _get_recovery_suggestions(self, category: str, specific_type: str) -> List[str]:
        """Get recovery suggestions for the error."""
        suggestion_key = f"{category}_{specific_type}"
        
        if suggestion_key in self.recovery_suggestions:
            return self.recovery_suggestions[suggestion_key]
        
        return self.recovery_suggestions.get('general_error', [])
    
    def _show_error_dialog(self, error_info: Dict[str, Any]):
        """Show user-friendly error dialog with suggestions."""
        dialog = EnhancedErrorDialog(
            parent=self.theme_manager.parent if hasattr(self.theme_manager, 'parent') else None,
            error_info=error_info,
            theme_manager=self.theme_manager
        )
        dialog.show()
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error information."""
        self.error_log.append(error_info)
        
        # Keep only last 100 errors to prevent memory buildup
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
        
        # Print to console for debugging
        print(f"ERROR [{error_info['timestamp']}]: {error_info['user_message']}")
        print(f"Technical: {error_info['technical_details']}")
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent error log entries."""
        return self.error_log[-count:] if self.error_log else []


class EnhancedErrorDialog:
    """
    Enhanced error dialog with user-friendly presentation and recovery suggestions.
    """
    
    def __init__(self, parent, error_info: Dict[str, Any], theme_manager: ThemeManager):
        self.parent = parent
        self.error_info = error_info
        self.theme_manager = theme_manager
        self.dialog = None
    
    def show(self):
        """Show the error dialog."""
        self.dialog = tk.Toplevel(self.parent if self.parent else tk.Tk())
        self.dialog.title("Error")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Center dialog
        if self.parent:
            self.dialog.transient(self.parent)
            self.dialog.grab_set()
        
        theme = self.theme_manager.themes[self.theme_manager.current_theme]
        self.dialog.configure(bg=theme['background'])
        
        self.create_content()
        self.center_dialog()
    
    def create_content(self):
        """Create dialog content."""
        theme = self.theme_manager.themes[self.theme_manager.current_theme]
        
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Error icon and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Error icon
        icon_label = tk.Label(header_frame, text="⚠️", font=('Arial', 24),
                             bg=theme['background'])
        icon_label.pack(side='left', padx=(0, 15))
        
        # Title and main message
        text_frame = ttk.Frame(header_frame)
        text_frame.pack(side='left', fill='x', expand=True)
        
        title_label = tk.Label(text_frame, text="An Error Occurred",
                              font=('Inter', 14, 'bold'),
                              bg=theme['background'], fg=theme['text'])
        title_label.pack(anchor='w')
        
        message_label = tk.Label(text_frame, text=self.error_info['user_message'],
                                font=('Inter', 10), wraplength=350,
                                bg=theme['background'], fg=theme['text'],
                                justify='left')
        message_label.pack(anchor='w', pady=(5, 0))
        
        # Suggestions section
        if self.error_info['suggestions']:
            suggestions_frame = ttk.LabelFrame(main_frame, text="Suggested Solutions",
                                              padding="10")
            suggestions_frame.pack(fill='both', expand=True, pady=(15, 0))
            
            for i, suggestion in enumerate(self.error_info['suggestions'], 1):
                suggestion_text = f"{i}. {suggestion}"
                suggestion_label = tk.Label(suggestions_frame, text=suggestion_text,
                                           font=('Inter', 9), wraplength=450,
                                           bg=theme['background'], fg=theme['text'],
                                           justify='left')
                suggestion_label.pack(anchor='w', pady=(0, 5))
        
        # Technical details (expandable)
        details_frame = ttk.LabelFrame(main_frame, text="Technical Details",
                                      padding="10")
        details_frame.pack(fill='x', pady=(15, 0))
        
        details_text = tk.Text(details_frame, height=4, wrap='word',
                              font=('Consolas', 8), state='disabled')
        details_text.pack(fill='x')
        
        # Insert technical details
        details_text.config(state='normal')
        details_text.insert('1.0', self.error_info['technical_details'])
        details_text.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ok_button = ttk.Button(button_frame, text="OK", command=self.dialog.destroy)
        ok_button.pack(side='right', padx=(10, 0))
        
        copy_button = ttk.Button(button_frame, text="Copy Details",
                                command=self.copy_to_clipboard)
        copy_button.pack(side='right')
    
    def center_dialog(self):
        """Center dialog on parent or screen."""
        self.dialog.update_idletasks()
        
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 250
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 200
        else:
            x = (self.dialog.winfo_screenwidth() // 2) - 250
            y = (self.dialog.winfo_screenheight() // 2) - 200
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def copy_to_clipboard(self):
        """Copy error details to clipboard."""
        clipboard_text = f"Error: {self.error_info['user_message']}\n"
        clipboard_text += f"Type: {self.error_info['error_type']}\n"
        clipboard_text += f"Context: {self.error_info['context']}\n"
        clipboard_text += f"Time: {self.error_info['timestamp']}\n"
        clipboard_text += f"Details: {self.error_info['technical_details']}"
        
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(clipboard_text)


class UserPreferencesSystem:
    """
    Advanced user preferences system with persistent settings, customizable themes,
    and personalized interface configurations.
    """
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.preferences_file = "user_preferences.json"
        self.preferences = self._load_default_preferences()
        self.preference_callbacks = {}
        self.load_preferences()
        
    def _load_default_preferences(self) -> Dict[str, Any]:
        """Load default user preferences."""
        return {
            'appearance': {
                'theme': 'light',
                'font_size': 9,
                'font_family': 'Inter',
                'show_tooltips': True,
                'animation_enabled': True,
                'compact_mode': False
            },
            'interface': {
                'sidebar_width': 280,
                'sidebar_collapsed': False,
                'toolbar_visible': True,
                'status_bar_detailed': True,
                'auto_refresh': True,
                'remember_window_size': True
            },
            'workflow': {
                'auto_save_interval': 300,  # seconds
                'recent_items_limit': 10,
                'confirm_destructive_actions': True,
                'smart_caching_enabled': True,
                'background_operations': True
            },
            'keyboard': {
                'enable_shortcuts': True,
                'vim_mode': False,
                'custom_shortcuts': {}
            },
            'data_display': {
                'default_page_size': 50,
                'show_row_numbers': True,
                'highlight_changes': True,
                'group_similar_items': True
            },
            'privacy': {
                'remember_passwords': False,
                'auto_clear_logs': True,
                'telemetry_enabled': False
            }
        }
    
    def load_preferences(self):
        """Load preferences from file."""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    saved_prefs = json.load(f)
                    self._merge_preferences(saved_prefs)
                print("[Phase 2] User preferences loaded successfully")
            else:
                print("[Phase 2] Using default preferences")
                self.save_preferences()  # Create initial file
        except Exception as e:
            print(f"[Phase 2] Error loading preferences: {e}")
            # Use defaults if loading fails
    
    def _merge_preferences(self, saved_prefs: Dict[str, Any]):
        """Merge saved preferences with defaults to handle new settings."""
        def merge_dict(default: Dict, saved: Dict) -> Dict:
            result = default.copy()
            for key, value in saved.items():
                if key in result:
                    if isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = merge_dict(result[key], value)
                    else:
                        result[key] = value
            return result
        
        self.preferences = merge_dict(self.preferences, saved_prefs)
    
    def save_preferences(self):
        """Save preferences to file."""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            print("[Phase 2] User preferences saved")
        except Exception as e:
            print(f"[Phase 2] Error saving preferences: {e}")
    
    def get_preference(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific preference value."""
        try:
            return self.preferences.get(category, {}).get(key, default)
        except Exception:
            return default
    
    def set_preference(self, category: str, key: str, value: Any):
        """Set a specific preference value."""
        if category not in self.preferences:
            self.preferences[category] = {}
        
        old_value = self.preferences[category].get(key)
        self.preferences[category][key] = value
        
        # Trigger callbacks if value changed
        if old_value != value:
            callback_key = f"{category}.{key}"
            if callback_key in self.preference_callbacks:
                try:
                    self.preference_callbacks[callback_key](old_value, value)
                except Exception as e:
                    print(f"Error in preference callback: {e}")
        
        # Auto-save
        self.save_preferences()
    
    def register_preference_callback(self, category: str, key: str, callback: Callable):
        """Register a callback for preference changes."""
        callback_key = f"{category}.{key}"
        self.preference_callbacks[callback_key] = callback
    
    def get_category_preferences(self, category: str) -> Dict[str, Any]:
        """Get all preferences for a category."""
        return self.preferences.get(category, {}).copy()
    
    def reset_category(self, category: str):
        """Reset a category to default values."""
        defaults = self._load_default_preferences()
        if category in defaults:
            self.preferences[category] = defaults[category].copy()
            self.save_preferences()
    
    def reset_all_preferences(self):
        """Reset all preferences to defaults."""
        self.preferences = self._load_default_preferences()
        self.save_preferences()
    
    def export_preferences(self, file_path: str):
        """Export preferences to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting preferences: {e}")
            return False
    
    def import_preferences(self, file_path: str) -> bool:
        """Import preferences from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)
                self._merge_preferences(imported_prefs)
                self.save_preferences()
            return True
        except Exception as e:
            print(f"Error importing preferences: {e}")
            return False
    
    def register_callback(self, category: str, key: str, callback: Callable):
        """Alias for register_preference_callback for convenience."""
        self.register_preference_callback(category, key, callback)


class CustomizableThemeManager:
    """
    Extended theme manager with user customization capabilities and theme creation tools.
    """
    
    def __init__(self, preferences_system: UserPreferencesSystem):
        self.preferences = preferences_system
        self.base_theme_manager = ThemeManager()
        self.custom_themes = {}
        self.load_custom_themes()
    
    def load_custom_themes(self):
        """Load user-created custom themes."""
        custom_themes_file = "custom_themes.json"
        try:
            if os.path.exists(custom_themes_file):
                with open(custom_themes_file, 'r', encoding='utf-8') as f:
                    self.custom_themes = json.load(f)
                print(f"[Phase 2] Loaded {len(self.custom_themes)} custom themes")
        except Exception as e:
            print(f"Error loading custom themes: {e}")
    
    def save_custom_themes(self):
        """Save custom themes to file."""
        try:
            with open("custom_themes.json", 'w', encoding='utf-8') as f:
                json.dump(self.custom_themes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving custom themes: {e}")
    
    def create_custom_theme(self, name: str, base_theme: str, customizations: Dict[str, str]):
        """Create a new custom theme based on an existing theme."""
        if base_theme not in self.base_theme_manager.themes:
            raise ValueError(f"Base theme '{base_theme}' not found")
        
        # Start with base theme
        base_colors = self.base_theme_manager.themes[base_theme].copy()
        
        # Apply customizations
        base_colors.update(customizations)
        
        # Store custom theme
        self.custom_themes[name] = {
            'base_theme': base_theme,
            'customizations': customizations,
            'colors': base_colors,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat()
        }
        
        self.save_custom_themes()
        return name
    
    def get_available_themes(self) -> List[str]:
        """Get list of all available themes (built-in + custom)."""
        builtin_themes = list(self.base_theme_manager.themes.keys())
        custom_theme_names = list(self.custom_themes.keys())
        return builtin_themes + custom_theme_names
    
    def get_theme_colors(self, theme_name: str) -> Dict[str, str]:
        """Get color palette for a theme."""
        if theme_name in self.custom_themes:
            return self.custom_themes[theme_name]['colors'].copy()
        elif theme_name in self.base_theme_manager.themes:
            return self.base_theme_manager.themes[theme_name].copy()
        else:
            raise ValueError(f"Theme '{theme_name}' not found")
    
    def apply_theme(self, theme_name: str, style: ttk.Style = None):
        """Apply a theme (built-in or custom) to the application."""
        colors = self.get_theme_colors(theme_name)
        
        # Update the base theme manager with the colors
        self.base_theme_manager.current_theme = theme_name
        if theme_name not in self.base_theme_manager.themes:
            self.base_theme_manager.themes[theme_name] = colors
        
        if style:
            self.base_theme_manager.style = style
            self.base_theme_manager._configure_ttk_styles(colors)
        
        # Update user preference
        self.preferences.set_preference('appearance', 'theme', theme_name)
    
    def delete_custom_theme(self, theme_name: str):
        """Delete a custom theme."""
        if theme_name in self.custom_themes:
            del self.custom_themes[theme_name]
            self.save_custom_themes()
            return True
        return False
    
    def duplicate_theme(self, source_theme: str, new_name: str):
        """Duplicate an existing theme."""
        colors = self.get_theme_colors(source_theme)
        return self.create_custom_theme(new_name, 'light', colors)


class WorkspaceManager:
    """
    Advanced workspace management system for saving and restoring interface layouts,
    view configurations, and personalized workspace arrangements.
    """
    
    def __init__(self, preferences_system: UserPreferencesSystem):
        self.preferences = preferences_system
        self.workspaces_file = "workspaces.json"
        self.workspaces = {}
        self.current_workspace = None
        self.load_workspaces()
    
    def load_workspaces(self):
        """Load saved workspaces."""
        try:
            if os.path.exists(self.workspaces_file):
                with open(self.workspaces_file, 'r', encoding='utf-8') as f:
                    self.workspaces = json.load(f)
                print(f"[Phase 2] Loaded {len(self.workspaces)} workspaces")
        except Exception as e:
            print(f"Error loading workspaces: {e}")
    
    def save_workspaces(self):
        """Save workspaces to file."""
        try:
            with open(self.workspaces_file, 'w', encoding='utf-8') as f:
                json.dump(self.workspaces, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving workspaces: {e}")
    
    def create_workspace(self, name: str, description: str = ""):
        """Create a new workspace configuration."""
        workspace = {
            'name': name,
            'description': description,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat(),
            'layout': {
                'sidebar_width': self.preferences.get_preference('interface', 'sidebar_width', 280),
                'sidebar_collapsed': self.preferences.get_preference('interface', 'sidebar_collapsed', False),
                'toolbar_visible': self.preferences.get_preference('interface', 'toolbar_visible', True),
                'panels': [],
                'active_view': 'dashboard'
            },
            'theme': self.preferences.get_preference('appearance', 'theme', 'light'),
            'shortcuts': self.preferences.get_preference('keyboard', 'custom_shortcuts', {}),
            'data_settings': {
                'page_size': self.preferences.get_preference('data_display', 'default_page_size', 50),
                'show_row_numbers': self.preferences.get_preference('data_display', 'show_row_numbers', True)
            }
        }
        
        self.workspaces[name] = workspace
        self.save_workspaces()
        return workspace
    
    def apply_workspace(self, name: str) -> bool:
        """Apply a workspace configuration."""
        if name not in self.workspaces:
            return False
        
        workspace = self.workspaces[name]
        self.current_workspace = name
        
        # Apply interface settings
        layout = workspace.get('layout', {})
        self.preferences.set_preference('interface', 'sidebar_width', layout.get('sidebar_width', 280))
        self.preferences.set_preference('interface', 'sidebar_collapsed', layout.get('sidebar_collapsed', False))
        self.preferences.set_preference('interface', 'toolbar_visible', layout.get('toolbar_visible', True))
        
        # Apply theme
        if 'theme' in workspace:
            self.preferences.set_preference('appearance', 'theme', workspace['theme'])
        
        # Apply shortcuts
        if 'shortcuts' in workspace:
            self.preferences.set_preference('keyboard', 'custom_shortcuts', workspace['shortcuts'])
        
        # Apply data settings
        data_settings = workspace.get('data_settings', {})
        for key, value in data_settings.items():
            self.preferences.set_preference('data_display', key, value)
        
        return True
    
    def update_current_workspace(self):
        """Update the current workspace with current settings."""
        if not self.current_workspace or self.current_workspace not in self.workspaces:
            return False
        
        workspace = self.workspaces[self.current_workspace]
        workspace['modified_date'] = datetime.now().isoformat()
        
        # Update layout
        workspace['layout'] = {
            'sidebar_width': self.preferences.get_preference('interface', 'sidebar_width', 280),
            'sidebar_collapsed': self.preferences.get_preference('interface', 'sidebar_collapsed', False),
            'toolbar_visible': self.preferences.get_preference('interface', 'toolbar_visible', True),
        }
        
        # Update theme
        workspace['theme'] = self.preferences.get_preference('appearance', 'theme', 'light')
        
        self.save_workspaces()
        return True
    
    def delete_workspace(self, name: str) -> bool:
        """Delete a workspace."""
        if name in self.workspaces:
            del self.workspaces[name]
            if self.current_workspace == name:
                self.current_workspace = None
            self.save_workspaces()
            return True
        return False
    
    def get_workspace_list(self) -> List[Dict[str, Any]]:
        """Get list of available workspaces."""
        return [
            {
                'name': name,
                'description': ws.get('description', ''),
                'created_date': ws.get('created_date', ''),
                'modified_date': ws.get('modified_date', ''),
                'theme': ws.get('theme', 'light')
            }
            for name, ws in self.workspaces.items()
        ]
    
    def export_workspace(self, name: str, file_path: str) -> bool:
        """Export a workspace to a file."""
        if name not in self.workspaces:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({name: self.workspaces[name]}, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting workspace: {e}")
            return False
    
    def import_workspace(self, file_path: str) -> List[str]:
        """Import workspace(s) from a file."""
        imported_names = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_workspaces = json.load(f)
                
                for name, workspace in imported_workspaces.items():
                    # Avoid overwriting existing workspaces
                    original_name = name
                    counter = 1
                    while name in self.workspaces:
                        name = f"{original_name}_{counter}"
                        counter += 1
                    
                    self.workspaces[name] = workspace
                    imported_names.append(name)
                
                self.save_workspaces()
        except Exception as e:
            print(f"Error importing workspace: {e}")
        
        return imported_names


class AdvancedSearchSystem:
    """
    Advanced search and filtering system with intelligent query parsing,
    saved searches, and context-aware filtering capabilities.
    """
    
    def __init__(self, preferences_system: UserPreferencesSystem):
        self.preferences = preferences_system
        self.saved_searches_file = "saved_searches.json"
        self.saved_searches = {}
        self.search_history = []
        self.load_saved_searches()
    
    def load_saved_searches(self):
        """Load saved searches from file."""
        try:
            if os.path.exists(self.saved_searches_file):
                with open(self.saved_searches_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.saved_searches = data.get('searches', {})
                    self.search_history = data.get('history', [])
                print(f"[Phase 2] Loaded {len(self.saved_searches)} saved searches")
        except Exception as e:
            print(f"Error loading saved searches: {e}")
    
    def save_searches(self):
        """Save searches to file."""
        try:
            data = {
                'searches': self.saved_searches,
                'history': self.search_history[-50:]  # Keep last 50 searches
            }
            with open(self.saved_searches_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving searches: {e}")
    
    def parse_search_query(self, query: str) -> Dict[str, Any]:
        """Parse search query with advanced syntax support."""
        parsed = {
            'text': '',
            'filters': {},
            'operators': [],
            'modifiers': []
        }
        
        # Handle quoted strings
        import re
        quoted_pattern = r'"([^"]*)"'
        quoted_matches = re.findall(quoted_pattern, query)
        
        # Remove quoted strings temporarily
        temp_query = re.sub(quoted_pattern, '__QUOTED__', query)
        
        # Split by spaces but preserve quoted strings
        parts = temp_query.split()
        quoted_index = 0
        
        for part in parts:
            if part == '__QUOTED__':
                if quoted_index < len(quoted_matches):
                    parsed['text'] += f'"{quoted_matches[quoted_index]}" '
                    quoted_index += 1
            elif ':' in part and not part.startswith('http'):
                # Filter syntax: field:value
                key, value = part.split(':', 1)
                parsed['filters'][key.lower()] = value
            elif part.upper() in ['AND', 'OR', 'NOT']:
                parsed['operators'].append(part.upper())
            elif part.startswith('-'):
                # Exclusion modifier
                parsed['modifiers'].append(('exclude', part[1:]))
            elif part.startswith('+'):
                # Inclusion modifier
                parsed['modifiers'].append(('include', part[1:]))
            else:
                parsed['text'] += part + ' '
        
        parsed['text'] = parsed['text'].strip()
        return parsed
    
    def create_filter_set(self, name: str, filters: Dict[str, Any], description: str = ""):
        """Create a reusable filter set."""
        filter_set = {
            'name': name,
            'description': description,
            'filters': filters,
            'created_date': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        self.saved_searches[name] = filter_set
        self.save_searches()
        return filter_set
    
    def apply_filters(self, data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filters to a dataset."""
        if not filters:
            return data
        
        filtered_data = []
        
        for item in data:
            matches = True
            
            for field, filter_value in filters.items():
                if field not in item:
                    matches = False
                    break
                
                item_value = str(item[field]).lower()
                filter_value = str(filter_value).lower()
                
                # Support different filter types
                if filter_value.startswith('>='):
                    try:
                        if float(item_value) < float(filter_value[2:]):
                            matches = False
                            break
                    except ValueError:
                        matches = False
                        break
                elif filter_value.startswith('<='):
                    try:
                        if float(item_value) > float(filter_value[2:]):
                            matches = False
                            break
                    except ValueError:
                        matches = False
                        break
                elif filter_value.startswith('>'):
                    try:
                        if float(item_value) <= float(filter_value[1:]):
                            matches = False
                            break
                    except ValueError:
                        matches = False
                        break
                elif filter_value.startswith('<'):
                    try:
                        if float(item_value) >= float(filter_value[1:]):
                            matches = False
                            break
                    except ValueError:
                        matches = False
                        break
                elif filter_value.startswith('*') and filter_value.endswith('*'):
                    # Contains
                    if filter_value[1:-1] not in item_value:
                        matches = False
                        break
                elif filter_value.startswith('*'):
                    # Ends with
                    if not item_value.endswith(filter_value[1:]):
                        matches = False
                        break
                elif filter_value.endswith('*'):
                    # Starts with
                    if not item_value.startswith(filter_value[:-1]):
                        matches = False
                        break
                else:
                    # Exact match
                    if filter_value not in item_value:
                        matches = False
                        break
            
            if matches:
                filtered_data.append(item)
        
        return filtered_data
    
    def search_full_text(self, data: List[Dict], query: str, fields: List[str] = None) -> List[Dict]:
        """Perform full-text search across specified fields."""
        if not query:
            return data
        
        query_lower = query.lower()
        results = []
        
        for item in data:
            match_found = False
            search_fields = fields or item.keys()
            
            for field in search_fields:
                if field in item:
                    field_value = str(item[field]).lower()
                    if query_lower in field_value:
                        match_found = True
                        break
            
            if match_found:
                results.append(item)
        
        return results
    
    def get_search_suggestions(self, partial_query: str, context: str = "general") -> List[str]:
        """Get search suggestions based on partial query and context."""
        suggestions = []
        
        # Common filter suggestions based on context
        context_suggestions = {
            'database': ['table:', 'schema:', 'type:', 'rows:>', 'created:', 'modified:'],
            'tables': ['name:', 'schema:', 'rows:>', 'columns:>', 'indexes:', 'type:'],
            'columns': ['name:', 'type:', 'nullable:', 'default:', 'identity:'],
            'procedures': ['name:', 'schema:', 'parameters:', 'created:', 'modified:'],
            'general': ['name:', 'type:', 'created:', 'modified:', 'size:>', 'count:>']
        }
        
        base_suggestions = context_suggestions.get(context, context_suggestions['general'])
        
        # Add suggestions that match the partial query
        for suggestion in base_suggestions:
            if suggestion.startswith(partial_query.lower()):
                suggestions.append(suggestion)
        
        # Add saved search names
        for name in self.saved_searches.keys():
            if name.lower().startswith(partial_query.lower()):
                suggestions.append(f'saved:{name}')
        
        # Add recent search terms from history
        for historical_search in reversed(self.search_history[-10:]):
            if partial_query.lower() in historical_search.lower() and historical_search not in suggestions:
                suggestions.append(historical_search)
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def add_to_search_history(self, query: str):
        """Add search query to history."""
        if query and query not in self.search_history:
            self.search_history.append(query)
            if len(self.search_history) > 100:  # Keep last 100 searches
                self.search_history = self.search_history[-100:]
            self.save_searches()
    
    def get_popular_filters(self, context: str = "general") -> List[Dict[str, Any]]:
        """Get popular/frequently used filters for context."""
        # Sort saved searches by usage count
        popular = sorted(
            self.saved_searches.values(),
            key=lambda x: x.get('usage_count', 0),
            reverse=True
        )
        
        return popular[:5]  # Return top 5


class DataVisualizationSystem:
    """
    Enhanced data visualization system with multiple chart types, interactive features,
    and customizable visual representations.
    """
    
    def __init__(self, preferences_system: UserPreferencesSystem, theme_manager: ThemeManager):
        self.preferences = preferences_system
        self.theme_manager = theme_manager
        self.chart_configs = {}
        self.visualization_history = []
    
    def create_table_relationship_graph(self, schema_data: Dict[str, Any], 
                                       layout_type: str = "hierarchical") -> Dict[str, Any]:
        """Create an interactive table relationship visualization."""
        graph_data = {
            'nodes': [],
            'edges': [],
            'layout': layout_type,
            'config': {
                'node_size_based_on': 'row_count',
                'edge_width_based_on': 'relationship_strength',
                'color_scheme': self.theme_manager.current_theme,
                'show_labels': True,
                'interactive': True
            }
        }
        
        # Process tables as nodes
        tables = schema_data.get('tables', [])
        for table in tables:
            node = {
                'id': f"{table['schema_name']}.{table['table_name']}",
                'label': table['table_name'],
                'schema': table['schema_name'],
                'row_count': table.get('row_count', 0),
                'column_count': len(table.get('columns', [])),
                'type': 'table',
                'description': table.get('description', ''),
                'size': min(max(table.get('row_count', 0) / 1000, 10), 50)  # Size based on rows
            }
            graph_data['nodes'].append(node)
        
        # Process foreign key relationships as edges
        for table in tables:
            for fk in table.get('foreign_keys', []):
                edge = {
                    'source': f"{table['schema_name']}.{table['table_name']}",
                    'target': f"{fk.get('referenced_schema', table['schema_name'])}.{fk['referenced_table']}",
                    'label': fk['constraint_name'],
                    'type': 'foreign_key',
                    'strength': 1.0
                }
                graph_data['edges'].append(edge)
        
        return graph_data
    
    def create_schema_overview_chart(self, schema_data: Dict[str, Any], 
                                   chart_type: str = "sunburst") -> Dict[str, Any]:
        """Create schema overview visualization."""
        chart_data = {
            'type': chart_type,
            'title': f"Schema Overview - {schema_data.get('metadata', {}).get('database_name', 'Unknown')}",
            'data': [],
            'config': {
                'theme': self.theme_manager.current_theme,
                'interactive': True,
                'show_percentages': True,
                'drill_down': True
            }
        }
        
        if chart_type == "sunburst":
            # Hierarchical sunburst chart
            schemas = {}
            for table in schema_data.get('tables', []):
                schema_name = table['schema_name']
                if schema_name not in schemas:
                    schemas[schema_name] = {
                        'name': schema_name,
                        'tables': [],
                        'total_rows': 0,
                        'total_columns': 0
                    }
                
                schemas[schema_name]['tables'].append({
                    'name': table['table_name'],
                    'rows': table.get('row_count', 0),
                    'columns': len(table.get('columns', []))
                })
                schemas[schema_name]['total_rows'] += table.get('row_count', 0)
                schemas[schema_name]['total_columns'] += len(table.get('columns', []))
            
            for schema_name, schema_info in schemas.items():
                schema_item = {
                    'name': schema_name,
                    'value': schema_info['total_rows'],
                    'children': []
                }
                
                for table in schema_info['tables']:
                    table_item = {
                        'name': table['name'],
                        'value': table['rows'],
                        'columns': table['columns']
                    }
                    schema_item['children'].append(table_item)
                
                chart_data['data'].append(schema_item)
        
        elif chart_type == "treemap":
            # Treemap visualization
            for table in schema_data.get('tables', []):
                item = {
                    'name': f"{table['schema_name']}.{table['table_name']}",
                    'value': table.get('row_count', 1),
                    'schema': table['schema_name'],
                    'table': table['table_name'],
                    'columns': len(table.get('columns', []))
                }
                chart_data['data'].append(item)
        
        return chart_data
    
    def create_performance_dashboard(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance monitoring dashboard."""
        dashboard = {
            'title': 'Database Performance Dashboard',
            'widgets': [],
            'refresh_interval': 30,  # seconds
            'config': {
                'theme': self.theme_manager.current_theme,
                'auto_refresh': True,
                'real_time': True
            }
        }
        
        # CPU Usage Widget
        cpu_widget = {
            'type': 'gauge',
            'title': 'CPU Usage',
            'data': {
                'value': performance_data.get('cpu_percent', 0),
                'max': 100,
                'unit': '%',
                'thresholds': [70, 85]  # Yellow at 70%, Red at 85%
            },
            'size': {'width': 2, 'height': 2}
        }
        dashboard['widgets'].append(cpu_widget)
        
        # Memory Usage Widget
        memory_widget = {
            'type': 'gauge',
            'title': 'Memory Usage',
            'data': {
                'value': performance_data.get('memory_percent', 0),
                'max': 100,
                'unit': '%',
                'thresholds': [75, 90]
            },
            'size': {'width': 2, 'height': 2}
        }
        dashboard['widgets'].append(memory_widget)
        
        # Query Performance Chart
        query_widget = {
            'type': 'line_chart',
            'title': 'Query Response Time',
            'data': {
                'x_axis': 'time',
                'y_axis': 'response_time_ms',
                'series': performance_data.get('query_times', [])
            },
            'size': {'width': 4, 'height': 2}
        }
        dashboard['widgets'].append(query_widget)
        
        # Connection Count
        connections_widget = {
            'type': 'counter',
            'title': 'Active Connections',
            'data': {
                'value': performance_data.get('active_connections', 0),
                'trend': performance_data.get('connection_trend', 0)
            },
            'size': {'width': 2, 'height': 1}
        }
        dashboard['widgets'].append(connections_widget)
        
        return dashboard
    
    def export_visualization(self, viz_data: Dict[str, Any], 
                           format_type: str = "svg", file_path: str = None) -> bool:
        """Export visualization to various formats."""
        try:
            if format_type == "json":
                # Export raw data
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(viz_data, f, indent=2, ensure_ascii=False)
                return True
            
            elif format_type in ["svg", "png", "pdf"]:
                # For actual image export, you would integrate with a charting library
                # This is a placeholder for the export functionality
                print(f"Exporting visualization as {format_type} to {file_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error exporting visualization: {e}")
            return False
    
    def get_visualization_templates(self) -> List[Dict[str, Any]]:
        """Get available visualization templates."""
        templates = [
            {
                'name': 'Schema Overview',
                'type': 'sunburst',
                'description': 'Hierarchical view of database schemas and tables',
                'data_requirements': ['tables', 'schemas'],
                'customizable': True
            },
            {
                'name': 'Table Relationships',
                'type': 'network_graph',
                'description': 'Interactive graph showing table relationships',
                'data_requirements': ['foreign_keys', 'tables'],
                'customizable': True
            },
            {
                'name': 'Data Distribution',
                'type': 'treemap',
                'description': 'Visual representation of data size distribution',
                'data_requirements': ['row_counts', 'table_sizes'],
                'customizable': True
            },
            {
                'name': 'Performance Dashboard',
                'type': 'dashboard',
                'description': 'Real-time performance monitoring widgets',
                'data_requirements': ['performance_metrics'],
                'customizable': True
            }
        ]
        
        return templates


class LoadingOverlay:
    """Loading overlay component."""
    
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
        
    def show(self, message: str = "Loading..."):
        """Show loading overlay."""
        if self.overlay:
            return
        
        # Create overlay
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.title("")
        self.overlay.overrideredirect(True)
        self.overlay.configure(bg='white')
        self.overlay.attributes('-alpha', 0.8)
        self.overlay.attributes('-topmost', True)
        
        # Position overlay over parent
        self.position_overlay()
        
        # Content
        content_frame = tk.Frame(self.overlay, bg='white')
        content_frame.pack(expand=True, fill='both')
        
        # Spinner (using text animation)
        self.spinner_label = tk.Label(content_frame, text="⟳", font=('Arial', 24), bg='white')
        self.spinner_label.pack(expand=True)
        
        # Message
        message_label = tk.Label(content_frame, text=message, font=('Arial', 12), bg='white')
        message_label.pack()
        
        # Start spinner animation
        self.animate_spinner()
    
    def position_overlay(self):
        """Position overlay over parent widget."""
        self.parent.update_idletasks()
        
        x = self.parent.winfo_rootx()
        y = self.parent.winfo_rooty()
        width = self.parent.winfo_width()
        height = self.parent.winfo_height()
        
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
    
    def animate_spinner(self):
        """Animate the spinner."""
        if self.overlay:
            current = self.spinner_label.cget('text')
            spinners = ['⟳', '⟲', '⟳', '⟲']
            next_spinner = spinners[(spinners.index(current) + 1) % len(spinners)]
            self.spinner_label.config(text=next_spinner)
            
            self.overlay.after(200, self.animate_spinner)
    
    def hide(self):
        """Hide loading overlay."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None


# Test the framework
if __name__ == "__main__":
    root = tk.Tk()
    root.title("UI Framework Test")
    root.geometry("1200x800")
    
    # Initialize theme manager
    theme_manager = ThemeManager()
    style = ttk.Style()
    theme_manager.initialize_styles(style)
    
    # Initialize status manager
    status_manager = StatusManager(root)
    
    # Create status bar
    status_bar = status_manager.create_status_bar(root)
    status_bar.pack(side='bottom', fill='x')
    
    # Create main content
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill='both', expand=True)
    
    # Create dashboard
    dashboard = DashboardHome(main_frame, theme_manager, status_manager)
    dashboard_widget = dashboard.create_dashboard(main_frame)
    dashboard_widget.pack(fill='both', expand=True)
    
    # Test theme switching
    def switch_theme():
        current_themes = theme_manager.get_available_themes()
        current_index = current_themes.index(theme_manager.current_theme)
        next_theme = current_themes[(current_index + 1) % len(current_themes)]
        theme_manager.apply_theme(next_theme)
        status_manager.show_toast_notification(f"Switched to {next_theme} theme", 'info')
    
    # Theme switch button
    theme_button = ttk.Button(main_frame, text="Switch Theme", command=switch_theme)
    theme_button.pack(pady=10)
    
    # Test notifications
    def test_notifications():
        status_manager.show_toast_notification("This is an info message", 'info')
        root.after(1000, lambda: status_manager.show_toast_notification("This is a success message", 'success'))
        root.after(2000, lambda: status_manager.show_toast_notification("This is a warning message", 'warning'))
        root.after(3000, lambda: status_manager.show_toast_notification("This is an error message", 'error'))
    
    notify_button = ttk.Button(main_frame, text="Test Notifications", command=test_notifications)
    notify_button.pack(pady=5)
    
    root.mainloop()


# ===== PHASE 3: ADVANCED FEATURES =====

class EnterpriseProjectManager:
    """
    Advanced project management system with multi-database coordination,
    environment management, and collaborative workflows.
    """
    
    def __init__(self, preferences_system: 'UserPreferencesSystem'):
        self.preferences = preferences_system
        self.project_db = None
        self.current_project = None
        self.project_callbacks = {}
        self._initialize_project_database()
    
    def _initialize_project_database(self):
        """Initialize project management database."""
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path("projects.db")
            self.project_db = sqlite3.connect(str(db_path), check_same_thread=False)
            
            # Create projects table
            cursor = self.project_db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config JSON,
                    metadata JSON
                )
            """)
            
            # Create project databases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_databases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    database_name TEXT,
                    connection_config JSON,
                    environment TEXT DEFAULT 'production',
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            
            self.project_db.commit()
            print("[Phase 3] Project management database initialized")
            
        except Exception as e:
            print(f"[Phase 3] Error initializing project database: {e}")
    
    def create_project(self, name: str, description: str = "") -> str:
        """Create a new project."""
        import uuid
        import json
        
        project_id = str(uuid.uuid4())
        
        try:
            cursor = self.project_db.cursor()
            cursor.execute("""
                INSERT INTO projects (id, name, description, config, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, name, description, 
                  json.dumps({'auto_sync': True, 'notifications': True}),
                  json.dumps({'created_by': 'user', 'version': '1.0'})))
            
            self.project_db.commit()
            
            # Trigger callbacks
            self._trigger_callback('project_created', project_id)
            
            return project_id
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        try:
            cursor = self.project_db.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
            
            projects = []
            for row in cursor.fetchall():
                project = {
                    'id': row[0],
                    'name': row[1], 
                    'description': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'config': json.loads(row[5]) if row[5] else {},
                    'metadata': json.loads(row[6]) if row[6] else {}
                }
                projects.append(project)
            
            return projects
            
        except Exception as e:
            print(f"Error getting projects: {e}")
            return []
    
    def switch_project(self, project_id: str):
        """Switch to a different project."""
        self.current_project = project_id
        self.preferences.set_preference('workspace', 'current_project', project_id)
        self._trigger_callback('project_switched', project_id)
    
    def add_database_to_project(self, project_id: str, database_config: Dict[str, Any], 
                               environment: str = 'production'):
        """Add database to project."""
        try:
            cursor = self.project_db.cursor()
            cursor.execute("""
                INSERT INTO project_databases (project_id, database_name, connection_config, environment)
                VALUES (?, ?, ?, ?)
            """, (project_id, database_config.get('name'), 
                  json.dumps(database_config), environment))
            
            self.project_db.commit()
            self._trigger_callback('database_added', project_id)
            
        except Exception as e:
            print(f"Error adding database to project: {e}")
    
    def get_project_databases(self, project_id: str) -> List[Dict[str, Any]]:
        """Get databases for a project."""
        try:
            cursor = self.project_db.cursor()
            cursor.execute("""
                SELECT database_name, connection_config, environment
                FROM project_databases WHERE project_id = ?
            """, (project_id,))
            
            databases = []
            for row in cursor.fetchall():
                databases.append({
                    'name': row[0],
                    'config': json.loads(row[1]),
                    'environment': row[2]
                })
            
            return databases
            
        except Exception as e:
            print(f"Error getting project databases: {e}")
            return []
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for project events."""
        if event not in self.project_callbacks:
            self.project_callbacks[event] = []
        self.project_callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, data: Any):
        """Trigger callbacks for an event."""
        if event in self.project_callbacks:
            for callback in self.project_callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in project callback: {e}")


class IntelligentAPIIntegration:
    """
    Smart API integration system with webhook management, external platform
    connectivity, and automated workflow triggers.
    """
    
    def __init__(self, preferences_system: 'UserPreferencesSystem', project_manager: EnterpriseProjectManager):
        self.preferences = preferences_system
        self.project_manager = project_manager
        self.webhook_db = None
        self.api_server = None
        self.integrations = {}
        self._initialize_webhook_database()
    
    def _initialize_webhook_database(self):
        """Initialize webhook management database."""
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path("webhooks.db")
            self.webhook_db = sqlite3.connect(str(db_path), check_same_thread=False)
            
            cursor = self.webhook_db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhooks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    events JSON,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    secret_key TEXT,
                    retry_count INTEGER DEFAULT 3
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook_deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webhook_id TEXT,
                    event_type TEXT,
                    payload JSON,
                    status TEXT,
                    response_code INTEGER,
                    delivered_at TIMESTAMP,
                    FOREIGN KEY (webhook_id) REFERENCES webhooks (id)
                )
            """)
            
            self.webhook_db.commit()
            print("[Phase 3] API integration database initialized")
            
        except Exception as e:
            print(f"[Phase 3] Error initializing webhook database: {e}")
    
    def register_webhook(self, name: str, url: str, events: List[str], 
                        secret_key: str = None) -> str:
        """Register a new webhook."""
        import uuid
        import json
        
        webhook_id = str(uuid.uuid4())
        
        try:
            cursor = self.webhook_db.cursor()
            cursor.execute("""
                INSERT INTO webhooks (id, name, url, events, secret_key)
                VALUES (?, ?, ?, ?, ?)
            """, (webhook_id, name, url, json.dumps(events), secret_key))
            
            self.webhook_db.commit()
            return webhook_id
            
        except Exception as e:
            print(f"Error registering webhook: {e}")
            return None
    
    def trigger_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Trigger webhooks for an event."""
        import threading
        
        # Run webhook delivery in background
        thread = threading.Thread(target=self._deliver_webhooks, 
                                 args=(event_type, payload))
        thread.daemon = True
        thread.start()
    
    def _deliver_webhooks(self, event_type: str, payload: Dict[str, Any]):
        """Deliver webhook payloads."""
        try:
            import requests
            import json
            import hmac
            import hashlib
            from datetime import datetime
            
            cursor = self.webhook_db.cursor()
            cursor.execute("""
                SELECT id, url, secret_key FROM webhooks 
                WHERE active = 1 AND JSON_EXTRACT(events, '$') LIKE ?
            """, (f'%{event_type}%',))
            
            for webhook_id, url, secret_key in cursor.fetchall():
                try:
                    headers = {'Content-Type': 'application/json'}
                    
                    # Add signature if secret key provided
                    if secret_key:
                        signature = hmac.new(
                            secret_key.encode(),
                            json.dumps(payload).encode(),
                            hashlib.sha256
                        ).hexdigest()
                        headers['X-Signature-SHA256'] = f'sha256={signature}'
                    
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    
                    # Log delivery
                    cursor.execute("""
                        INSERT INTO webhook_deliveries 
                        (webhook_id, event_type, payload, status, response_code, delivered_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (webhook_id, event_type, json.dumps(payload),
                          'success' if response.status_code == 200 else 'failed',
                          response.status_code, datetime.now()))
                    
                except Exception as e:
                    # Log failed delivery
                    cursor.execute("""
                        INSERT INTO webhook_deliveries 
                        (webhook_id, event_type, payload, status, delivered_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (webhook_id, event_type, json.dumps(payload), 
                          'error', datetime.now()))
            
            self.webhook_db.commit()
            
        except Exception as e:
            print(f"Error delivering webhooks: {e}")
    
    def setup_github_integration(self, repo_owner: str, repo_name: str, access_token: str):
        """Setup GitHub integration for automated documentation updates."""
        self.integrations['github'] = {
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'access_token': access_token,
            'enabled': True
        }
        
        # Register webhook for documentation updates
        webhook_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
        self.register_webhook("GitHub Documentation", webhook_url, 
                            ['documentation_generated', 'schema_updated'])
    
    def setup_slack_integration(self, webhook_url: str, channel: str):
        """Setup Slack integration for notifications."""
        self.integrations['slack'] = {
            'webhook_url': webhook_url,
            'channel': channel,
            'enabled': True
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        status = {}
        for name, config in self.integrations.items():
            status[name] = {
                'enabled': config.get('enabled', False),
                'last_used': config.get('last_used'),
                'status': 'active' if config.get('enabled') else 'inactive'
            }
        return status


class AdvancedAnalyticsEngine:
    """
    Comprehensive analytics engine with trend analysis, usage patterns,
    performance metrics, and predictive insights.
    """
    
    def __init__(self, preferences_system: 'UserPreferencesSystem', project_manager: EnterpriseProjectManager):
        self.preferences = preferences_system
        self.project_manager = project_manager
        self.analytics_db = None
        self.collectors = {}
        self._initialize_analytics_database()
    
    def _initialize_analytics_database(self):
        """Initialize analytics tracking database."""
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path("analytics.db")
            self.analytics_db = sqlite3.connect(str(db_path), check_same_thread=False)
            
            cursor = self.analytics_db.cursor()
            
            # User activity tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type TEXT NOT NULL,
                    details JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_ms INTEGER,
                    user_id TEXT DEFAULT 'default'
                )
            """)
            
            # Database operation metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    database_name TEXT,
                    execution_time_ms INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Usage patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data JSON,
                    frequency INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.analytics_db.commit()
            print("[Phase 3] Analytics engine initialized")
            
        except Exception as e:
            print(f"[Phase 3] Error initializing analytics database: {e}")
    
    def track_activity(self, activity_type: str, details: Dict[str, Any] = None, 
                      duration_ms: int = None):
        """Track user activity."""
        try:
            import json
            
            cursor = self.analytics_db.cursor()
            cursor.execute("""
                INSERT INTO user_activities (activity_type, details, duration_ms)
                VALUES (?, ?, ?)
            """, (activity_type, json.dumps(details or {}), duration_ms))
            
            self.analytics_db.commit()
            
        except Exception as e:
            print(f"Error tracking activity: {e}")
    
    def track_operation(self, operation_type: str, database_name: str,
                       execution_time_ms: int, success: bool, error_message: str = None):
        """Track database operation metrics."""
        try:
            cursor = self.analytics_db.cursor()
            cursor.execute("""
                INSERT INTO operation_metrics 
                (operation_type, database_name, execution_time_ms, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (operation_type, database_name, execution_time_ms, success, error_message))
            
            self.analytics_db.commit()
            
        except Exception as e:
            print(f"Error tracking operation: {e}")
    
    def get_activity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get activity trends for the specified period."""
        try:
            cursor = self.analytics_db.cursor()
            cursor.execute("""
                SELECT activity_type, COUNT(*) as count,
                       DATE(timestamp) as date
                FROM user_activities 
                WHERE timestamp >= date('now', '-{} days')
                GROUP BY activity_type, DATE(timestamp)
                ORDER BY date DESC
            """.format(days))
            
            trends = {}
            for row in cursor.fetchall():
                activity_type, count, date = row
                if activity_type not in trends:
                    trends[activity_type] = {}
                trends[activity_type][date] = count
            
            return trends
            
        except Exception as e:
            print(f"Error getting activity trends: {e}")
            return {}
    
    def get_performance_metrics(self, operation_type: str = None) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            cursor = self.analytics_db.cursor()
            
            where_clause = ""
            params = []
            if operation_type:
                where_clause = "WHERE operation_type = ?"
                params.append(operation_type)
            
            cursor.execute(f"""
                SELECT 
                    AVG(execution_time_ms) as avg_time,
                    MIN(execution_time_ms) as min_time,
                    MAX(execution_time_ms) as max_time,
                    COUNT(*) as total_operations,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_operations,
                    COUNT(DISTINCT database_name) as unique_databases
                FROM operation_metrics
                {where_clause}
            """, params)
            
            row = cursor.fetchone()
            if row:
                return {
                    'average_execution_time': row[0] or 0,
                    'min_execution_time': row[1] or 0,
                    'max_execution_time': row[2] or 0,
                    'total_operations': row[3] or 0,
                    'successful_operations': row[4] or 0,
                    'success_rate': (row[4] / row[3] * 100) if row[3] > 0 else 0,
                    'unique_databases': row[5] or 0
                }
            
            return {}
            
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return {}
    
    def predict_usage_patterns(self) -> Dict[str, Any]:
        """Predict usage patterns based on historical data."""
        try:
            # Simple prediction based on recent trends
            cursor = self.analytics_db.cursor()
            cursor.execute("""
                SELECT activity_type, 
                       COUNT(*) as recent_count,
                       AVG(duration_ms) as avg_duration
                FROM user_activities 
                WHERE timestamp >= date('now', '-7 days')
                GROUP BY activity_type
                ORDER BY recent_count DESC
            """)
            
            predictions = {}
            for row in cursor.fetchall():
                activity_type, count, avg_duration = row
                predictions[activity_type] = {
                    'weekly_frequency': count,
                    'predicted_next_week': int(count * 1.1),  # Simple growth prediction
                    'average_duration': avg_duration or 0,
                    'trend': 'increasing' if count > 5 else 'stable'
                }
            
            return predictions
            
        except Exception as e:
            print(f"Error predicting usage patterns: {e}")
            return {}
    
    def generate_insights(self) -> List[str]:
        """Generate intelligent insights from analytics data."""
        insights = []
        
        try:
            # Performance insights
            metrics = self.get_performance_metrics()
            if metrics.get('success_rate', 100) < 90:
                insights.append(f"Operation success rate is {metrics['success_rate']:.1f}% - consider reviewing error patterns")
            
            if metrics.get('average_execution_time', 0) > 5000:
                insights.append("Average operation time is high - consider optimizing database queries")
            
            # Usage pattern insights
            trends = self.get_activity_trends(7)
            if trends:
                most_used = max(trends.keys(), 
                              key=lambda x: sum(trends[x].values()))
                insights.append(f"Most used feature: {most_used}")
            
            # Predictive insights
            predictions = self.predict_usage_patterns()
            growing_activities = [act for act, pred in predictions.items() 
                                if pred.get('trend') == 'increasing']
            if growing_activities:
                insights.append(f"Growing activity trends: {', '.join(growing_activities)}")
            
            if not insights:
                insights.append("System performance is optimal - all metrics within normal ranges")
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            insights.append("Analytics data collection in progress")
        
        return insights


class SmartSecurityAuditor:
    """
    Comprehensive security auditing system with vulnerability detection,
    compliance checking, and security recommendations.
    """
    
    def __init__(self, preferences_system: 'UserPreferencesSystem'):
        self.preferences = preferences_system
        self.audit_db = None
        self.security_rules = {}
        self.compliance_frameworks = {}
        self._initialize_security_database()
        self._load_security_rules()
    
    def _initialize_security_database(self):
        """Initialize security audit database."""
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path("security_audit.db")
            self.audit_db = sqlite3.connect(str(db_path), check_same_thread=False)
            
            cursor = self.audit_db.cursor()
            
            # Security findings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_name TEXT NOT NULL,
                    finding_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    recommendation TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at TIMESTAMP
                )
            """)
            
            # Compliance checks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    database_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details JSON,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.audit_db.commit()
            print("[Phase 3] Security auditor initialized")
            
        except Exception as e:
            print(f"[Phase 3] Error initializing security database: {e}")
    
    def _load_security_rules(self):
        """Load security audit rules."""
        self.security_rules = {
            'weak_passwords': {
                'severity': 'HIGH',
                'description': 'Weak or default passwords detected',
                'query': """
                    SELECT name FROM sys.sql_logins 
                    WHERE PWDCOMPARE('', password_hash) = 1
                    OR PWDCOMPARE('password', password_hash) = 1
                """
            },
            'excessive_permissions': {
                'severity': 'MEDIUM',
                'description': 'Users with excessive database permissions',
                'query': """
                    SELECT p.name, r.name as role 
                    FROM sys.database_principals p
                    JOIN sys.database_role_members rm ON p.principal_id = rm.member_principal_id
                    JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
                    WHERE r.name IN ('db_owner', 'db_securityadmin')
                """
            },
            'unencrypted_connections': {
                'severity': 'HIGH',
                'description': 'Unencrypted database connections detected',
                'query': "SELECT * FROM sys.dm_exec_connections WHERE encrypt_option = 'FALSE'"
            }
        }
        
        self.compliance_frameworks = {
            'GDPR': ['data_encryption', 'access_logging', 'data_retention'],
            'HIPAA': ['data_encryption', 'audit_trails', 'access_controls'],
            'SOX': ['data_integrity', 'change_tracking', 'access_controls'],
            'PCI_DSS': ['data_encryption', 'access_logging', 'network_security']
        }
    
    def run_security_audit(self, database_name: str, connection) -> List[Dict[str, Any]]:
        """Run comprehensive security audit."""
        findings = []
        
        try:
            cursor = connection.cursor()
            
            for rule_name, rule_config in self.security_rules.items():
                try:
                    cursor.execute(rule_config['query'])
                    results = cursor.fetchall()
                    
                    if results:
                        finding = {
                            'type': rule_name,
                            'severity': rule_config['severity'],
                            'title': rule_config['description'],
                            'description': f"Found {len(results)} instances",
                            'details': [str(row) for row in results],
                            'recommendation': self._get_recommendation(rule_name)
                        }
                        findings.append(finding)
                        
                        # Store in database
                        self._store_finding(database_name, finding)
                        
                except Exception as e:
                    print(f"Error running security rule {rule_name}: {e}")
            
        except Exception as e:
            print(f"Error during security audit: {e}")
        
        return findings
    
    def _store_finding(self, database_name: str, finding: Dict[str, Any]):
        """Store security finding in database."""
        try:
            cursor = self.audit_db.cursor()
            cursor.execute("""
                INSERT INTO security_findings 
                (database_name, finding_type, severity, title, description, recommendation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (database_name, finding['type'], finding['severity'],
                  finding['title'], finding['description'], finding['recommendation']))
            
            self.audit_db.commit()
            
        except Exception as e:
            print(f"Error storing finding: {e}")
    
    def _get_recommendation(self, rule_name: str) -> str:
        """Get security recommendation for a rule."""
        recommendations = {
            'weak_passwords': "Implement strong password policy and force password resets",
            'excessive_permissions': "Review and restrict user permissions following principle of least privilege",
            'unencrypted_connections': "Enable SSL/TLS encryption for all database connections"
        }
        return recommendations.get(rule_name, "Review security configuration")
    
    def check_compliance(self, database_name: str, framework: str, connection) -> Dict[str, Any]:
        """Check compliance with specific framework."""
        if framework not in self.compliance_frameworks:
            return {'error': f'Unknown compliance framework: {framework}'}
        
        results = {
            'framework': framework,
            'database': database_name,
            'checks': {},
            'compliance_score': 0,
            'total_checks': 0
        }
        
        try:
            required_checks = self.compliance_frameworks[framework]
            
            for check in required_checks:
                status = self._run_compliance_check(check, connection)
                results['checks'][check] = status
                results['total_checks'] += 1
                if status['passed']:
                    results['compliance_score'] += 1
            
            # Calculate percentage
            if results['total_checks'] > 0:
                results['compliance_percentage'] = (
                    results['compliance_score'] / results['total_checks'] * 100
                )
            
            # Store results
            self._store_compliance_check(database_name, framework, results)
            
        except Exception as e:
            print(f"Error checking compliance: {e}")
            results['error'] = str(e)
        
        return results
    
    def _run_compliance_check(self, check_type: str, connection) -> Dict[str, Any]:
        """Run specific compliance check."""
        try:
            cursor = connection.cursor()
            
            check_queries = {
                'data_encryption': "SELECT * FROM sys.dm_database_encryption_keys WHERE encryption_state = 3",
                'access_logging': "SELECT * FROM sys.fn_get_audit_file('*', NULL, NULL) WHERE action_id IN ('LX', 'LG')",
                'audit_trails': "SELECT COUNT(*) FROM sys.server_audits WHERE is_state_enabled = 1",
                'access_controls': "SELECT COUNT(*) FROM sys.database_permissions WHERE permission_name = 'CONTROL'",
                'data_retention': "SELECT * FROM sys.tables WHERE temporal_type = 2",
                'change_tracking': "SELECT * FROM sys.change_tracking_databases",
                'network_security': "SELECT * FROM sys.dm_exec_connections WHERE net_transport != 'Shared memory'"
            }
            
            if check_type in check_queries:
                cursor.execute(check_queries[check_type])
                results = cursor.fetchall()
                
                return {
                    'check_type': check_type,
                    'passed': len(results) > 0,
                    'details': f"Found {len(results)} compliant configurations",
                    'raw_results': len(results)
                }
            
            return {
                'check_type': check_type,
                'passed': False,
                'details': 'Check not implemented',
                'raw_results': 0
            }
            
        except Exception as e:
            return {
                'check_type': check_type,
                'passed': False,
                'details': f'Check failed: {str(e)}',
                'error': str(e)
            }
    
    def _store_compliance_check(self, database_name: str, framework: str, results: Dict[str, Any]):
        """Store compliance check results."""
        try:
            import json
            
            cursor = self.audit_db.cursor()
            
            for check_type, check_result in results['checks'].items():
                cursor.execute("""
                    INSERT INTO compliance_checks 
                    (framework, rule_id, database_name, status, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (framework, check_type, database_name,
                      'PASS' if check_result['passed'] else 'FAIL',
                      json.dumps(check_result)))
            
            self.audit_db.commit()
            
        except Exception as e:
            print(f"Error storing compliance check: {e}")
    
    def get_security_dashboard(self, database_name: str = None) -> Dict[str, Any]:
        """Get security dashboard data."""
        try:
            cursor = self.audit_db.cursor()
            
            where_clause = ""
            params = []
            if database_name:
                where_clause = "WHERE database_name = ?"
                params.append(database_name)
            
            # Get findings summary
            cursor.execute(f"""
                SELECT severity, COUNT(*) as count
                FROM security_findings
                {where_clause}
                AND resolved = 0
                GROUP BY severity
            """, params)
            
            findings_summary = {}
            total_findings = 0
            for row in cursor.fetchall():
                severity, count = row
                findings_summary[severity] = count
                total_findings += count
            
            # Get recent findings
            cursor.execute(f"""
                SELECT title, severity, detected_at
                FROM security_findings
                {where_clause}
                ORDER BY detected_at DESC
                LIMIT 5
            """, params)
            
            recent_findings = []
            for row in cursor.fetchall():
                recent_findings.append({
                    'title': row[0],
                    'severity': row[1],
                    'detected_at': row[2]
                })
            
            return {
                'total_findings': total_findings,
                'findings_by_severity': findings_summary,
                'recent_findings': recent_findings,
                'security_score': max(0, 100 - total_findings * 5)  # Simple scoring
            }
            
        except Exception as e:
            print(f"Error getting security dashboard: {e}")
            return {}
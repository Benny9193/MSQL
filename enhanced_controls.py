#!/usr/bin/env python3
"""
Enhanced UI Controls and Form Components
=======================================

Advanced form controls with validation, interactive elements, and modern styling
for the Azure SQL Database Documentation Generator.

Features:
- Enhanced form controls with validation
- Interactive data displays
- Help system with tooltips and guided tours
- Command palette functionality
- Advanced search and filtering
- Favorites and bookmarks management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union
import threading
import sqlite3
from pathlib import Path


class ValidationMixin:
    """Mixin for form validation functionality."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_server_name(server: str) -> bool:
        """Validate server name format."""
        if not server or len(server) < 3:
            return False
        # Basic server name validation
        pattern = r'^[a-zA-Z0-9.-]+$'
        return bool(re.match(pattern, server))
    
    @staticmethod
    def validate_database_name(db_name: str) -> bool:
        """Validate database name."""
        if not db_name or len(db_name) < 1:
            return False
        # SQL Server database name rules
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(char in db_name for char in invalid_chars)
    
    @staticmethod
    def validate_port(port: str) -> bool:
        """Validate port number."""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except ValueError:
            return False
    
    @staticmethod
    def validate_required(value: str) -> bool:
        """Validate required field."""
        return bool(value and value.strip())


class ToggleSwitch(tk.Frame):
    """Modern toggle switch widget."""
    
    def __init__(self, parent, text: str = "", variable: tk.BooleanVar = None, 
                 command: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.text = text
        self.variable = variable or tk.BooleanVar()
        self.command = command
        self.enabled = True
        
        self.create_widgets()
        
        # Bind variable trace
        self.variable.trace('w', self.on_variable_changed)
    
    def create_widgets(self):
        """Create toggle switch widgets."""
        # Text label
        if self.text:
            self.label = ttk.Label(self, text=self.text)
            self.label.pack(side='left', padx=(0, 10))
        
        # Switch frame
        self.switch_frame = tk.Frame(self, bg='#cccccc', width=50, height=25, relief='flat')
        self.switch_frame.pack(side='left')
        self.switch_frame.pack_propagate(False)
        
        # Switch handle
        self.handle = tk.Frame(self.switch_frame, bg='white', width=23, height=23)
        self.handle.place(x=1, y=1)
        
        # Bind clicks
        self.switch_frame.bind('<Button-1>', self.toggle)
        self.handle.bind('<Button-1>', self.toggle)
        if hasattr(self, 'label'):
            self.label.bind('<Button-1>', self.toggle)
        
        # Initial state
        self.update_appearance()
    
    def toggle(self, event=None):
        """Toggle the switch."""
        if self.enabled:
            self.variable.set(not self.variable.get())
    
    def on_variable_changed(self, *args):
        """Handle variable change."""
        self.update_appearance()
        if self.command:
            self.command()
    
    def update_appearance(self):
        """Update switch appearance based on state."""
        is_on = self.variable.get()
        
        if is_on:
            self.switch_frame.config(bg='#4CAF50')  # Green
            self.handle.place(x=26, y=1)
        else:
            self.switch_frame.config(bg='#cccccc')  # Gray
            self.handle.place(x=1, y=1)
    
    def enable(self):
        """Enable the toggle switch."""
        self.enabled = True
        self.switch_frame.config(cursor='hand2')
        self.handle.config(cursor='hand2')
        if hasattr(self, 'label'):
            self.label.config(cursor='hand2', foreground='black')
    
    def disable(self):
        """Disable the toggle switch."""
        self.enabled = False
        self.switch_frame.config(cursor='')
        self.handle.config(cursor='')
        if hasattr(self, 'label'):
            self.label.config(cursor='', foreground='gray')


class ValidatedEntry(tk.Frame, ValidationMixin):
    """Entry widget with built-in validation and visual feedback."""
    
    def __init__(self, parent, placeholder: str = "", validation_type: str = None,
                 custom_validator: Callable = None, required: bool = False, **kwargs):
        super().__init__(parent)
        
        self.placeholder = placeholder
        self.validation_type = validation_type
        self.custom_validator = custom_validator
        self.required = required
        self.is_valid = True
        
        # Extract entry-specific kwargs
        entry_kwargs = {k: v for k, v in kwargs.items() 
                       if k in ['textvariable', 'show', 'width', 'font']}
        
        self.create_widgets(entry_kwargs)
        
    def create_widgets(self, entry_kwargs):
        """Create entry and validation widgets."""
        # Main entry widget
        self.entry = tk.Entry(self, **entry_kwargs)
        self.entry.pack(fill='x')
        
        # Placeholder handling
        if self.placeholder:
            self.show_placeholder()
            self.entry.bind('<FocusIn>', self.on_focus_in)
            self.entry.bind('<FocusOut>', self.on_focus_out)
        
        # Validation binding
        self.entry.bind('<KeyRelease>', self.on_key_release)
        
        # Validation message label
        self.message_label = tk.Label(self, text="", fg='red', font=('Arial', 8))
        
        # Icon for validation state
        self.icon_label = tk.Label(self, text="", font=('Arial', 10))
        self.icon_label.pack(side='right', padx=(5, 0))
    
    def show_placeholder(self):
        """Show placeholder text."""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg='gray')
    
    def hide_placeholder(self):
        """Hide placeholder text."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg='black')
    
    def on_focus_in(self, event):
        """Handle focus in event."""
        self.hide_placeholder()
    
    def on_focus_out(self, event):
        """Handle focus out event."""
        if not self.entry.get():
            self.show_placeholder()
        self.validate()
    
    def on_key_release(self, event):
        """Handle key release for real-time validation."""
        if self.entry.get() != self.placeholder:
            self.validate()
    
    def validate(self) -> bool:
        """Validate entry content."""
        value = self.get()
        
        # Required field check
        if self.required and not value:
            self.set_invalid("This field is required")
            return False
        
        # Skip validation if empty and not required
        if not value and not self.required:
            self.set_valid()
            return True
        
        # Apply specific validation
        if self.validation_type:
            validator_map = {
                'email': self.validate_email,
                'server': self.validate_server_name,
                'database': self.validate_database_name,
                'port': self.validate_port,
                'required': self.validate_required
            }
            
            validator = validator_map.get(self.validation_type)
            if validator:
                if validator(value):
                    self.set_valid()
                    return True
                else:
                    self.set_invalid(f"Invalid {self.validation_type} format")
                    return False
        
        # Custom validation
        if self.custom_validator:
            try:
                result = self.custom_validator(value)
                if isinstance(result, tuple):
                    is_valid, message = result
                    if is_valid:
                        self.set_valid()
                        return True
                    else:
                        self.set_invalid(message)
                        return False
                elif result:
                    self.set_valid()
                    return True
                else:
                    self.set_invalid("Invalid input")
                    return False
            except Exception as e:
                self.set_invalid(f"Validation error: {str(e)}")
                return False
        
        self.set_valid()
        return True
    
    def set_valid(self):
        """Set entry to valid state."""
        self.is_valid = True
        self.entry.config(bg='white')
        self.icon_label.config(text="✓", fg='green')
        self.message_label.pack_forget()
    
    def set_invalid(self, message: str):
        """Set entry to invalid state."""
        self.is_valid = False
        self.entry.config(bg='#ffebee')
        self.icon_label.config(text="✗", fg='red')
        self.message_label.config(text=message)
        self.message_label.pack(fill='x', pady=(2, 0))
    
    def get(self) -> str:
        """Get entry value, excluding placeholder."""
        value = self.entry.get()
        return '' if value == self.placeholder else value
    
    def set(self, value: str):
        """Set entry value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.entry.config(fg='black')


class CollapsibleFrame(tk.Frame):
    """Collapsible frame for progressive disclosure."""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.expanded = tk.BooleanVar(value=False)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create collapsible frame widgets."""
        # Header frame
        self.header = tk.Frame(self, bg='#f0f0f0', relief='raised', bd=1)
        self.header.pack(fill='x')
        
        # Expand/collapse button
        self.toggle_btn = tk.Label(self.header, text="▶", font=('Arial', 10), 
                                 bg='#f0f0f0', cursor='hand2')
        self.toggle_btn.pack(side='left', padx=10, pady=5)
        
        # Title label
        self.title_label = tk.Label(self.header, text=self.title, font=('Arial', 10, 'bold'), 
                                  bg='#f0f0f0', cursor='hand2')
        self.title_label.pack(side='left', pady=5)
        
        # Content frame
        self.content_frame = tk.Frame(self, relief='solid', bd=1)
        
        # Bind clicks
        self.toggle_btn.bind('<Button-1>', self.toggle)
        self.title_label.bind('<Button-1>', self.toggle)
        self.header.bind('<Button-1>', self.toggle)
        
        # Bind variable change
        self.expanded.trace('w', self.update_display)
    
    def toggle(self, event=None):
        """Toggle the frame expansion."""
        self.expanded.set(not self.expanded.get())
    
    def update_display(self, *args):
        """Update the display based on expansion state."""
        if self.expanded.get():
            self.toggle_btn.config(text="▼")
            self.content_frame.pack(fill='both', expand=True, padx=1, pady=(0, 1))
        else:
            self.toggle_btn.config(text="▶")
            self.content_frame.pack_forget()
    
    def get_content_frame(self) -> tk.Frame:
        """Get the content frame for adding widgets."""
        return self.content_frame


class TooltipManager:
    """Manages tooltips for widgets."""
    
    def __init__(self):
        self.tooltips = {}
    
    def add_tooltip(self, widget, text: str, delay: int = 1000):
        """Add tooltip to a widget."""
        tooltip = ToolTip(widget, text, delay)
        self.tooltips[widget] = tooltip
        return tooltip
    
    def remove_tooltip(self, widget):
        """Remove tooltip from widget."""
        if widget in self.tooltips:
            self.tooltips[widget].destroy()
            del self.tooltips[widget]


class ToolTip:
    """Tooltip widget implementation."""
    
    def __init__(self, widget, text: str, delay: int = 1000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.timer = None
        
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<Motion>', self.on_motion)
    
    def on_enter(self, event):
        """Handle mouse enter event."""
        self.schedule_tooltip()
    
    def on_leave(self, event):
        """Handle mouse leave event."""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def on_motion(self, event):
        """Handle mouse motion event."""
        if self.tooltip_window:
            self.update_position(event)
    
    def schedule_tooltip(self):
        """Schedule tooltip to show after delay."""
        self.cancel_tooltip()
        self.timer = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_tooltip(self):
        """Cancel scheduled tooltip."""
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
    
    def show_tooltip(self):
        """Show the tooltip."""
        if self.tooltip_window:
            return
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        
        # Create tooltip content
        label = tk.Label(self.tooltip_window, text=self.text, 
                        bg='#ffffcc', fg='black', font=('Arial', 9),
                        relief='solid', bd=1, padx=5, pady=3)
        label.pack()
        
        # Position tooltip
        self.update_position()
    
    def update_position(self, event=None):
        """Update tooltip position."""
        if not self.tooltip_window:
            return
        
        # Get mouse position
        if event:
            x, y = event.x_root, event.y_root
        else:
            x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
            y = self.widget.winfo_rooty() - 30
        
        # Adjust position to keep tooltip on screen
        self.tooltip_window.update_idletasks()
        width = self.tooltip_window.winfo_reqwidth()
        height = self.tooltip_window.winfo_reqheight()
        
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = y - height - 40
        
        self.tooltip_window.wm_geometry(f"+{x+10}+{y+10}")
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def destroy(self):
        """Destroy the tooltip."""
        self.cancel_tooltip()
        self.hide_tooltip()


class CommandPalette:
    """Command palette for quick access to features."""
    
    def __init__(self, parent):
        self.parent = parent
        self.commands = {}
        self.palette_window = None
        
        # Register default commands
        self.register_default_commands()
        
        # Bind keyboard shortcut
        parent.bind('<Control-Shift-P>', self.show_palette)
    
    def register_command(self, name: str, description: str, callback: Callable, 
                        keywords: List[str] = None):
        """Register a command in the palette."""
        self.commands[name] = {
            'description': description,
            'callback': callback,
            'keywords': keywords or []
        }
    
    def register_default_commands(self):
        """Register default application commands."""
        default_commands = [
            ('Connect Database', 'Connect to a database', None, ['connect', 'database', 'db']),
            ('Generate Documentation', 'Generate database documentation', None, ['generate', 'docs', 'documentation']),
            ('Run Compliance Audit', 'Run security compliance audit', None, ['audit', 'compliance', 'security']),
            ('View Analytics', 'Open analytics dashboard', None, ['analytics', 'dashboard', 'reports']),
            ('Settings', 'Open application settings', None, ['settings', 'preferences', 'config']),
            ('Help', 'Show help documentation', None, ['help', 'docs', 'manual']),
            ('About', 'Show application information', None, ['about', 'info', 'version'])
        ]
        
        for name, desc, callback, keywords in default_commands:
            self.register_command(name, desc, callback, keywords)
    
    def show_palette(self, event=None):
        """Show the command palette."""
        if self.palette_window:
            return
        
        # Create palette window
        self.palette_window = tk.Toplevel(self.parent)
        self.palette_window.title("Command Palette")
        self.palette_window.geometry("600x400")
        self.palette_window.transient(self.parent)
        self.palette_window.grab_set()
        
        # Center window
        self.center_window()
        
        self.create_palette_widgets()
        
        # Focus on search entry
        self.search_entry.focus_set()
    
    def center_window(self):
        """Center the palette window."""
        self.palette_window.update_idletasks()
        x = (self.parent.winfo_rootx() + 
             (self.parent.winfo_width() // 2) - 300)
        y = (self.parent.winfo_rooty() + 
             (self.parent.winfo_height() // 2) - 200)
        self.palette_window.geometry(f"600x400+{x}+{y}")
    
    def create_palette_widgets(self):
        """Create palette UI widgets."""
        main_frame = tk.Frame(self.palette_window, bg='white')
        main_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='white', pady=10)
        search_frame.pack(fill='x', padx=10)
        
        search_label = tk.Label(search_frame, text="🔍", font=('Arial', 16), bg='white')
        search_label.pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                   font=('Arial', 12), relief='flat', bg='#f8f9fa')
        self.search_entry.pack(fill='x', ipady=8)
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        self.search_entry.bind('<Return>', self.execute_selected)
        self.search_entry.bind('<Down>', self.navigate_down)
        self.search_entry.bind('<Up>', self.navigate_up)
        self.search_entry.bind('<Escape>', self.hide_palette)
        
        # Results frame
        results_frame = tk.Frame(main_frame, bg='white')
        results_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Results listbox
        self.results_listbox = tk.Listbox(results_frame, font=('Arial', 11),
                                        relief='flat', bg='white', 
                                        selectbackground='#e3f2fd')
        self.results_listbox.pack(fill='both', expand=True)
        self.results_listbox.bind('<Return>', self.execute_selected)
        self.results_listbox.bind('<Double-Button-1>', self.execute_selected)
        
        # Populate initial results
        self.update_results()
    
    def on_search_changed(self, event=None):
        """Handle search text changes."""
        self.update_results()
    
    def update_results(self):
        """Update search results."""
        query = self.search_var.get().lower()
        
        # Clear current results
        self.results_listbox.delete(0, tk.END)
        
        # Filter commands
        matching_commands = []
        for name, cmd in self.commands.items():
            if self.matches_command(query, name, cmd):
                matching_commands.append((name, cmd))
        
        # Sort by relevance (exact matches first)
        matching_commands.sort(key=lambda x: self.calculate_relevance(query, x[0], x[1]), reverse=True)
        
        # Add to listbox
        for name, cmd in matching_commands[:20]:  # Limit to 20 results
            display_text = f"{name} - {cmd['description']}"
            self.results_listbox.insert(tk.END, display_text)
        
        # Select first item
        if self.results_listbox.size() > 0:
            self.results_listbox.selection_set(0)
    
    def matches_command(self, query: str, name: str, cmd: Dict) -> bool:
        """Check if command matches search query."""
        if not query:
            return True
        
        # Check name
        if query in name.lower():
            return True
        
        # Check description
        if query in cmd['description'].lower():
            return True
        
        # Check keywords
        for keyword in cmd.get('keywords', []):
            if query in keyword.lower():
                return True
        
        return False
    
    def calculate_relevance(self, query: str, name: str, cmd: Dict) -> int:
        """Calculate relevance score for sorting."""
        score = 0
        query_lower = query.lower()
        name_lower = name.lower()
        
        # Exact name match
        if query_lower == name_lower:
            score += 100
        # Name starts with query
        elif name_lower.startswith(query_lower):
            score += 50
        # Query in name
        elif query_lower in name_lower:
            score += 25
        
        # Keywords match
        for keyword in cmd.get('keywords', []):
            if query_lower == keyword.lower():
                score += 20
            elif keyword.lower().startswith(query_lower):
                score += 10
        
        return score
    
    def navigate_down(self, event=None):
        """Navigate down in results."""
        current = self.results_listbox.curselection()
        if current:
            next_index = (current[0] + 1) % self.results_listbox.size()
        else:
            next_index = 0
        
        if self.results_listbox.size() > 0:
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(next_index)
            self.results_listbox.see(next_index)
    
    def navigate_up(self, event=None):
        """Navigate up in results."""
        current = self.results_listbox.curselection()
        if current:
            prev_index = (current[0] - 1) % self.results_listbox.size()
        else:
            prev_index = self.results_listbox.size() - 1
        
        if self.results_listbox.size() > 0:
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(prev_index)
            self.results_listbox.see(prev_index)
    
    def execute_selected(self, event=None):
        """Execute the selected command."""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        # Get selected command name
        display_text = self.results_listbox.get(selection[0])
        command_name = display_text.split(' - ')[0]
        
        # Find and execute command
        if command_name in self.commands:
            callback = self.commands[command_name]['callback']
            if callback:
                try:
                    callback()
                except Exception as e:
                    messagebox.showerror("Command Error", f"Error executing command: {str(e)}")
        
        self.hide_palette()
    
    def hide_palette(self, event=None):
        """Hide the command palette."""
        if self.palette_window:
            self.palette_window.destroy()
            self.palette_window = None


class FavoritesManager:
    """Manages user favorites and bookmarks."""
    
    def __init__(self):
        self.db_path = Path("favorites.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize favorites database."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL, -- 'connection', 'database', 'object', 'report'
                    name TEXT NOT NULL,
                    data TEXT NOT NULL, -- JSON data
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recent_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def add_favorite(self, fav_type: str, name: str, data: Dict):
        """Add item to favorites."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO favorites (type, name, data)
                VALUES (?, ?, ?)
            """, (fav_type, name, json.dumps(data)))
            conn.commit()
        finally:
            conn.close()
    
    def remove_favorite(self, fav_type: str, name: str):
        """Remove item from favorites."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM favorites WHERE type = ? AND name = ?
            """, (fav_type, name))
            conn.commit()
        finally:
            conn.close()
    
    def get_favorites(self, fav_type: str = None) -> List[Dict]:
        """Get favorite items."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            if fav_type:
                cursor.execute("""
                    SELECT * FROM favorites WHERE type = ?
                    ORDER BY use_count DESC, last_used DESC
                """, (fav_type,))
            else:
                cursor.execute("""
                    SELECT * FROM favorites
                    ORDER BY use_count DESC, last_used DESC
                """)
            
            columns = [desc[0] for desc in cursor.description]
            favorites = []
            for row in cursor.fetchall():
                fav = dict(zip(columns, row))
                fav['data'] = json.loads(fav['data'])
                favorites.append(fav)
            return favorites
        finally:
            conn.close()
    
    def add_recent_item(self, item_type: str, name: str, data: Dict):
        """Add item to recent items."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Remove old entry if exists
            cursor.execute("""
                DELETE FROM recent_items WHERE type = ? AND name = ?
            """, (item_type, name))
            
            # Add new entry
            cursor.execute("""
                INSERT INTO recent_items (type, name, data)
                VALUES (?, ?, ?)
            """, (item_type, name, json.dumps(data)))
            
            # Keep only last 20 items per type
            cursor.execute("""
                DELETE FROM recent_items 
                WHERE type = ? AND id NOT IN (
                    SELECT id FROM recent_items 
                    WHERE type = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                )
            """, (item_type, item_type))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_recent_items(self, item_type: str = None, limit: int = 10) -> List[Dict]:
        """Get recent items."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            if item_type:
                cursor.execute("""
                    SELECT * FROM recent_items WHERE type = ?
                    ORDER BY timestamp DESC LIMIT ?
                """, (item_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM recent_items
                    ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            items = []
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                item['data'] = json.loads(item['data'])
                items.append(item)
            return items
        finally:
            conn.close()
    
    def update_favorite_usage(self, fav_type: str, name: str):
        """Update favorite usage statistics."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE favorites 
                SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE type = ? AND name = ?
            """, (fav_type, name))
            conn.commit()
        finally:
            conn.close()


class FavoritesWidget(tk.Frame):
    """Widget for displaying and managing favorites."""
    
    def __init__(self, parent, favorites_manager: FavoritesManager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.favorites_manager = favorites_manager
        self.current_type = None
        
        self.create_widgets()
        self.refresh_favorites()
    
    def create_widgets(self):
        """Create favorites widget components."""
        # Header
        header_frame = tk.Frame(self, bg='#f0f0f0', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="⭐ Favorites", 
                             font=('Arial', 12, 'bold'), bg='#f0f0f0')
        title_label.pack(side='left', padx=10, pady=10)
        
        # Filter dropdown
        self.type_var = tk.StringVar(value='All')
        type_combo = ttk.Combobox(header_frame, textvariable=self.type_var,
                                values=['All', 'Connections', 'Databases', 'Objects', 'Reports'],
                                width=12, state='readonly')
        type_combo.pack(side='right', padx=10, pady=10)
        type_combo.bind('<<ComboboxSelected>>', self.on_type_changed)
        
        # Favorites list
        list_frame = tk.Frame(self)
        list_frame.pack(fill='both', expand=True)
        
        # Scrollable listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.favorites_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                          font=('Arial', 10), bg='white')
        self.favorites_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.favorites_listbox.yview)
        
        # Context menu
        self.create_context_menu()
        
        # Bind events
        self.favorites_listbox.bind('<Double-Button-1>', self.on_double_click)
        self.favorites_listbox.bind('<Button-3>', self.show_context_menu)
    
    def create_context_menu(self):
        """Create context menu for favorites."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_favorite)
        self.context_menu.add_command(label="Remove from Favorites", command=self.remove_favorite)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Refresh", command=self.refresh_favorites)
    
    def on_type_changed(self, event=None):
        """Handle type filter change."""
        type_map = {
            'All': None,
            'Connections': 'connection',
            'Databases': 'database',
            'Objects': 'object',
            'Reports': 'report'
        }
        self.current_type = type_map.get(self.type_var.get())
        self.refresh_favorites()
    
    def refresh_favorites(self):
        """Refresh the favorites list."""
        self.favorites_listbox.delete(0, tk.END)
        
        favorites = self.favorites_manager.get_favorites(self.current_type)
        
        for fav in favorites:
            display_text = f"{fav['name']} ({fav['type']}) - Used {fav['use_count']} times"
            self.favorites_listbox.insert(tk.END, display_text)
    
    def on_double_click(self, event=None):
        """Handle double-click on favorite."""
        self.open_favorite()
    
    def open_favorite(self):
        """Open selected favorite."""
        selection = self.favorites_listbox.curselection()
        if not selection:
            return
        
        # Get favorite data and handle opening
        # This would be implemented based on favorite type
        messagebox.showinfo("Open Favorite", "Opening favorite functionality to be implemented")
    
    def remove_favorite(self):
        """Remove selected favorite."""
        selection = self.favorites_listbox.curselection()
        if not selection:
            return
        
        # Confirm removal
        result = messagebox.askyesno("Remove Favorite", "Remove this item from favorites?")
        if result:
            # Remove from database and refresh
            # Implementation would extract name and type from selection
            self.refresh_favorites()
    
    def show_context_menu(self, event):
        """Show context menu."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()


# Test the enhanced controls
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Enhanced Controls Test")
    root.geometry("800x600")
    
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # Test validated entries
    tk.Label(main_frame, text="Validated Entry Examples:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
    
    email_entry = ValidatedEntry(main_frame, placeholder="Enter email address", validation_type="email", required=True)
    email_entry.pack(fill='x', pady=5)
    
    server_entry = ValidatedEntry(main_frame, placeholder="Enter server name", validation_type="server")
    server_entry.pack(fill='x', pady=5)
    
    # Test toggle switch
    tk.Label(main_frame, text="Toggle Switch:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(20, 10))
    
    toggle_var = tk.BooleanVar()
    toggle = ToggleSwitch(main_frame, text="Enable notifications", variable=toggle_var)
    toggle.pack(anchor='w', pady=5)
    
    # Test collapsible frame
    tk.Label(main_frame, text="Collapsible Frame:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(20, 10))
    
    collapsible = CollapsibleFrame(main_frame, title="Advanced Settings")
    collapsible.pack(fill='x', pady=5)
    
    # Add content to collapsible frame
    content_frame = collapsible.get_content_frame()
    tk.Label(content_frame, text="This content can be collapsed/expanded").pack(padx=10, pady=10)
    tk.Button(content_frame, text="Sample Button").pack(padx=10, pady=5)
    
    # Test tooltips
    tooltip_manager = TooltipManager()
    
    test_button = tk.Button(main_frame, text="Button with Tooltip")
    test_button.pack(pady=20)
    tooltip_manager.add_tooltip(test_button, "This button has a helpful tooltip!")
    
    # Test command palette
    palette = CommandPalette(root)
    
    tk.Label(main_frame, text="Press Ctrl+Shift+P for Command Palette", 
             font=('Arial', 10), fg='blue').pack(pady=10)
    
    # Test favorites
    favorites_manager = FavoritesManager()
    
    # Add some sample favorites
    favorites_manager.add_favorite('connection', 'Production DB', {'server': 'prod-server', 'database': 'maindb'})
    favorites_manager.add_favorite('database', 'Analytics DB', {'server': 'analytics-server', 'database': 'analytics'})
    
    tk.Label(main_frame, text="Favorites Widget:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(20, 10))
    
    favorites_widget = FavoritesWidget(main_frame, favorites_manager, height=150)
    favorites_widget.pack(fill='x', pady=5)
    
    root.mainloop()
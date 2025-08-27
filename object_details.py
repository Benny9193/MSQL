#!/usr/bin/env python3
"""
Object Details Manager
=====================

Provides comprehensive object detail views with expandable information for
database objects including tables, views, procedures, functions, and relationships.

Features:
- Rich object information display
- Expandable detail sections
- SQL definition viewing
- Relationship visualization
- Column analysis with constraints
- Index information
- Permission details
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Any, Optional
import json


class ObjectDetailsManager:
    """Manages comprehensive object detail displays."""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.current_object = None
        self.current_schema_data = None
        
    def show_object_details(self, obj_data: Dict[str, Any], schema_data: Dict[str, Any] = None):
        """Show comprehensive object details in a new window."""
        self.current_object = obj_data
        self.current_schema_data = schema_data
        
        # Create details window
        self.details_window = tk.Toplevel(self.parent)
        self.details_window.title(f"Object Details: {obj_data.get('name', 'Unknown')}")
        self.details_window.geometry("1000x700")
        self.details_window.minsize(800, 600)
        
        # Configure window
        self.setup_details_window()
        
    def setup_details_window(self):
        """Setup the details window layout."""
        # Main container with paned window for resizable panels
        main_paned = ttk.PanedWindow(self.details_window, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Object tree and quick info
        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Detailed information
        right_frame = ttk.Frame(main_paned, width=700)
        main_paned.add(right_frame, weight=2)
        
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_left_panel(self, parent):
        """Create the left panel with object overview and navigation."""
        # Object overview
        overview_frame = ttk.LabelFrame(parent, text="Object Overview", padding="10")
        overview_frame.pack(fill="x", padx=5, pady=5)
        
        obj = self.current_object
        
        # Basic info grid
        info_grid = ttk.Frame(overview_frame)
        info_grid.pack(fill="x")
        
        # Object name
        ttk.Label(info_grid, text="Name:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(info_grid, text=obj.get('name', 'Unknown')).grid(row=0, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Object type
        ttk.Label(info_grid, text="Type:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", pady=2)
        obj_type = obj.get('type', self._infer_object_type(obj))
        ttk.Label(info_grid, text=obj_type).grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Schema
        ttk.Label(info_grid, text="Schema:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(info_grid, text=obj.get('schema', 'dbo')).grid(row=2, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Row count (if applicable)
        if 'row_count' in obj:
            ttk.Label(info_grid, text="Rows:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky="w", pady=2)
            ttk.Label(info_grid, text=f"{obj['row_count']:,}").grid(row=3, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding="10")
        actions_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Export Definition", command=self.export_definition).pack(fill="x", pady=2)
        ttk.Button(actions_frame, text="Generate Script", command=self.generate_script).pack(fill="x", pady=2)
        ttk.Button(actions_frame, text="View Relationships", command=self.view_relationships).pack(fill="x", pady=2)
        
        # Object navigation tree
        nav_frame = ttk.LabelFrame(parent, text="Object Structure", padding="10")
        nav_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.nav_tree = ttk.Treeview(nav_frame, show="tree")
        nav_scroll = ttk.Scrollbar(nav_frame, orient="vertical", command=self.nav_tree.yview)
        self.nav_tree.configure(yscrollcommand=nav_scroll.set)
        
        self.nav_tree.pack(side="left", fill="both", expand=True)
        nav_scroll.pack(side="right", fill="y")
        
        # Bind selection event
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_selection)
        
        # Populate navigation tree
        self.populate_nav_tree()
        
    def create_right_panel(self, parent):
        """Create the right panel with detailed information."""
        # Create notebook for different detail sections
        self.details_notebook = ttk.Notebook(parent)
        self.details_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Basic Information tab
        self.create_basic_info_tab()
        
        # Columns tab (for tables/views)
        if self._has_columns():
            self.create_columns_tab()
        
        # Definition tab (for procedures/functions/views)
        if self._has_definition():
            self.create_definition_tab()
        
        # Constraints tab (for tables)
        if self._has_constraints():
            self.create_constraints_tab()
        
        # Indexes tab (for tables)
        if self._has_indexes():
            self.create_indexes_tab()
        
        # Relationships tab
        if self.current_schema_data:
            self.create_relationships_tab()
        
        # Properties tab
        self.create_properties_tab()
        
    def create_basic_info_tab(self):
        """Create the basic information tab."""
        info_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(info_frame, text="Basic Information")
        
        # Scrollable text widget
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=20, font=("Consolas", 10))
        info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Build information content
        obj = self.current_object
        content = self._build_basic_info_content(obj)
        
        info_text.insert(1.0, content)
        info_text.config(state="disabled")
        
        self.basic_info_text = info_text
        
    def create_columns_tab(self):
        """Create the columns information tab."""
        columns_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(columns_frame, text="Columns")
        
        # Columns treeview
        columns_tree = ttk.Treeview(
            columns_frame,
            columns=("data_type", "nullable", "default", "constraints", "description"),
            show="tree headings"
        )
        
        # Configure columns
        columns_tree.heading("#0", text="Column Name")
        columns_tree.heading("data_type", text="Data Type")
        columns_tree.heading("nullable", text="Nullable")
        columns_tree.heading("default", text="Default")
        columns_tree.heading("constraints", text="Constraints")
        columns_tree.heading("description", text="Description")
        
        columns_tree.column("#0", width=150)
        columns_tree.column("data_type", width=100)
        columns_tree.column("nullable", width=80)
        columns_tree.column("default", width=100)
        columns_tree.column("constraints", width=120)
        columns_tree.column("description", width=200)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(columns_frame, orient="vertical", command=columns_tree.yview)
        h_scroll = ttk.Scrollbar(columns_frame, orient="horizontal", command=columns_tree.xview)
        columns_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack widgets
        columns_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.rowconfigure(0, weight=1)
        
        # Populate columns
        self._populate_columns_tree(columns_tree)
        
        self.columns_tree = columns_tree
        
    def create_definition_tab(self):
        """Create the definition/SQL tab."""
        def_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(def_frame, text="Definition")
        
        # Definition text with syntax highlighting
        def_text = scrolledtext.ScrolledText(
            def_frame, 
            wrap=tk.NONE, 
            height=20, 
            font=("Consolas", 10),
            bg="#2b2b2b", 
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        def_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get definition
        definition = self.current_object.get('definition', '')
        if definition:
            def_text.insert(1.0, definition)
            self._apply_sql_syntax_highlighting(def_text)
        else:
            def_text.insert(1.0, "-- No definition available")
        
        def_text.config(state="disabled")
        
        self.definition_text = def_text
        
    def create_constraints_tab(self):
        """Create the constraints tab."""
        constraints_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(constraints_frame, text="Constraints")
        
        # Constraints treeview
        constraints_tree = ttk.Treeview(
            constraints_frame,
            columns=("type", "columns", "reference", "description"),
            show="tree headings"
        )
        
        # Configure columns
        constraints_tree.heading("#0", text="Constraint Name")
        constraints_tree.heading("type", text="Type")
        constraints_tree.heading("columns", text="Columns")
        constraints_tree.heading("reference", text="References")
        constraints_tree.heading("description", text="Description")
        
        # Pack and populate
        constraints_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._populate_constraints_tree(constraints_tree)
        
    def create_indexes_tab(self):
        """Create the indexes tab."""
        indexes_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(indexes_frame, text="Indexes")
        
        # Indexes treeview
        indexes_tree = ttk.Treeview(
            indexes_frame,
            columns=("type", "unique", "columns", "includes"),
            show="tree headings"
        )
        
        # Configure columns
        indexes_tree.heading("#0", text="Index Name")
        indexes_tree.heading("type", text="Type")
        indexes_tree.heading("unique", text="Unique")
        indexes_tree.heading("columns", text="Key Columns")
        indexes_tree.heading("includes", text="Included Columns")
        
        # Pack and populate
        indexes_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._populate_indexes_tree(indexes_tree)
        
    def create_relationships_tab(self):
        """Create the relationships tab."""
        rel_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(rel_frame, text="Relationships")
        
        # Create paned window for incoming/outgoing relationships
        rel_paned = ttk.PanedWindow(rel_frame, orient="vertical")
        rel_paned.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Incoming relationships (foreign keys pointing to this table)
        incoming_frame = ttk.LabelFrame(rel_paned, text="Incoming References", padding="10")
        rel_paned.add(incoming_frame, weight=1)
        
        incoming_tree = ttk.Treeview(
            incoming_frame,
            columns=("table", "column", "fk_column"),
            show="tree headings"
        )
        incoming_tree.heading("#0", text="Constraint")
        incoming_tree.heading("table", text="From Table")
        incoming_tree.heading("column", text="From Column")
        incoming_tree.heading("fk_column", text="To Column")
        incoming_tree.pack(fill="both", expand=True)
        
        # Outgoing relationships (foreign keys from this table)
        outgoing_frame = ttk.LabelFrame(rel_paned, text="Outgoing References", padding="10")
        rel_paned.add(outgoing_frame, weight=1)
        
        outgoing_tree = ttk.Treeview(
            outgoing_frame,
            columns=("table", "column", "ref_column"),
            show="tree headings"
        )
        outgoing_tree.heading("#0", text="Constraint")
        outgoing_tree.heading("table", text="To Table")
        outgoing_tree.heading("column", text="From Column")
        outgoing_tree.heading("ref_column", text="To Column")
        outgoing_tree.pack(fill="both", expand=True)
        
        # Populate relationships
        self._populate_relationships_trees(incoming_tree, outgoing_tree)
        
    def create_properties_tab(self):
        """Create the properties tab with extended metadata."""
        props_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(props_frame, text="Properties")
        
        # Properties text
        props_text = scrolledtext.ScrolledText(props_frame, wrap=tk.WORD, height=20, font=("Consolas", 10))
        props_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Build properties content
        content = self._build_properties_content()
        props_text.insert(1.0, content)
        props_text.config(state="disabled")
        
    def create_status_bar(self):
        """Create status bar at bottom of window."""
        status_frame = ttk.Frame(self.details_window, relief="sunken")
        status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(status_frame, text="Ready", padding="5")
        self.status_label.pack(side="left")
        
    # Helper methods
    
    def _infer_object_type(self, obj):
        """Infer object type from its structure."""
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
    
    def _has_columns(self):
        """Check if object has columns."""
        return 'columns' in self.current_object and self.current_object['columns']
    
    def _has_definition(self):
        """Check if object has definition."""
        return 'definition' in self.current_object and self.current_object['definition']
    
    def _has_constraints(self):
        """Check if object has constraints."""
        return 'constraints' in self.current_object or 'foreign_keys' in self.current_object
    
    def _has_indexes(self):
        """Check if object has indexes."""
        return 'indexes' in self.current_object and self.current_object['indexes']
    
    def _build_basic_info_content(self, obj):
        """Build basic information content."""
        lines = []
        
        lines.append("OBJECT INFORMATION")
        lines.append("=" * 50)
        lines.append("")
        
        lines.append(f"Name: {obj.get('name', 'Unknown')}")
        lines.append(f"Schema: {obj.get('schema', 'dbo')}")
        lines.append(f"Type: {obj.get('type', self._infer_object_type(obj))}")
        
        if 'created_date' in obj:
            lines.append(f"Created: {obj['created_date']}")
        
        if 'modified_date' in obj:
            lines.append(f"Modified: {obj['modified_date']}")
        
        if 'row_count' in obj:
            lines.append(f"Row Count: {obj['row_count']:,}")
        
        lines.append("")
        
        if obj.get('description'):
            lines.append("DESCRIPTION")
            lines.append("-" * 20)
            lines.append(obj['description'])
            lines.append("")
        
        if 'columns' in obj:
            lines.append(f"STRUCTURE")
            lines.append("-" * 20)
            lines.append(f"Columns: {len(obj['columns'])}")
            
        return "\n".join(lines)
    
    def _populate_columns_tree(self, tree):
        """Populate the columns tree view."""
        obj = self.current_object
        if 'columns' not in obj:
            return
            
        for col in obj['columns']:
            constraints = []
            if col.get('is_primary_key'):
                constraints.append("PK")
            if col.get('is_foreign_key'):
                constraints.append("FK")
            if col.get('is_identity'):
                constraints.append("IDENTITY")
                
            tree.insert("", "end", 
                       text=col.get('name', 'Unknown'),
                       values=(
                           col.get('data_type', 'Unknown'),
                           "NULL" if col.get('is_nullable', True) else "NOT NULL",
                           col.get('default_value', ''),
                           ", ".join(constraints),
                           col.get('description', '')
                       ))
    
    def _populate_constraints_tree(self, tree):
        """Populate constraints tree."""
        # This would be implemented with actual constraint data
        pass
    
    def _populate_indexes_tree(self, tree):
        """Populate indexes tree."""
        obj = self.current_object
        if 'indexes' not in obj:
            return
            
        for idx in obj['indexes']:
            tree.insert("", "end",
                       text=idx.get('name', 'Unknown'),
                       values=(
                           idx.get('type', 'Unknown'),
                           "Yes" if idx.get('is_unique', False) else "No",
                           ", ".join(idx.get('columns', [])),
                           ", ".join(idx.get('included_columns', []))
                       ))
    
    def _populate_relationships_trees(self, incoming_tree, outgoing_tree):
        """Populate relationship trees."""
        # This would analyze schema data for relationships
        pass
    
    def _build_properties_content(self):
        """Build extended properties content."""
        obj = self.current_object
        lines = []
        
        lines.append("EXTENDED PROPERTIES")
        lines.append("=" * 50)
        lines.append("")
        
        # Add all object properties
        for key, value in obj.items():
            if key not in ['columns', 'definition', 'constraints', 'indexes']:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(lines)
    
    def _apply_sql_syntax_highlighting(self, text_widget):
        """Apply basic SQL syntax highlighting."""
        # This is a simplified version - could be enhanced
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP',
            'TABLE', 'VIEW', 'PROCEDURE', 'FUNCTION', 'INDEX', 'DATABASE', 'SCHEMA',
            'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'NOT', 'NULL', 'UNIQUE', 'DEFAULT',
            'AND', 'OR', 'IN', 'EXISTS', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON',
            'GROUP', 'BY', 'ORDER', 'HAVING', 'DISTINCT', 'TOP', 'AS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        ]
        
        # Configure tags
        text_widget.tag_configure("keyword", foreground="#569cd6")
        text_widget.tag_configure("string", foreground="#ce9178")
        text_widget.tag_configure("comment", foreground="#6a9955")
        
        content = text_widget.get(1.0, tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Highlight keywords
            for keyword in sql_keywords:
                start = 0
                while True:
                    pos = line.upper().find(keyword, start)
                    if pos == -1:
                        break
                    
                    # Check if it's a whole word
                    if (pos == 0 or not line[pos-1].isalnum()) and \
                       (pos + len(keyword) >= len(line) or not line[pos + len(keyword)].isalnum()):
                        start_idx = f"{line_num}.{pos}"
                        end_idx = f"{line_num}.{pos + len(keyword)}"
                        text_widget.tag_add("keyword", start_idx, end_idx)
                    
                    start = pos + 1
    
    def populate_nav_tree(self):
        """Populate the navigation tree."""
        obj = self.current_object
        
        # Main object node
        main_node = self.nav_tree.insert("", "end", text=f"{obj.get('name', 'Unknown')} (Main)")
        
        # Add columns if available
        if 'columns' in obj and obj['columns']:
            columns_node = self.nav_tree.insert(main_node, "end", text=f"Columns ({len(obj['columns'])})")
            for col in obj['columns'][:10]:  # Limit to first 10 for navigation
                self.nav_tree.insert(columns_node, "end", text=col.get('name', 'Unknown'))
            if len(obj['columns']) > 10:
                self.nav_tree.insert(columns_node, "end", text="... and more")
        
        # Add indexes if available
        if 'indexes' in obj and obj['indexes']:
            indexes_node = self.nav_tree.insert(main_node, "end", text=f"Indexes ({len(obj['indexes'])})")
            for idx in obj['indexes']:
                self.nav_tree.insert(indexes_node, "end", text=idx.get('name', 'Unknown'))
        
        # Expand main node
        self.nav_tree.item(main_node, open=True)
    
    def on_nav_selection(self, event):
        """Handle navigation tree selection."""
        selection = self.nav_tree.selection()
        if selection:
            item = self.nav_tree.item(selection[0])
            self.status_label.config(text=f"Selected: {item['text']}")
    
    # Action methods
    
    def export_definition(self):
        """Export object definition."""
        from tkinter import filedialog
        
        obj = self.current_object
        if not obj.get('definition'):
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
                    f.write(obj['definition'])
                messagebox.showinfo("Export Complete", f"Definition exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export definition: {str(e)}")
    
    def generate_script(self):
        """Generate CREATE script for object."""
        messagebox.showinfo("Feature Coming Soon", "Script generation will be implemented in the next phase.")
    
    def view_relationships(self):
        """View object relationships in a diagram."""
        if not self.current_schema_data:
            messagebox.showwarning("No Schema Data", "Schema data is required to view relationships.")
            return
        
        messagebox.showinfo("Feature Coming Soon", "Relationship diagram will be implemented using the dependency visualizer.")
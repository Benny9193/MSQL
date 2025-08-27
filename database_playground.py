#!/usr/bin/env python3
"""
Interactive Database Playground
==============================

A safe, interactive environment for exploring database schemas, building queries,
and learning database concepts through hands-on experimentation.

Features:
- Visual query builder with drag-and-drop interface
- Safe sandbox environment with query validation
- Real-time results preview with performance metrics
- Interactive tutorials and guided learning
- Schema exploration with live data samples
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import logging
import threading
import time
import sqlite3
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from db_connection import AzureSQLConnection
from schema_analyzer import SchemaAnalyzer
from ui_framework import ThemeManager, CardComponent

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries supported in the playground."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE_TABLE = "CREATE_TABLE"
    DROP_TABLE = "DROP_TABLE"

@dataclass
class QueryElement:
    """Represents a draggable query building element."""
    element_type: str  # 'table', 'column', 'function', 'operator'
    name: str
    schema: Optional[str] = None
    data_type: Optional[str] = None
    description: Optional[str] = None
    sample_values: Optional[List[str]] = None

@dataclass
class QueryResult:
    """Results from query execution."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    rows_affected: int = 0
    columns: Optional[List[str]] = None

class SafeSandbox:
    """Provides a safe environment for query execution."""
    
    def __init__(self, db_connection: AzureSQLConnection):
        self.db_connection = db_connection
        self.sandbox_db_path = None
        self.allowed_operations = {
            QueryType.SELECT,
            QueryType.CREATE_TABLE,
            QueryType.INSERT,
            QueryType.UPDATE,
            QueryType.DELETE
        }
        self.forbidden_keywords = [
            'DROP DATABASE', 'ALTER DATABASE', 'SHUTDOWN', 'RESTORE',
            'BACKUP', 'DBCC', 'EXEC', 'EXECUTE', 'SP_', 'XP_'
        ]
        self.setup_sandbox()
    
    def setup_sandbox(self):
        """Create a temporary SQLite database for safe experimentation."""
        try:
            # Create temporary database file
            temp_dir = tempfile.mkdtemp()
            self.sandbox_db_path = os.path.join(temp_dir, 'playground_sandbox.db')
            
            # Initialize sandbox with sample schema
            self._create_sample_schema()
            logger.info(f"Sandbox database created at: {self.sandbox_db_path}")
            
        except Exception as e:
            logger.error(f"Failed to setup sandbox: {e}")
            raise
    
    def _create_sample_schema(self):
        """Create sample tables with data for playground experimentation."""
        conn = sqlite3.connect(self.sandbox_db_path)
        cursor = conn.cursor()
        
        try:
            # Create sample tables
            cursor.execute('''
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT,
                    salary REAL,
                    hire_date DATE,
                    email TEXT UNIQUE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    manager_id INTEGER,
                    budget REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    department_id INTEGER,
                    start_date DATE,
                    end_date DATE,
                    status TEXT,
                    FOREIGN KEY (department_id) REFERENCES departments(id)
                )
            ''')
            
            # Insert sample data
            employees_data = [
                (1, 'John Smith', 'Engineering', 75000, '2022-01-15', 'john.smith@company.com'),
                (2, 'Sarah Johnson', 'Marketing', 65000, '2021-03-20', 'sarah.johnson@company.com'),
                (3, 'Mike Davis', 'Engineering', 80000, '2020-11-10', 'mike.davis@company.com'),
                (4, 'Lisa Brown', 'HR', 55000, '2023-02-01', 'lisa.brown@company.com'),
                (5, 'Tom Wilson', 'Sales', 70000, '2021-09-15', 'tom.wilson@company.com')
            ]
            
            cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)', employees_data)
            
            departments_data = [
                (1, 'Engineering', 3, 500000),
                (2, 'Marketing', 2, 200000),
                (3, 'HR', 4, 150000),
                (4, 'Sales', 5, 300000)
            ]
            
            cursor.executemany('INSERT INTO departments VALUES (?, ?, ?, ?)', departments_data)
            
            projects_data = [
                (1, 'Website Redesign', 2, '2024-01-01', '2024-06-30', 'In Progress'),
                (2, 'Database Migration', 1, '2024-02-15', '2024-05-15', 'Planning'),
                (3, 'Employee Portal', 1, '2023-12-01', '2024-03-31', 'In Progress'),
                (4, 'Sales Analytics', 4, '2024-01-15', '2024-04-15', 'Planning')
            ]
            
            cursor.executemany('INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?)', projects_data)
            
            conn.commit()
            logger.info("Sample schema and data created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create sample schema: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate query for safety before execution."""
        query_upper = query.upper().strip()
        
        # Check for forbidden keywords
        for forbidden in self.forbidden_keywords:
            if forbidden in query_upper:
                return False, f"Forbidden operation: {forbidden}"
        
        # Basic SQL injection checks
        dangerous_patterns = [
            ';--', '/*', '*/', 'UNION SELECT', 'OR 1=1', 'DROP TABLE'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                return False, f"Potentially dangerous pattern detected: {pattern}"
        
        return True, None
    
    def execute_query(self, query: str) -> QueryResult:
        """Execute query safely in the sandbox environment."""
        start_time = time.time()
        
        # Validate query first
        is_valid, error_msg = self.validate_query(query)
        if not is_valid:
            return QueryResult(
                success=False,
                error_message=f"Query validation failed: {error_msg}"
            )
        
        try:
            conn = sqlite3.connect(self.sandbox_db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            cursor.execute(query)
            
            execution_time = time.time() - start_time
            
            if query.strip().upper().startswith('SELECT'):
                # Query returns data
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                return QueryResult(
                    success=True,
                    data=data,
                    execution_time=execution_time,
                    rows_affected=len(data),
                    columns=columns
                )
            else:
                # Query modifies data
                conn.commit()
                return QueryResult(
                    success=True,
                    execution_time=execution_time,
                    rows_affected=cursor.rowcount
                )
                
        except Exception as e:
            return QueryResult(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_schema_elements(self) -> List[QueryElement]:
        """Get schema elements available for query building."""
        elements = []
        
        try:
            conn = sqlite3.connect(self.sandbox_db_path)
            cursor = conn.cursor()
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                elements.append(QueryElement(
                    element_type='table',
                    name=table_name,
                    description=f"Table: {table_name}"
                ))
                
                # Get columns for each table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                for column in columns:
                    col_name, col_type = column[1], column[2]
                    
                    # Get sample values
                    try:
                        cursor.execute(f"SELECT DISTINCT {col_name} FROM {table_name} LIMIT 5")
                        sample_values = [str(row[0]) for row in cursor.fetchall()]
                    except:
                        sample_values = []
                    
                    elements.append(QueryElement(
                        element_type='column',
                        name=col_name,
                        schema=table_name,
                        data_type=col_type,
                        description=f"Column: {table_name}.{col_name} ({col_type})",
                        sample_values=sample_values
                    ))
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to get schema elements: {e}")
        
        return elements
    
    def cleanup(self):
        """Clean up sandbox resources."""
        if self.sandbox_db_path and os.path.exists(self.sandbox_db_path):
            try:
                os.remove(self.sandbox_db_path)
                logger.info("Sandbox database cleaned up")
            except Exception as e:
                logger.error(f"Failed to cleanup sandbox: {e}")

class QueryBuilder:
    """Visual query builder with drag-and-drop interface."""
    
    def __init__(self, parent: tk.Widget, theme_manager: ThemeManager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.query_elements = []
        self.current_query = ""
        self.query_change_callbacks = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the query builder interface."""
        # Create main container
        self.container = ttk.Frame(self.parent)
        self.container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Schema elements panel
        self.setup_schema_panel()
        
        # Query construction area
        self.setup_query_area()
        
        # Generated SQL preview
        self.setup_sql_preview()
    
    def setup_schema_panel(self):
        """Setup the schema elements panel."""
        schema_frame = ttk.LabelFrame(self.container, text="Schema Elements", padding=10)
        schema_frame.pack(side='left', fill='y', padx=(0, 5))
        
        # Search box
        ttk.Label(schema_frame, text="Search:").pack(anchor='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(schema_frame, textvariable=self.search_var)
        search_entry.pack(fill='x', pady=(0, 10))
        self.search_var.trace('w', self.filter_elements)
        
        # Elements tree
        self.elements_tree = ttk.Treeview(schema_frame, height=15)
        self.elements_tree.heading('#0', text='Available Elements')
        self.elements_tree.pack(fill='both', expand=True)
        
        # Bind double-click to add element
        self.elements_tree.bind('<Double-1>', self.add_element_to_query)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(schema_frame, orient='vertical', command=self.elements_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.elements_tree.configure(yscrollcommand=scrollbar.set)
    
    def setup_query_area(self):
        """Setup the visual query construction area."""
        query_frame = ttk.LabelFrame(self.container, text="Query Builder", padding=10)
        query_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Query type selection
        type_frame = ttk.Frame(query_frame)
        type_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(type_frame, text="Query Type:").pack(side='left')
        self.query_type_var = tk.StringVar(value="SELECT")
        query_type_combo = ttk.Combobox(type_frame, textvariable=self.query_type_var, 
                                       values=["SELECT", "INSERT", "UPDATE", "DELETE"], 
                                       state="readonly", width=15)
        query_type_combo.pack(side='left', padx=(5, 0))
        query_type_combo.bind('<<ComboboxSelected>>', self.on_query_type_change)
        
        # Clear button
        ttk.Button(type_frame, text="Clear", command=self.clear_query).pack(side='right')
        
        # Visual query elements area
        self.query_canvas = tk.Canvas(query_frame, bg='white', height=200)
        self.query_canvas.pack(fill='both', expand=True, pady=(10, 0))
        
        # Enable drag and drop on canvas
        self.query_canvas.bind('<Button-1>', self.on_canvas_click)
        self.query_canvas.bind('<B1-Motion>', self.on_canvas_drag)
    
    def setup_sql_preview(self):
        """Setup the generated SQL preview area."""
        sql_frame = ttk.LabelFrame(self.container, text="Generated SQL", padding=10)
        sql_frame.pack(side='right', fill='both', padx=(5, 0))
        
        self.sql_text = scrolledtext.ScrolledText(sql_frame, width=40, height=10, 
                                                 state='disabled', wrap='word')
        self.sql_text.pack(fill='both', expand=True)
        
        # Execute button
        ttk.Button(sql_frame, text="Execute Query", 
                  command=self.execute_current_query).pack(pady=(10, 0), fill='x')
    
    def load_schema_elements(self, elements: List[QueryElement]):
        """Load schema elements into the tree view."""
        self.query_elements = elements
        self.refresh_elements_tree()
    
    def refresh_elements_tree(self):
        """Refresh the elements tree view."""
        # Clear existing items
        for item in self.elements_tree.get_children():
            self.elements_tree.delete(item)
        
        # Group elements by type
        tables = {}
        functions = []
        
        search_term = self.search_var.get().lower()
        
        for element in self.query_elements:
            if search_term and search_term not in element.name.lower():
                continue
                
            if element.element_type == 'table':
                tables[element.name] = self.elements_tree.insert(
                    '', 'end', text=f"📊 {element.name}", 
                    values=(element.element_type,))
            elif element.element_type == 'column' and element.schema:
                if element.schema in tables:
                    self.elements_tree.insert(
                        tables[element.schema], 'end',
                        text=f"  📋 {element.name} ({element.data_type})",
                        values=(element.element_type, element.schema, element.name))
        
        # Expand all tables
        for table_id in tables.values():
            self.elements_tree.item(table_id, open=True)
    
    def filter_elements(self, *args):
        """Filter elements based on search term."""
        self.refresh_elements_tree()
    
    def add_element_to_query(self, event):
        """Add selected element to query."""
        selection = self.elements_tree.selection()
        if not selection:
            return
        
        item = self.elements_tree.item(selection[0])
        values = item['values']
        
        if values and len(values) >= 2:
            element_type = values[0]
            if element_type == 'column' and len(values) >= 3:
                schema_name = values[1]
                column_name = values[2]
                self.add_column_to_query(schema_name, column_name)
    
    def add_column_to_query(self, table_name: str, column_name: str):
        """Add a column to the current query."""
        current_sql = self.sql_text.get('1.0', 'end-1c')
        
        if self.query_type_var.get() == "SELECT":
            if "SELECT " not in current_sql:
                new_sql = f"SELECT {table_name}.{column_name}\nFROM {table_name}"
            else:
                # Add to existing SELECT
                lines = current_sql.split('\n')
                select_line = lines[0]
                if select_line.endswith(','):
                    select_line += f" {table_name}.{column_name}"
                else:
                    select_line += f", {table_name}.{column_name}"
                lines[0] = select_line
                new_sql = '\n'.join(lines)
        else:
            new_sql = current_sql + f" {table_name}.{column_name}"
        
        self.update_sql_preview(new_sql)
    
    def on_query_type_change(self, event):
        """Handle query type change."""
        self.clear_query()
    
    def clear_query(self):
        """Clear the current query."""
        self.update_sql_preview("")
        self.query_canvas.delete("all")
    
    def on_canvas_click(self, event):
        """Handle canvas click events."""
        pass
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events."""
        pass
    
    def update_sql_preview(self, sql: str):
        """Update the SQL preview area."""
        self.sql_text.config(state='normal')
        self.sql_text.delete('1.0', tk.END)
        self.sql_text.insert('1.0', sql)
        self.sql_text.config(state='disabled')
        
        self.current_query = sql
        
        # Notify callbacks
        for callback in self.query_change_callbacks:
            callback(sql)
    
    def execute_current_query(self):
        """Execute the current query."""
        if hasattr(self, 'execute_callback'):
            self.execute_callback(self.current_query)
    
    def set_execute_callback(self, callback: Callable[[str], None]):
        """Set callback for query execution."""
        self.execute_callback = callback
    
    def add_query_change_callback(self, callback: Callable[[str], None]):
        """Add callback for query changes."""
        self.query_change_callbacks.append(callback)

class DatabasePlayground:
    """Main playground controller class."""
    
    def __init__(self, parent: tk.Widget, db_connection: AzureSQLConnection, 
                 schema_analyzer: SchemaAnalyzer, theme_manager: ThemeManager):
        self.parent = parent
        self.db_connection = db_connection
        self.schema_analyzer = schema_analyzer
        self.theme_manager = theme_manager
        
        # Initialize components
        self.sandbox = SafeSandbox(db_connection)
        self.setup_ui()
        self.load_schema_data()
    
    def setup_ui(self):
        """Setup the main playground interface."""
        # Create main container
        self.container = ttk.Frame(self.parent)
        self.container.pack(fill='both', expand=True)
        
        # Create notebook for different playground modes
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Query Builder tab
        self.query_builder_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.query_builder_frame, text="📊 Query Builder")
        
        # Results tab
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📋 Results")
        
        # Tutorial tab
        self.tutorial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tutorial_frame, text="🎓 Tutorials")
        
        # Setup individual components
        self.setup_query_builder()
        self.setup_results_panel()
        self.setup_tutorial_system()
    
    def setup_query_builder(self):
        """Setup the query builder interface."""
        self.query_builder = QueryBuilder(self.query_builder_frame, self.theme_manager)
        self.query_builder.set_execute_callback(self.execute_query)
    
    def setup_results_panel(self):
        """Setup the results display panel."""
        # Results display
        results_container = ttk.Frame(self.results_frame)
        results_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Results text area
        ttk.Label(results_container, text="Query Results:").pack(anchor='w')
        self.results_text = scrolledtext.ScrolledText(results_container, height=15)
        self.results_text.pack(fill='both', expand=True, pady=(5, 10))
        
        # Performance metrics
        metrics_frame = ttk.LabelFrame(results_container, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill='x')
        
        self.metrics_vars = {
            'execution_time': tk.StringVar(value="Execution Time: -"),
            'rows_affected': tk.StringVar(value="Rows Affected: -"),
            'query_status': tk.StringVar(value="Status: Ready")
        }
        
        for var in self.metrics_vars.values():
            ttk.Label(metrics_frame, textvariable=var).pack(anchor='w')
    
    def setup_tutorial_system(self):
        """Setup the interactive tutorial system."""
        tutorial_container = ttk.Frame(self.tutorial_frame)
        tutorial_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(tutorial_container, text="Interactive Database Tutorials", 
                 font=('TkDefaultFont', 14, 'bold')).pack(pady=(0, 20))
        
        # Tutorial list
        tutorials = [
            "🚀 Getting Started with SQL",
            "📊 Basic SELECT Queries",
            "🔗 Working with JOINs",
            "📈 Aggregate Functions",
            "🎯 Filtering Data with WHERE",
            "📝 Data Modification (INSERT, UPDATE, DELETE)"
        ]
        
        for tutorial in tutorials:
            btn = ttk.Button(tutorial_container, text=tutorial, 
                           command=lambda t=tutorial: self.start_tutorial(t))
            btn.pack(fill='x', pady=2)
    
    def load_schema_data(self):
        """Load schema data from the sandbox."""
        try:
            elements = self.sandbox.get_schema_elements()
            self.query_builder.load_schema_elements(elements)
        except Exception as e:
            logger.error(f"Failed to load schema data: {e}")
            messagebox.showerror("Error", f"Failed to load schema data: {e}")
    
    def execute_query(self, query: str):
        """Execute a query in the sandbox."""
        if not query.strip():
            messagebox.showwarning("Warning", "Please enter a query to execute.")
            return
        
        try:
            # Update status
            self.metrics_vars['query_status'].set("Status: Executing...")
            self.parent.update()
            
            # Execute query
            result = self.sandbox.execute_query(query)
            
            # Update metrics
            self.metrics_vars['execution_time'].set(f"Execution Time: {result.execution_time:.3f}s")
            self.metrics_vars['rows_affected'].set(f"Rows Affected: {result.rows_affected}")
            
            if result.success:
                self.metrics_vars['query_status'].set("Status: Success ✓")
                self.display_results(result)
            else:
                self.metrics_vars['query_status'].set("Status: Error ✗")
                self.display_error(result.error_message)
                
            # Switch to results tab
            self.notebook.select(1)
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.metrics_vars['query_status'].set("Status: Error ✗")
            self.display_error(str(e))
    
    def display_results(self, result: QueryResult):
        """Display query results."""
        self.results_text.delete('1.0', tk.END)
        
        if result.data:
            # Format results as table
            if result.columns:
                # Header
                header = " | ".join(f"{col:15}" for col in result.columns)
                self.results_text.insert(tk.END, header + "\n")
                self.results_text.insert(tk.END, "-" * len(header) + "\n")
                
                # Data rows
                for row in result.data:
                    row_text = " | ".join(f"{str(row.get(col, '')):15}" for col in result.columns)
                    self.results_text.insert(tk.END, row_text + "\n")
            
            self.results_text.insert(tk.END, f"\n✓ Query completed successfully")
            self.results_text.insert(tk.END, f"\n📊 {len(result.data)} rows returned")
        else:
            self.results_text.insert(tk.END, "✓ Query executed successfully\n")
            self.results_text.insert(tk.END, f"📝 {result.rows_affected} rows affected")
    
    def display_error(self, error_message: str):
        """Display error message."""
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, f"❌ Error: {error_message}")
    
    def start_tutorial(self, tutorial_name: str):
        """Start an interactive tutorial."""
        messagebox.showinfo("Tutorial", f"Starting tutorial: {tutorial_name}")
        # TODO: Implement tutorial system
    
    def cleanup(self):
        """Clean up playground resources."""
        if hasattr(self, 'sandbox'):
            self.sandbox.cleanup()


def create_playground_panel(parent: tk.Widget, db_connection: AzureSQLConnection, 
                          schema_analyzer: SchemaAnalyzer, theme_manager: ThemeManager) -> DatabasePlayground:
    """Factory function to create a playground panel."""
    return DatabasePlayground(parent, db_connection, schema_analyzer, theme_manager)
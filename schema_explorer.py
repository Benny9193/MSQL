#!/usr/bin/env python3
"""
Dynamic Visual Schema Explorer
==============================

An interactive GUI-based schema explorer that provides visual representation of 
database structures, relationships, and detailed object information. This component 
focuses on real-time exploration, filtering, and navigation of database schemas.

Features:
- Interactive schema diagram with drag-and-drop navigation
- Real-time table and relationship visualization
- Detailed object panels with column information
- Foreign key navigation and dependency tracking
- Advanced search and filtering capabilities
- Integration with existing UI framework and theme system
"""

import tkinter as tk
from tkinter import ttk
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math

# Import existing components
from schema_analyzer import SchemaAnalyzer
from dependency_visualizer import DependencyVisualizer, VisualizationType, Node, Edge
from ui_framework import ThemeManager

logger = logging.getLogger(__name__)

class SchemaViewMode(Enum):
    OVERVIEW = "overview"
    TABLE_FOCUS = "table_focus"
    RELATIONSHIP_FOCUS = "relationship_focus"
    SEARCH_RESULTS = "search_results"

@dataclass
class SchemaElement:
    """Represents a schema element for visualization."""
    id: str
    name: str
    type: str  # table, view, procedure, function, trigger
    schema: str
    properties: Dict[str, Any]
    position: Tuple[float, float] = (0, 0)
    selected: bool = False
    visible: bool = True

class InteractiveCanvas:
    """Interactive canvas for schema visualization."""
    
    def __init__(self, parent, width: int = 800, height: int = 600):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Create canvas with scrollbars
        self.canvas_frame = ttk.Frame(parent)
        self.canvas = tk.Canvas(self.canvas_frame, width=width, height=height, 
                               bg='white', highlightthickness=0)
        
        # Add scrollbars
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='horizontal', 
                                        command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='vertical', 
                                        command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set,
                            yscrollcommand=self.v_scrollbar.set)
        
        # Pack scrollbars and canvas
        self.h_scrollbar.pack(side='bottom', fill='x')
        self.v_scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Initialize drawing state
        self.elements = {}  # id -> SchemaElement
        self.connections = []  # List of connection tuples
        self.selected_element = None
        self.drag_data = {'x': 0, 'y': 0, 'item': None}
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Double-Button-1>', self.on_canvas_double_click)
        self.canvas.bind('<MouseWheel>', self.on_canvas_zoom)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Colors for different object types
        self.colors = {
            'table': {'fill': '#4CAF50', 'border': '#2E7D32', 'text': 'white'},
            'view': {'fill': '#2196F3', 'border': '#1565C0', 'text': 'white'},
            'procedure': {'fill': '#FF9800', 'border': '#E65100', 'text': 'white'},
            'function': {'fill': '#9C27B0', 'border': '#4A148C', 'text': 'white'},
            'selected': {'fill': '#F44336', 'border': '#C62828', 'text': 'white'}
        }
        
        # Zoom settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 3.0
        
    def pack(self, **kwargs):
        """Pack the canvas frame."""
        self.canvas_frame.pack(**kwargs)
    
    def clear(self):
        """Clear all elements from canvas."""
        self.canvas.delete('all')
        self.elements.clear()
        self.connections.clear()
        self.selected_element = None
    
    def add_element(self, element: SchemaElement):
        """Add a schema element to the canvas."""
        self.elements[element.id] = element
        self._draw_element(element)
    
    def add_connection(self, source_id: str, target_id: str, 
                      connection_type: str = 'foreign_key'):
        """Add a connection between two elements."""
        self.connections.append((source_id, target_id, connection_type))
        self._draw_connection(source_id, target_id, connection_type)
    
    def _draw_element(self, element: SchemaElement):
        """Draw a schema element on the canvas."""
        if not element.visible:
            return
        
        x, y = element.position
        
        # Determine size based on element properties
        column_count = element.properties.get('column_count', 1)
        width = max(80, min(150, 60 + column_count * 3))
        height = max(40, min(80, 30 + column_count * 2))
        
        # Choose colors
        colors = self.colors.get(element.type, self.colors['table'])
        if element.selected:
            colors = self.colors['selected']
        
        # Draw rectangle
        rect_id = self.canvas.create_rectangle(
            x - width//2, y - height//2,
            x + width//2, y + height//2,
            fill=colors['fill'], outline=colors['border'], width=2,
            tags=(f'element_{element.id}', 'element')
        )
        
        # Draw text
        display_name = element.name
        if len(display_name) > 12:
            display_name = display_name[:12] + '...'
        
        text_id = self.canvas.create_text(
            x, y, text=display_name, fill=colors['text'],
            font=('Arial', 9, 'bold'),
            tags=(f'element_{element.id}', 'element')
        )
        
        # Store canvas item IDs
        element.properties['canvas_items'] = [rect_id, text_id]
    
    def _draw_connection(self, source_id: str, target_id: str, connection_type: str):
        """Draw a connection line between two elements."""
        if source_id not in self.elements or target_id not in self.elements:
            return
        
        source = self.elements[source_id]
        target = self.elements[target_id]
        
        if not (source.visible and target.visible):
            return
        
        # Calculate connection points
        sx, sy = source.position
        tx, ty = target.position
        
        # Connection colors
        line_colors = {
            'foreign_key': '#4CAF50',
            'dependency': '#2196F3',
            'reference': '#FF9800'
        }
        color = line_colors.get(connection_type, '#999999')
        
        # Draw line with arrow
        line_id = self.canvas.create_line(
            sx, sy, tx, ty,
            fill=color, width=2, arrow=tk.LAST, arrowshape=(10, 12, 3),
            tags=(f'connection_{source_id}_{target_id}', 'connection')
        )
        
        # Add connection label if needed
        mid_x = (sx + tx) / 2
        mid_y = (sy + ty) / 2
        
        if connection_type == 'foreign_key':
            label_id = self.canvas.create_text(
                mid_x, mid_y - 10, text='FK', fill=color,
                font=('Arial', 7), tags=('connection_label',)
            )
    
    def update_element_position(self, element_id: str, x: float, y: float):
        """Update an element's position and redraw."""
        if element_id not in self.elements:
            return
        
        element = self.elements[element_id]
        old_x, old_y = element.position
        element.position = (x, y)
        
        # Move canvas items
        dx = x - old_x
        dy = y - old_y
        
        for item_id in element.properties.get('canvas_items', []):
            self.canvas.move(item_id, dx, dy)
        
        # Update connections
        self._update_connections_for_element(element_id)
    
    def _update_connections_for_element(self, element_id: str):
        """Update all connections involving an element."""
        # Remove old connection lines
        for source_id, target_id, conn_type in self.connections:
            if source_id == element_id or target_id == element_id:
                self.canvas.delete(f'connection_{source_id}_{target_id}')
        
        # Redraw connections
        for source_id, target_id, conn_type in self.connections:
            if source_id == element_id or target_id == element_id:
                self._draw_connection(source_id, target_id, conn_type)
    
    def select_element(self, element_id: str):
        """Select an element and update its appearance."""
        # Deselect previous element
        if self.selected_element:
            self.elements[self.selected_element].selected = False
            self._redraw_element(self.selected_element)
        
        # Select new element
        if element_id in self.elements:
            self.elements[element_id].selected = True
            self.selected_element = element_id
            self._redraw_element(element_id)
    
    def _redraw_element(self, element_id: str):
        """Redraw a specific element."""
        if element_id not in self.elements:
            return
        
        element = self.elements[element_id]
        
        # Remove old drawing
        for item_id in element.properties.get('canvas_items', []):
            self.canvas.delete(item_id)
        
        # Redraw
        self._draw_element(element)
    
    def filter_elements(self, filter_func: Callable[[SchemaElement], bool]):
        """Filter elements based on a function."""
        for element in self.elements.values():
            element.visible = filter_func(element)
        
        # Redraw canvas
        self.redraw_all()
    
    def redraw_all(self):
        """Redraw all elements and connections."""
        self.canvas.delete('all')
        
        # Draw connections first (behind elements)
        for source_id, target_id, conn_type in self.connections:
            self._draw_connection(source_id, target_id, conn_type)
        
        # Draw elements
        for element in self.elements.values():
            self._draw_element(element)
    
    def zoom(self, factor: float, center_x: float = None, center_y: float = None):
        """Zoom the canvas."""
        if center_x is None:
            center_x = self.width / 2
        if center_y is None:
            center_y = self.height / 2
        
        new_zoom = self.zoom_factor * factor
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        
        self.zoom_factor = new_zoom
        
        # Scale all elements
        self.canvas.scale('all', center_x, center_y, factor, factor)
        
        # Update element positions
        for element in self.elements.values():
            x, y = element.position
            new_x = center_x + (x - center_x) * factor
            new_y = center_y + (y - center_y) * factor
            element.position = (new_x, new_y)
    
    def fit_to_view(self):
        """Fit all elements to the canvas view."""
        if not self.elements:
            return
        
        # Find bounds
        min_x = min(elem.position[0] for elem in self.elements.values())
        max_x = max(elem.position[0] for elem in self.elements.values())
        min_y = min(elem.position[1] for elem in self.elements.values())
        max_y = max(elem.position[1] for elem in self.elements.values())
        
        # Calculate scaling
        content_width = max_x - min_x + 200  # Add padding
        content_height = max_y - min_y + 200
        
        if content_width == 0 or content_height == 0:
            return
        
        scale_x = self.width / content_width
        scale_y = self.height / content_height
        scale = min(scale_x, scale_y, 1.0)  # Don't zoom in beyond 100%
        
        # Center content
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        target_x = self.width / 2
        target_y = self.height / 2
        
        # Apply transformation
        for element in self.elements.values():
            x, y = element.position
            new_x = target_x + (x - center_x) * scale
            new_y = target_y + (y - center_y) * scale
            element.position = (new_x, new_y)
        
        self.zoom_factor = scale
        self.redraw_all()
    
    # Event handlers
    def on_canvas_click(self, event):
        """Handle canvas click events."""
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        
        # Check if clicked on an element
        for tag in tags:
            if tag.startswith('element_'):
                element_id = tag.replace('element_', '')
                self.select_element(element_id)
                
                # Prepare for dragging
                self.drag_data['x'] = event.x
                self.drag_data['y'] = event.y
                self.drag_data['item'] = element_id
                break
        else:
            # Clicked on empty space - deselect
            if self.selected_element:
                self.elements[self.selected_element].selected = False
                self._redraw_element(self.selected_element)
                self.selected_element = None
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events."""
        if self.drag_data['item']:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            
            element = self.elements[self.drag_data['item']]
            new_x = element.position[0] + dx
            new_y = element.position[1] + dy
            
            self.update_element_position(self.drag_data['item'], new_x, new_y)
            
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y
    
    def on_canvas_release(self, event):
        """Handle canvas release events."""
        self.drag_data['item'] = None
    
    def on_canvas_double_click(self, event):
        """Handle canvas double-click events."""
        if self.selected_element:
            # Trigger detail view for selected element
            element = self.elements[self.selected_element]
            self.on_element_double_click(element)
    
    def on_canvas_zoom(self, event):
        """Handle mouse wheel zoom."""
        if event.delta > 0:
            self.zoom(1.1, event.x, event.y)
        else:
            self.zoom(0.9, event.x, event.y)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize."""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def on_element_double_click(self, element: SchemaElement):
        """Override this method to handle element double-clicks."""
        pass

class SchemaExplorer:
    """Main Dynamic Visual Schema Explorer component."""
    
    def __init__(self, parent, db_connection=None, schema_analyzer: SchemaAnalyzer = None,
                 theme_manager: ThemeManager = None):
        self.parent = parent
        self.db_connection = db_connection
        self.schema_analyzer = schema_analyzer
        self.theme_manager = theme_manager or ThemeManager()
        
        # Data
        self.schema_data = None
        self.filtered_data = None
        self.current_view_mode = SchemaViewMode.OVERVIEW
        self.current_focus_object = None
        
        # UI Components
        self.main_frame = None
        self.toolbar_frame = None
        self.content_frame = None
        self.canvas = None
        self.detail_panel = None
        self.search_var = None
        self.schema_filter_var = None
        
        # Callbacks
        self.on_object_selected = None
        self.on_relationship_clicked = None
        
        self._create_interface()
        
        if self.db_connection and self.schema_analyzer:
            self._load_schema_data()
    
    def _create_interface(self):
        """Create the main interface."""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create main content area with paned window
        self.content_frame = ttk.PanedWindow(self.main_frame, orient='horizontal')
        self.content_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        # Left panel - Schema canvas
        self.canvas_frame = ttk.LabelFrame(self.content_frame, text="Schema Diagram", padding=5)
        self.content_frame.add(self.canvas_frame, weight=3)
        
        self.canvas = InteractiveCanvas(self.canvas_frame, width=600, height=400)
        self.canvas.on_element_double_click = self._on_element_double_click
        self.canvas.pack(fill='both', expand=True)
        
        # Right panel - Detail and controls
        self.detail_frame = ttk.LabelFrame(self.content_frame, text="Object Details", padding=5)
        self.content_frame.add(self.detail_frame, weight=1)
        
        self._create_detail_panel()
    
    def _create_toolbar(self):
        """Create the toolbar with controls."""
        self.toolbar_frame = ttk.Frame(self.main_frame)
        self.toolbar_frame.pack(fill='x', pady=(0, 5))
        
        # Search
        ttk.Label(self.toolbar_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(self.toolbar_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=(0, 15))
        
        # Schema filter
        ttk.Label(self.toolbar_frame, text="Schema:").pack(side='left', padx=(0, 5))
        self.schema_filter_var = tk.StringVar()
        self.schema_filter_combo = ttk.Combobox(self.toolbar_frame, textvariable=self.schema_filter_var,
                                              width=15, state='readonly')
        self.schema_filter_combo.bind('<<ComboboxSelected>>', self._on_schema_filter_changed)
        self.schema_filter_combo.pack(side='left', padx=(0, 15))
        
        # View mode buttons
        view_frame = ttk.LabelFrame(self.toolbar_frame, text="View Mode", padding=5)
        view_frame.pack(side='left', padx=(0, 15))
        
        self.view_mode_var = tk.StringVar(value=SchemaViewMode.OVERVIEW.value)
        
        ttk.Radiobutton(view_frame, text="Overview", variable=self.view_mode_var,
                       value=SchemaViewMode.OVERVIEW.value,
                       command=self._on_view_mode_changed).pack(side='left')
        ttk.Radiobutton(view_frame, text="Table Focus", variable=self.view_mode_var,
                       value=SchemaViewMode.TABLE_FOCUS.value,
                       command=self._on_view_mode_changed).pack(side='left')
        ttk.Radiobutton(view_frame, text="Relationships", variable=self.view_mode_var,
                       value=SchemaViewMode.RELATIONSHIP_FOCUS.value,
                       command=self._on_view_mode_changed).pack(side='left')
        
        # Action buttons
        actions_frame = ttk.Frame(self.toolbar_frame)
        actions_frame.pack(side='right')
        
        ttk.Button(actions_frame, text="Refresh", command=self._refresh_data).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="Fit to View", command=self._fit_to_view).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="Export", command=self._export_diagram).pack(side='left', padx=2)
    
    def _create_detail_panel(self):
        """Create the detail panel for object information."""
        # Object info section
        info_frame = ttk.LabelFrame(self.detail_frame, text="Selected Object", padding=5)
        info_frame.pack(fill='x', pady=(0, 5))
        
        self.object_info_text = tk.Text(info_frame, height=8, wrap='word', font=('Consolas', 9))
        info_scrollbar = ttk.Scrollbar(info_frame, command=self.object_info_text.yview)
        self.object_info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.object_info_text.pack(side='left', fill='both', expand=True)
        info_scrollbar.pack(side='right', fill='y')
        
        # Relationships section
        rel_frame = ttk.LabelFrame(self.detail_frame, text="Relationships", padding=5)
        rel_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        # Create treeview for relationships
        self.relationships_tree = ttk.Treeview(rel_frame, columns=('type', 'target', 'column'), 
                                             show='headings', height=6)
        self.relationships_tree.heading('#1', text='Type')
        self.relationships_tree.heading('#2', text='Target')
        self.relationships_tree.heading('#3', text='Column')
        
        self.relationships_tree.column('#1', width=80)
        self.relationships_tree.column('#2', width=120)
        self.relationships_tree.column('#3', width=100)
        
        rel_scrollbar = ttk.Scrollbar(rel_frame, command=self.relationships_tree.yview)
        self.relationships_tree.configure(yscrollcommand=rel_scrollbar.set)
        
        self.relationships_tree.pack(side='left', fill='both', expand=True)
        rel_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click for navigation
        self.relationships_tree.bind('<Double-1>', self._on_relationship_double_click)
        
        # Navigation buttons
        nav_frame = ttk.Frame(rel_frame)
        nav_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(nav_frame, text="Navigate to Selected", 
                  command=self._navigate_to_selected_relationship).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="Show Dependencies", 
                  command=self._show_dependencies).pack(side='left', padx=2)
    
    def _load_schema_data(self):
        """Load schema data from the database."""
        if not self.schema_analyzer:
            return
        
        try:
            logger.info("Loading schema data for explorer...")
            
            # Get comprehensive schema information
            schema_data = {
                'schemas': self.schema_analyzer.get_all_schemas(),
                'tables': self.schema_analyzer.get_all_tables(),
                'views': self.schema_analyzer.get_all_views(),
                'stored_procedures': self.schema_analyzer.get_stored_procedures(),
                'functions': self.schema_analyzer.get_functions(),
            }
            
            # Enhance tables with detailed information
            enhanced_tables = []
            for table in schema_data['tables']:
                table_obj_id = table.get('object_id')
                if table_obj_id:
                    # Get columns
                    columns = self.schema_analyzer.get_table_columns(table_obj_id)
                    table['columns'] = columns
                    
                    # Get primary keys
                    primary_keys = self.schema_analyzer.get_primary_keys(table_obj_id)
                    table['primary_keys'] = primary_keys
                    
                    # Get foreign keys
                    foreign_keys = self.schema_analyzer.get_foreign_keys(table_obj_id)
                    table['foreign_keys'] = foreign_keys
                    
                    # Get indexes
                    indexes = self.schema_analyzer.get_indexes(table_obj_id)
                    table['indexes'] = indexes
                
                enhanced_tables.append(table)
            
            schema_data['tables'] = enhanced_tables
            
            # Get all foreign key relationships
            all_foreign_keys = self.schema_analyzer.get_foreign_keys()
            schema_data['relationships'] = {'foreign_keys': all_foreign_keys}
            
            self.schema_data = schema_data
            self.filtered_data = schema_data
            
            # Update UI
            self._update_schema_filter_options()
            self._refresh_visualization()
            
            logger.info(f"Schema data loaded: {len(schema_data['tables'])} tables, "
                       f"{len(schema_data['views'])} views, "
                       f"{len(all_foreign_keys)} relationships")
            
        except Exception as e:
            logger.error(f"Failed to load schema data: {e}")
            self._show_error_message(f"Failed to load schema data: {e}")
    
    def _update_schema_filter_options(self):
        """Update the schema filter dropdown options."""
        if not self.schema_data:
            return
        
        schemas = set()
        for table in self.schema_data['tables']:
            schemas.add(table.get('schema_name', 'dbo'))
        
        schema_list = ['All Schemas'] + sorted(schemas)
        self.schema_filter_combo['values'] = schema_list
        self.schema_filter_combo.set('All Schemas')
    
    def _refresh_visualization(self):
        """Refresh the schema visualization based on current filters and mode."""
        if not self.filtered_data or not self.canvas:
            return
        
        try:
            self.canvas.clear()
            
            if self.current_view_mode == SchemaViewMode.OVERVIEW:
                self._create_overview_visualization()
            elif self.current_view_mode == SchemaViewMode.TABLE_FOCUS:
                self._create_table_focus_visualization()
            elif self.current_view_mode == SchemaViewMode.RELATIONSHIP_FOCUS:
                self._create_relationship_visualization()
            
            # Auto-fit to view
            self.canvas.fit_to_view()
            
        except Exception as e:
            logger.error(f"Failed to refresh visualization: {e}")
    
    def _create_overview_visualization(self):
        """Create overview visualization showing all objects."""
        tables = self.filtered_data.get('tables', [])
        views = self.filtered_data.get('views', [])
        relationships = self.filtered_data.get('relationships', {}).get('foreign_keys', [])
        
        # Add tables
        table_positions = self._calculate_layout_positions(tables, 'table')
        for table, (x, y) in zip(tables, table_positions):
            element = SchemaElement(
                id=f"{table.get('schema_name', 'dbo')}.{table.get('table_name')}",
                name=table.get('table_name'),
                type='table',
                schema=table.get('schema_name', 'dbo'),
                properties={
                    'column_count': len(table.get('columns', [])),
                    'row_count': table.get('row_count', 0),
                    'has_primary_key': bool(table.get('primary_keys', [])),
                    'foreign_key_count': len(table.get('foreign_keys', [])),
                    'index_count': len(table.get('indexes', [])),
                    'table_data': table
                },
                position=(x, y)
            )
            self.canvas.add_element(element)
        
        # Add views
        view_positions = self._calculate_layout_positions(views, 'view', offset_y=200)
        for view, (x, y) in zip(views, view_positions):
            element = SchemaElement(
                id=f"{view.get('schema_name', 'dbo')}.{view.get('view_name')}",
                name=view.get('view_name'),
                type='view',
                schema=view.get('schema_name', 'dbo'),
                properties={
                    'column_count': len(view.get('columns', [])),
                    'view_data': view
                },
                position=(x, y)
            )
            self.canvas.add_element(element)
        
        # Add relationships
        for rel in relationships:
            source_id = f"{rel.get('parent_schema', 'dbo')}.{rel.get('parent_table')}"
            target_id = f"{rel.get('referenced_schema', 'dbo')}.{rel.get('referenced_table')}"
            self.canvas.add_connection(source_id, target_id, 'foreign_key')
    
    def _create_table_focus_visualization(self):
        """Create table-focused visualization."""
        if not self.current_focus_object:
            # Show largest table by default
            tables = self.filtered_data.get('tables', [])
            if tables:
                self.current_focus_object = max(tables, 
                    key=lambda t: len(t.get('columns', [])))
        
        if not self.current_focus_object:
            return
        
        focus_table = self.current_focus_object
        focus_id = f"{focus_table.get('schema_name', 'dbo')}.{focus_table.get('table_name')}"
        
        # Add focus table in center
        focus_element = SchemaElement(
            id=focus_id,
            name=focus_table.get('table_name'),
            type='table',
            schema=focus_table.get('schema_name', 'dbo'),
            properties={
                'column_count': len(focus_table.get('columns', [])),
                'is_focus': True,
                'table_data': focus_table
            },
            position=(0, 0)
        )
        self.canvas.add_element(focus_element)
        
        # Add related tables in a circle around focus
        related_tables = self._find_related_tables(focus_table)
        if related_tables:
            positions = self._calculate_circular_positions(len(related_tables), radius=200)
            for table, (x, y) in zip(related_tables, positions):
                element = SchemaElement(
                    id=f"{table.get('schema_name', 'dbo')}.{table.get('table_name')}",
                    name=table.get('table_name'),
                    type='table',
                    schema=table.get('schema_name', 'dbo'),
                    properties={
                        'column_count': len(table.get('columns', [])),
                        'table_data': table
                    },
                    position=(x, y)
                )
                self.canvas.add_element(element)
                
                # Add relationship
                other_id = f"{table.get('schema_name', 'dbo')}.{table.get('table_name')}"
                self.canvas.add_connection(focus_id, other_id, 'foreign_key')
    
    def _create_relationship_visualization(self):
        """Create relationship-focused visualization."""
        relationships = self.filtered_data.get('relationships', {}).get('foreign_keys', [])
        
        if not relationships:
            return
        
        # Group tables by relationship density
        table_connections = {}
        for rel in relationships:
            parent_table = f"{rel.get('parent_schema', 'dbo')}.{rel.get('parent_table')}"
            ref_table = f"{rel.get('referenced_schema', 'dbo')}.{rel.get('referenced_table')}"
            
            table_connections.setdefault(parent_table, set()).add(ref_table)
            table_connections.setdefault(ref_table, set()).add(parent_table)
        
        # Find most connected tables
        sorted_tables = sorted(table_connections.items(), 
                             key=lambda x: len(x[1]), reverse=True)
        
        # Layout tables based on connection density
        main_tables = sorted_tables[:10]  # Top 10 most connected
        positions = self._calculate_circular_positions(len(main_tables), radius=250)
        
        for (table_id, connections), (x, y) in zip(main_tables, positions):
            # Find table data
            table_data = self._find_table_by_id(table_id)
            if not table_data:
                continue
            
            element = SchemaElement(
                id=table_id,
                name=table_id.split('.')[-1],
                type='table',
                schema=table_id.split('.')[0] if '.' in table_id else 'dbo',
                properties={
                    'column_count': len(table_data.get('columns', [])),
                    'connection_count': len(connections),
                    'table_data': table_data
                },
                position=(x, y)
            )
            self.canvas.add_element(element)
        
        # Add relationships
        for rel in relationships:
            source_id = f"{rel.get('parent_schema', 'dbo')}.{rel.get('parent_table')}"
            target_id = f"{rel.get('referenced_schema', 'dbo')}.{rel.get('referenced_table')}"
            
            # Only show relationships between displayed tables
            if (source_id in [t[0] for t in main_tables] and 
                target_id in [t[0] for t in main_tables]):
                self.canvas.add_connection(source_id, target_id, 'foreign_key')
    
    def _calculate_layout_positions(self, objects: List[Dict], obj_type: str, 
                                  offset_x: float = 0, offset_y: float = 0) -> List[Tuple[float, float]]:
        """Calculate layout positions for objects."""
        if not objects:
            return []
        
        # Simple grid layout
        cols = math.ceil(math.sqrt(len(objects)))
        rows = math.ceil(len(objects) / cols)
        
        spacing_x = 150
        spacing_y = 100
        
        positions = []
        for i, obj in enumerate(objects):
            col = i % cols
            row = i // cols
            
            x = offset_x + (col - cols/2) * spacing_x
            y = offset_y + (row - rows/2) * spacing_y
            
            positions.append((x, y))
        
        return positions
    
    def _calculate_circular_positions(self, count: int, radius: float = 200) -> List[Tuple[float, float]]:
        """Calculate circular positions for objects."""
        if count == 0:
            return []
        
        positions = []
        angle_step = 2 * math.pi / count
        
        for i in range(count):
            angle = i * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions.append((x, y))
        
        return positions
    
    def _find_related_tables(self, focus_table: Dict) -> List[Dict]:
        """Find tables related to the focus table."""
        if not focus_table or not self.schema_data:
            return []
        
        focus_name = focus_table.get('table_name')
        focus_schema = focus_table.get('schema_name', 'dbo')
        
        related_tables = []
        relationships = self.schema_data.get('relationships', {}).get('foreign_keys', [])
        
        # Find tables referenced by focus table
        related_table_names = set()
        for rel in relationships:
            if (rel.get('parent_table') == focus_name and 
                rel.get('parent_schema', 'dbo') == focus_schema):
                related_table_names.add(
                    (rel.get('referenced_table'), rel.get('referenced_schema', 'dbo'))
                )
            elif (rel.get('referenced_table') == focus_name and 
                  rel.get('referenced_schema', 'dbo') == focus_schema):
                related_table_names.add(
                    (rel.get('parent_table'), rel.get('parent_schema', 'dbo'))
                )
        
        # Find table objects
        for table in self.schema_data.get('tables', []):
            table_name = table.get('table_name')
            table_schema = table.get('schema_name', 'dbo')
            if (table_name, table_schema) in related_table_names:
                related_tables.append(table)
        
        return related_tables
    
    def _find_table_by_id(self, table_id: str) -> Optional[Dict]:
        """Find table data by ID."""
        if not self.schema_data:
            return None
        
        schema_name, table_name = table_id.split('.') if '.' in table_id else ('dbo', table_id)
        
        for table in self.schema_data.get('tables', []):
            if (table.get('table_name') == table_name and 
                table.get('schema_name', 'dbo') == schema_name):
                return table
        
        return None
    
    def _on_search_changed(self, *args):
        """Handle search input changes."""
        search_text = self.search_var.get().lower().strip()
        
        if not search_text:
            self.filtered_data = self.schema_data
        else:
            # Filter data based on search
            filtered = {
                'schemas': self.schema_data.get('schemas', []),
                'tables': [],
                'views': [],
                'stored_procedures': [],
                'functions': [],
                'relationships': self.schema_data.get('relationships', {})
            }
            
            # Filter tables
            for table in self.schema_data.get('tables', []):
                table_name = table.get('table_name', '').lower()
                schema_name = table.get('schema_name', '').lower()
                if search_text in table_name or search_text in schema_name:
                    filtered['tables'].append(table)
            
            # Filter views
            for view in self.schema_data.get('views', []):
                view_name = view.get('view_name', '').lower()
                schema_name = view.get('schema_name', '').lower()
                if search_text in view_name or search_text in schema_name:
                    filtered['views'].append(view)
            
            self.filtered_data = filtered
            self.current_view_mode = SchemaViewMode.SEARCH_RESULTS
        
        self._refresh_visualization()
    
    def _on_schema_filter_changed(self, event=None):
        """Handle schema filter changes."""
        selected_schema = self.schema_filter_var.get()
        
        if selected_schema == 'All Schemas' or not selected_schema:
            self.filtered_data = self.schema_data
        else:
            # Filter by schema
            filtered = {
                'schemas': [s for s in self.schema_data.get('schemas', []) 
                           if s.get('schema_name') == selected_schema],
                'tables': [t for t in self.schema_data.get('tables', []) 
                          if t.get('schema_name') == selected_schema],
                'views': [v for v in self.schema_data.get('views', []) 
                         if v.get('schema_name') == selected_schema],
                'stored_procedures': [p for p in self.schema_data.get('stored_procedures', []) 
                                    if p.get('schema_name') == selected_schema],
                'functions': [f for f in self.schema_data.get('functions', []) 
                            if f.get('schema_name') == selected_schema],
                'relationships': self.schema_data.get('relationships', {})
            }
            
            # Filter relationships to only include filtered objects
            filtered_fks = []
            table_names = {f"{t.get('schema_name')}.{t.get('table_name')}" 
                          for t in filtered['tables']}
            
            for rel in self.schema_data.get('relationships', {}).get('foreign_keys', []):
                parent_id = f"{rel.get('parent_schema')}.{rel.get('parent_table')}"
                ref_id = f"{rel.get('referenced_schema')}.{rel.get('referenced_table')}"
                if parent_id in table_names and ref_id in table_names:
                    filtered_fks.append(rel)
            
            filtered['relationships'] = {'foreign_keys': filtered_fks}
            self.filtered_data = filtered
        
        self._refresh_visualization()
    
    def _on_view_mode_changed(self):
        """Handle view mode changes."""
        mode_value = self.view_mode_var.get()
        self.current_view_mode = SchemaViewMode(mode_value)
        self._refresh_visualization()
    
    def _on_element_double_click(self, element: SchemaElement):
        """Handle element double-click for detailed view."""
        self._select_object(element)
        
        # Set as focus object for table focus mode
        if element.type == 'table':
            table_data = element.properties.get('table_data')
            if table_data:
                self.current_focus_object = table_data
    
    def _select_object(self, element: SchemaElement):
        """Select an object and show its details."""
        # Update detail panel
        self.object_info_text.delete(1.0, tk.END)
        
        # Get object details
        if element.type == 'table':
            self._show_table_details(element)
        elif element.type == 'view':
            self._show_view_details(element)
        
        # Update relationships
        self._update_relationships_panel(element)
        
        # Call callback if set
        if self.on_object_selected:
            self.on_object_selected(element)
    
    def _show_table_details(self, element: SchemaElement):
        """Show table details in the info panel."""
        table_data = element.properties.get('table_data')
        if not table_data:
            return
        
        details = f"Table: {element.schema}.{element.name}\n"
        details += f"Type: {table_data.get('type_desc', 'TABLE')}\n"
        details += f"Created: {table_data.get('create_date', 'Unknown')}\n"
        details += f"Modified: {table_data.get('modify_date', 'Unknown')}\n\n"
        
        # Columns
        columns = table_data.get('columns', [])
        details += f"Columns ({len(columns)}):\n"
        for col in columns[:10]:  # Show first 10 columns
            data_type = col.get('data_type', 'unknown')
            max_length = col.get('max_length', '')
            if max_length and max_length > 0 and data_type in ['varchar', 'nvarchar', 'char', 'nchar']:
                data_type += f"({max_length})"
            
            nullable = "NULL" if col.get('is_nullable') else "NOT NULL"
            pk_indicator = " (PK)" if col.get('is_primary_key') else ""
            
            details += f"  • {col.get('column_name')} - {data_type} {nullable}{pk_indicator}\n"
        
        if len(columns) > 10:
            details += f"  ... and {len(columns) - 10} more columns\n"
        
        # Indexes
        indexes = table_data.get('indexes', [])
        if indexes:
            details += f"\nIndexes ({len(indexes)}):\n"
            for idx in indexes[:5]:  # Show first 5 indexes
                idx_type = "PK" if idx.get('is_primary_key') else "IX"
                unique = " (UNIQUE)" if idx.get('is_unique') else ""
                details += f"  • {idx.get('index_name')} ({idx_type}){unique}\n"
        
        self.object_info_text.insert(tk.END, details)
    
    def _show_view_details(self, element: SchemaElement):
        """Show view details in the info panel."""
        view_data = element.properties.get('view_data')
        if not view_data:
            return
        
        details = f"View: {element.schema}.{element.name}\n"
        details += f"Created: {view_data.get('create_date', 'Unknown')}\n"
        details += f"Modified: {view_data.get('modify_date', 'Unknown')}\n\n"
        
        # Columns
        columns = view_data.get('columns', [])
        if columns:
            details += f"Columns ({len(columns)}):\n"
            for col in columns[:10]:  # Show first 10 columns
                data_type = col.get('data_type', 'unknown')
                nullable = "NULL" if col.get('is_nullable') else "NOT NULL"
                details += f"  • {col.get('column_name')} - {data_type} {nullable}\n"
        
        self.object_info_text.insert(tk.END, details)
    
    def _update_relationships_panel(self, element: SchemaElement):
        """Update the relationships panel for the selected object."""
        # Clear existing items
        for item in self.relationships_tree.get_children():
            self.relationships_tree.delete(item)
        
        if element.type == 'table':
            table_data = element.properties.get('table_data')
            if table_data:
                # Show foreign keys
                foreign_keys = table_data.get('foreign_keys', [])
                for fk in foreign_keys:
                    self.relationships_tree.insert('', tk.END, values=(
                        'Foreign Key',
                        f"{fk.get('referenced_schema', 'dbo')}.{fk.get('referenced_table')}",
                        f"{fk.get('parent_column')} → {fk.get('referenced_column')}"
                    ))
                
                # Find incoming foreign keys
                table_name = table_data.get('table_name')
                schema_name = table_data.get('schema_name', 'dbo')
                
                if self.schema_data:
                    all_fks = self.schema_data.get('relationships', {}).get('foreign_keys', [])
                    for fk in all_fks:
                        if (fk.get('referenced_table') == table_name and 
                            fk.get('referenced_schema', 'dbo') == schema_name):
                            self.relationships_tree.insert('', tk.END, values=(
                                'Referenced By',
                                f"{fk.get('parent_schema', 'dbo')}.{fk.get('parent_table')}",
                                f"{fk.get('parent_column')} ← {fk.get('referenced_column')}"
                            ))
    
    def _on_relationship_double_click(self, event):
        """Handle double-click on relationship item."""
        selection = self.relationships_tree.selection()
        if selection:
            item = self.relationships_tree.item(selection[0])
            target_table = item['values'][1] if len(item['values']) > 1 else None
            if target_table:
                self._navigate_to_table(target_table)
    
    def _navigate_to_selected_relationship(self):
        """Navigate to the selected relationship target."""
        selection = self.relationships_tree.selection()
        if selection:
            item = self.relationships_tree.item(selection[0])
            target_table = item['values'][1] if len(item['values']) > 1 else None
            if target_table:
                self._navigate_to_table(target_table)
    
    def _navigate_to_table(self, table_id: str):
        """Navigate to a specific table."""
        # Find the table element and select it
        if table_id in self.canvas.elements:
            self.canvas.select_element(table_id)
            element = self.canvas.elements[table_id]
            self._select_object(element)
            
            # Center the view on the table
            x, y = element.position
            # This is a simplified centering - in a real implementation,
            # you'd want to adjust the canvas scroll region
    
    def _show_dependencies(self):
        """Show dependency visualization for selected object."""
        if self.canvas.selected_element:
            element = self.canvas.elements[self.canvas.selected_element]
            if element.type == 'table':
                table_data = element.properties.get('table_data')
                if table_data:
                    self.current_focus_object = table_data
                    self.current_view_mode = SchemaViewMode.TABLE_FOCUS
                    self.view_mode_var.set(SchemaViewMode.TABLE_FOCUS.value)
                    self._refresh_visualization()
    
    def _refresh_data(self):
        """Refresh schema data from database."""
        self._load_schema_data()
    
    def _fit_to_view(self):
        """Fit canvas to view (safe wrapper method)."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.fit_to_view()
    
    def _export_diagram(self):
        """Export the current diagram."""
        try:
            # Create visualization data using existing dependency visualizer
            if not self.filtered_data:
                return
            
            visualizer = DependencyVisualizer()
            viz_data = visualizer.generate_visualization(
                self.filtered_data,
                VisualizationType.RELATIONSHIP_DIAGRAM,
                {'schema_filter': [self.schema_filter_var.get()] 
                 if self.schema_filter_var.get() != 'All Schemas' else None}
            )
            
            # Export as HTML
            output_file = "schema_diagram.html"
            html_content = visualizer.generate_html_visualization(viz_data, output_file)
            
            tk.messagebox.showinfo("Export Complete", 
                                 f"Schema diagram exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export diagram: {e}")
            tk.messagebox.showerror("Export Error", f"Failed to export diagram: {e}")
    
    def _show_error_message(self, message: str):
        """Show an error message to the user."""
        self.object_info_text.delete(1.0, tk.END)
        self.object_info_text.insert(tk.END, f"Error: {message}")
    
    def set_callbacks(self, on_object_selected: Callable = None, 
                     on_relationship_clicked: Callable = None):
        """Set callback functions."""
        self.on_object_selected = on_object_selected
        self.on_relationship_clicked = on_relationship_clicked


def create_schema_explorer_panel(parent, db_connection=None, schema_analyzer=None, 
                                theme_manager=None) -> SchemaExplorer:
    """
    Factory function to create a Schema Explorer panel.
    
    Args:
        parent: Parent tkinter widget
        db_connection: Database connection object
        schema_analyzer: SchemaAnalyzer instance
        theme_manager: ThemeManager instance
    
    Returns:
        SchemaExplorer instance
    """
    return SchemaExplorer(parent, db_connection, schema_analyzer, theme_manager)


# Example usage and testing
if __name__ == "__main__":
    import sys
    import os
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    def test_schema_explorer():
        """Test the schema explorer with mock data."""
        root = tk.Tk()
        root.title("Schema Explorer Test")
        root.geometry("1200x800")
        
        # Create mock schema data for testing
        mock_data = {
            'tables': [
                {
                    'schema_name': 'dbo',
                    'table_name': 'Users',
                    'object_id': 1,
                    'columns': [
                        {'column_name': 'ID', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'Name', 'data_type': 'varchar', 'is_nullable': False},
                        {'column_name': 'Email', 'data_type': 'varchar', 'is_nullable': True}
                    ],
                    'primary_keys': [{'column_name': 'ID'}],
                    'foreign_keys': [],
                    'indexes': [{'index_name': 'PK_Users', 'is_primary_key': True}]
                },
                {
                    'schema_name': 'dbo',
                    'table_name': 'Orders',
                    'object_id': 2,
                    'columns': [
                        {'column_name': 'ID', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'UserID', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'OrderDate', 'data_type': 'datetime', 'is_nullable': False}
                    ],
                    'primary_keys': [{'column_name': 'ID'}],
                    'foreign_keys': [{'parent_column': 'UserID', 'referenced_table': 'Users', 'referenced_column': 'ID'}],
                    'indexes': [{'index_name': 'PK_Orders', 'is_primary_key': True}]
                }
            ],
            'views': [],
            'relationships': {
                'foreign_keys': [
                    {
                        'parent_table': 'Orders',
                        'parent_schema': 'dbo',
                        'parent_column': 'UserID',
                        'referenced_table': 'Users',
                        'referenced_schema': 'dbo',
                        'referenced_column': 'ID'
                    }
                ]
            }
        }
        
        # Create explorer without database connection (using mock data)
        explorer = SchemaExplorer(root)
        explorer.schema_data = mock_data
        explorer.filtered_data = mock_data
        explorer._update_schema_filter_options()
        explorer._refresh_visualization()
        
        root.mainloop()
    
    test_schema_explorer()
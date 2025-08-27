#!/usr/bin/env python3
"""
Dependency Visualization Module
==============================

Creates interactive visual representations of database dependencies, relationships,
and schema structures. Provides multiple visualization types including relationship
diagrams, dependency graphs, and hierarchical views.

Features:
- Foreign key relationship diagrams
- Table dependency graphs
- Hierarchical schema visualization
- Interactive filtering and exploration
- Export to various formats (SVG, PNG, HTML)
- Customizable layouts and styling
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import os
import tempfile
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class VisualizationType(Enum):
    RELATIONSHIP_DIAGRAM = "relationship_diagram"
    DEPENDENCY_GRAPH = "dependency_graph"
    HIERARCHICAL_VIEW = "hierarchical_view"
    CIRCULAR_LAYOUT = "circular_layout"

@dataclass
class Node:
    """Represents a node in the dependency graph."""
    id: str
    label: str
    type: str  # table, view, procedure, function
    properties: Dict[str, Any]
    x: float = 0.0
    y: float = 0.0

@dataclass
class Edge:
    """Represents an edge (relationship) in the dependency graph."""
    source: str
    target: str
    type: str  # foreign_key, dependency, reference
    properties: Dict[str, Any]
    label: str = ""

class DependencyVisualizer:
    """Creates visual representations of database dependencies."""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.schema_data = None
        
    def generate_visualization(self, schema_data: Dict[str, Any], 
                             viz_type: VisualizationType = VisualizationType.RELATIONSHIP_DIAGRAM,
                             options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a visualization from schema data.
        
        Args:
            schema_data: Complete database schema information
            viz_type: Type of visualization to create
            options: Visualization options and filters
            
        Returns:
            Visualization data structure
        """
        self.schema_data = schema_data
        options = options or {}
        
        logger.info(f"Generating {viz_type.value} visualization")
        
        # Reset state
        self.nodes = {}
        self.edges = []
        
        # Build nodes and edges based on visualization type
        if viz_type == VisualizationType.RELATIONSHIP_DIAGRAM:
            self._build_relationship_diagram(options)
        elif viz_type == VisualizationType.DEPENDENCY_GRAPH:
            self._build_dependency_graph(options)
        elif viz_type == VisualizationType.HIERARCHICAL_VIEW:
            self._build_hierarchical_view(options)
        elif viz_type == VisualizationType.CIRCULAR_LAYOUT:
            self._build_circular_layout(options)
        
        # Apply layout algorithm
        self._apply_layout(viz_type, options)
        
        # Generate visualization data
        viz_data = {
            'type': viz_type.value,
            'nodes': list(self.nodes.values()),
            'edges': self.edges,
            'metadata': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'schemas': self._get_schema_names(),
                'options': options
            }
        }
        
        return viz_data
    
    def _build_relationship_diagram(self, options: Dict[str, Any]):
        """Build nodes and edges for relationship diagram."""
        tables = self.schema_data.get('tables', [])
        relationships = self.schema_data.get('relationships', {}).get('foreign_keys', [])
        
        # Filter tables if schema filter is specified
        schema_filter = options.get('schema_filter')
        if schema_filter:
            tables = [t for t in tables if t.get('schema_name') in schema_filter]
        
        # Create table nodes
        for table in tables:
            table_name = f"{table.get('schema_name', 'dbo')}.{table.get('table_name')}"
            
            # Count columns by type for node properties
            columns = table.get('columns', [])
            column_types = {}
            for col in columns:
                data_type = col.get('data_type', 'unknown')
                column_types[data_type] = column_types.get(data_type, 0) + 1
            
            node = Node(
                id=table_name,
                label=table.get('table_name'),
                type='table',
                properties={
                    'schema': table.get('schema_name', 'dbo'),
                    'column_count': len(columns),
                    'column_types': column_types,
                    'row_count': table.get('row_count', 0),
                    'size_mb': table.get('size_mb', 0),
                    'has_primary_key': any(col.get('is_primary_key') for col in columns),
                    'has_foreign_keys': any(col.get('is_foreign_key') for col in columns),
                    'indexes': len(table.get('indexes', []))
                }
            )
            self.nodes[table_name] = node
        
        # Create relationship edges
        for rel in relationships:
            source_table = f"{rel.get('table_schema', 'dbo')}.{rel.get('table_name')}"
            target_table = f"{rel.get('referenced_table_schema', 'dbo')}.{rel.get('referenced_table_name')}"
            
            # Only include relationships where both tables are in our node set
            if source_table in self.nodes and target_table in self.nodes:
                edge = Edge(
                    source=source_table,
                    target=target_table,
                    type='foreign_key',
                    properties={
                        'constraint_name': rel.get('constraint_name'),
                        'column': rel.get('column_name'),
                        'referenced_column': rel.get('referenced_column_name'),
                        'delete_action': rel.get('delete_referential_action'),
                        'update_action': rel.get('update_referential_action')
                    },
                    label=f"{rel.get('column_name')} → {rel.get('referenced_column_name')}"
                )
                self.edges.append(edge)
    
    def _build_dependency_graph(self, options: Dict[str, Any]):
        """Build nodes and edges for dependency graph including views and procedures."""
        # Include tables
        self._build_relationship_diagram(options)
        
        # Add views
        views = self.schema_data.get('views', [])
        schema_filter = options.get('schema_filter')
        
        if schema_filter:
            views = [v for v in views if v.get('schema_name') in schema_filter]
        
        for view in views:
            view_name = f"{view.get('schema_name', 'dbo')}.{view.get('view_name')}"
            
            node = Node(
                id=view_name,
                label=view.get('view_name'),
                type='view',
                properties={
                    'schema': view.get('schema_name', 'dbo'),
                    'column_count': len(view.get('columns', [])),
                    'definition_length': len(view.get('definition', '')),
                    'is_updatable': view.get('is_updatable', False)
                }
            )
            self.nodes[view_name] = node
            
            # Try to identify view dependencies from definition
            definition = view.get('definition', '').upper()
            for table_name in self.nodes:
                if self.nodes[table_name].type == 'table':
                    # Simple heuristic: check if table name appears in view definition
                    table_simple_name = table_name.split('.')[-1].upper()
                    if table_simple_name in definition:
                        edge = Edge(
                            source=view_name,
                            target=table_name,
                            type='dependency',
                            properties={'dependency_type': 'table_reference'},
                            label='depends on'
                        )
                        self.edges.append(edge)
        
        # Add stored procedures (simplified)
        procedures = self.schema_data.get('stored_procedures', [])
        if schema_filter:
            procedures = [p for p in procedures if p.get('schema_name') in schema_filter]
        
        for proc in procedures[:20]:  # Limit to prevent overcrowding
            proc_name = f"{proc.get('schema_name', 'dbo')}.{proc.get('procedure_name')}"
            
            node = Node(
                id=proc_name,
                label=proc.get('procedure_name'),
                type='procedure',
                properties={
                    'schema': proc.get('schema_name', 'dbo'),
                    'parameter_count': len(proc.get('parameters', [])),
                    'definition_length': len(proc.get('definition', ''))
                }
            )
            self.nodes[proc_name] = node
    
    def _build_hierarchical_view(self, options: Dict[str, Any]):
        """Build hierarchical view based on schema organization."""
        # Group objects by schema
        schemas = {}
        
        # Process tables
        for table in self.schema_data.get('tables', []):
            schema_name = table.get('schema_name', 'dbo')
            if schema_name not in schemas:
                schemas[schema_name] = {'tables': [], 'views': [], 'procedures': []}
            schemas[schema_name]['tables'].append(table)
        
        # Process views
        for view in self.schema_data.get('views', []):
            schema_name = view.get('schema_name', 'dbo')
            if schema_name not in schemas:
                schemas[schema_name] = {'tables': [], 'views': [], 'procedures': []}
            schemas[schema_name]['views'].append(view)
        
        # Process procedures
        for proc in self.schema_data.get('stored_procedures', []):
            schema_name = proc.get('schema_name', 'dbo')
            if schema_name not in schemas:
                schemas[schema_name] = {'tables': [], 'views': [], 'procedures': []}
            schemas[schema_name]['procedures'].append(proc)
        
        # Create schema nodes
        for schema_name, objects in schemas.items():
            schema_node_id = f"schema_{schema_name}"
            node = Node(
                id=schema_node_id,
                label=schema_name,
                type='schema',
                properties={
                    'table_count': len(objects['tables']),
                    'view_count': len(objects['views']),
                    'procedure_count': len(objects['procedures']),
                    'total_objects': len(objects['tables']) + len(objects['views']) + len(objects['procedures'])
                }
            )
            self.nodes[schema_node_id] = node
            
            # Add object nodes and edges to schema
            for table in objects['tables']:
                table_name = f"{schema_name}.{table.get('table_name')}"
                table_node = Node(
                    id=table_name,
                    label=table.get('table_name'),
                    type='table',
                    properties={
                        'parent_schema': schema_name,
                        'column_count': len(table.get('columns', [])),
                        'row_count': table.get('row_count', 0)
                    }
                )
                self.nodes[table_name] = table_node
                
                # Add edge from schema to table
                edge = Edge(
                    source=schema_node_id,
                    target=table_name,
                    type='contains',
                    properties={'relationship_type': 'schema_contains_table'},
                    label='contains'
                )
                self.edges.append(edge)
    
    def _build_circular_layout(self, options: Dict[str, Any]):
        """Build circular layout focusing on a central object."""
        center_object = options.get('center_object')
        if not center_object:
            # Default to the table with most relationships
            center_object = self._find_most_connected_table()
        
        # Start with relationship diagram
        self._build_relationship_diagram(options)
        
        # Mark the center object
        if center_object in self.nodes:
            self.nodes[center_object].properties['is_center'] = True
    
    def _find_most_connected_table(self) -> Optional[str]:
        """Find the table with the most foreign key relationships."""
        relationships = self.schema_data.get('relationships', {}).get('foreign_keys', [])
        
        connection_count = {}
        for rel in relationships:
            source = f"{rel.get('table_schema', 'dbo')}.{rel.get('table_name')}"
            target = f"{rel.get('referenced_table_schema', 'dbo')}.{rel.get('referenced_table_name')}"
            
            connection_count[source] = connection_count.get(source, 0) + 1
            connection_count[target] = connection_count.get(target, 0) + 1
        
        if connection_count:
            return max(connection_count, key=connection_count.get)
        return None
    
    def _apply_layout(self, viz_type: VisualizationType, options: Dict[str, Any]):
        """Apply layout algorithm to position nodes."""
        if viz_type == VisualizationType.CIRCULAR_LAYOUT:
            self._apply_circular_layout(options)
        elif viz_type == VisualizationType.HIERARCHICAL_VIEW:
            self._apply_hierarchical_layout(options)
        else:
            self._apply_force_directed_layout(options)
    
    def _apply_circular_layout(self, options: Dict[str, Any]):
        """Apply circular layout with center object."""
        import math
        
        center_object = options.get('center_object')
        if not center_object or center_object not in self.nodes:
            center_object = self._find_most_connected_table()
        
        if not center_object:
            return
        
        # Position center object
        self.nodes[center_object].x = 0
        self.nodes[center_object].y = 0
        
        # Find connected objects
        connected_objects = set()
        for edge in self.edges:
            if edge.source == center_object:
                connected_objects.add(edge.target)
            elif edge.target == center_object:
                connected_objects.add(edge.source)
        
        # Position connected objects in a circle
        if connected_objects:
            angle_step = 2 * math.pi / len(connected_objects)
            radius = 200
            
            for i, obj_id in enumerate(connected_objects):
                angle = i * angle_step
                self.nodes[obj_id].x = radius * math.cos(angle)
                self.nodes[obj_id].y = radius * math.sin(angle)
        
        # Position remaining objects in outer circle
        remaining_objects = [node_id for node_id in self.nodes 
                           if node_id != center_object and node_id not in connected_objects]
        
        if remaining_objects:
            outer_radius = 350
            angle_step = 2 * math.pi / len(remaining_objects)
            
            for i, obj_id in enumerate(remaining_objects):
                angle = i * angle_step
                self.nodes[obj_id].x = outer_radius * math.cos(angle)
                self.nodes[obj_id].y = outer_radius * math.sin(angle)
    
    def _apply_hierarchical_layout(self, options: Dict[str, Any]):
        """Apply hierarchical layout for schema organization."""
        # Group nodes by type
        schema_nodes = [node for node in self.nodes.values() if node.type == 'schema']
        table_nodes = [node for node in self.nodes.values() if node.type == 'table']
        
        # Position schema nodes horizontally
        schema_spacing = 300
        for i, node in enumerate(schema_nodes):
            node.x = i * schema_spacing
            node.y = 0
        
        # Position tables under their schemas
        for schema_node in schema_nodes:
            schema_name = schema_node.label
            schema_tables = [node for node in table_nodes 
                           if node.properties.get('parent_schema') == schema_name]
            
            if schema_tables:
                table_spacing = 80
                start_x = schema_node.x - (len(schema_tables) - 1) * table_spacing / 2
                
                for i, table_node in enumerate(schema_tables):
                    table_node.x = start_x + i * table_spacing
                    table_node.y = 150
    
    def _apply_force_directed_layout(self, options: Dict[str, Any]):
        """Apply simple force-directed layout algorithm."""
        import math
        import random
        
        # Initialize random positions
        for node in self.nodes.values():
            node.x = random.uniform(-200, 200)
            node.y = random.uniform(-200, 200)
        
        # Simple force-directed algorithm (simplified)
        iterations = 50
        for _ in range(iterations):
            # Calculate repulsive forces between all nodes
            for node1 in self.nodes.values():
                force_x = 0
                force_y = 0
                
                for node2 in self.nodes.values():
                    if node1.id != node2.id:
                        dx = node1.x - node2.x
                        dy = node1.y - node2.y
                        distance = math.sqrt(dx*dx + dy*dy) + 0.1  # Avoid division by zero
                        
                        # Repulsive force
                        force = 1000 / (distance * distance)
                        force_x += force * dx / distance
                        force_y += force * dy / distance
                
                # Calculate attractive forces from edges
                for edge in self.edges:
                    other_node = None
                    if edge.source == node1.id:
                        other_node = self.nodes[edge.target]
                    elif edge.target == node1.id:
                        other_node = self.nodes[edge.source]
                    
                    if other_node:
                        dx = other_node.x - node1.x
                        dy = other_node.y - node1.y
                        distance = math.sqrt(dx*dx + dy*dy) + 0.1
                        
                        # Attractive force
                        force = distance / 100
                        force_x += force * dx / distance
                        force_y += force * dy / distance
                
                # Apply forces (with damping)
                damping = 0.1
                node1.x += force_x * damping
                node1.y += force_y * damping
    
    def _get_schema_names(self) -> List[str]:
        """Get list of schema names from the data."""
        schemas = set()
        
        for table in self.schema_data.get('tables', []):
            schemas.add(table.get('schema_name', 'dbo'))
        
        for view in self.schema_data.get('views', []):
            schemas.add(view.get('schema_name', 'dbo'))
        
        return sorted(list(schemas))
    
    def generate_html_visualization(self, viz_data: Dict[str, Any], 
                                  output_file: str = None) -> str:
        """Generate interactive HTML visualization using D3.js."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Database Dependency Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        #visualization {{ border: 1px solid #ccc; }}
        .controls {{ margin-bottom: 10px; }}
        .node {{ cursor: pointer; }}
        .node-table {{ fill: #4CAF50; stroke: #2E7D32; }}
        .node-view {{ fill: #2196F3; stroke: #1565C0; }}
        .node-procedure {{ fill: #FF9800; stroke: #E65100; }}
        .node-schema {{ fill: #9C27B0; stroke: #4A148C; }}
        .link {{ stroke: #999; stroke-width: 2px; }}
        .link-foreign_key {{ stroke: #4CAF50; }}
        .link-dependency {{ stroke: #2196F3; }}
        .link-contains {{ stroke: #9C27B0; }}
        .node-text {{ fill: white; text-anchor: middle; font-size: 12px; }}
        .tooltip {{ position: absolute; background: rgba(0,0,0,0.8); color: white; 
                    padding: 8px; border-radius: 4px; font-size: 12px; pointer-events: none; }}
    </style>
</head>
<body>
    <h1>Database Dependency Visualization</h1>
    <div class="controls">
        <button onclick="resetZoom()">Reset Zoom</button>
        <button onclick="toggleLabels()">Toggle Labels</button>
        <span>Visualization Type: {viz_type}</span>
        <span>Nodes: {node_count}</span>
        <span>Edges: {edge_count}</span>
    </div>
    <svg id="visualization" width="1000" height="600"></svg>
    <div id="tooltip" class="tooltip" style="display: none;"></div>

    <script>
        const data = {viz_data};
        
        const svg = d3.select("#visualization");
        const width = +svg.attr("width");
        const height = +svg.attr("height");
        
        const g = svg.append("g");
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", (event) => g.attr("transform", event.transform));
        
        svg.call(zoom);
        
        // Create links
        const links = g.selectAll(".link")
            .data(data.edges)
            .enter().append("line")
            .attr("class", d => `link link-${{d.type}}`)
            .attr("x1", d => getNodeById(d.source).x + width/2)
            .attr("y1", d => getNodeById(d.source).y + height/2)
            .attr("x2", d => getNodeById(d.target).x + width/2)
            .attr("y2", d => getNodeById(d.target).y + height/2);
        
        // Create nodes
        const nodes = g.selectAll(".node")
            .data(data.nodes)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${{d.x + width/2}}, ${{d.y + height/2}})`);
        
        nodes.append("circle")
            .attr("class", d => `node-${{d.type}}`)
            .attr("r", d => Math.max(20, Math.min(40, Math.sqrt(d.properties.column_count || 1) * 5)));
        
        nodes.append("text")
            .attr("class", "node-text")
            .attr("dy", 4)
            .text(d => d.label.length > 10 ? d.label.substring(0, 10) + "..." : d.label);
        
        // Add tooltips
        nodes.on("mouseover", function(event, d) {{
            const tooltip = d3.select("#tooltip");
            let content = `<strong>${{d.label}}</strong><br/>Type: ${{d.type}}<br/>`;
            
            if (d.properties.column_count) content += `Columns: ${{d.properties.column_count}}<br/>`;
            if (d.properties.row_count) content += `Rows: ${{d.properties.row_count}}<br/>`;
            if (d.properties.schema) content += `Schema: ${{d.properties.schema}}<br/>`;
            
            tooltip.html(content)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .style("display", "block");
        }})
        .on("mouseout", function() {{
            d3.select("#tooltip").style("display", "none");
        }});
        
        function getNodeById(id) {{
            return data.nodes.find(n => n.id === id);
        }}
        
        function resetZoom() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}
        
        let labelsVisible = true;
        function toggleLabels() {{
            labelsVisible = !labelsVisible;
            nodes.selectAll("text").style("display", labelsVisible ? "block" : "none");
        }}
    </script>
</body>
</html>
"""
        
        html_content = html_template.format(
            viz_data=json.dumps(viz_data),
            viz_type=viz_data['type'],
            node_count=viz_data['metadata']['node_count'],
            edge_count=viz_data['metadata']['edge_count']
        )
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML visualization saved to {output_file}")
        
        return html_content
    
    def export_svg(self, viz_data: Dict[str, Any], output_file: str):
        """Export visualization as SVG."""
        # This would require additional libraries like matplotlib or Graphviz
        # For now, we'll create a simple SVG representation
        
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <title>Database Visualization - {viz_data['type']}</title>
  <defs>
    <style>
      .node-table {{ fill: #4CAF50; stroke: #2E7D32; }}
      .node-view {{ fill: #2196F3; stroke: #1565C0; }}
      .node-procedure {{ fill: #FF9800; stroke: #E65100; }}
      .link {{ stroke: #999; stroke-width: 2px; }}
    </style>
  </defs>
  
  <!-- Edges -->
  <g id="edges">
"""
        
        for edge in viz_data['edges']:
            source_node = next((n for n in viz_data['nodes'] if n['id'] == edge['source']), None)
            target_node = next((n for n in viz_data['nodes'] if n['id'] == edge['target']), None)
            
            if source_node and target_node:
                svg_content += f"""    <line class="link" 
                      x1="{source_node['x'] + 400}" y1="{source_node['y'] + 300}"
                      x2="{target_node['x'] + 400}" y2="{target_node['y'] + 300}" />
"""
        
        svg_content += """  </g>
  
  <!-- Nodes -->
  <g id="nodes">
"""
        
        for node in viz_data['nodes']:
            radius = max(15, min(30, (node['properties'].get('column_count', 1) ** 0.5) * 3))
            svg_content += f"""    <circle class="node-{node['type']}" 
                    cx="{node['x'] + 400}" cy="{node['y'] + 300}" r="{radius}" />
    <text x="{node['x'] + 400}" y="{node['y'] + 300}" 
          text-anchor="middle" dy="4" font-size="10" fill="white">
      {node['label'][:8]}
    </text>
"""
        
        svg_content += """  </g>
</svg>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        logger.info(f"SVG visualization saved to {output_file}")
    
    def get_visualization_statistics(self, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the visualization."""
        node_types = {}
        edge_types = {}
        
        for node in viz_data['nodes']:
            node_type = node['type']
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        for edge in viz_data['edges']:
            edge_type = edge['type']
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            'total_nodes': len(viz_data['nodes']),
            'total_edges': len(viz_data['edges']),
            'node_types': node_types,
            'edge_types': edge_types,
            'schemas': viz_data['metadata']['schemas'],
            'visualization_type': viz_data['type']
        }
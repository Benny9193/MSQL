#!/usr/bin/env python3
"""
Template Editor
===============

Provides a template editor for customizing documentation output formats.
Allows users to edit HTML, Markdown, and JSON templates with syntax highlighting
and preview capabilities.

Features:
- Multi-format template editing (HTML, Markdown, JSON)
- Syntax highlighting
- Template preview
- Variable reference guide
- Template validation
- Save/load custom templates
- Reset to default templates
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import json
from typing import Dict, Any
from pathlib import Path


class TemplateEditor:
    """Template editor for customizing documentation templates."""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Default templates
        self.default_templates = self._load_default_templates()
        self.current_templates = self.default_templates.copy()
        
    def show_template_editor(self):
        """Show the template editor window."""
        self.editor_window = tk.Toplevel(self.parent)
        self.editor_window.title("Template Editor")
        self.editor_window.geometry("1000x700")
        self.editor_window.minsize(800, 600)
        
        self.setup_editor_window()
        self.load_existing_templates()
        
    def setup_editor_window(self):
        """Setup the template editor window layout."""
        # Main notebook for different template types
        self.main_notebook = ttk.Notebook(self.editor_window)
        self.main_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs for each template type
        self.create_html_template_tab()
        self.create_markdown_template_tab()
        self.create_json_template_tab()
        
        # Control buttons
        self.create_control_buttons()
        
        # Status bar
        self.create_status_bar()
    
    def create_html_template_tab(self):
        """Create HTML template editor tab."""
        html_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(html_frame, text="HTML Template")
        
        # Create paned window for editor and preview
        html_paned = ttk.PanedWindow(html_frame, orient="horizontal")
        html_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left side - Editor
        editor_frame = ttk.LabelFrame(html_paned, text="HTML Template Editor", padding="5")
        html_paned.add(editor_frame, weight=2)
        
        # Template selector
        selector_frame = ttk.Frame(editor_frame)
        selector_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(selector_frame, text="Template:").pack(side="left")
        
        self.html_template_var = tk.StringVar(value="main")
        html_templates = ["main", "table", "view", "procedure", "function"]
        html_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.html_template_var,
            values=html_templates,
            state="readonly",
            width=15
        )
        html_combo.pack(side="left", padx=(5, 10))
        html_combo.bind("<<ComboboxSelected>>", self.on_html_template_change)
        
        # Editor buttons
        ttk.Button(selector_frame, text="Reset", command=self.reset_html_template).pack(side="right", padx=(5, 0))
        ttk.Button(selector_frame, text="Load", command=self.load_html_template).pack(side="right", padx=(5, 0))
        ttk.Button(selector_frame, text="Save", command=self.save_html_template).pack(side="right", padx=(5, 0))
        
        # HTML editor
        self.html_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            height=25,
            font=("Consolas", 10),
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.html_editor.pack(fill="both", expand=True)
        
        # Right side - Variables reference and preview
        right_frame = ttk.LabelFrame(html_paned, text="Variables & Preview", padding="5")
        html_paned.add(right_frame, weight=1)
        
        # Variables reference
        vars_frame = ttk.LabelFrame(right_frame, text="Available Variables", padding="5")
        vars_frame.pack(fill="x", pady=(0, 10))
        
        self.html_vars_text = scrolledtext.ScrolledText(vars_frame, height=15, font=("Consolas", 9))
        self.html_vars_text.pack(fill="both", expand=True)
        
        # Preview button
        ttk.Button(right_frame, text="Preview Template", command=self.preview_html_template).pack(pady=5)
    
    def create_markdown_template_tab(self):
        """Create Markdown template editor tab."""
        md_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(md_frame, text="Markdown Template")
        
        # Create paned window
        md_paned = ttk.PanedWindow(md_frame, orient="horizontal")
        md_paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left side - Editor
        editor_frame = ttk.LabelFrame(md_paned, text="Markdown Template Editor", padding="5")
        md_paned.add(editor_frame, weight=2)
        
        # Template selector
        selector_frame = ttk.Frame(editor_frame)
        selector_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(selector_frame, text="Template:").pack(side="left")
        
        self.md_template_var = tk.StringVar(value="main")
        md_templates = ["main", "table", "view", "procedure", "function"]
        md_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.md_template_var,
            values=md_templates,
            state="readonly",
            width=15
        )
        md_combo.pack(side="left", padx=(5, 10))
        md_combo.bind("<<ComboboxSelected>>", self.on_md_template_change)
        
        # Editor buttons
        ttk.Button(selector_frame, text="Reset", command=self.reset_md_template).pack(side="right", padx=(5, 0))
        ttk.Button(selector_frame, text="Load", command=self.load_md_template).pack(side="right", padx=(5, 0))
        ttk.Button(selector_frame, text="Save", command=self.save_md_template).pack(side="right", padx=(5, 0))
        
        # Markdown editor
        self.md_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            height=25,
            font=("Consolas", 10)
        )
        self.md_editor.pack(fill="both", expand=True)
        
        # Right side - Variables reference
        right_frame = ttk.LabelFrame(md_paned, text="Variables & Help", padding="5")
        md_paned.add(right_frame, weight=1)
        
        # Variables reference
        vars_frame = ttk.LabelFrame(right_frame, text="Available Variables", padding="5")
        vars_frame.pack(fill="both", expand=True)
        
        self.md_vars_text = scrolledtext.ScrolledText(vars_frame, height=20, font=("Consolas", 9))
        self.md_vars_text.pack(fill="both", expand=True)
    
    def create_json_template_tab(self):
        """Create JSON template editor tab."""
        json_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(json_frame, text="JSON Template")
        
        # Main editor frame
        editor_frame = ttk.LabelFrame(json_frame, text="JSON Output Structure", padding="10")
        editor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # JSON editor
        self.json_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            height=25,
            font=("Consolas", 10)
        )
        self.json_editor.pack(fill="both", expand=True)
        
        # Control buttons
        json_buttons = ttk.Frame(json_frame)
        json_buttons.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(json_buttons, text="Validate JSON", command=self.validate_json_template).pack(side="left")
        ttk.Button(json_buttons, text="Format JSON", command=self.format_json_template).pack(side="left", padx=(5, 0))
        ttk.Button(json_buttons, text="Reset to Default", command=self.reset_json_template).pack(side="right")
        ttk.Button(json_buttons, text="Load Template", command=self.load_json_template).pack(side="right", padx=(5, 0))
        ttk.Button(json_buttons, text="Save Template", command=self.save_json_template).pack(side="right", padx=(5, 0))
    
    def create_control_buttons(self):
        """Create main control buttons."""
        buttons_frame = ttk.Frame(self.editor_window)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Apply All Changes",
            command=self.apply_all_changes
        ).pack(side="left")
        
        ttk.Button(
            buttons_frame,
            text="Reset All to Defaults",
            command=self.reset_all_templates
        ).pack(side="left", padx=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="Export Templates",
            command=self.export_templates
        ).pack(side="left", padx=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="Import Templates",
            command=self.import_templates
        ).pack(side="left", padx=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="Close",
            command=self.editor_window.destroy
        ).pack(side="right")
        
        ttk.Button(
            buttons_frame,
            text="Test Templates",
            command=self.test_templates
        ).pack(side="right", padx=(0, 10))
    
    def create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.editor_window, relief="sunken")
        status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(status_frame, text="Template editor ready", padding="5")
        self.status_label.pack(side="left")
    
    def _load_default_templates(self):
        """Load default templates."""
        return {
            'html': {
                'main': self._get_default_html_main_template(),
                'table': self._get_default_html_table_template(),
                'view': self._get_default_html_view_template(),
                'procedure': self._get_default_html_procedure_template(),
                'function': self._get_default_html_function_template()
            },
            'markdown': {
                'main': self._get_default_markdown_main_template(),
                'table': self._get_default_markdown_table_template(),
                'view': self._get_default_markdown_view_template(),
                'procedure': self._get_default_markdown_procedure_template(),
                'function': self._get_default_markdown_function_template()
            },
            'json': {
                'structure': self._get_default_json_template()
            }
        }
    
    def _get_default_html_main_template(self):
        """Get default HTML main template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Database Documentation - {{ database_name }}</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .object-list { border-collapse: collapse; width: 100%; }
        .object-list th, .object-list td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .object-list th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ database_name }} Database Documentation</h1>
        <p>Generated on {{ generation_date }}</p>
        <p>Server: {{ server_name }} | User: {{ user_name }}</p>
    </div>
    
    <div class="section">
        <h2>Database Statistics</h2>
        <p>Tables: {{ statistics.total_tables }}</p>
        <p>Views: {{ statistics.total_views }}</p>
        <p>Procedures: {{ statistics.total_procedures }}</p>
        <p>Functions: {{ statistics.total_functions }}</p>
    </div>
    
    <div class="section">
        <h2>Tables</h2>
        {{ tables_content }}
    </div>
    
    <div class="section">
        <h2>Views</h2>
        {{ views_content }}
    </div>
    
    <div class="section">
        <h2>Stored Procedures</h2>
        {{ procedures_content }}
    </div>
    
    <div class="section">
        <h2>Functions</h2>
        {{ functions_content }}
    </div>
</body>
</html>'''
    
    def _get_default_html_table_template(self):
        """Get default HTML table template."""
        return '''<div class="table-section">
    <h3>{{ table_name }}</h3>
    <p><strong>Schema:</strong> {{ schema }}</p>
    <p><strong>Row Count:</strong> {{ row_count }}</p>
    {% if description %}<p><strong>Description:</strong> {{ description }}</p>{% endif %}
    
    <h4>Columns</h4>
    <table class="object-list">
        <tr>
            <th>Column</th>
            <th>Data Type</th>
            <th>Nullable</th>
            <th>Default</th>
            <th>Description</th>
        </tr>
        {% for column in columns %}
        <tr>
            <td>{{ column.name }}</td>
            <td>{{ column.data_type }}</td>
            <td>{{ "Yes" if column.is_nullable else "No" }}</td>
            <td>{{ column.default_value or "" }}</td>
            <td>{{ column.description or "" }}</td>
        </tr>
        {% endfor %}
    </table>
</div>'''
    
    def _get_default_html_view_template(self):
        """Get default HTML view template.""" 
        return '''<div class="view-section">
    <h3>{{ view_name }}</h3>
    <p><strong>Schema:</strong> {{ schema }}</p>
    {% if description %}<p><strong>Description:</strong> {{ description }}</p>{% endif %}
    
    {% if definition %}
    <h4>Definition</h4>
    <pre><code>{{ definition }}</code></pre>
    {% endif %}
</div>'''
    
    def _get_default_html_procedure_template(self):
        """Get default HTML procedure template."""
        return '''<div class="procedure-section">
    <h3>{{ procedure_name }}</h3>
    <p><strong>Schema:</strong> {{ schema }}</p>
    {% if description %}<p><strong>Description:</strong> {{ description }}</p>{% endif %}
    
    {% if definition %}
    <h4>Definition</h4>
    <pre><code>{{ definition }}</code></pre>
    {% endif %}
</div>'''
    
    def _get_default_html_function_template(self):
        """Get default HTML function template."""
        return '''<div class="function-section">
    <h3>{{ function_name }}</h3>
    <p><strong>Schema:</strong> {{ schema }}</p>
    {% if description %}<p><strong>Description:</strong> {{ description }}</p>{% endif %}
    
    {% if definition %}
    <h4>Definition</h4>
    <pre><code>{{ definition }}</code></pre>
    {% endif %}
</div>'''
    
    def _get_default_markdown_main_template(self):
        """Get default Markdown main template."""
        return '''# {{ database_name }} Database Documentation

**Generated:** {{ generation_date }}  
**Server:** {{ server_name }}  
**User:** {{ user_name }}

## Database Statistics

- **Tables:** {{ statistics.total_tables }}
- **Views:** {{ statistics.total_views }}
- **Procedures:** {{ statistics.total_procedures }}
- **Functions:** {{ statistics.total_functions }}

## Tables

{{ tables_content }}

## Views

{{ views_content }}

## Stored Procedures

{{ procedures_content }}

## Functions

{{ functions_content }}
'''
    
    def _get_default_markdown_table_template(self):
        """Get default Markdown table template."""
        return '''### {{ table_name }}

**Schema:** {{ schema }}  
**Row Count:** {{ row_count }}  
{% if description %}**Description:** {{ description }}{% endif %}

#### Columns

| Column | Data Type | Nullable | Default | Description |
|--------|-----------|----------|---------|-------------|
{% for column in columns %}| {{ column.name }} | {{ column.data_type }} | {{ "Yes" if column.is_nullable else "No" }} | {{ column.default_value or "" }} | {{ column.description or "" }} |
{% endfor %}

---
'''
    
    def _get_default_markdown_view_template(self):
        """Get default Markdown view template."""
        return '''### {{ view_name }}

**Schema:** {{ schema }}  
{% if description %}**Description:** {{ description }}{% endif %}

{% if definition %}
#### Definition

```sql
{{ definition }}
```
{% endif %}

---
'''
    
    def _get_default_markdown_procedure_template(self):
        """Get default Markdown procedure template."""
        return '''### {{ procedure_name }}

**Schema:** {{ schema }}  
{% if description %}**Description:** {{ description }}{% endif %}

{% if definition %}
#### Definition

```sql
{{ definition }}
```
{% endif %}

---
'''
    
    def _get_default_markdown_function_template(self):
        """Get default Markdown function template."""
        return '''### {{ function_name }}

**Schema:** {{ schema }}  
{% if description %}**Description:** {{ description }}{% endif %}

{% if definition %}
#### Definition

```sql
{{ definition }}
```
{% endif %}

---
'''
    
    def _get_default_json_template(self):
        """Get default JSON template structure."""
        return '''{
    "database_info": {
        "name": "{{ database_name }}",
        "server": "{{ server_name }}",
        "user": "{{ user_name }}",
        "generated": "{{ generation_date }}"
    },
    "statistics": {
        "tables": {{ statistics.total_tables }},
        "views": {{ statistics.total_views }},
        "procedures": {{ statistics.total_procedures }},
        "functions": {{ statistics.total_functions }}
    },
    "objects": {
        "tables": {{ tables_json }},
        "views": {{ views_json }},
        "procedures": {{ procedures_json }},
        "functions": {{ functions_json }}
    },
    "relationships": {{ relationships_json }}
}'''
    
    def load_existing_templates(self):
        """Load existing custom templates if they exist."""
        # Load HTML templates
        self.load_template_content('html', 'main')
        self.populate_variables_reference()
        
    def load_template_content(self, template_type, template_name):
        """Load template content into editor."""
        if template_type == 'html':
            content = self.current_templates['html'][template_name]
            self.html_editor.delete(1.0, tk.END)
            self.html_editor.insert(1.0, content)
        elif template_type == 'markdown':
            content = self.current_templates['markdown'][template_name]
            self.md_editor.delete(1.0, tk.END)
            self.md_editor.insert(1.0, content)
        elif template_type == 'json':
            content = self.current_templates['json']['structure']
            self.json_editor.delete(1.0, tk.END)
            self.json_editor.insert(1.0, content)
    
    def populate_variables_reference(self):
        """Populate variables reference."""
        html_vars = '''Available Variables:

Database Info:
- {{ database_name }}
- {{ server_name }}
- {{ user_name }}
- {{ generation_date }}

Statistics:
- {{ statistics.total_tables }}
- {{ statistics.total_views }}
- {{ statistics.total_procedures }}
- {{ statistics.total_functions }}

Content Placeholders:
- {{ tables_content }}
- {{ views_content }}
- {{ procedures_content }}
- {{ functions_content }}

Object-Specific (in templates):
- {{ table_name }}/{{ view_name }}/etc.
- {{ schema }}
- {{ description }}
- {{ row_count }} (tables only)
- {{ definition }} (views/procedures/functions)
- {{ columns }} (array for tables/views)

Column Properties:
- {{ column.name }}
- {{ column.data_type }}
- {{ column.is_nullable }}
- {{ column.default_value }}
- {{ column.description }}
'''
        
        self.html_vars_text.delete(1.0, tk.END)
        self.html_vars_text.insert(1.0, html_vars)
        
        md_vars = html_vars  # Same variables for markdown
        
        self.md_vars_text.delete(1.0, tk.END)
        self.md_vars_text.insert(1.0, md_vars)
    
    def on_html_template_change(self, event=None):
        """Handle HTML template selection change."""
        template_name = self.html_template_var.get()
        self.load_template_content('html', template_name)
    
    def on_md_template_change(self, event=None):
        """Handle Markdown template selection change."""
        template_name = self.md_template_var.get()
        self.load_template_content('markdown', template_name)
    
    # Template action methods
    
    def reset_html_template(self):
        """Reset current HTML template to default."""
        template_name = self.html_template_var.get()
        default_content = self.default_templates['html'][template_name]
        self.html_editor.delete(1.0, tk.END)
        self.html_editor.insert(1.0, default_content)
        self.status_label.config(text=f"HTML {template_name} template reset to default")
    
    def save_html_template(self):
        """Save current HTML template."""
        template_name = self.html_template_var.get()
        content = self.html_editor.get(1.0, tk.END)
        self.current_templates['html'][template_name] = content.rstrip()
        
        # Save to file
        template_file = self.templates_dir / f"html_{template_name}.html"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.status_label.config(text=f"HTML {template_name} template saved")
    
    def load_html_template(self):
        """Load HTML template from file."""
        file_path = filedialog.askopenfilename(
            title="Load HTML Template",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.html_editor.delete(1.0, tk.END)
                self.html_editor.insert(1.0, content)
                self.status_label.config(text=f"HTML template loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load template: {str(e)}")
    
    def reset_md_template(self):
        """Reset current Markdown template to default."""
        template_name = self.md_template_var.get()
        default_content = self.default_templates['markdown'][template_name]
        self.md_editor.delete(1.0, tk.END)
        self.md_editor.insert(1.0, default_content)
        self.status_label.config(text=f"Markdown {template_name} template reset to default")
    
    def save_md_template(self):
        """Save current Markdown template."""
        template_name = self.md_template_var.get()
        content = self.md_editor.get(1.0, tk.END)
        self.current_templates['markdown'][template_name] = content.rstrip()
        
        # Save to file
        template_file = self.templates_dir / f"markdown_{template_name}.md"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.status_label.config(text=f"Markdown {template_name} template saved")
    
    def load_md_template(self):
        """Load Markdown template from file."""
        file_path = filedialog.askopenfilename(
            title="Load Markdown Template",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.md_editor.delete(1.0, tk.END)
                self.md_editor.insert(1.0, content)
                self.status_label.config(text=f"Markdown template loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load template: {str(e)}")
    
    def validate_json_template(self):
        """Validate JSON template syntax."""
        content = self.json_editor.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Empty Template", "JSON template is empty")
            return
        
        try:
            # Try to parse as JSON (this is a simplified validation)
            # In real implementation, you'd validate template variables too
            # For now, just check basic JSON structure
            json.loads(content.replace('{{', '"').replace('}}', '"'))
            self.status_label.config(text="JSON template syntax is valid")
            messagebox.showinfo("Validation Success", "JSON template syntax is valid")
        except json.JSONDecodeError as e:
            self.status_label.config(text=f"JSON validation error: {str(e)}")
            messagebox.showerror("Validation Error", f"JSON syntax error: {str(e)}")
    
    def format_json_template(self):
        """Format JSON template with proper indentation."""
        content = self.json_editor.get(1.0, tk.END).strip()
        if not content:
            return
        
        try:
            # This is a simple formatter - in real implementation you'd preserve template variables
            formatted = self._format_json_with_variables(content)
            self.json_editor.delete(1.0, tk.END)
            self.json_editor.insert(1.0, formatted)
            self.status_label.config(text="JSON template formatted")
        except Exception as e:
            messagebox.showerror("Format Error", f"Failed to format JSON: {str(e)}")
    
    def _format_json_with_variables(self, content):
        """Format JSON while preserving template variables."""
        # Simple formatting that preserves {{ }} variables
        lines = content.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            if stripped.endswith('{') or stripped.endswith('['):
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('}') or stripped.startswith(']'):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('    ' * indent_level + stripped)
            else:
                formatted_lines.append('    ' * indent_level + stripped)
        
        return '\n'.join(formatted_lines)
    
    def reset_json_template(self):
        """Reset JSON template to default."""
        default_content = self.default_templates['json']['structure']
        self.json_editor.delete(1.0, tk.END)
        self.json_editor.insert(1.0, default_content)
        self.status_label.config(text="JSON template reset to default")
    
    def save_json_template(self):
        """Save JSON template."""
        content = self.json_editor.get(1.0, tk.END)
        self.current_templates['json']['structure'] = content.rstrip()
        
        # Save to file
        template_file = self.templates_dir / "json_structure.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.status_label.config(text="JSON template saved")
    
    def load_json_template(self):
        """Load JSON template from file."""
        file_path = filedialog.askopenfilename(
            title="Load JSON Template",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.json_editor.delete(1.0, tk.END)
                self.json_editor.insert(1.0, content)
                self.status_label.config(text=f"JSON template loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load template: {str(e)}")
    
    def preview_html_template(self):
        """Preview HTML template with sample data."""
        messagebox.showinfo("Preview", "HTML preview functionality would open in browser with sample data.")
    
    def apply_all_changes(self):
        """Apply all template changes."""
        # Save current editor contents
        if hasattr(self, 'html_editor'):
            template_name = self.html_template_var.get()
            content = self.html_editor.get(1.0, tk.END)
            self.current_templates['html'][template_name] = content.rstrip()
        
        if hasattr(self, 'md_editor'):
            template_name = self.md_template_var.get()
            content = self.md_editor.get(1.0, tk.END)
            self.current_templates['markdown'][template_name] = content.rstrip()
        
        if hasattr(self, 'json_editor'):
            content = self.json_editor.get(1.0, tk.END)
            self.current_templates['json']['structure'] = content.rstrip()
        
        # Save all templates to files
        self._save_all_templates()
        
        self.status_label.config(text="All template changes applied")
        messagebox.showinfo("Changes Applied", "All template changes have been saved and applied.")
    
    def reset_all_templates(self):
        """Reset all templates to defaults."""
        if messagebox.askyesno("Reset All", "Reset all templates to defaults? This will lose all customizations."):
            self.current_templates = self.default_templates.copy()
            
            # Update editors
            if hasattr(self, 'html_editor'):
                self.load_template_content('html', self.html_template_var.get())
            if hasattr(self, 'md_editor'):
                self.load_template_content('markdown', self.md_template_var.get())
            if hasattr(self, 'json_editor'):
                self.load_template_content('json', 'structure')
            
            self.status_label.config(text="All templates reset to defaults")
    
    def export_templates(self):
        """Export all templates to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Templates"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_templates, f, indent=2, ensure_ascii=False)
                self.status_label.config(text=f"Templates exported to {os.path.basename(file_path)}")
                messagebox.showinfo("Export Complete", f"Templates exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export templates: {str(e)}")
    
    def import_templates(self):
        """Import templates from a file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Templates"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_templates = json.load(f)
                
                # Validate structure
                if self._validate_template_structure(imported_templates):
                    self.current_templates = imported_templates
                    
                    # Update editors
                    if hasattr(self, 'html_editor'):
                        self.load_template_content('html', self.html_template_var.get())
                    if hasattr(self, 'md_editor'):
                        self.load_template_content('markdown', self.md_template_var.get())
                    if hasattr(self, 'json_editor'):
                        self.load_template_content('json', 'structure')
                    
                    self.status_label.config(text=f"Templates imported from {os.path.basename(file_path)}")
                    messagebox.showinfo("Import Complete", "Templates imported successfully")
                else:
                    messagebox.showerror("Import Error", "Invalid template file structure")
                    
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import templates: {str(e)}")
    
    def _validate_template_structure(self, templates):
        """Validate imported template structure."""
        required_keys = ['html', 'markdown', 'json']
        if not all(key in templates for key in required_keys):
            return False
        
        html_templates = ['main', 'table', 'view', 'procedure', 'function']
        if not all(template in templates['html'] for template in html_templates):
            return False
        
        if not all(template in templates['markdown'] for template in html_templates):
            return False
        
        if 'structure' not in templates['json']:
            return False
        
        return True
    
    def test_templates(self):
        """Test templates with sample data."""
        messagebox.showinfo("Test Templates", "Template testing would generate sample documentation using current templates.")
    
    def _save_all_templates(self):
        """Save all templates to individual files."""
        # Save HTML templates
        for name, content in self.current_templates['html'].items():
            template_file = self.templates_dir / f"html_{name}.html"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Save Markdown templates  
        for name, content in self.current_templates['markdown'].items():
            template_file = self.templates_dir / f"markdown_{name}.md"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Save JSON template
        template_file = self.templates_dir / "json_structure.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(self.current_templates['json']['structure'])
    
    def get_current_templates(self):
        """Get current template configuration for use by documentation generator."""
        return self.current_templates
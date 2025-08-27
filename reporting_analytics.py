#!/usr/bin/env python3
"""
Advanced Reporting and Analytics Module
=====================================

Provides comprehensive reporting and analytics capabilities for database documentation,
including trend analysis, usage statistics, performance metrics, and visual dashboards.

Features:
- Database documentation trend analysis
- Usage statistics and patterns
- Performance metrics tracking
- Interactive charts and visualizations
- Export capabilities for reports
- Scheduled report generation
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from collections import defaultdict, Counter


class ReportingDatabase:
    """Manages the reporting database for storing analytics data."""
    
    def __init__(self, db_path: str = "reporting.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the reporting database with required tables."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Documentation generation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documentation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    database_name TEXT NOT NULL,
                    server_name TEXT,
                    tables_count INTEGER,
                    views_count INTEGER,
                    procedures_count INTEGER,
                    functions_count INTEGER,
                    relationships_count INTEGER,
                    generation_time_seconds REAL,
                    output_formats TEXT, -- JSON array of formats
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT
                )
            """)
            
            # Database schema changes tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    database_name TEXT NOT NULL,
                    change_type TEXT, -- 'table_added', 'table_removed', 'column_added', etc.
                    object_name TEXT,
                    object_type TEXT,
                    change_details TEXT -- JSON with change details
                )
            """)
            
            # Usage statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL, -- 'generate_docs', 'view_report', 'export_data', etc.
                    database_name TEXT,
                    details TEXT -- JSON with additional details
                )
            """)
            
            # Performance metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    database_name TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    unit TEXT
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def log_documentation_run(self, database_name: str, server_name: str, 
                            tables_count: int, views_count: int, procedures_count: int,
                            functions_count: int, relationships_count: int,
                            generation_time: float, output_formats: List[str],
                            success: bool = True, error_message: str = None):
        """Log a documentation generation run."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documentation_runs 
                (database_name, server_name, tables_count, views_count, procedures_count,
                 functions_count, relationships_count, generation_time_seconds, 
                 output_formats, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (database_name, server_name, tables_count, views_count, procedures_count,
                  functions_count, relationships_count, generation_time, 
                  json.dumps(output_formats), success, error_message))
            conn.commit()
        finally:
            conn.close()
    
    def log_usage_action(self, action: str, database_name: str = None, details: Dict = None):
        """Log a usage action."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usage_stats (action, database_name, details)
                VALUES (?, ?, ?)
            """, (action, database_name, json.dumps(details) if details else None))
            conn.commit()
        finally:
            conn.close()
    
    def get_documentation_trends(self, days: int = 30) -> List[Dict]:
        """Get documentation generation trends."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documentation_runs 
                WHERE timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            """.format(days))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_usage_statistics(self, days: int = 30) -> List[Dict]:
        """Get usage statistics."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM usage_stats 
                WHERE timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
            """.format(days))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()


class AnalyticsEngine:
    """Core analytics engine for processing and analyzing data."""
    
    def __init__(self, reporting_db: ReportingDatabase):
        self.db = reporting_db
    
    def analyze_documentation_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze documentation generation trends."""
        runs = self.db.get_documentation_trends(days)
        
        if not runs:
            return {
                'total_runs': 0,
                'success_rate': 0,
                'avg_generation_time': 0,
                'trends': {},
                'top_databases': []
            }
        
        # Basic statistics
        total_runs = len(runs)
        successful_runs = sum(1 for run in runs if run['success'])
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        
        # Average generation time
        generation_times = [run['generation_time_seconds'] for run in runs if run['generation_time_seconds']]
        avg_generation_time = sum(generation_times) / len(generation_times) if generation_times else 0
        
        # Daily trends
        daily_counts = defaultdict(int)
        for run in runs:
            date = datetime.fromisoformat(run['timestamp']).date()
            daily_counts[str(date)] += 1
        
        # Top databases
        db_counts = Counter(run['database_name'] for run in runs)
        top_databases = db_counts.most_common(10)
        
        # Schema complexity trends
        complexity_trends = []
        for run in runs:
            total_objects = (run['tables_count'] or 0) + (run['views_count'] or 0) + \
                           (run['procedures_count'] or 0) + (run['functions_count'] or 0)
            complexity_trends.append({
                'timestamp': run['timestamp'],
                'database_name': run['database_name'],
                'total_objects': total_objects,
                'relationships': run['relationships_count'] or 0
            })
        
        return {
            'total_runs': total_runs,
            'success_rate': success_rate,
            'avg_generation_time': avg_generation_time,
            'daily_trends': dict(daily_counts),
            'top_databases': top_databases,
            'complexity_trends': complexity_trends
        }
    
    def analyze_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze usage patterns and user behavior."""
        usage_data = self.db.get_usage_statistics(days)
        
        if not usage_data:
            return {
                'total_actions': 0,
                'action_breakdown': {},
                'hourly_patterns': {},
                'peak_usage_times': []
            }
        
        # Action breakdown
        action_counts = Counter(action['action'] for action in usage_data)
        
        # Hourly usage patterns
        hourly_patterns = defaultdict(int)
        for action in usage_data:
            hour = datetime.fromisoformat(action['timestamp']).hour
            hourly_patterns[hour] += 1
        
        # Peak usage times
        sorted_hours = sorted(hourly_patterns.items(), key=lambda x: x[1], reverse=True)
        peak_usage_times = sorted_hours[:5]  # Top 5 peak hours
        
        return {
            'total_actions': len(usage_data),
            'action_breakdown': dict(action_counts),
            'hourly_patterns': dict(hourly_patterns),
            'peak_usage_times': peak_usage_times
        }
    
    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        doc_trends = self.analyze_documentation_trends(days)
        usage_patterns = self.analyze_usage_patterns(days)
        
        # Performance insights
        insights = []
        
        if doc_trends['success_rate'] < 90:
            insights.append("Low success rate detected. Consider investigating common failure causes.")
        
        if doc_trends['avg_generation_time'] > 300:  # 5 minutes
            insights.append("High average generation time. Consider optimizing queries or database performance.")
        
        # Top performing databases (by success rate)
        runs = self.db.get_documentation_trends(days)
        db_performance = defaultdict(lambda: {'total': 0, 'success': 0})
        
        for run in runs:
            db_name = run['database_name']
            db_performance[db_name]['total'] += 1
            if run['success']:
                db_performance[db_name]['success'] += 1
        
        db_success_rates = []
        for db_name, stats in db_performance.items():
            success_rate = (stats['success'] / stats['total']) * 100
            db_success_rates.append((db_name, success_rate, stats['total']))
        
        db_success_rates.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'documentation_trends': doc_trends,
            'usage_patterns': usage_patterns,
            'performance_insights': insights,
            'database_performance': db_success_rates[:10],
            'report_generated': datetime.now().isoformat()
        }


class ReportExporter:
    """Handles exporting reports to various formats."""
    
    @staticmethod
    def export_to_csv(data: Dict[str, Any], filename: str):
        """Export report data to CSV format."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write summary data
            writer.writerow(['Report Summary'])
            writer.writerow(['Generated', data.get('report_generated', '')])
            writer.writerow([])
            
            # Documentation trends
            if 'documentation_trends' in data:
                trends = data['documentation_trends']
                writer.writerow(['Documentation Trends'])
                writer.writerow(['Total Runs', trends['total_runs']])
                writer.writerow(['Success Rate (%)', f"{trends['success_rate']:.1f}"])
                writer.writerow(['Avg Generation Time (seconds)', f"{trends['avg_generation_time']:.1f}"])
                writer.writerow([])
                
                # Top databases
                writer.writerow(['Top Databases'])
                writer.writerow(['Database Name', 'Documentation Count'])
                for db_name, count in trends['top_databases']:
                    writer.writerow([db_name, count])
                writer.writerow([])
            
            # Usage patterns
            if 'usage_patterns' in data:
                patterns = data['usage_patterns']
                writer.writerow(['Usage Patterns'])
                writer.writerow(['Total Actions', patterns['total_actions']])
                writer.writerow([])
                
                writer.writerow(['Action Breakdown'])
                writer.writerow(['Action', 'Count'])
                for action, count in patterns['action_breakdown'].items():
                    writer.writerow([action, count])
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], filename: str):
        """Export report data to JSON format."""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_to_html(data: Dict[str, Any], filename: str):
        """Export report data to HTML format."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Documentation Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #007acc; }}
                .metric-label {{ font-size: 14px; color: #666; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .insights {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Database Documentation Analytics Report</h1>
                <p>Generated: {report_date}</p>
            </div>
            
            <div class="section">
                <h2>Documentation Performance</h2>
                <div class="metric">
                    <div class="metric-value">{total_runs}</div>
                    <div class="metric-label">Total Runs</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{success_rate:.1f}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{avg_time:.1f}s</div>
                    <div class="metric-label">Avg Generation Time</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Top Databases</h2>
                <table>
                    <tr><th>Database Name</th><th>Documentation Count</th></tr>
                    {top_databases_rows}
                </table>
            </div>
            
            <div class="section">
                <h2>Usage Statistics</h2>
                <div class="metric">
                    <div class="metric-value">{total_actions}</div>
                    <div class="metric-label">Total Actions</div>
                </div>
                <table>
                    <tr><th>Action</th><th>Count</th></tr>
                    {action_rows}
                </table>
            </div>
            
            <div class="section">
                <h2>Performance Insights</h2>
                <div class="insights">
                    {insights_list}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Extract data for template
        doc_trends = data.get('documentation_trends', {})
        usage_patterns = data.get('usage_patterns', {})
        
        # Generate table rows
        top_databases_rows = ""
        for db_name, count in doc_trends.get('top_databases', []):
            top_databases_rows += f"<tr><td>{db_name}</td><td>{count}</td></tr>"
        
        action_rows = ""
        for action, count in usage_patterns.get('action_breakdown', {}).items():
            action_rows += f"<tr><td>{action}</td><td>{count}</td></tr>"
        
        insights_list = ""
        for insight in data.get('performance_insights', []):
            insights_list += f"<li>{insight}</li>"
        if insights_list:
            insights_list = f"<ul>{insights_list}</ul>"
        else:
            insights_list = "<p>No specific insights at this time.</p>"
        
        # Format HTML
        html_content = html_template.format(
            report_date=data.get('report_generated', datetime.now().isoformat()),
            total_runs=doc_trends.get('total_runs', 0),
            success_rate=doc_trends.get('success_rate', 0),
            avg_time=doc_trends.get('avg_generation_time', 0),
            total_actions=usage_patterns.get('total_actions', 0),
            top_databases_rows=top_databases_rows,
            action_rows=action_rows,
            insights_list=insights_list
        )
        
        with open(filename, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)


class ChartGenerator:
    """Generates various charts and visualizations for analytics."""
    
    @staticmethod
    def create_trends_chart(data: Dict[str, Any], figure: Figure) -> None:
        """Create documentation trends chart."""
        figure.clear()
        
        doc_trends = data.get('documentation_trends', {})
        daily_trends = doc_trends.get('daily_trends', {})
        
        if not daily_trends:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Documentation Generation Trends')
            return
        
        # Sort dates
        dates = sorted(daily_trends.keys())
        counts = [daily_trends[date] for date in dates]
        
        ax = figure.add_subplot(111)
        ax.plot(dates, counts, marker='o', linewidth=2, markersize=6)
        ax.set_title('Documentation Generation Trends (Last 30 Days)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Generations')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        figure.tight_layout()
    
    @staticmethod
    def create_usage_patterns_chart(data: Dict[str, Any], figure: Figure) -> None:
        """Create usage patterns pie chart."""
        figure.clear()
        
        usage_patterns = data.get('usage_patterns', {})
        action_breakdown = usage_patterns.get('action_breakdown', {})
        
        if not action_breakdown:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Usage Patterns')
            return
        
        # Create pie chart
        labels = list(action_breakdown.keys())
        sizes = list(action_breakdown.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        ax = figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Usage Patterns Distribution')
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        figure.tight_layout()
    
    @staticmethod
    def create_performance_chart(data: Dict[str, Any], figure: Figure) -> None:
        """Create database performance comparison chart."""
        figure.clear()
        
        db_performance = data.get('database_performance', [])
        
        if not db_performance:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Database Performance')
            return
        
        # Extract data for chart
        db_names = [item[0] for item in db_performance[:8]]  # Top 8 databases
        success_rates = [item[1] for item in db_performance[:8]]
        
        ax = figure.add_subplot(111)
        bars = ax.bar(range(len(db_names)), success_rates, color='skyblue', alpha=0.7)
        ax.set_title('Database Documentation Success Rates')
        ax.set_xlabel('Database')
        ax.set_ylabel('Success Rate (%)')
        ax.set_xticks(range(len(db_names)))
        ax.set_xticklabels(db_names, rotation=45, ha='right')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, rate in zip(bars, success_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{rate:.1f}%', ha='center', va='bottom')
        
        figure.tight_layout()


class ReportingDashboard:
    """Main reporting and analytics dashboard GUI."""
    
    def __init__(self, parent):
        self.parent = parent
        self.reporting_db = ReportingDatabase()
        self.analytics = AnalyticsEngine(self.reporting_db)
        self.current_report_data = None
        
        # Initialize matplotlib
        plt.style.use('default')
        
    def create_dashboard_tab(self, notebook: ttk.Notebook):
        """Create the reporting dashboard tab."""
        # Create main frame
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="📊 Analytics Dashboard")
        
        # Create paned window for layout
        main_paned = ttk.PanedWindow(dashboard_frame, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Controls and metrics
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Charts
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)
        
        # Controls section
        controls_frame = ttk.LabelFrame(left_frame, text="Report Controls")
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Time Period:").pack(anchor='w', padx=10, pady=2)
        self.time_period_var = tk.StringVar(value="30")
        time_period_combo = ttk.Combobox(controls_frame, textvariable=self.time_period_var,
                                       values=["7", "30", "90", "180", "365"], state="readonly")
        time_period_combo.pack(fill='x', padx=10, pady=2)
        
        ttk.Button(controls_frame, text="Generate Report",
                  command=self.generate_report).pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Export Report",
                  command=self.export_report).pack(fill='x', padx=10, pady=2)
        
        # Metrics display
        metrics_frame = ttk.LabelFrame(left_frame, text="Key Metrics")
        metrics_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, height=15, wrap='word')
        metrics_scroll = ttk.Scrollbar(metrics_frame, orient='vertical', command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=metrics_scroll.set)
        
        self.metrics_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        metrics_scroll.pack(side='right', fill='y')
        
        # Charts section
        charts_notebook = ttk.Notebook(right_frame)
        charts_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Trends chart
        trends_frame = ttk.Frame(charts_notebook)
        charts_notebook.add(trends_frame, text="Trends")
        
        self.trends_figure = Figure(figsize=(10, 6), dpi=100)
        self.trends_canvas = FigureCanvasTkAgg(self.trends_figure, trends_frame)
        self.trends_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Usage patterns chart
        usage_frame = ttk.Frame(charts_notebook)
        charts_notebook.add(usage_frame, text="Usage Patterns")
        
        self.usage_figure = Figure(figsize=(10, 6), dpi=100)
        self.usage_canvas = FigureCanvasTkAgg(self.usage_figure, usage_frame)
        self.usage_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Performance chart
        performance_frame = ttk.Frame(charts_notebook)
        charts_notebook.add(performance_frame, text="Performance")
        
        self.performance_figure = Figure(figsize=(10, 6), dpi=100)
        self.performance_canvas = FigureCanvasTkAgg(self.performance_figure, performance_frame)
        self.performance_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Generate initial report
        self.generate_report()
    
    def generate_report(self):
        """Generate analytics report and update dashboard."""
        try:
            days = int(self.time_period_var.get())
            self.current_report_data = self.analytics.generate_performance_report(days)
            
            # Update metrics display
            self.update_metrics_display()
            
            # Update charts
            self.update_charts()
            
            # Log usage
            self.reporting_db.log_usage_action("generate_analytics_report", 
                                             details={"time_period_days": days})
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def update_metrics_display(self):
        """Update the metrics text display."""
        if not self.current_report_data:
            return
        
        self.metrics_text.delete(1.0, tk.END)
        
        doc_trends = self.current_report_data.get('documentation_trends', {})
        usage_patterns = self.current_report_data.get('usage_patterns', {})
        
        # Format metrics text
        metrics_text = f"""DOCUMENTATION PERFORMANCE
{'='*30}
Total Runs: {doc_trends.get('total_runs', 0)}
Success Rate: {doc_trends.get('success_rate', 0):.1f}%
Avg Generation Time: {doc_trends.get('avg_generation_time', 0):.1f}s

USAGE STATISTICS
{'='*30}
Total Actions: {usage_patterns.get('total_actions', 0)}

Top Databases:
"""
        
        for db_name, count in doc_trends.get('top_databases', [])[:5]:
            metrics_text += f"  • {db_name}: {count} runs\n"
        
        metrics_text += f"\nMost Common Actions:\n"
        for action, count in list(usage_patterns.get('action_breakdown', {}).items())[:5]:
            metrics_text += f"  • {action}: {count}\n"
        
        # Performance insights
        insights = self.current_report_data.get('performance_insights', [])
        if insights:
            metrics_text += f"\nPERFORMANCE INSIGHTS\n{'='*30}\n"
            for insight in insights:
                metrics_text += f"• {insight}\n"
        
        self.metrics_text.insert(1.0, metrics_text)
    
    def update_charts(self):
        """Update all charts with current data."""
        if not self.current_report_data:
            return
        
        try:
            # Update trends chart
            ChartGenerator.create_trends_chart(self.current_report_data, self.trends_figure)
            self.trends_canvas.draw()
            
            # Update usage patterns chart
            ChartGenerator.create_usage_patterns_chart(self.current_report_data, self.usage_figure)
            self.usage_canvas.draw()
            
            # Update performance chart
            ChartGenerator.create_performance_chart(self.current_report_data, self.performance_figure)
            self.performance_canvas.draw()
            
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def export_report(self):
        """Export the current report to file."""
        if not self.current_report_data:
            messagebox.showwarning("Warning", "No report data to export. Generate a report first.")
            return
        
        # Ask user for export format and location
        file_types = [
            ("HTML files", "*.html"),
            ("JSON files", "*.json"), 
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="Export Report",
            filetypes=file_types,
            defaultextension=".html"
        )
        
        if not filename:
            return
        
        try:
            file_extension = Path(filename).suffix.lower()
            
            if file_extension == '.html':
                ReportExporter.export_to_html(self.current_report_data, filename)
            elif file_extension == '.json':
                ReportExporter.export_to_json(self.current_report_data, filename)
            elif file_extension == '.csv':
                ReportExporter.export_to_csv(self.current_report_data, filename)
            else:
                # Default to JSON
                ReportExporter.export_to_json(self.current_report_data, filename)
            
            messagebox.showinfo("Success", f"Report exported to: {filename}")
            
            # Log usage
            self.reporting_db.log_usage_action("export_report", 
                                             details={"format": file_extension, "filename": filename})
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def log_documentation_generation(self, database_name: str, server_name: str,
                                   stats: Dict[str, int], generation_time: float,
                                   output_formats: List[str], success: bool = True):
        """Log a documentation generation event."""
        self.reporting_db.log_documentation_run(
            database_name=database_name,
            server_name=server_name,
            tables_count=stats.get('tables', 0),
            views_count=stats.get('views', 0),
            procedures_count=stats.get('procedures', 0),
            functions_count=stats.get('functions', 0),
            relationships_count=stats.get('relationships', 0),
            generation_time=generation_time,
            output_formats=output_formats,
            success=success
        )


# Test function for standalone execution
if __name__ == "__main__":
    # Create test data
    db = ReportingDatabase()
    
    # Add some sample data
    import random
    from datetime import datetime, timedelta
    
    databases = ["ProductionDB", "TestDB", "StagingDB", "AnalyticsDB"]
    
    for i in range(50):
        db_name = random.choice(databases)
        db.log_documentation_run(
            database_name=db_name,
            server_name="test-server.database.windows.net",
            tables_count=random.randint(10, 100),
            views_count=random.randint(0, 20),
            procedures_count=random.randint(0, 50),
            functions_count=random.randint(0, 30),
            relationships_count=random.randint(5, 80),
            generation_time=random.uniform(10, 300),
            output_formats=random.choice([["html"], ["json"], ["html", "markdown"]]),
            success=random.random() > 0.1  # 90% success rate
        )
    
    # Generate analytics
    analytics = AnalyticsEngine(db)
    report = analytics.generate_performance_report()
    
    print("Analytics Report Generated:")
    print(f"Total Runs: {report['documentation_trends']['total_runs']}")
    print(f"Success Rate: {report['documentation_trends']['success_rate']:.1f}%")
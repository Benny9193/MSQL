#!/usr/bin/env python3
"""
Performance Dashboard Demo Application
=====================================

A standalone demo showcasing the Real-Time Performance Dashboard features.
This demonstrates live metrics monitoring, alert management, and performance
visualization capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import time
import threading
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from performance_dashboard import (
    PerformanceDashboard, PerformanceMetric, Alert, MetricType, 
    AlertSeverity, create_performance_dashboard_panel
)
from ui_framework import ThemeManager, StatusManager

class PerformanceDashboardDemo:
    """Demo application for the Performance Dashboard."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.running = False
        self.demo_thread = None
        self.setup_window()
        self.create_demo_interface()
    
    def setup_window(self):
        """Setup the demo window."""
        self.root.title("Real-Time Performance Dashboard Demo")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_demo_interface(self):
        """Create the demo interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="Real-Time Performance Dashboard Demo",
                               font=('TkDefaultFont', 18, 'bold'))
        title_label.pack(side='left')
        
        info_label = ttk.Label(header_frame, 
                              text="Live database performance monitoring and alerting system",
                              font=('TkDefaultFont', 11))
        info_label.pack(side='right')
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Demo Controls", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Start Live Demo", 
                                      command=self.start_demo)
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Demo", 
                                     command=self.stop_demo, state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))
        
        self.scenario_var = tk.StringVar(value="normal")
        scenarios_label = ttk.Label(control_frame, text="Scenario:")
        scenarios_label.pack(side='left', padx=(20, 5))
        
        scenarios = ttk.Combobox(control_frame, textvariable=self.scenario_var,
                                values=["normal", "high_load", "critical_alerts", "mixed"], 
                                state="readonly", width=15)
        scenarios.pack(side='left')
        
        # Status indicator
        self.status_label = ttk.Label(control_frame, text="Demo Stopped", 
                                     foreground='red')
        self.status_label.pack(side='right')
        
        # Create theme and status managers
        self.theme_manager = ThemeManager()
        self.status_manager = StatusManager(self.root)
        
        # Create performance dashboard
        self.dashboard = PerformanceDashboard(main_frame, None, None, 
                                            self.theme_manager, self.status_manager)
        
        # Bottom info panel
        info_frame = ttk.LabelFrame(main_frame, text="Demo Information", padding=10)
        info_frame.pack(fill='x', pady=(15, 0))
        
        info_text = """
This demo showcases the Real-Time Performance Dashboard features:

🔴 LIVE METRICS MONITORING:
• CPU, Memory, I/O, DTU, and Storage utilization tracking
• Active connections and blocked processes monitoring
• Wait statistics and query performance analysis

📊 INTERACTIVE VISUALIZATIONS:
• Real-time charts with historical trending
• Color-coded performance indicators
• Visual alert notifications with severity levels

🚨 INTELLIGENT ALERTING:
• Configurable threshold-based alerts
• Multiple severity levels (Info, Warning, Critical)
• Alert acknowledgment and management system

🎯 DEMO SCENARIOS:
• Normal: Typical database performance patterns
• High Load: Elevated resource utilization 
• Critical Alerts: Performance issues requiring attention
• Mixed: Combination of various performance patterns

INSTRUCTIONS:
1. Click "Start Live Demo" to begin real-time simulation
2. Select different scenarios to see various performance patterns
3. Watch the metrics update in real-time on the Overview tab
4. Check the "Detailed Metrics" tab for trending charts
5. Monitor the "Alerts" tab for performance warnings
6. Explore "Query Analysis" for resource-intensive operations

The demo simulates realistic Azure SQL Database performance patterns with live updates every second.
        """
        
        info_text_widget = tk.Text(info_frame, height=18, wrap='word', font=('TkDefaultFont', 9))
        info_scrollbar = ttk.Scrollbar(info_frame, command=info_text_widget.yview)
        info_text_widget.configure(yscrollcommand=info_scrollbar.set)
        
        info_text_widget.pack(side='left', fill='both', expand=True)
        info_scrollbar.pack(side='right', fill='y')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
    
    def start_demo(self):
        """Start the live demo simulation."""
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Demo Running", foreground='green')
        
        # Start demo simulation thread
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()
        
        self.status_manager.show_message("Performance Dashboard demo started", "success")
    
    def stop_demo(self):
        """Stop the demo simulation."""
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Demo Stopped", foreground='red')
        
        self.status_manager.show_message("Performance Dashboard demo stopped", "info")
    
    def _demo_loop(self):
        """Main demo simulation loop."""
        while self.running:
            try:
                scenario = self.scenario_var.get()
                metrics = self._generate_scenario_metrics(scenario)
                
                # Update dashboard on main thread
                self.root.after(0, self._update_dashboard, metrics)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Demo loop error: {e}")
                time.sleep(1)
    
    def _generate_scenario_metrics(self, scenario: str) -> list:
        """Generate metrics based on selected scenario."""
        base_time = datetime.now()
        
        if scenario == "normal":
            return [
                PerformanceMetric(MetricType.CPU_PERCENT, random.uniform(20, 50), base_time, "%"),
                PerformanceMetric(MetricType.MEMORY_PERCENT, random.uniform(30, 60), base_time, "%"),
                PerformanceMetric(MetricType.IO_PERCENT, random.uniform(10, 40), base_time, "%"),
                PerformanceMetric(MetricType.DTU_PERCENT, random.uniform(15, 45), base_time, "%"),
                PerformanceMetric(MetricType.STORAGE_PERCENT, random.uniform(40, 70), base_time, "%"),
                PerformanceMetric(MetricType.ACTIVE_CONNECTIONS, random.randint(5, 25), base_time, "connections"),
                PerformanceMetric(MetricType.BLOCKED_PROCESSES, random.randint(0, 2), base_time, "processes"),
                PerformanceMetric(MetricType.WAIT_TIME, random.uniform(100, 2000), base_time, "ms"),
            ]
        
        elif scenario == "high_load":
            return [
                PerformanceMetric(MetricType.CPU_PERCENT, random.uniform(60, 85), base_time, "%"),
                PerformanceMetric(MetricType.MEMORY_PERCENT, random.uniform(65, 90), base_time, "%"),
                PerformanceMetric(MetricType.IO_PERCENT, random.uniform(50, 80), base_time, "%"),
                PerformanceMetric(MetricType.DTU_PERCENT, random.uniform(55, 85), base_time, "%"),
                PerformanceMetric(MetricType.STORAGE_PERCENT, random.uniform(70, 85), base_time, "%"),
                PerformanceMetric(MetricType.ACTIVE_CONNECTIONS, random.randint(40, 80), base_time, "connections"),
                PerformanceMetric(MetricType.BLOCKED_PROCESSES, random.randint(2, 8), base_time, "processes"),
                PerformanceMetric(MetricType.WAIT_TIME, random.uniform(5000, 15000), base_time, "ms"),
            ]
        
        elif scenario == "critical_alerts":
            return [
                PerformanceMetric(MetricType.CPU_PERCENT, random.uniform(85, 98), base_time, "%"),
                PerformanceMetric(MetricType.MEMORY_PERCENT, random.uniform(88, 95), base_time, "%"),
                PerformanceMetric(MetricType.IO_PERCENT, random.uniform(85, 95), base_time, "%"),
                PerformanceMetric(MetricType.DTU_PERCENT, random.uniform(85, 98), base_time, "%"),
                PerformanceMetric(MetricType.STORAGE_PERCENT, random.uniform(88, 95), base_time, "%"),
                PerformanceMetric(MetricType.ACTIVE_CONNECTIONS, random.randint(80, 120), base_time, "connections"),
                PerformanceMetric(MetricType.BLOCKED_PROCESSES, random.randint(8, 20), base_time, "processes"),
                PerformanceMetric(MetricType.WAIT_TIME, random.uniform(15000, 30000), base_time, "ms"),
            ]
        
        elif scenario == "mixed":
            # Randomly choose between different load patterns
            pattern = random.choice(["normal", "high_load", "critical_alerts"])
            return self._generate_scenario_metrics(pattern)
        
        else:
            return self._generate_scenario_metrics("normal")
    
    def _update_dashboard(self, metrics: list):
        """Update dashboard with new metrics."""
        try:
            for metric in metrics:
                # Update metric cards
                self.dashboard._update_metric_card(metric)
                
                # Update charts
                if metric.metric_type in self.dashboard.charts:
                    self.dashboard.charts[metric.metric_type].update_data(metric)
                
                # Check for alerts
                self.dashboard.alert_manager.check_metrics([metric])
            
            # Process any new alerts
            active_alerts = self.dashboard.alert_manager.get_active_alerts()
            for alert in active_alerts:
                # Check if alert is already in the tree
                existing_items = self.dashboard.alerts_tree.get_children()
                alert_exists = False
                
                for item in existing_items:
                    item_values = self.dashboard.alerts_tree.item(item)['values']
                    if len(item_values) >= 3 and item_values[2] == alert.metric_type.value.replace('_', ' ').title():
                        alert_exists = True
                        break
                
                if not alert_exists:
                    self.dashboard._on_new_alert(alert)
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
    
    def on_closing(self):
        """Handle application closing."""
        self.stop_demo()
        time.sleep(0.5)  # Give time for threads to stop
        self.root.destroy()
    
    def run(self):
        """Run the demo application."""
        try:
            print("Starting Real-Time Performance Dashboard Demo...")
            print("The demo simulates live Azure SQL Database performance metrics.")
            print("Try different scenarios to see various performance patterns.")
            print("Monitor alerts and trends in real-time.")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nDemo terminated by user")
        except Exception as e:
            print(f"Demo error: {e}")
            messagebox.showerror("Demo Error", f"An error occurred: {e}")

def main():
    """Run the performance dashboard demo."""
    try:
        demo = PerformanceDashboardDemo()
        demo.run()
    except Exception as e:
        print(f"Failed to start demo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
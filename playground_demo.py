#!/usr/bin/env python3
"""
Interactive Database Playground Demo
====================================

A standalone demo showcasing the Interactive Database Playground features.
This demonstrates the safe sandbox environment, query builder, and results preview.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_playground import DatabasePlayground, create_playground_panel
from ui_framework import ThemeManager

class PlaygroundDemo:
    """Demo application for the Database Playground."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_demo_interface()
    
    def setup_window(self):
        """Setup the demo window."""
        self.root.title("Database Playground Demo")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
    
    def create_demo_interface(self):
        """Create the demo interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Interactive Database Playground Demo",
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(side='left')
        
        info_label = ttk.Label(header_frame, 
                              text="Safe SQL learning environment with sample data",
                              font=('TkDefaultFont', 10))
        info_label.pack(side='right')
        
        # Create theme manager
        self.theme_manager = ThemeManager()
        
        # Create playground
        self.playground = create_playground_panel(main_frame, None, None, self.theme_manager)
        
        # Bottom info panel
        info_frame = ttk.LabelFrame(main_frame, text="Demo Information", padding=10)
        info_frame.pack(fill='x', pady=(10, 0))
        
        info_text = """
This demo showcases the Interactive Database Playground features:

• Safe Sandbox Environment: Uses SQLite with sample employee/department data
• Visual Query Builder: Drag-and-drop interface for building SQL queries  
• Instant Results Preview: Real-time query execution with performance metrics
• Query Validation: Prevents dangerous operations and SQL injection attempts
• Interactive Tutorials: Guided learning experiences (coming soon)
• Schema Explorer: Browse database structure and sample data

Sample Tables Available:
- employees: Employee records with names, departments, salaries
- departments: Department information with managers and budgets  
- projects: Project data linked to departments

Try executing queries like:
- SELECT * FROM employees WHERE salary > 70000
- SELECT d.name, COUNT(e.id) as employee_count FROM departments d LEFT JOIN employees e ON e.department = d.name GROUP BY d.name
        """
        
        info_text_widget = tk.Text(info_frame, height=12, wrap='word', font=('TkDefaultFont', 9))
        info_text_widget.pack(fill='both', expand=True)
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
    
    def run(self):
        """Run the demo application."""
        try:
            print("Starting Database Playground Demo...")
            print("Sample database with employees, departments, and projects is ready!")
            print("Use the Query Builder tab to construct queries visually.")
            print("Check the Results tab to see query output and performance metrics.")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nDemo terminated by user")
        except Exception as e:
            print(f"Demo error: {e}")
            messagebox.showerror("Demo Error", f"An error occurred: {e}")

def main():
    """Run the playground demo."""
    try:
        demo = PlaygroundDemo()
        demo.run()
    except Exception as e:
        print(f"Failed to start demo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
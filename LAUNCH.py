#!/usr/bin/env python3
"""
Azure SQL Database Documentation Generator - Launch Menu
=======================================================

Quick launch menu for all major components of the application.
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

class LaunchMenu:
    """Launch menu for the Azure SQL Database Documentation Generator."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_interface()
    
    def setup_window(self):
        """Setup the launch window."""
        self.root.title("Azure SQL Database Documentation Generator - Launch Menu")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_interface(self):
        """Create the launch interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="Azure SQL Database Documentation Generator",
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Complete Database Documentation & Interactive Exploration Suite",
                                  font=('TkDefaultFont', 10))
        subtitle_label.pack(pady=(5, 0))
        
        # Main Application Section
        main_section = ttk.LabelFrame(main_frame, text="Main Application", padding=15)
        main_section.pack(fill='x', pady=(0, 15))
        
        ttk.Button(main_section, text="Launch Main Application", 
                  command=lambda: self.launch_app("modern_gui.py"),
                  width=30).pack(pady=2)
        
        ttk.Label(main_section, text="Complete application with all features",
                 font=('TkDefaultFont', 9)).pack(pady=(0, 5))
        
        # Interactive Features Section
        features_section = ttk.LabelFrame(main_frame, text="Interactive Features Demos", padding=15)
        features_section.pack(fill='x', pady=(0, 15))
        
        # Phase 1
        phase1_frame = ttk.Frame(features_section)
        phase1_frame.pack(fill='x', pady=2)
        
        ttk.Button(phase1_frame, text="Phase 1: Database Playground", 
                  command=lambda: self.launch_app("playground_demo.py"),
                  width=30).pack(side='left')
        ttk.Label(phase1_frame, text="Safe SQL experimentation & learning",
                 font=('TkDefaultFont', 9)).pack(side='left', padx=(10, 0))
        
        # Phase 2  
        phase2_frame = ttk.Frame(features_section)
        phase2_frame.pack(fill='x', pady=2)
        
        ttk.Button(phase2_frame, text="Phase 2: Schema Explorer", 
                  command=lambda: self.launch_app("schema_explorer_demo.py"),
                  width=30).pack(side='left')
        ttk.Label(phase2_frame, text="Interactive visual schema exploration",
                 font=('TkDefaultFont', 9)).pack(side='left', padx=(10, 0))
        
        # Phase 3
        phase3_frame = ttk.Frame(features_section)
        phase3_frame.pack(fill='x', pady=2)
        
        ttk.Button(phase3_frame, text="Phase 3: Performance Dashboard", 
                  command=lambda: self.launch_app("performance_dashboard_demo.py"),
                  width=30).pack(side='left')
        ttk.Label(phase3_frame, text="Real-time performance monitoring",
                 font=('TkDefaultFont', 9)).pack(side='left', padx=(10, 0))
        
        # Modern UI Demo
        ui_demo_frame = ttk.Frame(features_section)
        ui_demo_frame.pack(fill='x', pady=2)
        
        ttk.Button(ui_demo_frame, text="Modern UI Showcase", 
                  command=lambda: self.launch_app("modern_ui_demo.py"),
                  width=30).pack(side='left')
        ttk.Label(ui_demo_frame, text="Sleek and modernized interface demo",
                 font=('TkDefaultFont', 9)).pack(side='left', padx=(10, 0))
        
        # Testing Section
        test_section = ttk.LabelFrame(main_frame, text="Testing & Verification", padding=15)
        test_section.pack(fill='x', pady=(0, 15))
        
        ttk.Button(test_section, text="Run All Tests", 
                  command=lambda: self.launch_app("run_all_tests.py"),
                  width=30).pack(pady=2)
        
        ttk.Label(test_section, text="Comprehensive test suite for all components",
                 font=('TkDefaultFont', 9)).pack(pady=(0, 5))
        
        # Information Section
        info_section = ttk.LabelFrame(main_frame, text="Project Information", padding=15)
        info_section.pack(fill='x', pady=(0, 15))
        
        info_text = """
📊 Project Status: COMPLETE - All 3 phases implemented and tested
🎯 Ready for Production: Full feature set with comprehensive testing
🔧 Pre-configured: Azure SQL Database credentials included
📚 Documentation: Complete README and project guides available

Default Database Connection:
• Server: eds-sqlserver.eastus2.cloudapp.azure.com
• Database: master
• Username: EDSAdmin
• Password: Consultant~!

Quick Start:
1. Click "Launch Main Application" above
2. Navigate to "Connection" to verify database connection
3. Explore all features through the sidebar navigation
4. Try the demo applications to see individual features
        """
        
        info_label = ttk.Label(info_section, text=info_text.strip(),
                              font=('TkDefaultFont', 9), justify='left')
        info_label.pack(anchor='w')
        
        # Action Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(buttons_frame, text="Open Project Folder", 
                  command=self.open_folder).pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="View Documentation", 
                  command=self.view_docs).pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Exit", 
                  command=self.root.quit).pack(side='right')
    
    def launch_app(self, script_name):
        """Launch an application script."""
        try:
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            
            if not os.path.exists(script_path):
                messagebox.showerror("Error", f"Script not found: {script_name}")
                return
            
            # Launch the script
            subprocess.Popen([sys.executable, script_path], 
                           cwd=os.path.dirname(__file__))
            
            messagebox.showinfo("Launched", f"Successfully launched {script_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {script_name}: {str(e)}")
    
    def open_folder(self):
        """Open the project folder."""
        try:
            project_dir = os.path.dirname(__file__)
            if sys.platform == 'win32':
                os.startfile(project_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', project_dir])
            else:  # Linux
                subprocess.Popen(['xdg-open', project_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
    
    def view_docs(self):
        """Open the README file."""
        try:
            readme_path = os.path.join(os.path.dirname(__file__), "README.md")
            if os.path.exists(readme_path):
                if sys.platform == 'win32':
                    os.startfile(readme_path)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.Popen(['open', readme_path])
                else:  # Linux
                    subprocess.Popen(['xdg-open', readme_path])
            else:
                messagebox.showinfo("Documentation", 
                    "README.md not found. Check PROJECT_OVERVIEW.md and PROJECT_STRUCTURE.md for documentation.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open documentation: {str(e)}")
    
    def run(self):
        """Run the launch menu."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nLaunch menu closed by user")
        except Exception as e:
            print(f"Launch menu error: {e}")

def main():
    """Main entry point."""
    print("Azure SQL Database Documentation Generator - Launch Menu")
    print("=" * 60)
    
    launcher = LaunchMenu()
    launcher.run()

if __name__ == "__main__":
    main()
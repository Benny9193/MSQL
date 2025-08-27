#!/usr/bin/env python3
"""
Modern GUI Launcher for Azure SQL Database Documentation Generator
==================================================================

Launcher script to start the modern GUI application with enhanced UI framework,
comprehensive dependency checking, and proper error handling.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are available."""
    missing = []
    
    try:
        import pyodbc
    except ImportError:
        missing.append("pyodbc")
    
    try:
        import jinja2
    except ImportError:
        missing.append("jinja2")
    
    try:
        import colorama
    except ImportError:
        missing.append("colorama")
    
    try:
        import click
    except ImportError:
        missing.append("click")
        
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing.append("python-dotenv")
    
    # Check modern GUI specific dependencies
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
        
    try:
        import pandas
    except ImportError:
        missing.append("pandas")
        
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    return missing

def main():
    """Launch the GUI application."""
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        # Create a simple error dialog
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        deps_text = "\n".join(f"  - {dep}" for dep in missing_deps)
        message = f"""Missing Required Dependencies:
{deps_text}

Please install the required packages by running:
pip install -r requirements.txt

Then try launching the GUI again."""
        
        messagebox.showerror("Missing Dependencies", message)
        return
    
    try:
        # Import and launch Modern GUI
        from modern_gui import ModernDatabaseDocumentationGUI
        
        app = ModernDatabaseDocumentationGUI()
        app.run()
        
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error", f"Failed to import GUI module: {str(e)}")
        
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
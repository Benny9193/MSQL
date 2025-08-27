#!/usr/bin/env python3
"""
Test script for Database Playground functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_playground import DatabasePlayground, SafeSandbox
from ui_framework import ThemeManager

def test_sandbox():
    """Test the SafeSandbox functionality."""
    print("Testing SafeSandbox...")
    
    try:
        # Create a mock connection (SafeSandbox doesn't actually need a real connection)
        sandbox = SafeSandbox(None)  # Passing None since it uses SQLite internally
        
        # Test schema elements
        elements = sandbox.get_schema_elements()
        print(f"[OK] Schema elements loaded: {len(elements)} items")
        
        # Test query validation
        valid_queries = [
            "SELECT * FROM employees",
            "SELECT name, department FROM employees WHERE salary > 50000",
            "INSERT INTO employees (name, department) VALUES ('Test User', 'IT')"
        ]
        
        invalid_queries = [
            "DROP DATABASE master",
            "EXEC sp_configure",
            "SELECT * FROM employees; DROP TABLE employees;"
        ]
        
        print("\nTesting query validation...")
        for query in valid_queries:
            is_valid, error = sandbox.validate_query(query)
            print(f"[OK] Valid query passed: {query[:30]}...")
            assert is_valid, f"Valid query rejected: {error}"
        
        for query in invalid_queries:
            is_valid, error = sandbox.validate_query(query)
            print(f"[OK] Invalid query blocked: {query[:30]}...")
            assert not is_valid, f"Invalid query allowed: {query}"
        
        # Test query execution
        print("\nTesting query execution...")
        result = sandbox.execute_query("SELECT COUNT(*) as employee_count FROM employees")
        assert result.success, f"Query execution failed: {result.error_message}"
        print(f"[OK] Query executed successfully: {result.rows_affected} rows")
        
        # Test data query
        result = sandbox.execute_query("SELECT name, department FROM employees LIMIT 3")
        assert result.success, f"Data query failed: {result.error_message}"
        assert len(result.data) > 0, "No data returned"
        print(f"[OK] Data query returned {len(result.data)} rows")
        
        # Cleanup
        sandbox.cleanup()
        print("[OK] Sandbox cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Sandbox test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration."""
    print("\nTesting GUI integration...")
    
    try:
        # Create test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test theme manager
        theme_manager = ThemeManager()
        print("[OK] ThemeManager created")
        
        # Test frame creation
        test_frame = ttk.Frame(root)
        print("[OK] Test frame created")
        
        # Test playground instantiation (without actual DB connection)
        # This should show the "no connection" interface
        from database_playground import create_playground_panel
        
        # Mock minimal objects
        class MockConnection:
            pass
        
        class MockSchemaAnalyzer:
            pass
        
        # Test with mock objects
        playground = create_playground_panel(test_frame, None, None, theme_manager)
        print("[OK] Playground panel created (no connection mode)")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[FAIL] GUI integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Database Playground Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Test sandbox functionality
    if not test_sandbox():
        all_passed = False
    
    # Test GUI integration
    if not test_gui_integration():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! Database Playground is ready.")
    else:
        print("Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
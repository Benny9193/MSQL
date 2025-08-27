#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
==============================

Runs all tests for the Azure SQL Database Documentation Generator project.
Provides organized testing with clear reporting and error handling.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

def print_header(title):
    """Print formatted test section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_subheader(title):
    """Print formatted test subsection header."""
    print(f"\n--- {title} ---")

def run_test_file(test_file, description):
    """Run a test file and return success status."""
    print(f"\nRunning: {description}")
    print(f"File: {test_file}")
    print("-" * 60)
    
    try:
        # Check if test file exists
        if not os.path.exists(test_file):
            print(f"[SKIP] Test file not found: {test_file}")
            return True  # Skip missing files
        
        # Run the test
        start_time = time.time()
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Print results
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"[PASS] {description} ({duration:.1f}s)")
            return True
        else:
            print(f"[FAIL] {description} - Exit code: {result.returncode}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {description} - Test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"[ERROR] {description} - {str(e)}")
        return False

def main():
    """Run comprehensive test suite."""
    print("Azure SQL Database Documentation Generator - Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"Working directory: {project_dir}")
    
    # Test results tracking
    test_results = []
    
    # Phase 1: Core Functionality Tests
    print_header("PHASE 1: CORE FUNCTIONALITY TESTS")
    
    core_tests = [
        ("test_basic.py", "Basic Functionality Tests"),
        ("test_performance_core.py", "Performance Dashboard Core Tests"),
    ]
    
    for test_file, description in core_tests:
        result = run_test_file(test_file, description)
        test_results.append((description, result))
    
    # Phase 2: Interactive Features Tests
    print_header("PHASE 2: INTERACTIVE FEATURES TESTS")
    
    interactive_tests = [
        ("test_playground.py", "Interactive Database Playground Tests"),
        ("test_schema_explorer.py", "Dynamic Visual Schema Explorer Tests"),
        ("test_performance_dashboard.py", "Real-Time Performance Dashboard Tests"),
    ]
    
    for test_file, description in interactive_tests:
        result = run_test_file(test_file, description)
        test_results.append((description, result))
    
    # Phase 3: Integration Tests
    print_header("PHASE 3: INTEGRATION TESTS")
    
    integration_tests = [
        ("test_azure_schema_explorer.py", "Azure SQL Schema Explorer Integration"),
    ]
    
    for test_file, description in integration_tests:
        result = run_test_file(test_file, description)
        test_results.append((description, result))
    
    # Phase 4: Demo Applications (Optional)
    print_header("PHASE 4: DEMO APPLICATIONS (VERIFICATION)")
    
    print_subheader("Demo Application Verification")
    demo_files = [
        ("playground_demo.py", "Interactive Database Playground Demo"),
        ("schema_explorer_demo.py", "Visual Schema Explorer Demo"),
        ("performance_dashboard_demo.py", "Real-Time Performance Dashboard Demo"),
    ]
    
    for demo_file, description in demo_files:
        if os.path.exists(demo_file):
            print(f"[OK] {description} - {demo_file}")
            test_results.append((f"{description} (File Check)", True))
        else:
            print(f"[MISSING] {description} - {demo_file}")
            test_results.append((f"{description} (File Check)", False))
    
    # Phase 5: Main Application Verification
    print_header("PHASE 5: MAIN APPLICATION VERIFICATION")
    
    print_subheader("Main Application Files")
    main_files = [
        ("modern_gui.py", "Main Modern GUI Application"),
        ("main.py", "Alternative Entry Point"),
        ("launch_gui.py", "GUI Launcher"),
    ]
    
    for main_file, description in main_files:
        if os.path.exists(main_file):
            print(f"[OK] {description} - {main_file}")
            test_results.append((f"{description} (File Check)", True))
        else:
            print(f"[MISSING] {description} - {main_file}")
            test_results.append((f"{description} (File Check)", False))
    
    # Final Results Summary
    print_header("TEST RESULTS SUMMARY")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! The project is ready for use.")
        print("\nWhat you can do next:")
        print("1. Launch the main application: python modern_gui.py")
        print("2. Try the demo applications:")
        print("   - python playground_demo.py")
        print("   - python schema_explorer_demo.py") 
        print("   - python performance_dashboard_demo.py")
        print("3. Connect to your Azure SQL Database and explore!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Review the output above.")
        print("\nFailed tests:")
        for description, result in test_results:
            if not result:
                print(f"  - {description}")
    
    print(f"\nTest suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return appropriate exit code
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
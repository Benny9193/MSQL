#!/usr/bin/env python3
"""
Basic functionality test for the database documentation generator.
Tests configuration management and template generation without requiring database connection.
"""

import sys
import os
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

def test_imports():
    """Test that all required modules can be imported."""
    print(f"{Fore.YELLOW}Testing module imports...{Style.RESET_ALL}")
    
    try:
        from config_manager import ConfigManager
        print(f"{Fore.GREEN}+ ConfigManager imported successfully{Style.RESET_ALL}")
        
        from documentation_generator import DocumentationGenerator  
        print(f"{Fore.GREEN}+ DocumentationGenerator imported successfully{Style.RESET_ALL}")
        
        # Test database connection import (should show pyodbc warning)
        try:
            from db_connection import AzureSQLConnection
            print(f"{Fore.YELLOW}! AzureSQLConnection imported (pyodbc check will occur during instantiation){Style.RESET_ALL}")
        except ImportError as e:
            print(f"{Fore.RED}- AzureSQLConnection import failed: {e}{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}- Import failed: {e}{Style.RESET_ALL}")
        return False

def test_config_manager():
    """Test configuration management functionality."""
    print(f"\n{Fore.YELLOW}Testing ConfigManager...{Style.RESET_ALL}")
    
    try:
        from config_manager import ConfigManager
        # Create config manager
        config = ConfigManager('test_config.json')
        
        # Test getting configuration
        db_config = config.get_database_config()
        doc_config = config.get_documentation_config()
        
        print(f"{Fore.GREEN}+ Configuration loaded successfully{Style.RESET_ALL}")
        print(f"  Database config keys: {list(db_config.keys())}")
        print(f"  Documentation config keys: {list(doc_config.keys())}")
        
        # Test creating sample files
        config.create_sample_config()
        config.create_sample_env()
        print(f"{Fore.GREEN}+ Sample files created successfully{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}- ConfigManager test failed: {e}{Style.RESET_ALL}")
        return False

def test_template_generation():
    """Test documentation template generation."""
    print(f"\n{Fore.YELLOW}Testing DocumentationGenerator template creation...{Style.RESET_ALL}")
    
    try:
        from documentation_generator import DocumentationGenerator
        # Create generator (should create templates)
        generator = DocumentationGenerator('test_output')
        print(f"{Fore.GREEN}+ DocumentationGenerator created successfully{Style.RESET_ALL}")
        
        # Check if templates directory was created
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        if os.path.exists(templates_dir):
            print(f"{Fore.GREEN}+ Templates directory created{Style.RESET_ALL}")
            
            # List template files
            template_files = os.listdir(templates_dir)
            print(f"  Template files: {template_files}")
        else:
            print(f"{Fore.YELLOW}! Templates directory not found{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}- Template generation test failed: {e}{Style.RESET_ALL}")
        return False

def test_sample_documentation():
    """Test generating documentation with sample data."""
    print(f"\n{Fore.YELLOW}Testing sample documentation generation...{Style.RESET_ALL}")
    
    try:
        from documentation_generator import DocumentationGenerator
        
        # Create sample documentation data
        sample_data = {
            'metadata': {
                'database_name': 'SampleDatabase',
                'server_name': 'sample-server.database.windows.net',
                'version': 'Microsoft SQL Azure (RTM) - 12.0.2000.8',
                'user_name': 'sample_user',
                'extraction_date': '2024-01-01T12:00:00',
                'size_mb': 1024.0,
                'used_mb': 512.0
            },
            'schemas': [
                {'name': 'dbo', 'schema_id': 1, 'principal': 'dbo'},
                {'name': 'sales', 'schema_id': 2, 'principal': 'dbo'}
            ],
            'tables': [
                {
                    'schema_name': 'dbo',
                    'table_name': 'Users',
                    'object_id': 100,
                    'type': 'USER_TABLE',
                    'created': '2024-01-01T10:00:00',
                    'modified': '2024-01-01T10:00:00',
                    'description': 'User account information',
                    'row_count': 1500,
                    'columns': [
                        {
                            'column_id': 1,
                            'name': 'UserID',
                            'data_type': 'int',
                            'is_nullable': False,
                            'is_identity': True,
                            'is_computed': False,
                            'default_value': '',
                            'description': 'Unique user identifier'
                        },
                        {
                            'column_id': 2,
                            'name': 'Username',
                            'data_type': 'nvarchar(50)',
                            'is_nullable': False,
                            'is_identity': False,
                            'is_computed': False,
                            'default_value': '',
                            'description': 'User login name'
                        },
                        {
                            'column_id': 3,
                            'name': 'Email',
                            'data_type': 'nvarchar(255)',
                            'is_nullable': False,
                            'is_identity': False,
                            'is_computed': False,
                            'default_value': '',
                            'description': 'User email address'
                        }
                    ],
                    'primary_keys': [{'column_name': 'UserID', 'constraint_name': 'PK_Users', 'key_ordinal': 1}],
                    'foreign_keys': [],
                    'indexes': [
                        {
                            'index_name': 'PK_Users',
                            'index_type': 'CLUSTERED',
                            'is_unique': True,
                            'is_primary_key': True,
                            'columns': 'UserID'
                        }
                    ],
                    'check_constraints': [],
                    'triggers': []
                }
            ],
            'views': [],
            'stored_procedures': [
                {
                    'schema_name': 'dbo',
                    'procedure_name': 'GetUserByID',
                    'object_id': 200,
                    'created': '2024-01-01T11:00:00',
                    'modified': '2024-01-01T11:00:00',
                    'description': 'Retrieves user information by ID'
                }
            ],
            'functions': [
                {
                    'schema_name': 'dbo',
                    'function_name': 'FormatUserName',
                    'object_id': 300,
                    'type': 'SCALAR_FUNCTION',
                    'created': '2024-01-01T11:30:00',
                    'modified': '2024-01-01T11:30:00',
                    'description': 'Formats user display name'
                }
            ],
            'relationships': {
                'foreign_keys': [],
                'relationship_count': 0
            },
            'statistics': {
                'total_schemas': 2,
                'total_tables': 1,
                'total_views': 0,
                'total_procedures': 1,
                'total_functions': 1,
                'total_rows': 1500,
                'largest_tables': [
                    {'schema_name': 'dbo', 'table_name': 'Users', 'row_count': 1500}
                ]
            }
        }
        
        generator = DocumentationGenerator('test_output')
        
        # Generate all formats
        results = generator.generate_all_formats(sample_data)
        
        print(f"{Fore.GREEN}+ Sample documentation generated successfully{Style.RESET_ALL}")
        for format_type, file_path in results.items():
            abs_path = os.path.abspath(file_path)
            print(f"  {format_type.upper()}: {abs_path}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}- Sample documentation generation failed: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Azure SQL Database Documentation Generator Test{Style.RESET_ALL}")
    print(f"{Fore.CYAN}               Basic Functionality{Style.RESET_ALL}")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    tests = [
        ("Module Imports", test_imports),
        ("Config Manager", test_config_manager),
        ("Template Generation", test_template_generation),
        ("Sample Documentation", test_sample_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Running: {test_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        if test_func():
            passed += 1
        else:
            print(f"{Fore.RED}Test '{test_name}' failed{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Test Summary{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    if passed == total:
        print(f"{Fore.GREEN}All {total} tests passed! SUCCESS{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}Basic functionality is working correctly.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Note: Database connectivity requires pyodbc installation.{Style.RESET_ALL}")
        print(f"      Install pyodbc with: pip install pyodbc")
    else:
        print(f"{Fore.RED}{passed}/{total} tests passed{Style.RESET_ALL}")
        print(f"{Fore.RED}Some functionality is not working correctly.{Style.RESET_ALL}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
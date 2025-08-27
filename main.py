#!/usr/bin/env python3
"""
Azure SQL Database Documentation Generator
==========================================

A comprehensive tool for generating complete documentation of Microsoft SQL Server
databases hosted on Azure SQL Database.

Features:
- Multiple authentication methods (username/password, Azure AD, Service Principal)
- Complete schema analysis (tables, views, procedures, functions, relationships)
- Multiple output formats (HTML, Markdown, JSON)
- Configurable via JSON file or environment variables
- Detailed logging and error handling

Usage:
    python main.py [OPTIONS]

Examples:
    # Generate documentation with default settings
    python main.py

    # Use specific configuration file
    python main.py --config my_config.json

    # Generate only HTML documentation
    python main.py --html-only

    # Create sample configuration files
    python main.py --create-samples
"""

import argparse
import sys
import os
import logging
from datetime import datetime
from colorama import init, Fore, Style
import click

# Initialize colorama for Windows
init()

from db_connection import AzureSQLConnection
from schema_analyzer import SchemaAnalyzer
from documentation_extractor import DocumentationExtractor
from documentation_generator import DocumentationGenerator
from config_manager import ConfigManager

def setup_logging(config_manager: ConfigManager):
    """Setup logging configuration."""
    log_config = config_manager.get_logging_config()
    
    # Configure logging
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_file = log_config.get('log_file', 'database_docs.log')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # If log_file is just filename, put it in logs directory
    if not os.path.dirname(log_file):
        log_file = os.path.join('logs', log_file)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}============================================================
      Azure SQL Database Documentation Generator
                                                              
  Comprehensive database documentation tool for Azure SQL    
  Supports multiple authentication methods and output formats 
============================================================{Style.RESET_ALL}
"""
    print(banner)

def validate_requirements():
    """Validate that required dependencies are installed."""
    try:
        import pyodbc
        import jinja2
        import colorama
        import click
        return True
    except ImportError as e:
        print(f"{Fore.RED}Error: Missing required dependency: {e}{Style.RESET_ALL}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False

@click.command()
@click.option('--config', '-c', default='config.json', help='Configuration file path')
@click.option('--html-only', is_flag=True, help='Generate only HTML documentation')
@click.option('--markdown-only', is_flag=True, help='Generate only Markdown documentation')
@click.option('--json-only', is_flag=True, help='Generate only JSON documentation')
@click.option('--output-dir', '-o', help='Output directory (overrides config)')
@click.option('--create-samples', is_flag=True, help='Create sample configuration files and exit')
@click.option('--test-connection', is_flag=True, help='Test database connection and exit')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode (errors only)')
def main(config, html_only, markdown_only, json_only, output_dir, create_samples, test_connection, verbose, quiet):
    """Generate comprehensive documentation for Azure SQL Database."""
    
    if not validate_requirements():
        sys.exit(1)
    
    print_banner()
    
    # Load configuration
    config_manager = ConfigManager(config)
    
    # Handle create samples command
    if create_samples:
        try:
            config_manager.create_sample_config()
            config_manager.create_sample_env()
            print(f"{Fore.GREEN}+ Sample configuration files created:{Style.RESET_ALL}")
            print("  - config_sample.json")
            print("  - .env.sample")
            print("\nEdit these files with your database connection details.")
            return
        except Exception as e:
            print(f"{Fore.RED}- Failed to create sample files: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)
    
    # Setup logging
    if verbose:
        config_manager.update_config('logging', 'level', 'DEBUG')
    elif quiet:
        config_manager.update_config('logging', 'level', 'ERROR')
    
    setup_logging(config_manager)
    logger = logging.getLogger(__name__)
    
    # Override output directory if specified
    if output_dir:
        config_manager.update_config('documentation', 'output_directory', output_dir)
    
    # Override output format flags
    if html_only:
        config_manager.update_config('documentation', 'generate_html', True)
        config_manager.update_config('documentation', 'generate_markdown', False)
        config_manager.update_config('documentation', 'generate_json', False)
    elif markdown_only:
        config_manager.update_config('documentation', 'generate_html', False)
        config_manager.update_config('documentation', 'generate_markdown', True)
        config_manager.update_config('documentation', 'generate_json', False)
    elif json_only:
        config_manager.update_config('documentation', 'generate_html', False)
        config_manager.update_config('documentation', 'generate_markdown', False)
        config_manager.update_config('documentation', 'generate_json', True)
    
    # Print configuration summary
    if not quiet:
        config_manager.print_config_summary()
    
    # Validate configuration
    config_errors = config_manager.validate_config()
    if config_errors:
        print(f"{Fore.RED}- Configuration errors found:{Style.RESET_ALL}")
        for section, errors in config_errors.items():
            print(f"  {section.title()}:")
            for error in errors:
                print(f"    - {error}")
        print("\nPlease fix configuration errors before proceeding.")
        sys.exit(1)
    
    # Get connection parameters
    connection_params = config_manager.get_connection_params()
    
    try:
        # Establish database connection
        print(f"{Fore.YELLOW}Connecting to database...{Style.RESET_ALL}")
        
        with AzureSQLConnection() as db:
            # Connect based on method
            connection_method = connection_params['method']
            
            if connection_method == 'connection_string':
                success = db.connect_with_connection_string(connection_params['connection_string'])
            elif connection_method == 'credentials':
                success = db.connect_with_credentials(
                    server=connection_params['server'],
                    database=connection_params['database'],
                    username=connection_params['username'],
                    password=connection_params['password'],
                    driver=connection_params['driver']
                )
            elif connection_method == 'azure_ad':
                success = db.connect_with_azure_ad(
                    server=connection_params['server'],
                    database=connection_params['database'],
                    driver=connection_params['driver']
                )
            elif connection_method == 'service_principal':
                success = db.connect_with_service_principal(
                    server=connection_params['server'],
                    database=connection_params['database'],
                    client_id=connection_params['client_id'],
                    client_secret=connection_params['client_secret'],
                    tenant_id=connection_params['tenant_id'],
                    driver=connection_params['driver']
                )
            else:
                raise ValueError(f"Unknown connection method: {connection_method}")
            
            if not success:
                raise Exception("Failed to establish database connection")
            
            # Test connection
            if not db.test_connection():
                raise Exception("Database connection test failed")
            
            print(f"{Fore.GREEN}+ Database connection established{Style.RESET_ALL}")
            
            # Get database info
            db_info = db.get_database_info()
            print(f"  Database: {db_info.get('database_name', 'Unknown')}")
            print(f"  Server: {db_info.get('server_name', 'Unknown')}")
            print(f"  User: {db_info.get('user_name', 'Unknown')}")
            
            # Handle test connection command
            if test_connection:
                print(f"{Fore.GREEN}+ Connection test successful{Style.RESET_ALL}")
                return
            
            # Extract documentation
            print(f"\n{Fore.YELLOW}Extracting database schema and metadata...{Style.RESET_ALL}")
            
            extractor = DocumentationExtractor(db)
            documentation = extractor.extract_complete_documentation()
            
            print(f"{Fore.GREEN}+ Schema extraction completed{Style.RESET_ALL}")
            print(f"  Tables: {len(documentation.get('tables', []))}")
            print(f"  Views: {len(documentation.get('views', []))}")
            print(f"  Stored Procedures: {len(documentation.get('stored_procedures', []))}")
            print(f"  Functions: {len(documentation.get('functions', []))}")
            print(f"  Relationships: {documentation.get('relationships', {}).get('relationship_count', 0)}")
            
            # Generate documentation
            print(f"\n{Fore.YELLOW}Generating documentation...{Style.RESET_ALL}")
            
            doc_config = config_manager.get_documentation_config()
            output_directory = doc_config.get('output_directory', 'output')
            
            generator = DocumentationGenerator(output_directory)
            
            generated_files = []
            
            if doc_config.get('generate_html', True):
                html_file = generator.generate_html_documentation(documentation)
                generated_files.append(('HTML', html_file))
            
            if doc_config.get('generate_markdown', True):
                md_file = generator.generate_markdown_documentation(documentation)
                generated_files.append(('Markdown', md_file))
            
            if doc_config.get('generate_json', True):
                json_file = generator.generate_json_documentation(documentation)
                generated_files.append(('JSON', json_file))
            
            # Success message
            print(f"\n{Fore.GREEN}+ Documentation generation completed{Style.RESET_ALL}")
            print(f"\nGenerated files:")
            for format_type, file_path in generated_files:
                abs_path = os.path.abspath(file_path)
                print(f"  {format_type}: {abs_path}")
            
            print(f"\n{Fore.CYAN}Documentation generated successfully!{Style.RESET_ALL}")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Documentation generation failed: {str(e)}")
        print(f"\n{Fore.RED}- Error: {str(e)}{Style.RESET_ALL}")
        print("\nCheck the log file for detailed error information.")
        sys.exit(1)

if __name__ == "__main__":
    main()
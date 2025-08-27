import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration settings for database connections and documentation options."""
    
    def __init__(self, config_file: str = "config.json", env_file: str = ".env"):
        self.config_file = config_file
        self.env_file = env_file
        self.config = {}
        
        # Load environment variables
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file and environment variables."""
        # Default configuration
        self.config = {
            'database': {
                'connection_method': 'credentials',  # 'credentials', 'azure_ad', 'service_principal', 'connection_string'
                'server': 'eds-sqlserver.eastus2.cloudapp.azure.com',
                'database': 'master',
                'username': 'EDSAdmin',
                'password': 'Consultant~!',
                'client_id': '',
                'client_secret': '',
                'tenant_id': '',
                'connection_string': '',
                'driver': 'ODBC Driver 17 for SQL Server',
                'timeout': 30
            },
            'documentation': {
                'output_directory': 'output',
                'generate_html': True,
                'generate_markdown': True,
                'generate_json': True,
                'include_system_objects': False,
                'include_row_counts': True,
                'max_table_sample_size': 1000
            },
            'logging': {
                'level': 'INFO',
                'log_file': 'database_docs.log'
            }
        }
        
        # Load from JSON file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._merge_config(self.config, file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file}: {str(e)}")
        
        # Override with environment variables
        self._load_from_environment()
    
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            # Don't save sensitive information to config file
            safe_config = self._get_safe_config()
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
    
    def create_sample_config(self):
        """Create a sample configuration file."""
        sample_config = {
            'database': {
                'connection_method': 'credentials',
                'server': 'your-server.database.windows.net',
                'database': 'your-database',
                'driver': 'ODBC Driver 17 for SQL Server',
                'timeout': 30
            },
            'documentation': {
                'output_directory': 'output',
                'generate_html': True,
                'generate_markdown': True,
                'generate_json': True,
                'include_system_objects': False,
                'include_row_counts': True
            },
            'logging': {
                'level': 'INFO',
                'log_file': 'database_docs.log'
            }
        }
        
        with open('config_sample.json', 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        logger.info("Sample configuration created: config_sample.json")
    
    def create_sample_env(self):
        """Create a sample .env file."""
        env_content = '''# Azure SQL Database Connection Settings
DB_SERVER=your-server.database.windows.net
DB_DATABASE=your-database
DB_USERNAME=your-username
DB_PASSWORD=your-password

# For Azure AD Service Principal authentication
DB_CLIENT_ID=your-client-id
DB_CLIENT_SECRET=your-client-secret
DB_TENANT_ID=your-tenant-id

# Or use a complete connection string
DB_CONNECTION_STRING=

# Documentation settings
DOC_OUTPUT_DIR=output
DOC_INCLUDE_SYSTEM_OBJECTS=false
'''
        
        with open('.env.sample', 'w') as f:
            f.write(env_content)
        
        logger.info("Sample environment file created: .env.sample")
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'DB_SERVER': ('database', 'server'),
            'DB_DATABASE': ('database', 'database'),
            'DB_USERNAME': ('database', 'username'),
            'DB_PASSWORD': ('database', 'password'),
            'DB_CLIENT_ID': ('database', 'client_id'),
            'DB_CLIENT_SECRET': ('database', 'client_secret'),
            'DB_TENANT_ID': ('database', 'tenant_id'),
            'DB_CONNECTION_STRING': ('database', 'connection_string'),
            'DB_DRIVER': ('database', 'driver'),
            'DB_TIMEOUT': ('database', 'timeout'),
            'DB_CONNECTION_METHOD': ('database', 'connection_method'),
            'DOC_OUTPUT_DIR': ('documentation', 'output_directory'),
            'DOC_INCLUDE_SYSTEM_OBJECTS': ('documentation', 'include_system_objects'),
            'LOG_LEVEL': ('logging', 'level'),
            'LOG_FILE': ('logging', 'log_file')
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert boolean strings
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                # Convert numeric strings
                elif value.isdigit():
                    value = int(value)
                
                self.config[section][key] = value
    
    def _merge_config(self, base_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Recursively merge configuration dictionaries."""
        for key, value in new_config.items():
            if key in base_config:
                if isinstance(base_config[key], dict) and isinstance(value, dict):
                    self._merge_config(base_config[key], value)
                else:
                    base_config[key] = value
            else:
                base_config[key] = value
    
    def _get_safe_config(self) -> Dict[str, Any]:
        """Get configuration without sensitive information."""
        safe_config = json.loads(json.dumps(self.config))  # Deep copy
        
        # Remove sensitive fields
        sensitive_fields = ['password', 'client_secret', 'connection_string']
        for field in sensitive_fields:
            if field in safe_config['database']:
                safe_config['database'][field] = '***HIDDEN***'
        
        return safe_config
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database connection configuration."""
        return self.config.get('database', {})
    
    def get_documentation_config(self) -> Dict[str, Any]:
        """Get documentation generation configuration."""
        return self.config.get('documentation', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get('logging', {})
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters based on connection method."""
        db_config = self.get_database_config()
        connection_method = db_config.get('connection_method', 'credentials')
        
        params = {
            'method': connection_method,
            'driver': db_config.get('driver', 'ODBC Driver 17 for SQL Server')
        }
        
        if connection_method == 'connection_string':
            params['connection_string'] = db_config.get('connection_string', '')
        elif connection_method == 'credentials':
            params.update({
                'server': db_config.get('server', ''),
                'database': db_config.get('database', ''),
                'username': db_config.get('username', ''),
                'password': db_config.get('password', '')
            })
        elif connection_method == 'azure_ad':
            params.update({
                'server': db_config.get('server', ''),
                'database': db_config.get('database', '')
            })
        elif connection_method == 'service_principal':
            params.update({
                'server': db_config.get('server', ''),
                'database': db_config.get('database', ''),
                'client_id': db_config.get('client_id', ''),
                'client_secret': db_config.get('client_secret', ''),
                'tenant_id': db_config.get('tenant_id', '')
            })
        
        return params
    
    def validate_config(self) -> Dict[str, list]:
        """Validate configuration and return any errors."""
        errors = {
            'database': [],
            'documentation': [],
            'logging': []
        }
        
        # Validate database configuration
        db_config = self.get_database_config()
        connection_method = db_config.get('connection_method', 'credentials')
        
        if connection_method == 'connection_string':
            if not db_config.get('connection_string'):
                errors['database'].append("Connection string is required when using connection_string method")
        elif connection_method == 'credentials':
            required_fields = ['server', 'database', 'username', 'password']
            for field in required_fields:
                if not db_config.get(field):
                    errors['database'].append(f"{field} is required for credentials authentication")
        elif connection_method == 'azure_ad':
            required_fields = ['server', 'database']
            for field in required_fields:
                if not db_config.get(field):
                    errors['database'].append(f"{field} is required for Azure AD authentication")
        elif connection_method == 'service_principal':
            required_fields = ['server', 'database', 'client_id', 'client_secret', 'tenant_id']
            for field in required_fields:
                if not db_config.get(field):
                    errors['database'].append(f"{field} is required for service principal authentication")
        
        # Validate documentation configuration
        doc_config = self.get_documentation_config()
        output_dir = doc_config.get('output_directory', '')
        if output_dir:
            try:
                # Try to create the directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                errors['documentation'].append(f"Cannot create output directory '{output_dir}': {str(e)}")
        
        return {k: v for k, v in errors.items() if v}  # Return only sections with errors
    
    def update_config(self, section: str, key: str, value: Any):
        """Update a specific configuration value."""
        if section in self.config:
            self.config[section][key] = value
        else:
            self.config[section] = {key: value}
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        print("\n=== Configuration Summary ===")
        
        db_config = self.get_database_config()
        print(f"Database Connection Method: {db_config.get('connection_method', 'Not set')}")
        print(f"Server: {db_config.get('server', 'Not set')}")
        print(f"Database: {db_config.get('database', 'Not set')}")
        
        doc_config = self.get_documentation_config()
        print(f"Output Directory: {doc_config.get('output_directory', 'Not set')}")
        print(f"Generate HTML: {doc_config.get('generate_html', False)}")
        print(f"Generate Markdown: {doc_config.get('generate_markdown', False)}")
        print(f"Generate JSON: {doc_config.get('generate_json', False)}")
        
        log_config = self.get_logging_config()
        print(f"Log Level: {log_config.get('level', 'INFO')}")
        print("===============================\n")
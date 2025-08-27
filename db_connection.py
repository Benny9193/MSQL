try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    pyodbc = None

import os
from typing import Optional, Dict, Any
from azure.identity import DefaultAzureCredential, ClientSecretCredential
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureSQLConnection:
    """Handles connections to Azure SQL Database with multiple authentication methods."""
    
    def __init__(self):
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc is not installed. Please install pyodbc with: pip install pyodbc")
        self.connection = None
        self.cursor = None
    
    def connect_with_connection_string(self, connection_string: str) -> bool:
        """Connect using a full connection string."""
        try:
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            logger.info("Successfully connected using connection string")
            return True
        except Exception as e:
            logger.error(f"Failed to connect with connection string: {str(e)}")
            return False
    
    def connect_with_credentials(self, server: str, database: str, username: str, password: str, 
                               driver: str = "ODBC Driver 17 for SQL Server") -> bool:
        """Connect using username/password authentication."""
        try:
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            return self.connect_with_connection_string(connection_string)
        except Exception as e:
            logger.error(f"Failed to connect with credentials: {str(e)}")
            return False
    
    def connect_with_azure_ad(self, server: str, database: str, 
                            driver: str = "ODBC Driver 17 for SQL Server") -> bool:
        """Connect using Azure AD authentication (requires Azure CLI login or managed identity)."""
        try:
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Authentication=ActiveDirectoryInteractive;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            return self.connect_with_connection_string(connection_string)
        except Exception as e:
            logger.error(f"Failed to connect with Azure AD: {str(e)}")
            return False
    
    def connect_with_service_principal(self, server: str, database: str, 
                                     client_id: str, client_secret: str, tenant_id: str,
                                     driver: str = "ODBC Driver 17 for SQL Server") -> bool:
        """Connect using Azure Service Principal."""
        try:
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Authentication=ActiveDirectoryServicePrincipal;"
                f"UID={client_id};"
                f"PWD={client_secret};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            return self.connect_with_connection_string(connection_string)
        except Exception as e:
            logger.error(f"Failed to connect with service principal: {str(e)}")
            return False
    
    def execute_query(self, query: str, params=None) -> list:
        """Execute a query and return results."""
        if not self.cursor:
            raise Exception("No database connection established")
        
        try:
            if params is not None:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Handle queries that don't return results
            if self.cursor.description is None:
                return []
            
            columns = [column[0] for column in self.cursor.description]
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def execute_scalar(self, query: str, params=None) -> Any:
        """Execute a query and return a single value."""
        if not self.cursor:
            raise Exception("No database connection established")
        
        try:
            if params is not None:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Scalar query execution failed: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test if the connection is working."""
        try:
            result = self.execute_scalar("SELECT 1")
            return result == 1
        except:
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get basic database information."""
        if not self.cursor:
            raise Exception("No database connection established")
        
        info = {}
        try:
            info['database_name'] = self.execute_scalar("SELECT DB_NAME()")
            info['server_name'] = self.execute_scalar("SELECT @@SERVERNAME")
            info['version'] = self.execute_scalar("SELECT @@VERSION")
            info['user_name'] = self.execute_scalar("SELECT USER_NAME()")
        except Exception as e:
            logger.error(f"Failed to get database info: {str(e)}")
            raise
        
        return info
    
    def list_databases(self) -> list:
        """List all databases on the server with detailed information."""
        if not self.cursor:
            raise Exception("No database connection established")
        
        try:
            query = """
            SELECT 
                d.name,
                d.database_id,
                d.create_date,
                d.collation_name,
                d.state_desc as status,
                COALESCE(
                    (SELECT SUM(CAST(mf.size as bigint) * 8 / 1024) 
                     FROM sys.master_files mf 
                     WHERE mf.database_id = d.database_id 
                     AND mf.type = 0), 0) as size_mb,
                d.compatibility_level
            FROM sys.databases d
            WHERE d.name NOT IN ('master', 'tempdb', 'model', 'msdb')
            ORDER BY d.name
            """
            results = self.execute_query(query)
            return results
        except Exception as e:
            logger.error(f"Failed to list databases: {str(e)}")
            return []
    
    def get_databases(self) -> list:
        """Alternative method name for listing databases."""
        return self.list_databases()
    
    def close(self):
        """Close the database connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
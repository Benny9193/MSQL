#!/usr/bin/env python3
"""
Simple script to list available databases on the SQL Server
"""

import sys
from colorama import init, Fore, Style
from db_connection import AzureSQLConnection

# Initialize colorama for Windows
init()

def list_databases():
    """List all databases on the server."""
    print(f"{Fore.CYAN}Connecting to SQL Server...{Style.RESET_ALL}")
    
    try:
        with AzureSQLConnection() as db:
            # Connect to master database first to list all databases
            success = db.connect_with_credentials(
                server="eds-sqlserver.eastus2.cloudapp.azure.com",
                database="master",  # Connect to master to see all databases
                username="EDSAdmin",
                password="Consultant~!",
                driver="ODBC Driver 17 for SQL Server"
            )
            
            if not success:
                print(f"{Fore.RED}Failed to connect to server{Style.RESET_ALL}")
                return False
            
            print(f"{Fore.GREEN}Connection successful!{Style.RESET_ALL}")
            
            # Query to list all databases
            query = """
            SELECT 
                name as database_name,
                database_id,
                create_date,
                collation_name,
                state_desc as status
            FROM sys.databases 
            WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
            ORDER BY name
            """
            
            databases = db.execute_query(query)
            
            if databases:
                print(f"\n{Fore.CYAN}Available Databases:{Style.RESET_ALL}")
                print("-" * 80)
                print(f"{'Database Name':<30} {'Created':<20} {'Status':<15} {'Collation'}")
                print("-" * 80)
                
                for db_info in databases:
                    create_date = db_info['create_date'].strftime('%Y-%m-%d %H:%M:%S') if db_info['create_date'] else 'Unknown'
                    print(f"{db_info['database_name']:<30} {create_date:<20} {db_info['status']:<15} {db_info['collation_name']}")
                
                print(f"\n{Fore.YELLOW}Found {len(databases)} user database(s){Style.RESET_ALL}")
                
                # If there's only one database, suggest using it
                if len(databases) == 1:
                    db_name = databases[0]['database_name']
                    print(f"\n{Fore.GREEN}Recommendation: Use database '{db_name}' for documentation{Style.RESET_ALL}")
                    return db_name
                else:
                    print(f"\n{Fore.YELLOW}Please specify which database you want to document{Style.RESET_ALL}")
                    return None
            else:
                print(f"{Fore.YELLOW}No user databases found{Style.RESET_ALL}")
                return None
                
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    list_databases()
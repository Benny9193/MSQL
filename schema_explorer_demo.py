#!/usr/bin/env python3
"""
Schema Explorer Demo Application
================================

A standalone demo showcasing the Dynamic Visual Schema Explorer features.
This demonstrates the interactive schema diagrams, relationship visualization,
and navigation capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from schema_explorer import SchemaExplorer, create_schema_explorer_panel, SchemaViewMode
from ui_framework import ThemeManager

class SchemaExplorerDemo:
    """Demo application for the Schema Explorer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_demo_interface()
    
    def setup_window(self):
        """Setup the demo window."""
        self.root.title("Dynamic Visual Schema Explorer Demo")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
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
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="Dynamic Visual Schema Explorer Demo",
                               font=('TkDefaultFont', 18, 'bold'))
        title_label.pack(side='left')
        
        info_label = ttk.Label(header_frame, 
                              text="Interactive database schema visualization and exploration",
                              font=('TkDefaultFont', 11))
        info_label.pack(side='right')
        
        # Create theme manager
        self.theme_manager = ThemeManager()
        
        # Create schema explorer with demo data
        self.explorer = SchemaExplorer(main_frame, None, None, self.theme_manager)
        
        # Load comprehensive demo data
        demo_data = self.create_comprehensive_demo_data()
        self.explorer.schema_data = demo_data
        self.explorer.filtered_data = demo_data
        self.explorer._update_schema_filter_options()
        
        # Refresh visualization
        if hasattr(self.explorer, 'canvas') and self.explorer.canvas:
            self.explorer._refresh_visualization()
        
        # Bottom info panel
        info_frame = ttk.LabelFrame(main_frame, text="Demo Information", padding=10)
        info_frame.pack(fill='x', pady=(15, 0))
        
        info_text = """
This demo showcases the Dynamic Visual Schema Explorer features:

• Interactive Schema Diagrams: Visual representation of database tables, views, and relationships
• Drag-and-Drop Navigation: Move objects around to organize the diagram layout
• Multiple View Modes: Overview, Table Focus, and Relationship Focus modes
• Real-Time Search & Filtering: Find objects quickly with live search
• Detailed Object Information: Click objects to see columns, indexes, and constraints
• Foreign Key Navigation: Double-click relationships to navigate between related tables
• Schema Organization: Filter by schema and explore database structure
• Export Capabilities: Save diagrams as interactive HTML files

Demo Database Schema:
- E-Commerce tables: Users, Orders, Products, Categories, OrderItems
- Sales schema with CustomerAnalytics and SalesReports views
- Foreign key relationships showing data flow and dependencies
- Sample indexes and constraints for realistic database structure

Instructions:
1. Use the Search box to find specific tables (try "User" or "Order")
2. Change View Mode to see different visualization layouts
3. Click objects to see detailed information in the right panel
4. Double-click objects to navigate and explore relationships  
5. Use Schema filter to focus on specific schemas
6. Try the Export button to save diagrams
        """
        
        info_text_widget = tk.Text(info_frame, height=16, wrap='word', font=('TkDefaultFont', 9))
        info_scrollbar = ttk.Scrollbar(info_frame, command=info_text_widget.yview)
        info_text_widget.configure(yscrollcommand=info_scrollbar.set)
        
        info_text_widget.pack(side='left', fill='both', expand=True)
        info_scrollbar.pack(side='right', fill='y')
        info_text_widget.insert('1.0', info_text.strip())
        info_text_widget.config(state='disabled')
    
    def create_comprehensive_demo_data(self):
        """Create comprehensive demo data showcasing all features."""
        return {
            'schemas': [
                {'schema_name': 'dbo', 'schema_id': 1, 'principal_name': 'dbo'},
                {'schema_name': 'sales', 'schema_id': 2, 'principal_name': 'sales_role'},
                {'schema_name': 'inventory', 'schema_id': 3, 'principal_name': 'inventory_role'}
            ],
            'tables': [
                # Core e-commerce tables
                {
                    'schema_name': 'dbo',
                    'table_name': 'Users',
                    'object_id': 1001,
                    'type_desc': 'USER_TABLE',
                    'create_date': '2023-01-01T00:00:00',
                    'modify_date': '2023-08-15T14:30:00',
                    'table_description': 'Customer user accounts and profiles',
                    'columns': [
                        {'column_name': 'UserID', 'data_type': 'int', 'is_nullable': False, 'is_primary_key': True, 'is_identity': True},
                        {'column_name': 'Username', 'data_type': 'nvarchar', 'max_length': 50, 'is_nullable': False},
                        {'column_name': 'Email', 'data_type': 'nvarchar', 'max_length': 100, 'is_nullable': False},
                        {'column_name': 'FirstName', 'data_type': 'nvarchar', 'max_length': 50, 'is_nullable': True},
                        {'column_name': 'LastName', 'data_type': 'nvarchar', 'max_length': 50, 'is_nullable': True},
                        {'column_name': 'CreatedDate', 'data_type': 'datetime2', 'is_nullable': False},
                        {'column_name': 'LastLoginDate', 'data_type': 'datetime2', 'is_nullable': True},
                        {'column_name': 'IsActive', 'data_type': 'bit', 'is_nullable': False}
                    ],
                    'primary_keys': [{'column_name': 'UserID', 'constraint_name': 'PK_Users'}],
                    'foreign_keys': [],
                    'indexes': [
                        {'index_name': 'PK_Users', 'is_primary_key': True, 'is_unique': True, 'columns': 'UserID'},
                        {'index_name': 'IX_Users_Email', 'is_primary_key': False, 'is_unique': True, 'columns': 'Email'},
                        {'index_name': 'IX_Users_Username', 'is_primary_key': False, 'is_unique': True, 'columns': 'Username'}
                    ],
                    'row_count': 15000
                },
                {
                    'schema_name': 'dbo',
                    'table_name': 'Categories',
                    'object_id': 1002,
                    'type_desc': 'USER_TABLE',
                    'create_date': '2023-01-01T00:00:00',
                    'modify_date': '2023-03-10T09:15:00',
                    'table_description': 'Product categories and hierarchy',
                    'columns': [
                        {'column_name': 'CategoryID', 'data_type': 'int', 'is_nullable': False, 'is_primary_key': True, 'is_identity': True},
                        {'column_name': 'CategoryName', 'data_type': 'nvarchar', 'max_length': 100, 'is_nullable': False},
                        {'column_name': 'Description', 'data_type': 'nvarchar', 'max_length': 500, 'is_nullable': True},
                        {'column_name': 'ParentCategoryID', 'data_type': 'int', 'is_nullable': True, 'is_foreign_key': True}
                    ],
                    'primary_keys': [{'column_name': 'CategoryID', 'constraint_name': 'PK_Categories'}],
                    'foreign_keys': [
                        {
                            'foreign_key_name': 'FK_Categories_ParentCategory',
                            'parent_column': 'ParentCategoryID',
                            'referenced_table': 'Categories',
                            'referenced_column': 'CategoryID',
                            'referenced_schema': 'dbo'
                        }
                    ],
                    'indexes': [
                        {'index_name': 'PK_Categories', 'is_primary_key': True, 'is_unique': True, 'columns': 'CategoryID'},
                        {'index_name': 'IX_Categories_Name', 'is_primary_key': False, 'is_unique': False, 'columns': 'CategoryName'}
                    ],
                    'row_count': 250
                },
                {
                    'schema_name': 'inventory',
                    'table_name': 'Products',
                    'object_id': 1003,
                    'type_desc': 'USER_TABLE',
                    'create_date': '2023-01-01T00:00:00',
                    'modify_date': '2023-08-20T16:45:00',
                    'table_description': 'Product catalog with pricing and inventory',
                    'columns': [
                        {'column_name': 'ProductID', 'data_type': 'int', 'is_nullable': False, 'is_primary_key': True, 'is_identity': True},
                        {'column_name': 'ProductName', 'data_type': 'nvarchar', 'max_length': 200, 'is_nullable': False},
                        {'column_name': 'CategoryID', 'data_type': 'int', 'is_nullable': False, 'is_foreign_key': True},
                        {'column_name': 'Price', 'data_type': 'decimal', 'precision': 10, 'scale': 2, 'is_nullable': False},
                        {'column_name': 'StockQuantity', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'SKU', 'data_type': 'varchar', 'max_length': 50, 'is_nullable': False},
                        {'column_name': 'IsDiscontinued', 'data_type': 'bit', 'is_nullable': False}
                    ],
                    'primary_keys': [{'column_name': 'ProductID', 'constraint_name': 'PK_Products'}],
                    'foreign_keys': [
                        {
                            'foreign_key_name': 'FK_Products_Categories',
                            'parent_column': 'CategoryID',
                            'referenced_table': 'Categories',
                            'referenced_column': 'CategoryID',
                            'referenced_schema': 'dbo'
                        }
                    ],
                    'indexes': [
                        {'index_name': 'PK_Products', 'is_primary_key': True, 'is_unique': True, 'columns': 'ProductID'},
                        {'index_name': 'IX_Products_CategoryID', 'is_primary_key': False, 'is_unique': False, 'columns': 'CategoryID'},
                        {'index_name': 'IX_Products_SKU', 'is_primary_key': False, 'is_unique': True, 'columns': 'SKU'}
                    ],
                    'row_count': 5000
                },
                {
                    'schema_name': 'dbo',
                    'table_name': 'Orders',
                    'object_id': 1004,
                    'type_desc': 'USER_TABLE',
                    'create_date': '2023-01-01T00:00:00',
                    'modify_date': '2023-08-25T11:20:00',
                    'table_description': 'Customer orders and order tracking',
                    'columns': [
                        {'column_name': 'OrderID', 'data_type': 'int', 'is_nullable': False, 'is_primary_key': True, 'is_identity': True},
                        {'column_name': 'UserID', 'data_type': 'int', 'is_nullable': False, 'is_foreign_key': True},
                        {'column_name': 'OrderDate', 'data_type': 'datetime2', 'is_nullable': False},
                        {'column_name': 'Status', 'data_type': 'nvarchar', 'max_length': 20, 'is_nullable': False},
                        {'column_name': 'TotalAmount', 'data_type': 'decimal', 'precision': 12, 'scale': 2, 'is_nullable': False},
                        {'column_name': 'ShippingAddress', 'data_type': 'nvarchar', 'max_length': 500, 'is_nullable': True}
                    ],
                    'primary_keys': [{'column_name': 'OrderID', 'constraint_name': 'PK_Orders'}],
                    'foreign_keys': [
                        {
                            'foreign_key_name': 'FK_Orders_Users',
                            'parent_column': 'UserID',
                            'referenced_table': 'Users',
                            'referenced_column': 'UserID',
                            'referenced_schema': 'dbo'
                        }
                    ],
                    'indexes': [
                        {'index_name': 'PK_Orders', 'is_primary_key': True, 'is_unique': True, 'columns': 'OrderID'},
                        {'index_name': 'IX_Orders_UserID', 'is_primary_key': False, 'is_unique': False, 'columns': 'UserID'},
                        {'index_name': 'IX_Orders_OrderDate', 'is_primary_key': False, 'is_unique': False, 'columns': 'OrderDate'}
                    ],
                    'row_count': 25000
                },
                {
                    'schema_name': 'dbo',
                    'table_name': 'OrderItems',
                    'object_id': 1005,
                    'type_desc': 'USER_TABLE',
                    'create_date': '2023-01-01T00:00:00',
                    'modify_date': '2023-08-25T11:20:00',
                    'table_description': 'Individual items within orders',
                    'columns': [
                        {'column_name': 'OrderItemID', 'data_type': 'int', 'is_nullable': False, 'is_primary_key': True, 'is_identity': True},
                        {'column_name': 'OrderID', 'data_type': 'int', 'is_nullable': False, 'is_foreign_key': True},
                        {'column_name': 'ProductID', 'data_type': 'int', 'is_nullable': False, 'is_foreign_key': True},
                        {'column_name': 'Quantity', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'UnitPrice', 'data_type': 'decimal', 'precision': 10, 'scale': 2, 'is_nullable': False}
                    ],
                    'primary_keys': [{'column_name': 'OrderItemID', 'constraint_name': 'PK_OrderItems'}],
                    'foreign_keys': [
                        {
                            'foreign_key_name': 'FK_OrderItems_Orders',
                            'parent_column': 'OrderID',
                            'referenced_table': 'Orders',
                            'referenced_column': 'OrderID',
                            'referenced_schema': 'dbo'
                        },
                        {
                            'foreign_key_name': 'FK_OrderItems_Products',
                            'parent_column': 'ProductID',
                            'referenced_table': 'Products',
                            'referenced_column': 'ProductID',
                            'referenced_schema': 'inventory'
                        }
                    ],
                    'indexes': [
                        {'index_name': 'PK_OrderItems', 'is_primary_key': True, 'is_unique': True, 'columns': 'OrderItemID'},
                        {'index_name': 'IX_OrderItems_OrderID', 'is_primary_key': False, 'is_unique': False, 'columns': 'OrderID'},
                        {'index_name': 'IX_OrderItems_ProductID', 'is_primary_key': False, 'is_unique': False, 'columns': 'ProductID'}
                    ],
                    'row_count': 75000
                }
            ],
            'views': [
                {
                    'schema_name': 'sales',
                    'view_name': 'CustomerAnalytics',
                    'object_id': 2001,
                    'create_date': '2023-02-01T00:00:00',
                    'modify_date': '2023-08-10T13:45:00',
                    'view_description': 'Customer behavior and purchase analytics',
                    'columns': [
                        {'column_name': 'UserID', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'Username', 'data_type': 'nvarchar', 'is_nullable': False},
                        {'column_name': 'TotalOrders', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'TotalSpent', 'data_type': 'decimal', 'is_nullable': True},
                        {'column_name': 'LastOrderDate', 'data_type': 'datetime2', 'is_nullable': True},
                        {'column_name': 'AverageOrderValue', 'data_type': 'decimal', 'is_nullable': True}
                    ],
                    'definition': 'SELECT u.UserID, u.Username, COUNT(o.OrderID) as TotalOrders, SUM(o.TotalAmount) as TotalSpent, MAX(o.OrderDate) as LastOrderDate, AVG(o.TotalAmount) as AverageOrderValue FROM dbo.Users u LEFT JOIN dbo.Orders o ON u.UserID = o.UserID GROUP BY u.UserID, u.Username',
                    'is_updatable': False
                },
                {
                    'schema_name': 'sales',
                    'view_name': 'SalesReports',
                    'object_id': 2002,
                    'create_date': '2023-02-15T00:00:00',
                    'modify_date': '2023-07-20T10:30:00',
                    'view_description': 'Daily and monthly sales reporting',
                    'columns': [
                        {'column_name': 'ReportDate', 'data_type': 'date', 'is_nullable': False},
                        {'column_name': 'TotalSales', 'data_type': 'decimal', 'is_nullable': False},
                        {'column_name': 'OrderCount', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'UniqueCustomers', 'data_type': 'int', 'is_nullable': False},
                        {'column_name': 'AverageOrderValue', 'data_type': 'decimal', 'is_nullable': True}
                    ],
                    'definition': 'SELECT CAST(o.OrderDate AS DATE) as ReportDate, SUM(o.TotalAmount) as TotalSales, COUNT(o.OrderID) as OrderCount, COUNT(DISTINCT o.UserID) as UniqueCustomers, AVG(o.TotalAmount) as AverageOrderValue FROM dbo.Orders o GROUP BY CAST(o.OrderDate AS DATE)',
                    'is_updatable': False
                }
            ],
            'stored_procedures': [
                {
                    'schema_name': 'dbo',
                    'procedure_name': 'GetUserOrderHistory',
                    'object_id': 3001,
                    'create_date': '2023-02-01T00:00:00',
                    'modify_date': '2023-06-15T14:00:00',
                    'procedure_description': 'Retrieve complete order history for a user',
                    'parameters': [
                        {'parameter_name': '@UserID', 'data_type': 'int', 'is_output': False},
                        {'parameter_name': '@StartDate', 'data_type': 'datetime2', 'is_output': False},
                        {'parameter_name': '@EndDate', 'data_type': 'datetime2', 'is_output': False}
                    ]
                },
                {
                    'schema_name': 'inventory',
                    'procedure_name': 'UpdateProductStock',
                    'object_id': 3002,
                    'create_date': '2023-01-15T00:00:00',
                    'modify_date': '2023-08-01T12:30:00',
                    'procedure_description': 'Update product stock levels and track changes',
                    'parameters': [
                        {'parameter_name': '@ProductID', 'data_type': 'int', 'is_output': False},
                        {'parameter_name': '@QuantityChange', 'data_type': 'int', 'is_output': False},
                        {'parameter_name': '@Notes', 'data_type': 'nvarchar', 'is_output': False}
                    ]
                }
            ],
            'functions': [
                {
                    'schema_name': 'dbo',
                    'function_name': 'CalculateOrderTotal',
                    'object_id': 4001,
                    'type_desc': 'SCALAR_FUNCTION',
                    'create_date': '2023-01-20T00:00:00',
                    'modify_date': '2023-05-10T15:20:00',
                    'function_description': 'Calculate total amount for an order including tax'
                }
            ],
            'relationships': {
                'foreign_keys': [
                    {
                        'foreign_key_name': 'FK_Orders_Users',
                        'parent_schema': 'dbo',
                        'parent_table': 'Orders',
                        'parent_column': 'UserID',
                        'referenced_schema': 'dbo',
                        'referenced_table': 'Users',
                        'referenced_column': 'UserID',
                        'delete_referential_action_desc': 'CASCADE',
                        'update_referential_action_desc': 'CASCADE'
                    },
                    {
                        'foreign_key_name': 'FK_OrderItems_Orders',
                        'parent_schema': 'dbo',
                        'parent_table': 'OrderItems',
                        'parent_column': 'OrderID',
                        'referenced_schema': 'dbo',
                        'referenced_table': 'Orders',
                        'referenced_column': 'OrderID',
                        'delete_referential_action_desc': 'CASCADE',
                        'update_referential_action_desc': 'CASCADE'
                    },
                    {
                        'foreign_key_name': 'FK_OrderItems_Products',
                        'parent_schema': 'dbo',
                        'parent_table': 'OrderItems',
                        'parent_column': 'ProductID',
                        'referenced_schema': 'inventory',
                        'referenced_table': 'Products',
                        'referenced_column': 'ProductID',
                        'delete_referential_action_desc': 'RESTRICT',
                        'update_referential_action_desc': 'CASCADE'
                    },
                    {
                        'foreign_key_name': 'FK_Products_Categories',
                        'parent_schema': 'inventory',
                        'parent_table': 'Products',
                        'parent_column': 'CategoryID',
                        'referenced_schema': 'dbo',
                        'referenced_table': 'Categories',
                        'referenced_column': 'CategoryID',
                        'delete_referential_action_desc': 'RESTRICT',
                        'update_referential_action_desc': 'CASCADE'
                    },
                    {
                        'foreign_key_name': 'FK_Categories_ParentCategory',
                        'parent_schema': 'dbo',
                        'parent_table': 'Categories',
                        'parent_column': 'ParentCategoryID',
                        'referenced_schema': 'dbo',
                        'referenced_table': 'Categories',
                        'referenced_column': 'CategoryID',
                        'delete_referential_action_desc': 'SET_NULL',
                        'update_referential_action_desc': 'CASCADE'
                    }
                ]
            }
        }
    
    def run(self):
        """Run the demo application."""
        try:
            print("Starting Dynamic Visual Schema Explorer Demo...")
            print("Sample e-commerce database schema loaded!")
            print("Explore the interactive diagram with drag-and-drop navigation.")
            print("Try different view modes and search functionality.")
            print("Double-click objects to see detailed information.")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nDemo terminated by user")
        except Exception as e:
            print(f"Demo error: {e}")
            messagebox.showerror("Demo Error", f"An error occurred: {e}")

def main():
    """Run the schema explorer demo."""
    try:
        demo = SchemaExplorerDemo()
        demo.run()
    except Exception as e:
        print(f"Failed to start demo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from schema_analyzer import SchemaAnalyzer
from db_connection import AzureSQLConnection

logger = logging.getLogger(__name__)

class DocumentationExtractor:
    """Extracts and organizes complete database documentation."""
    
    def __init__(self, db_connection: AzureSQLConnection):
        self.db = db_connection
        self.analyzer = SchemaAnalyzer(db_connection)
    
    def extract_complete_documentation(self) -> Dict[str, Any]:
        """Extract all database documentation in a structured format."""
        logger.info("Starting complete documentation extraction...")
        
        documentation = {
            'metadata': self._extract_database_metadata(),
            'schemas': self._extract_schemas_documentation(),
            'tables': self._extract_tables_documentation(),
            'views': self._extract_views_documentation(),
            'stored_procedures': self._extract_procedures_documentation(),
            'functions': self._extract_functions_documentation(),
            'relationships': self._extract_relationships_documentation(),
            'statistics': self._extract_database_statistics()
        }
        
        logger.info("Documentation extraction completed")
        return documentation
    
    def _extract_database_metadata(self) -> Dict[str, Any]:
        """Extract basic database metadata."""
        try:
            db_info = self.db.get_database_info()
            size_info = self.analyzer.get_database_size()
            
            return {
                'database_name': db_info.get('database_name', ''),
                'server_name': db_info.get('server_name', ''),
                'version': db_info.get('version', ''),
                'user_name': db_info.get('user_name', ''),
                'extraction_date': datetime.now().isoformat(),
                'size_mb': size_info.get('allocated_mb', 0),
                'used_mb': size_info.get('used_mb', 0)
            }
        except Exception as e:
            logger.error(f"Failed to extract database metadata: {str(e)}")
            return {}
    
    def _extract_schemas_documentation(self) -> List[Dict[str, Any]]:
        """Extract schemas documentation."""
        try:
            schemas = self.analyzer.get_all_schemas()
            return [
                {
                    'name': schema['schema_name'],
                    'schema_id': schema['schema_id'],
                    'principal': schema['principal_name']
                }
                for schema in schemas
            ]
        except Exception as e:
            logger.error(f"Failed to extract schemas: {str(e)}")
            return []
    
    def _extract_tables_documentation(self) -> List[Dict[str, Any]]:
        """Extract complete tables documentation."""
        try:
            tables = self.analyzer.get_all_tables()
            tables_doc = []
            
            for table in tables:
                table_doc = {
                    'schema_name': table['schema_name'],
                    'table_name': table['table_name'],
                    'object_id': table['object_id'],
                    'type': table['type_desc'],
                    'created': table['create_date'].isoformat() if table['create_date'] else None,
                    'modified': table['modify_date'].isoformat() if table['modify_date'] else None,
                    'description': table['table_description'] or '',
                    'columns': self._extract_table_columns(table['object_id']),
                    'primary_keys': self._extract_primary_keys(table['object_id']),
                    'foreign_keys': self._extract_foreign_keys(table['object_id']),
                    'indexes': self._extract_indexes(table['object_id']),
                    'check_constraints': self._extract_check_constraints(table['object_id']),
                    'triggers': self._extract_triggers(table['object_id']),
                    'row_count': self._get_table_row_count(table['schema_name'], table['table_name'])
                }
                tables_doc.append(table_doc)
            
            return tables_doc
        except Exception as e:
            logger.error(f"Failed to extract tables documentation: {str(e)}")
            return []
    
    def _extract_table_columns(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Extract columns for a specific table."""
        try:
            columns = self.analyzer.get_table_columns(table_object_id)
            return [
                {
                    'column_id': col['column_id'],
                    'name': col['column_name'],
                    'data_type': self._format_data_type(col),
                    'is_nullable': bool(col['is_nullable']),
                    'is_identity': bool(col['is_identity']),
                    'is_computed': bool(col['is_computed']),
                    'default_value': col['default_constraint'] or '',
                    'description': col['column_description'] or ''
                }
                for col in columns
            ]
        except Exception as e:
            logger.error(f"Failed to extract columns for table {table_object_id}: {str(e)}")
            return []
    
    def _extract_views_documentation(self) -> List[Dict[str, Any]]:
        """Extract complete views documentation."""
        try:
            views = self.analyzer.get_all_views()
            views_doc = []
            
            for view in views:
                view_doc = {
                    'schema_name': view['schema_name'],
                    'view_name': view['view_name'],
                    'object_id': view['object_id'],
                    'created': view['create_date'].isoformat() if view['create_date'] else None,
                    'modified': view['modify_date'].isoformat() if view['modify_date'] else None,
                    'description': view['view_description'] or '',
                    'columns': self._extract_view_columns(view['object_id'])
                }
                views_doc.append(view_doc)
            
            return views_doc
        except Exception as e:
            logger.error(f"Failed to extract views documentation: {str(e)}")
            return []
    
    def _extract_view_columns(self, view_object_id: int) -> List[Dict[str, Any]]:
        """Extract columns for a specific view."""
        try:
            columns = self.analyzer.get_view_columns(view_object_id)
            return [
                {
                    'column_id': col['column_id'],
                    'name': col['column_name'],
                    'data_type': self._format_data_type(col),
                    'is_nullable': bool(col['is_nullable']),
                    'description': col['column_description'] or ''
                }
                for col in columns
            ]
        except Exception as e:
            logger.error(f"Failed to extract columns for view {view_object_id}: {str(e)}")
            return []
    
    def _extract_procedures_documentation(self) -> List[Dict[str, Any]]:
        """Extract stored procedures documentation."""
        try:
            procedures = self.analyzer.get_stored_procedures()
            return [
                {
                    'schema_name': proc['schema_name'],
                    'procedure_name': proc['procedure_name'],
                    'object_id': proc['object_id'],
                    'created': proc['create_date'].isoformat() if proc['create_date'] else None,
                    'modified': proc['modify_date'].isoformat() if proc['modify_date'] else None,
                    'description': proc['procedure_description'] or ''
                }
                for proc in procedures
            ]
        except Exception as e:
            logger.error(f"Failed to extract procedures documentation: {str(e)}")
            return []
    
    def _extract_functions_documentation(self) -> List[Dict[str, Any]]:
        """Extract functions documentation."""
        try:
            functions = self.analyzer.get_functions()
            return [
                {
                    'schema_name': func['schema_name'],
                    'function_name': func['function_name'],
                    'object_id': func['object_id'],
                    'type': func['type_desc'],
                    'created': func['create_date'].isoformat() if func['create_date'] else None,
                    'modified': func['modify_date'].isoformat() if func['modify_date'] else None,
                    'description': func['function_description'] or ''
                }
                for func in functions
            ]
        except Exception as e:
            logger.error(f"Failed to extract functions documentation: {str(e)}")
            return []
    
    def _extract_primary_keys(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Extract primary keys for a table."""
        try:
            return self.analyzer.get_primary_keys(table_object_id)
        except Exception as e:
            logger.error(f"Failed to extract primary keys for table {table_object_id}: {str(e)}")
            return []
    
    def _extract_foreign_keys(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Extract foreign keys for a table."""
        try:
            return self.analyzer.get_foreign_keys(table_object_id)
        except Exception as e:
            logger.error(f"Failed to extract foreign keys for table {table_object_id}: {str(e)}")
            return []
    
    def _extract_indexes(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Extract indexes for a table."""
        try:
            return self.analyzer.get_indexes(table_object_id)
        except Exception as e:
            logger.error(f"Failed to extract indexes for table {table_object_id}: {str(e)}")
            return []
    
    def _extract_check_constraints(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Extract check constraints for a table."""
        try:
            return self.analyzer.get_check_constraints(table_object_id)
        except Exception as e:
            logger.error(f"Failed to extract check constraints for table {table_object_id}: {str(e)}")
            return []
    
    def _extract_triggers(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Extract triggers for a table."""
        try:
            return self.analyzer.get_triggers(table_object_id)
        except Exception as e:
            logger.error(f"Failed to extract triggers for table {table_object_id}: {str(e)}")
            return []
    
    def _extract_relationships_documentation(self) -> Dict[str, Any]:
        """Extract all database relationships."""
        try:
            foreign_keys = self.analyzer.get_foreign_keys()
            
            relationships = {
                'foreign_keys': foreign_keys,
                'relationship_count': len(foreign_keys)
            }
            
            return relationships
        except Exception as e:
            logger.error(f"Failed to extract relationships: {str(e)}")
            return {'foreign_keys': [], 'relationship_count': 0}
    
    def _extract_database_statistics(self) -> Dict[str, Any]:
        """Extract database statistics."""
        try:
            row_counts = self.analyzer.get_table_row_counts()
            schemas = self.analyzer.get_all_schemas()
            tables = self.analyzer.get_all_tables()
            views = self.analyzer.get_all_views()
            procedures = self.analyzer.get_stored_procedures()
            functions = self.analyzer.get_functions()
            
            total_rows = sum(row['row_count'] for row in row_counts if row['row_count'])
            
            return {
                'total_schemas': len(schemas),
                'total_tables': len(tables),
                'total_views': len(views),
                'total_procedures': len(procedures),
                'total_functions': len(functions),
                'total_rows': total_rows,
                'largest_tables': sorted(row_counts, key=lambda x: x['row_count'] or 0, reverse=True)[:10]
            }
        except Exception as e:
            logger.error(f"Failed to extract database statistics: {str(e)}")
            return {}
    
    def _format_data_type(self, column: Dict[str, Any]) -> str:
        """Format column data type with length/precision."""
        data_type = column['data_type']
        
        if data_type in ['varchar', 'nvarchar', 'char', 'nchar']:
            if column['max_length'] == -1:
                return f"{data_type}(MAX)"
            elif data_type.startswith('n'):
                return f"{data_type}({column['max_length']//2})"
            else:
                return f"{data_type}({column['max_length']})"
        elif data_type in ['decimal', 'numeric']:
            return f"{data_type}({column['precision']},{column['scale']})"
        elif data_type in ['float']:
            return f"{data_type}({column['precision']})"
        elif data_type in ['binary', 'varbinary']:
            if column['max_length'] == -1:
                return f"{data_type}(MAX)"
            else:
                return f"{data_type}({column['max_length']})"
        else:
            return data_type
    
    def _get_table_row_count(self, schema_name: str, table_name: str) -> int:
        """Get row count for a specific table."""
        try:
            row_counts = self.analyzer.get_table_row_counts()
            for row in row_counts:
                if row['schema_name'] == schema_name and row['table_name'] == table_name:
                    return row['row_count'] or 0
            return 0
        except Exception as e:
            logger.error(f"Failed to get row count for {schema_name}.{table_name}: {str(e)}")
            return 0
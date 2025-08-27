from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from db_connection import AzureSQLConnection

logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    """Analyzes SQL Server database schema and extracts comprehensive metadata."""
    
    def __init__(self, db_connection: AzureSQLConnection):
        self.db = db_connection
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get all schemas in the database."""
        try:
            query = """
            SELECT 
                s.name as schema_name,
                s.schema_id,
                p.name as principal_name
            FROM sys.schemas s
            LEFT JOIN sys.database_principals p ON s.principal_id = p.principal_id
            WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA')
            ORDER BY s.name
            """
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get schemas: {str(e)}")
            return []
    
    def get_all_tables(self, schema_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tables, optionally filtered by schema."""
        try:
            if schema_name:
                query = """
                SELECT 
                    s.name as schema_name,
                    t.name as table_name,
                    t.object_id,
                    t.type_desc,
                    t.create_date,
                    t.modify_date,
                    ep.value as table_description
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON t.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE s.name = ?
                ORDER BY s.name, t.name
                """
                return self.db.execute_query(query, (schema_name,))
            else:
                query = """
                SELECT 
                    s.name as schema_name,
                    t.name as table_name,
                    t.object_id,
                    t.type_desc,
                    t.create_date,
                    t.modify_date,
                    ep.value as table_description
                FROM sys.tables t
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON t.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                ORDER BY s.name, t.name
                """
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get tables: {str(e)}")
            return []
    
    def get_all_views(self, schema_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all views, optionally filtered by schema."""
        try:
            if schema_name:
                query = """
                SELECT 
                    s.name as schema_name,
                    v.name as view_name,
                    v.object_id,
                    v.create_date,
                    v.modify_date,
                    ep.value as view_description
                FROM sys.views v
                INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON v.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE s.name = ?
                ORDER BY s.name, v.name
                """
                return self.db.execute_query(query, (schema_name,))
            else:
                query = """
                SELECT 
                    s.name as schema_name,
                    v.name as view_name,
                    v.object_id,
                    v.create_date,
                    v.modify_date,
                    ep.value as view_description
                FROM sys.views v
                INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON v.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                ORDER BY s.name, v.name
                """
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get views: {str(e)}")
            return []
    
    def get_table_columns(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Get all columns for a specific table."""
        try:
            query = """
            SELECT 
                c.column_id,
                c.name as column_name,
                t.name as data_type,
                c.max_length,
                c.precision,
                c.scale,
                c.is_nullable,
                c.is_identity,
                c.is_computed,
                ISNULL(dc.definition, '') as default_constraint,
                ep.value as column_description
            FROM sys.columns c
            INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
            LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
            LEFT JOIN sys.extended_properties ep ON c.object_id = ep.major_id 
                AND c.column_id = ep.minor_id AND ep.name = 'MS_Description'
            WHERE c.object_id = ?
            ORDER BY c.column_id
            """
            return self.db.execute_query(query, (table_object_id,))
        except Exception as e:
            logger.error(f"Failed to get table columns for object_id {table_object_id}: {str(e)}")
            return []
    
    def get_view_columns(self, view_object_id: int) -> List[Dict[str, Any]]:
        """Get all columns for a specific view."""
        try:
            query = """
            SELECT 
                c.column_id,
                c.name as column_name,
                t.name as data_type,
                c.max_length,
                c.precision,
                c.scale,
                c.is_nullable,
                ep.value as column_description
            FROM sys.columns c
            INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
            LEFT JOIN sys.extended_properties ep ON c.object_id = ep.major_id 
                AND c.column_id = ep.minor_id AND ep.name = 'MS_Description'
            WHERE c.object_id = ?
            ORDER BY c.column_id
            """
            return self.db.execute_query(query, (view_object_id,))
        except Exception as e:
            logger.error(f"Failed to get view columns for object_id {view_object_id}: {str(e)}")
            return []
    
    def get_primary_keys(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Get primary key information for a table."""
        try:
            query = """
            SELECT 
                kc.name as constraint_name,
                c.name as column_name,
                ic.key_ordinal
            FROM sys.key_constraints kc
            INNER JOIN sys.index_columns ic ON kc.parent_object_id = ic.object_id 
                AND kc.unique_index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id 
                AND ic.column_id = c.column_id
            WHERE kc.type = 'PK' AND kc.parent_object_id = ?
            ORDER BY ic.key_ordinal
            """
            return self.db.execute_query(query, (table_object_id,))
        except Exception as e:
            logger.error(f"Failed to get primary keys for table {table_object_id}: {str(e)}")
            return []
    
    def get_foreign_keys(self, table_object_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get foreign key relationships."""
        try:
            if table_object_id:
                query = """
                SELECT 
                    fk.name as foreign_key_name,
                    OBJECT_SCHEMA_NAME(fk.parent_object_id) as parent_schema,
                    OBJECT_NAME(fk.parent_object_id) as parent_table,
                    pc.name as parent_column,
                    OBJECT_SCHEMA_NAME(fk.referenced_object_id) as referenced_schema,
                    OBJECT_NAME(fk.referenced_object_id) as referenced_table,
                    rc.name as referenced_column,
                    fk.delete_referential_action_desc as on_delete,
                    fk.update_referential_action_desc as on_update
                FROM sys.foreign_keys fk
                INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.columns pc ON fkc.parent_object_id = pc.object_id 
                    AND fkc.parent_column_id = pc.column_id
                INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id 
                    AND fkc.referenced_column_id = rc.column_id
                WHERE fk.parent_object_id = ?
                ORDER BY fk.name, fkc.constraint_column_id
                """
                return self.db.execute_query(query, (table_object_id,))
            else:
                query = """
                SELECT 
                    fk.name as foreign_key_name,
                    OBJECT_SCHEMA_NAME(fk.parent_object_id) as parent_schema,
                    OBJECT_NAME(fk.parent_object_id) as parent_table,
                    pc.name as parent_column,
                    OBJECT_SCHEMA_NAME(fk.referenced_object_id) as referenced_schema,
                    OBJECT_NAME(fk.referenced_object_id) as referenced_table,
                    rc.name as referenced_column,
                    fk.delete_referential_action_desc as on_delete,
                    fk.update_referential_action_desc as on_update
                FROM sys.foreign_keys fk
                INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.columns pc ON fkc.parent_object_id = pc.object_id 
                    AND fkc.parent_column_id = pc.column_id
                INNER JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id 
                    AND fkc.referenced_column_id = rc.column_id
                ORDER BY fk.name, fkc.constraint_column_id
                """
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get foreign keys: {str(e)}")
            return []
    
    def get_indexes(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Get all indexes for a table."""
        try:
            # Check SQL Server version for STRING_AGG compatibility
            version_query = "SELECT @@VERSION as version"
            version_result = self.db.execute_query(version_query)
            
            # Use STRING_AGG for SQL Server 2017+ or fallback for older versions
            if version_result and 'Microsoft SQL Server 2017' in str(version_result[0].get('version', '')) or \
               version_result and any(year in str(version_result[0].get('version', '')) for year in ['2019', '2022']):
                # Modern SQL Server with STRING_AGG support
                query = """
                SELECT 
                    i.name as index_name,
                    i.type_desc as index_type,
                    i.is_unique,
                    i.is_primary_key,
                    STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) as columns
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
                INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                WHERE i.object_id = ? AND i.type > 0
                GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key
                ORDER BY i.is_primary_key DESC, i.name
                """
            else:
                # Fallback for older SQL Server versions
                query = """
                SELECT 
                    i.name as index_name,
                    i.type_desc as index_type,
                    i.is_unique,
                    i.is_primary_key,
                    STUFF((
                        SELECT ', ' + c2.name
                        FROM sys.index_columns ic2
                        INNER JOIN sys.columns c2 ON ic2.object_id = c2.object_id AND ic2.column_id = c2.column_id
                        WHERE ic2.object_id = i.object_id AND ic2.index_id = i.index_id
                        ORDER BY ic2.key_ordinal
                        FOR XML PATH('')
                    ), 1, 2, '') as columns
                FROM sys.indexes i
                WHERE i.object_id = ? AND i.type > 0
                ORDER BY i.is_primary_key DESC, i.name
                """
            
            return self.db.execute_query(query, (table_object_id,))
        except Exception as e:
            logger.error(f"Failed to get indexes for table {table_object_id}: {str(e)}")
            return []
    
    def get_check_constraints(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Get check constraints for a table."""
        try:
            query = """
            SELECT 
                cc.name as constraint_name,
                cc.definition as constraint_definition
            FROM sys.check_constraints cc
            WHERE cc.parent_object_id = ?
            ORDER BY cc.name
            """
            return self.db.execute_query(query, (table_object_id,))
        except Exception as e:
            logger.error(f"Failed to get check constraints for table {table_object_id}: {str(e)}")
            return []
    
    def get_stored_procedures(self, schema_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all stored procedures."""
        try:
            if schema_name:
                query = """
                SELECT 
                    s.name as schema_name,
                    p.name as procedure_name,
                    p.object_id,
                    p.create_date,
                    p.modify_date,
                    ep.value as procedure_description
                FROM sys.procedures p
                INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON p.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE s.name = ?
                ORDER BY s.name, p.name
                """
                return self.db.execute_query(query, (schema_name,))
            else:
                query = """
                SELECT 
                    s.name as schema_name,
                    p.name as procedure_name,
                    p.object_id,
                    p.create_date,
                    p.modify_date,
                    ep.value as procedure_description
                FROM sys.procedures p
                INNER JOIN sys.schemas s ON p.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON p.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                ORDER BY s.name, p.name
                """
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get stored procedures: {str(e)}")
            return []
    
    def get_functions(self, schema_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all functions."""
        try:
            if schema_name:
                query = """
                SELECT 
                    s.name as schema_name,
                    o.name as function_name,
                    o.object_id,
                    o.type_desc,
                    o.create_date,
                    o.modify_date,
                    ep.value as function_description
                FROM sys.objects o
                INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON o.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE o.type IN ('FN', 'IF', 'TF', 'FS', 'FT') AND s.name = ?
                ORDER BY s.name, o.name
                """
                return self.db.execute_query(query, (schema_name,))
            else:
                query = """
                SELECT 
                    s.name as schema_name,
                    o.name as function_name,
                    o.object_id,
                    o.type_desc,
                    o.create_date,
                    o.modify_date,
                    ep.value as function_description
                FROM sys.objects o
                INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
                LEFT JOIN sys.extended_properties ep ON o.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE o.type IN ('FN', 'IF', 'TF', 'FS', 'FT')
                ORDER BY s.name, o.name
                """
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get functions: {str(e)}")
            return []
    
    def get_triggers(self, table_object_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get triggers."""
        try:
            if table_object_id:
                query = """
                SELECT 
                    OBJECT_SCHEMA_NAME(tr.parent_id) as table_schema,
                    OBJECT_NAME(tr.parent_id) as table_name,
                    tr.name as trigger_name,
                    tr.type_desc,
                    tr.is_disabled,
                    ep.value as trigger_description
                FROM sys.triggers tr
                LEFT JOIN sys.extended_properties ep ON tr.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE tr.parent_id = ?
                ORDER BY tr.name
                """
                return self.db.execute_query(query, (table_object_id,))
            else:
                query = """
                SELECT 
                    OBJECT_SCHEMA_NAME(tr.parent_id) as table_schema,
                    OBJECT_NAME(tr.parent_id) as table_name,
                    tr.name as trigger_name,
                    tr.type_desc,
                    tr.is_disabled,
                    ep.value as trigger_description
                FROM sys.triggers tr
                LEFT JOIN sys.extended_properties ep ON tr.object_id = ep.major_id 
                    AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                WHERE tr.parent_id IS NOT NULL
                ORDER BY tr.name
                """
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get triggers: {str(e)}")
            return []
    
    def get_database_size(self) -> Dict[str, Any]:
        """Get database size information."""
        try:
            query = """
            SELECT 
                DB_NAME() as database_name,
                SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS bigint) * 8192.) / (1024 * 1024) as used_mb,
                SUM(size * 8192.) / (1024 * 1024) as allocated_mb
            FROM sys.database_files
            WHERE type IN (0,1)
            """
            result = self.db.execute_query(query)
            return result[0] if result else {'database_name': 'Unknown', 'used_mb': 0, 'allocated_mb': 0}
        except Exception as e:
            logger.error(f"Failed to get database size: {str(e)}")
            return {'database_name': 'Unknown', 'used_mb': 0, 'allocated_mb': 0}
    
    def get_table_row_counts(self) -> List[Dict[str, Any]]:
        """Get row counts for all tables."""
        try:
            query = """
            SELECT 
                s.name as schema_name,
                t.name as table_name,
                p.rows as row_count
            FROM sys.tables t
            INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
            INNER JOIN sys.partitions p ON t.object_id = p.object_id
            WHERE p.index_id IN (0,1)
            ORDER BY p.rows DESC
            """
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get table row counts: {str(e)}")
            return []
    
    def get_unique_constraints(self, table_object_id: int) -> List[Dict[str, Any]]:
        """Get unique constraints for a table."""
        try:
            query = """
            SELECT 
                kc.name as constraint_name,
                c.name as column_name,
                ic.key_ordinal
            FROM sys.key_constraints kc
            INNER JOIN sys.index_columns ic ON kc.parent_object_id = ic.object_id 
                AND kc.unique_index_id = ic.index_id
            INNER JOIN sys.columns c ON ic.object_id = c.object_id 
                AND ic.column_id = c.column_id
            WHERE kc.type = 'UQ' AND kc.parent_object_id = ?
            ORDER BY kc.name, ic.key_ordinal
            """
            return self.db.execute_query(query, (table_object_id,))
        except Exception as e:
            logger.error(f"Failed to get unique constraints for table {table_object_id}: {str(e)}")
            return []
    
    def get_table_dependencies(self, table_object_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get dependencies for a table (what it depends on and what depends on it)."""
        try:
            # Tables this table depends on (via foreign keys)
            dependencies_query = """
            SELECT DISTINCT
                'table' as dependency_type,
                OBJECT_SCHEMA_NAME(fk.referenced_object_id) as schema_name,
                OBJECT_NAME(fk.referenced_object_id) as object_name,
                'foreign_key' as relationship_type
            FROM sys.foreign_keys fk
            WHERE fk.parent_object_id = ?
            """
            
            dependencies = self.db.execute_query(dependencies_query, (table_object_id,))
            
            # Tables that depend on this table
            dependents_query = """
            SELECT DISTINCT
                'table' as dependency_type,
                OBJECT_SCHEMA_NAME(fk.parent_object_id) as schema_name,
                OBJECT_NAME(fk.parent_object_id) as object_name,
                'foreign_key' as relationship_type
            FROM sys.foreign_keys fk
            WHERE fk.referenced_object_id = ?
            """
            
            dependents = self.db.execute_query(dependents_query, (table_object_id,))
            
            return {
                'dependencies': dependencies,
                'dependents': dependents
            }
        except Exception as e:
            logger.error(f"Failed to get table dependencies for {table_object_id}: {str(e)}")
            return {'dependencies': [], 'dependents': []}
    
    def get_table_statistics(self, table_object_id: int) -> Dict[str, Any]:
        """Get statistics for a table."""
        try:
            # Get table statistics information
            stats_query = """
            SELECT 
                s.name as stats_name,
                STATS_DATE(s.object_id, s.stats_id) as last_updated,
                s.no_recompute,
                s.is_temporary,
                sp.last_updated as last_updated_alt,
                sp.rows,
                sp.rows_sampled,
                sp.modification_counter
            FROM sys.stats s
            CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
            WHERE s.object_id = ?
            ORDER BY s.name
            """
            
            statistics = self.db.execute_query(stats_query, (table_object_id,))
            
            # Get index statistics
            index_stats_query = """
            SELECT 
                i.name as index_name,
                ius.user_seeks,
                ius.user_scans,
                ius.user_lookups,
                ius.user_updates,
                ius.last_user_seek,
                ius.last_user_scan,
                ius.last_user_lookup,
                ius.last_user_update
            FROM sys.indexes i
            LEFT JOIN sys.dm_db_index_usage_stats ius ON i.object_id = ius.object_id AND i.index_id = ius.index_id
            WHERE i.object_id = ? AND i.type > 0
            ORDER BY i.name
            """
            
            index_stats = self.db.execute_query(index_stats_query, (table_object_id,))
            
            return {
                'statistics': statistics,
                'index_usage': index_stats
            }
        except Exception as e:
            logger.error(f"Failed to get table statistics for {table_object_id}: {str(e)}")
            return {'statistics': [], 'index_usage': []}
    
    def get_schema_objects_count(self, schema_name: str) -> Dict[str, int]:
        """Get count of different object types in a schema."""
        try:
            query = """
            SELECT 
                object_type,
                COUNT(*) as object_count
            FROM (
                SELECT 'table' as object_type FROM sys.tables t 
                INNER JOIN sys.schemas s ON t.schema_id = s.schema_id 
                WHERE s.name = ?
                
                UNION ALL
                
                SELECT 'view' as object_type FROM sys.views v 
                INNER JOIN sys.schemas s ON v.schema_id = s.schema_id 
                WHERE s.name = ?
                
                UNION ALL
                
                SELECT 'procedure' as object_type FROM sys.procedures p 
                INNER JOIN sys.schemas s ON p.schema_id = s.schema_id 
                WHERE s.name = ?
                
                UNION ALL
                
                SELECT 'function' as object_type FROM sys.objects o 
                INNER JOIN sys.schemas s ON o.schema_id = s.schema_id 
                WHERE s.name = ? AND o.type IN ('FN', 'IF', 'TF', 'FS', 'FT')
            ) obj_counts
            GROUP BY object_type
            """
            
            results = self.db.execute_query(query, (schema_name, schema_name, schema_name, schema_name))
            
            # Convert to dictionary with default values
            counts = {'table': 0, 'view': 0, 'procedure': 0, 'function': 0}
            for result in results:
                counts[result['object_type']] = result['object_count']
            
            return counts
        except Exception as e:
            logger.error(f"Failed to get schema object counts for {schema_name}: {str(e)}")
            return {'table': 0, 'view': 0, 'procedure': 0, 'function': 0}
    
    def get_database_collation(self) -> str:
        """Get database collation information."""
        try:
            query = "SELECT DATABASEPROPERTYEX(DB_NAME(), 'Collation') as collation"
            result = self.db.execute_query(query)
            return result[0]['collation'] if result else 'Unknown'
        except Exception as e:
            logger.error(f"Failed to get database collation: {str(e)}")
            return 'Unknown'
    
    def get_database_compatibility_level(self) -> str:
        """Get database compatibility level."""
        try:
            query = "SELECT compatibility_level FROM sys.databases WHERE name = DB_NAME()"
            result = self.db.execute_query(query)
            if result:
                level = result[0]['compatibility_level']
                return f"{level} (SQL Server {self._compatibility_level_to_version(level)})"
            return 'Unknown'
        except Exception as e:
            logger.error(f"Failed to get database compatibility level: {str(e)}")
            return 'Unknown'
    
    def _compatibility_level_to_version(self, level: int) -> str:
        """Convert compatibility level to SQL Server version."""
        mapping = {
            80: '2000',
            90: '2005', 
            100: '2008/2008R2',
            110: '2012',
            120: '2014',
            130: '2016',
            140: '2017',
            150: '2019',
            160: '2022'
        }
        return mapping.get(level, f'Unknown ({level})')
    
    def validate_connection(self) -> bool:
        """Validate database connection is working."""
        try:
            query = "SELECT 1 as test"
            result = self.db.execute_query(query)
            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
    
    def get_performance_counters(self) -> Dict[str, Any]:
        """Get basic performance counters for health monitoring."""
        try:
            counters = {}
            
            # Get wait statistics
            wait_stats_query = """
            SELECT TOP 10
                wait_type,
                waiting_tasks_count,
                wait_time_ms,
                max_wait_time_ms,
                signal_wait_time_ms
            FROM sys.dm_os_wait_stats
            WHERE wait_time_ms > 0
              AND wait_type NOT LIKE '%SLEEP%'
              AND wait_type NOT LIKE '%IDLE%'
              AND wait_type NOT LIKE '%QUEUE%'
            ORDER BY wait_time_ms DESC
            """
            
            wait_stats = self.db.execute_query(wait_stats_query)
            counters['wait_stats'] = wait_stats
            
            # Get connection count
            connection_query = """
            SELECT 
                COUNT(*) as total_connections,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_connections,
                COUNT(CASE WHEN status = 'sleeping' THEN 1 END) as sleeping_connections
            FROM sys.dm_exec_sessions
            WHERE is_user_process = 1
            """
            
            connection_stats = self.db.execute_query(connection_query)
            counters['connections'] = connection_stats[0] if connection_stats else {}
            
            # Get blocked process count
            blocked_query = """
            SELECT COUNT(*) as blocked_process_count
            FROM sys.dm_exec_requests
            WHERE blocking_session_id > 0
            """
            
            blocked_stats = self.db.execute_query(blocked_query)
            counters['blocked_processes'] = blocked_stats[0]['blocked_process_count'] if blocked_stats else 0
            
            return counters
        except Exception as e:
            logger.error(f"Failed to get performance counters: {str(e)}")
            return {'wait_stats': [], 'connections': {}, 'blocked_processes': 0}
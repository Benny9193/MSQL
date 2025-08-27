# {{ doc.metadata.database_name }} - Database Documentation

**Server:** {{ doc.metadata.server_name }}  
**Generated:** {{ doc.metadata.extraction_date | format_date }}  
**Size:** {{ doc.metadata.used_mb | format_number }} MB used of {{ doc.metadata.size_mb | format_number }} MB allocated

## Table of Contents
- [Database Overview](#database-overview)
- [Schemas](#schemas)
- [Tables](#tables)
- [Views](#views)
- [Stored Procedures](#stored-procedures)
- [Functions](#functions)
- [Relationships](#relationships)

## Database Overview

| Metric | Count |
|--------|-------|
| Schemas | {{ doc.statistics.total_schemas }} |
| Tables | {{ doc.statistics.total_tables }} |
| Views | {{ doc.statistics.total_views }} |
| Stored Procedures | {{ doc.statistics.total_procedures }} |
| Functions | {{ doc.statistics.total_functions }} |
| Total Rows | {{ doc.statistics.total_rows | format_number }} |

## Schemas

| Schema Name | Principal |
|-------------|-----------|
{% for schema in doc.schemas -%}
| {{ schema.name }} | {{ schema.principal }} |
{% endfor %}

## Tables

{% for table in doc.tables %}
### {{ table.schema_name }}.{{ table.table_name }}

{% if table.description %}
**Description:** {{ table.description }}
{% endif %}

**Rows:** {{ table.row_count | format_number }}

#### Columns

| Column | Data Type | Nullable | Identity | Default | Description |
|--------|-----------|----------|----------|---------|-------------|
{% for column in table.columns -%}
| {{ column.name }} | {{ column.data_type }} | {{ 'Yes' if column.is_nullable else 'No' }} | {{ 'Yes' if column.is_identity else 'No' }} | {{ column.default_value }} | {{ column.description }} |
{% endfor %}

{% if table.primary_keys %}
**Primary Key:** {{ table.primary_keys | map(attribute='column_name') | join(', ') }}
{% endif %}

{% if table.foreign_keys %}
**Foreign Keys:**
{% for fk in table.foreign_keys -%}
- {{ fk.parent_column }} → {{ fk.referenced_schema }}.{{ fk.referenced_table }}.{{ fk.referenced_column }}
{% endfor %}
{% endif %}

{% if table.indexes %}
**Indexes:**
{% for idx in table.indexes -%}
- {{ idx.index_name }} ({{ idx.index_type }}): {{ idx.columns }}
{% endfor %}
{% endif %}

{% endfor %}

## Views

{% for view in doc.views %}
### {{ view.schema_name }}.{{ view.view_name }}

{% if view.description %}
**Description:** {{ view.description }}
{% endif %}

#### Columns

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
{% for column in view.columns -%}
| {{ column.name }} | {{ column.data_type }} | {{ 'Yes' if column.is_nullable else 'No' }} | {{ column.description }} |
{% endfor %}

{% endfor %}

## Stored Procedures

| Schema | Procedure Name | Created | Modified | Description |
|--------|----------------|---------|----------|-------------|
{% for proc in doc.stored_procedures -%}
| {{ proc.schema_name }} | {{ proc.procedure_name }} | {{ proc.created | format_date }} | {{ proc.modified | format_date }} | {{ proc.description }} |
{% endfor %}

## Functions

| Schema | Function Name | Type | Created | Modified | Description |
|--------|---------------|------|---------|----------|-------------|
{% for func in doc.functions -%}
| {{ func.schema_name }} | {{ func.function_name }} | {{ func.type }} | {{ func.created | format_date }} | {{ func.modified | format_date }} | {{ func.description }} |
{% endfor %}

## Relationships

**Total Foreign Key Relationships:** {{ doc.relationships.relationship_count }}

| Foreign Key | Parent Table | Parent Column | Referenced Table | Referenced Column | On Delete | On Update |
|-------------|--------------|---------------|------------------|-------------------|-----------|-----------|
{% for fk in doc.relationships.foreign_keys -%}
| {{ fk.foreign_key_name }} | {{ fk.parent_schema }}.{{ fk.parent_table }} | {{ fk.parent_column }} | {{ fk.referenced_schema }}.{{ fk.referenced_table }} | {{ fk.referenced_column }} | {{ fk.on_delete }} | {{ fk.on_update }} |
{% endfor %}

---
*Generated on {{ doc.metadata.extraction_date | format_date }} using Azure SQL Database Documentation Tool*
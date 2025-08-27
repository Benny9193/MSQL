# SampleDatabase - Database Documentation

**Server:** sample-server.database.windows.net  
**Generated:** 2024-01-01 12:00:00  
**Size:** 512 MB used of 1,024 MB allocated

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
| Schemas | 2 |
| Tables | 1 |
| Views | 0 |
| Stored Procedures | 1 |
| Functions | 1 |
| Total Rows | 1,500 |

## Schemas

| Schema Name | Principal |
|-------------|-----------|
| dbo | dbo |
| sales | dbo |


## Tables


### dbo.Users


**Description:** User account information


**Rows:** 1,500

#### Columns

| Column | Data Type | Nullable | Identity | Default | Description |
|--------|-----------|----------|----------|---------|-------------|
| UserID | int | No | Yes |  | Unique user identifier |
| Username | nvarchar(50) | No | No |  | User login name |
| Email | nvarchar(255) | No | No |  | User email address |



**Primary Key:** UserID





**Indexes:**
- PK_Users (CLUSTERED): UserID





## Views



## Stored Procedures

| Schema | Procedure Name | Created | Modified | Description |
|--------|----------------|---------|----------|-------------|
| dbo | GetUserByID | 2024-01-01 11:00:00 | 2024-01-01 11:00:00 | Retrieves user information by ID |


## Functions

| Schema | Function Name | Type | Created | Modified | Description |
|--------|---------------|------|---------|----------|-------------|
| dbo | FormatUserName | SCALAR_FUNCTION | 2024-01-01 11:30:00 | 2024-01-01 11:30:00 | Formats user display name |


## Relationships

**Total Foreign Key Relationships:** 0

| Foreign Key | Parent Table | Parent Column | Referenced Table | Referenced Column | On Delete | On Update |
|-------------|--------------|---------------|------------------|-------------------|-----------|-----------|


---
*Generated on 2024-01-01 12:00:00 using Azure SQL Database Documentation Tool*
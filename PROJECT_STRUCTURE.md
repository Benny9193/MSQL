# Azure SQL Database Documentation Generator - Project Structure

## Overview
This document provides a comprehensive overview of the project structure and organization.

## Core Application Files

### Main Application
- `modern_gui.py` - Main application with modern UI framework
- `main.py` - Alternative entry point
- `launch_gui.py` - GUI launcher script
- `launch_gui.bat` - Windows batch launcher

### Database Connection & Analysis
- `db_connection.py` - Azure SQL Database connection management
- `schema_analyzer.py` - Database schema analysis and metadata extraction
- `config_manager.py` - Configuration management system
- `connection_profiles.py` - Database connection profile management

### Documentation Generation
- `documentation_generator.py` - Main documentation generation engine
- `documentation_extractor.py` - Database metadata extraction
- `template_editor.py` - Template customization interface

### Interactive Features (Phase 1-3)
- `database_playground.py` - **Phase 1**: Interactive Database Playground
- `schema_explorer.py` - **Phase 2**: Dynamic Visual Schema Explorer  
- `performance_dashboard.py` - **Phase 3**: Real-Time Performance Dashboard

### UI Framework & Components
- `ui_framework.py` - Modern UI framework with theming
- `enhanced_controls.py` - Enhanced UI controls and widgets
- `dependency_visualizer.py` - Database dependency visualization
- `object_details.py` - Database object detail management

### Enterprise Features
- `project_manager.py` - Multi-database project management
- `api_integration.py` - API server and webhook integration
- `reporting_analytics.py` - Advanced reporting and analytics
- `migration_planner.py` - Database migration planning
- `compliance_auditor.py` - Security and compliance auditing
- `scheduler_monitor.py` - Task scheduling and monitoring
- `schema_comparison.py` - Cross-database schema comparison
- `database_health_analyzer.py` - Database health analysis

## Demo Applications
- `playground_demo.py` - Standalone Interactive Playground demo
- `schema_explorer_demo.py` - Standalone Schema Explorer demo
- `performance_dashboard_demo.py` - Standalone Performance Dashboard demo
- `demo_modern_ui.py` - Modern UI demonstration

## Test Files
- `test_playground.py` - Interactive Playground tests
- `test_schema_explorer.py` - Schema Explorer tests
- `test_performance_dashboard.py` - Performance Dashboard tests (full)
- `test_performance_core.py` - Performance Dashboard core tests
- `test_azure_schema_explorer.py` - Azure SQL integration tests
- `test_basic.py` - Basic functionality tests

## Configuration & Data
- `config.json` - Application configuration
- `config_sample.json` - Sample configuration template
- `ui_config.json` - UI preferences and settings
- `requirements.txt` - Python dependencies

### Database Files
- `compliance.db` - Compliance audit data
- `favorites.db` - User favorites and bookmarks
- `migrations.db` - Migration planning data
- `reporting.db` - Reporting and analytics data
- `webhooks.db` - Webhook configuration data

## Directory Structure

### `/logs/`
- Application log files

### `/output/`
- Generated documentation files
- Export archives

### `/profiles/`
- Connection profile storage

### `/projects/`
- Multi-database project files
- `projects.db` - Project database
- `/templates/` - Project templates

### `/scheduler/`
- Task scheduling configuration
- `jobs.db` - Scheduled jobs database
- `scheduler_config.json` - Scheduler settings

### `/templates/`
- Documentation templates (HTML, Markdown)

### `/test_output/`
- Test result files and sample outputs

## Deprecated/Legacy Files
- `gui_deprecated.py` - Legacy GUI implementation
- `launch_classic_gui.py` - Classic GUI launcher
- `launch_classic_gui.bat` - Classic GUI batch launcher
- `DEPRECATED_GUI_NOTICE.md` - Deprecation notice

## Documentation Files
- `README.md` - Main project documentation
- `UI_IMPLEMENTATION_GUIDE.md` - UI development guide
- `PROJECT_STRUCTURE.md` - This file

## Key Features by Component

### Phase 1: Interactive Database Playground
- Safe SQL experimentation environment
- Visual query builder with drag-and-drop
- Real-time results preview with performance metrics
- Interactive tutorials and learning system

### Phase 2: Dynamic Visual Schema Explorer
- Interactive schema diagrams with relationship visualization
- Multiple view modes (Overview, Table Focus, Relationship Focus)
- Advanced search and filtering capabilities
- Detailed object information panels

### Phase 3: Real-Time Performance Dashboard
- Live performance metrics monitoring
- Interactive charts with historical trending
- Intelligent alerting system with configurable thresholds
- Query analysis and optimization recommendations

### Enterprise Features
- Multi-database project management
- API server with webhook support
- Advanced reporting and analytics
- Database migration planning
- Security and compliance auditing
- Task scheduling and monitoring

## Entry Points
1. **Main Application**: `python modern_gui.py`
2. **Alternative Entry**: `python main.py`
3. **Windows Launcher**: `launch_gui.bat`
4. **Playground Demo**: `python playground_demo.py`
5. **Schema Explorer Demo**: `python schema_explorer_demo.py`
6. **Performance Dashboard Demo**: `python performance_dashboard_demo.py`

## Dependencies
See `requirements.txt` for complete list of Python dependencies.

## Default Configuration
The application includes pre-configured Azure SQL Database credentials:
- Server: `eds-sqlserver.eastus2.cloudapp.azure.com`
- Database: `master`
- Username: `EDSAdmin`
- Password: `Consultant~!`
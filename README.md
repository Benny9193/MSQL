# Azure SQL Database Documentation Generator

A comprehensive Python tool for generating complete documentation of Microsoft SQL Server databases hosted on Azure SQL Database. Features modern GUI interface, interactive database exploration, real-time performance monitoring, and professional documentation generation.

## 🌟 Key Features

### 🎮 Interactive Database Exploration (Phase 1)
- **Safe SQL Playground**: Risk-free SQL experimentation environment
- **Visual Query Builder**: Drag-and-drop query construction
- **Real-time Results**: Instant query execution with performance metrics
- **Interactive Tutorials**: Step-by-step SQL learning system

### 🗂️ Visual Schema Explorer (Phase 2) 
- **Interactive Schema Diagrams**: Visual database structure representation
- **Relationship Visualization**: Foreign keys and dependency mapping
- **Multiple View Modes**: Overview, Table Focus, and Relationship Focus
- **Advanced Navigation**: Click-to-explore object relationships
- **Scrollable Interface**: Full content accessibility on any screen size

### 📊 Real-Time Performance Dashboard (Phase 3)
- **Live Metrics Monitoring**: CPU, Memory, I/O, DTU, and Storage tracking
- **Interactive Charts**: Historical trending with real-time updates
- **Intelligent Alerting**: Configurable thresholds with severity levels
- **Query Analysis**: Resource-intensive query identification

### 📋 Professional Documentation Generation
- **HTML Documentation**: Professional, styled output with navigation
- **Markdown Documentation**: GitHub-flavored Markdown
- **JSON Export**: Structured data for programmatic access
- **Multi-format Support**: Simultaneous generation in all formats
- **Responsive Interface**: Scrollable forms and content areas

### 🔗 Advanced Connection Management
- **Username/Password Authentication**: Traditional SQL Server auth
- **Azure Active Directory**: Interactive Azure AD authentication
- **Service Principal**: Automated authentication using Azure AD
- **Connection Profiles**: Save and manage multiple database connections

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Microsoft ODBC Driver 17 for SQL Server
- Access to an Azure SQL Database

### Installation
```bash
# Clone or download the project
# Install dependencies
pip install -r requirements.txt
```

### Launch Application
```bash
# Modern GUI (Recommended)
python modern_gui.py

# Or use the launcher
python launch_gui.py

# Windows batch launcher
launch_gui.bat
```

### Default Connection
The application comes pre-configured with Azure SQL Database credentials:
- **Server**: `eds-sqlserver.eastus2.cloudapp.azure.com`
- **Database**: `master`
- **Username**: `EDSAdmin`
- **Password**: `Consultant~!`

## 📖 Usage Guide

### 1. Database Connection
1. Launch the application
2. Navigate to **"Connection"** in the sidebar
3. The default credentials are pre-filled
4. Click **"Test Connection"** to verify connectivity
5. Click **"Connect"** to establish connection

### 2. Interactive Exploration

**Database Playground:**
1. Navigate to **"Playground"** 
2. Use the visual query builder or write SQL directly
3. Execute queries safely in the sandbox environment
4. View results with performance metrics

**Schema Explorer:**
1. Navigate to **"Schema Explorer"**
2. Explore interactive schema diagrams
3. Click objects to see detailed information
4. Use search and filtering to find specific objects

**Performance Dashboard:**
1. Navigate to **"Performance Dashboard"**
2. Click **"Start Monitoring"** for real-time metrics
3. Monitor alerts in the **"Alerts"** tab
4. Analyze queries in the **"Query Analysis"** tab

### 3. Documentation Generation
1. Navigate to **"Documentation"**
2. Select output formats (HTML, Markdown, JSON)
3. Configure documentation options
4. Click **"Generate Documentation"**
5. Find generated files in the **"output"** directory

## 🎯 Demo Applications

Try the standalone demos to explore features:

```bash
# Interactive Database Playground Demo
python playground_demo.py

# Visual Schema Explorer Demo  
python schema_explorer_demo.py

# Real-Time Performance Dashboard Demo
python performance_dashboard_demo.py
```

## 🧪 Testing

Run comprehensive tests:

```bash
# Test all interactive features
python test_playground.py
python test_schema_explorer.py
python test_performance_core.py

# Test Azure SQL integration
python test_azure_schema_explorer.py

# Basic functionality tests
python test_basic.py
```

## 📁 Project Structure

```
SQL Prog/
├── Core Application/
│   ├── modern_gui.py              # Main application
│   ├── db_connection.py           # Database connectivity
│   ├── schema_analyzer.py         # Schema analysis engine
│   └── config_manager.py          # Configuration management
├── Interactive Features/
│   ├── database_playground.py     # Phase 1: SQL Playground
│   ├── schema_explorer.py         # Phase 2: Schema Explorer
│   └── performance_dashboard.py   # Phase 3: Performance Dashboard
├── Documentation/
│   ├── documentation_generator.py # Documentation engine
│   ├── documentation_extractor.py # Metadata extraction
│   └── template_editor.py         # Template customization
├── Enterprise Features/
│   ├── project_manager.py         # Multi-database projects
│   ├── api_integration.py         # API server & webhooks
│   ├── reporting_analytics.py     # Advanced reporting
│   ├── migration_planner.py       # Migration planning
│   ├── compliance_auditor.py      # Security compliance
│   └── scheduler_monitor.py       # Task scheduling
├── UI Framework/
│   ├── ui_framework.py           # Modern UI components
│   └── enhanced_controls.py      # Enhanced widgets
├── Demo Applications/
│   ├── playground_demo.py        # Playground standalone demo
│   ├── schema_explorer_demo.py   # Schema Explorer demo
│   └── performance_dashboard_demo.py # Performance demo
├── Tests/
│   ├── test_playground.py        # Playground tests
│   ├── test_schema_explorer.py   # Schema Explorer tests
│   ├── test_performance_*.py     # Performance Dashboard tests
│   └── test_basic.py             # Basic functionality
├── Configuration/
│   ├── config.json              # Main configuration
│   ├── ui_config.json           # UI preferences
│   └── requirements.txt         # Python dependencies
└── Documentation/
    ├── README.md                # This file
    ├── PROJECT_STRUCTURE.md     # Detailed project structure
    └── UI_IMPLEMENTATION_GUIDE.md # UI development guide
```

## ⚙️ Configuration

### Database Configuration
Edit `config.json` to customize database connections:

```json
{
  "database": {
    "connection_method": "credentials",
    "server": "your-server.database.windows.net",
    "database": "your-database",
    "username": "your-username",
    "password": "your-password"
  }
}
```

### Documentation Options
```json
{
  "documentation": {
    "output_directory": "output",
    "generate_html": true,
    "generate_markdown": true,
    "generate_json": true,
    "include_system_objects": false,
    "include_row_counts": true
  }
}
```

## 🔧 Advanced Features

### Multi-Database Projects
- Manage multiple database connections
- Batch operations across databases
- Project templates and configurations

### API Integration
- RESTful API server for remote access
- Webhook support for automated workflows
- Platform integrations (Slack, Teams, etc.)

### Reporting & Analytics
- Advanced database analytics dashboard
- Custom report generation
- Performance trend analysis

### Security & Compliance
- Security compliance auditing
- Permission analysis and recommendations
- Audit trail generation

## 📝 Output Examples

### HTML Documentation
- Professional styling with Bootstrap
- Interactive navigation sidebar
- Searchable content
- Responsive design for mobile/desktop

### Markdown Documentation
- GitHub-flavored Markdown
- Table of contents generation
- Code syntax highlighting
- Compatible with documentation sites

### JSON Export
- Structured schema metadata
- Programmatic access to database information
- API integration ready
- Custom processing support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions, issues, or feature requests:
1. Check the documentation files in the project
2. Review the test files for usage examples
3. Run the demo applications to understand features
4. Create an issue for bugs or feature requests

## 🏆 Acknowledgments

- Built with Python and tkinter
- Uses Microsoft ODBC Driver for SQL Server
- Inspired by modern database management tools
- Designed for Azure SQL Database environments
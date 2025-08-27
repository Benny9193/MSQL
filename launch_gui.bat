@echo off
cd /d "%~dp0"
echo Starting Azure SQL Database Documentation Generator (Modern Interface)...
echo.
python launch_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start the application.
    echo Make sure Python is installed and dependencies are available.
    echo Run: pip install -r requirements.txt
    echo.
    pause
)
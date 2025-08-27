@echo off
cd /d "%~dp0"
echo Starting Azure SQL Database Documentation Generator (Classic Interface)...
echo.
python launch_classic_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start the classic application.
    echo Make sure Python is installed and dependencies are available.
    echo Run: pip install -r requirements.txt
    echo.
    pause
)
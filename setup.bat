@echo off
REM Campus Care Portal - Setup Script for Windows
REM This script sets up the entire project

echo ╔════════════════════════════════════════════════════════════╗
echo ║        Campus Care Portal - Installation Script            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found: 
python --version
echo.

REM Install dependencies
echo [*] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [✓] Dependencies installed successfully
echo.

REM Test MySQL connection
echo [*] Checking MySQL connection...
python -c "import pymysql; pymysql.connect(host='localhost', user='root', password='Kuntal@2006')" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Could not connect to MySQL
    echo Please ensure:
    echo   1. MySQL Server is running
    echo   2. Default credentials are: user=root, password=Kuntal@2006
    echo   3. Update credentials in app.py if different
    echo.
    echo [*] You will need to manually run: mysql -u root -p ^< database.sql
) else (
    echo [✓] MySQL connection successful
    echo.
    echo [*] Setting up database...
    REM Run database.sql
    mysql -u root -p < database.sql >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Could not auto-run database.sql
        echo Please run manually: mysql -u root -p ^< database.sql
    ) else (
        echo [✓] Database setup completed
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║              Setup Complete!                               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo   1. Start MySQL Server if not running
echo   2. Run: python app.py
echo   3. Open http://localhost:5000 in your browser
echo.
echo Default Credentials:
echo   Admin: admin / admin123
echo   Doctor: dr_sharma / doctor123
echo   Patient: (any roll number) / (no password)
echo.
pause

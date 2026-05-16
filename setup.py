#!/usr/bin/env python3
"""
Campus Care Portal - Setup and Verification Script
Installs dependencies, checks MySQL connection, and sets up database
"""

import subprocess
import sys
import os

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully\n")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies\n")
        return False

def test_mysql_connection():
    """Test MySQL connection"""
    print("Testing MySQL connection...")
    try:
        import pymysql
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Kuntal@2006"
        )
        conn.close()
        print("✓ MySQL connection successful\n")
        return True
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}\n")
        return False

def setup_database():
    """Setup database by running database.sql"""
    print("Setting up database...")
    try:
        import pymysql
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Kuntal@2006"
        )
        cursor = conn.cursor()
        
        with open("database.sql", "r") as f:
            sql_content = f.read()
        
        # Split by GO or ; and execute each statement
        statements = sql_content.split(";")
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"Warning: {e}")
        
        conn.commit()
        conn.close()
        print("✓ Database setup completed\n")
        return True
    except Exception as e:
        print(f"✗ Database setup failed: {e}\n")
        print("  Please run manually: mysql -u root -p < database.sql\n")
        return False

def verify_installation():
    """Verify all components"""
    print_header("VERIFICATION")
    
    checks = {
        "Flask": False,
        "PyMySQL": False,
        "Werkzeug": False,
    }
    
    try:
        import flask
        checks["Flask"] = True
        print(f"✓ Flask {flask.__version__}")
    except ImportError:
        print("✗ Flask not found")
    
    try:
        import pymysql
        checks["PyMySQL"] = True
        print(f"✓ PyMySQL installed")
    except ImportError:
        print("✗ PyMySQL not found")
    
    try:
        import werkzeug
        checks["Werkzeug"] = True
        print(f"✓ Werkzeug {werkzeug.__version__}")
    except ImportError:
        print("✗ Werkzeug not found")
    
    return all(checks.values())

def main():
    """Main setup flow"""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*15 + "Campus Care Portal - Setup" + " "*17 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Step 1: Check Python
    print_header("CHECKING PYTHON")
    check_python()
    
    # Step 2: Install Dependencies
    print_header("INSTALLING DEPENDENCIES")
    if not install_dependencies():
        print("Please install dependencies manually:")
        print("  pip install -r requirements.txt\n")
        return False
    
    # Step 3: Test MySQL
    print_header("TESTING MYSQL CONNECTION")
    mysql_ok = test_mysql_connection()
    
    # Step 4: Setup Database
    print_header("SETTING UP DATABASE")
    if mysql_ok:
        if not setup_database():
            print("⚠ Database setup incomplete. Please run manually:")
            print("  mysql -u root -p < database.sql\n")
    else:
        print("⚠ Skipping database setup (MySQL not connected)")
        print("  Please ensure MySQL is running and run:")
        print("  mysql -u root -p < database.sql\n")
    
    # Step 5: Verify
    print_header("VERIFYING INSTALLATION")
    if verify_installation():
        print("\n✓ All components verified!\n")
    else:
        print("\n⚠ Some components are missing.\n")
    
    # Final instructions
    print_header("NEXT STEPS")
    print("1. Ensure MySQL Server is running")
    print("2. Run the application: python app.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\n" + "="*60)
    print("DEFAULT CREDENTIALS:")
    print("="*60)
    print("Admin:    username=admin, password=admin123")
    print("Doctor:   username=dr_sharma, password=doctor123")
    print("Patient:  (any roll number), (no password required)")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

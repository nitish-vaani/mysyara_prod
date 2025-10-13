#!/usr/bin/env python3
"""
Migration helper script for easy database operations
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/app/backend/db_test/.env.local")

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = ["POSTGRES_URL", "SQLITE_DB_PATH", "DB_TYPE"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Don't print sensitive URLs completely
            if "URL" in var:
                masked_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
    
    if missing_vars:
        print(f"  ❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ All environment variables are set!")
    return True

def test_connections():
    """Test both SQLite and PostgreSQL connections"""
    print("\n🔗 Testing database connections...")
    
    # Test SQLite
    try:
        sqlite_path = os.getenv("SQLITE_DB_PATH", "/app/backend/db_test/test.db")
        sqlite_url = f"sqlite:///{sqlite_path}"
        sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        
        with sqlite_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  ✅ SQLite connection successful")
        
        # Check if SQLite has data
        with sqlite_engine.connect() as conn:
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
            if tables:
                print(f"  📊 SQLite tables found: {[table[0] for table in tables]}")
                for table in tables:
                    table_name = table[0]
                    try:
                        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()[0]
                        print(f"    - {table_name}: {count} rows")
                    except:
                        print(f"    - {table_name}: Error reading count")
            else:
                print("  ⚠️  No tables found in SQLite")
                
    except Exception as e:
        print(f"  ❌ SQLite connection failed: {e}")
        return False
    
    # Test PostgreSQL
    try:
        postgres_url = os.getenv("POSTGRES_URL")
        postgres_engine = create_engine(postgres_url, pool_size=5, max_overflow=10)
        
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  ✅ PostgreSQL connection successful")
        
        # Check if PostgreSQL has tables
        with postgres_engine.connect() as conn:
            tables = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )).fetchall()
            if tables:
                print(f"  📊 PostgreSQL tables found: {[table[0] for table in tables]}")
                for table in tables:
                    table_name = table[0]
                    try:
                        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()[0]
                        print(f"    - {table_name}: {count} rows")
                    except:
                        print(f"    - {table_name}: Error reading count")
            else:
                print("  ⚠️  No tables found in PostgreSQL")
                
    except Exception as e:
        print(f"  ❌ PostgreSQL connection failed: {e}")
        return False
    
    return True

def run_migration_step(step):
    """Run a specific migration step"""
    script_path = "/app/backend/db_test/migrate.py"  # Update this path as needed
    
    if not os.path.exists(script_path):
        print(f"❌ Migration script not found at: {script_path}")
        print("Please ensure the migrate.py script is in the correct location.")
        return False
    
    try:
        print(f"\n🚀 Running migration step: {step}")
        result = subprocess.run([
            sys.executable, script_path, step
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("✅ Migration step completed successfully!")
            print("Output:")
            print(result.stdout)
            return True
        else:
            print("❌ Migration step failed!")
            print("Error output:")
            print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Migration step timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running migration step: {e}")
        return False

def full_migration():
    """Run the complete migration process"""
    print("🎯 Starting full migration process...\n")
    
    steps = [
        ("Environment Check", check_environment),
        ("Connection Test", test_connections),
        ("Create Tables", lambda: run_migration_step("create_tables")),
        ("Migrate Data", lambda: run_migration_step("migrate_data")),
        ("Final Verification", test_connections)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*50}")
        print(f"Step: {step_name}")
        print('='*50)
        
        if not step_func():
            print(f"\n❌ Migration failed at step: {step_name}")
            return False
    
    print(f"\n{'='*50}")
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print('='*50)
    print("\nYour data has been migrated from SQLite to PostgreSQL.")
    print("You can now use your application with the PostgreSQL database.")
    return True

def show_help():
    """Show help information"""
    print("""
🛠️  Database Migration Helper

Available commands:
  check       - Check environment variables and connections
  create      - Create tables in PostgreSQL
  migrate     - Migrate data from SQLite to PostgreSQL  
  full        - Run complete migration process (recommended)
  help        - Show this help message

Examples:
  python migration_helper.py check
  python migration_helper.py full
  python migration_helper.py migrate

Environment variables required:
  - POSTGRES_URL: PostgreSQL connection string
  - SQLITE_DB_PATH: Path to SQLite database file
  - DB_TYPE: Database type (postgresql/sqlite)
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migration_helper.py [command]")
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    elif command == "check":
        if check_environment():
            test_connections()
    elif command == "create":
        if check_environment() and test_connections():
            run_migration_step("create_tables")
    elif command == "migrate":
        if check_environment() and test_connections():
            run_migration_step("migrate_data")
    elif command == "full":
        full_migration()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)
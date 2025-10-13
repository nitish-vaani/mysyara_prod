#verify_migration.py

#!/usr/bin/env python3
"""
Compare SQLite and PostgreSQL databases with identical queries
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(dotenv_path="/app/backend/db_test/.env.local")

def run_query_on_both_dbs(query, description):
    """Run the same query on both databases and compare results"""
    
    # Database connections
    sqlite_path = os.getenv("SQLITE_DB_PATH", "/app/backend/db_test/test.db")
    sqlite_url = f"sqlite:///{sqlite_path}"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        print("❌ POSTGRES_URL not found in environment")
        return
    
    postgres_engine = create_engine(postgres_url)
    
    print(f"\n🔍 {description}")
    print("=" * 80)
    print(f"Query: {query}")
    print("-" * 80)
    
    # Run query on SQLite
    sqlite_result = None
    sqlite_error = None
    try:
        with sqlite_engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            sqlite_result = [list(row) for row in result] if result else []
    except Exception as e:
        sqlite_error = str(e)
    
    # Run query on PostgreSQL
    postgres_result = None
    postgres_error = None
    try:
        with postgres_engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
            postgres_result = [list(row) for row in result] if result else []
    except Exception as e:
        postgres_error = str(e)
    
    # Display results side by side
    print("SQLite Result:")
    if sqlite_error:
        print(f"  ❌ Error: {sqlite_error}")
    elif not sqlite_result:
        print("  📭 No data returned")
    else:
        for i, row in enumerate(sqlite_result):
            print(f"  Row {i+1}: {row}")
    
    print("\nPostgreSQL Result:")
    if postgres_error:
        print(f"  ❌ Error: {postgres_error}")
    elif not postgres_result:
        print("  📭 No data returned")
    else:
        for i, row in enumerate(postgres_result):
            print(f"  Row {i+1}: {row}")
    
    # Compare results
    print("\nComparison:")
    if sqlite_error and postgres_error:
        print("  ⚠️  Both databases had errors")
    elif sqlite_error:
        print("  ⚠️  SQLite had an error, PostgreSQL worked")
    elif postgres_error:
        print("  ⚠️  PostgreSQL had an error, SQLite worked")
    elif sqlite_result == postgres_result:
        print("  ✅ RESULTS MATCH - Migration successful for this query!")
    else:
        print("  ❌ RESULTS DIFFER - Migration may have issues")
        print(f"     SQLite returned {len(sqlite_result) if sqlite_result else 0} rows")
        print(f"     PostgreSQL returned {len(postgres_result) if postgres_result else 0} rows")

def main():
    print("🔄 DATABASE COMPARISON VERIFICATION")
    print("Running identical queries on both SQLite and PostgreSQL")
    print("=" * 80)
    
    # Test database connections first
    print("Testing database connections...")
    
    sqlite_path = os.getenv("SQLITE_DB_PATH", "/app/backend/db_test/test.db")
    sqlite_url = f"sqlite:///{sqlite_path}"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        print("❌ POSTGRES_URL not found")
        return
    
    postgres_engine = create_engine(postgres_url)
    
    try:
        with sqlite_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ SQLite connection successful")
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return
    
    try:
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return
    
    # Test queries
    test_queries = [
        # Row counts for each table
        ("SELECT COUNT(*) FROM users", "Count of users table"),
        ("SELECT COUNT(*) FROM models", "Count of models table"),
        ("SELECT COUNT(*) FROM calls", "Count of calls table"),
        ("SELECT COUNT(*) FROM feedback", "Count of feedback table"),
        
        # Top 5 records from each table
        ("SELECT * FROM users LIMIT 5", "Top 5 users"),
        ("SELECT * FROM models LIMIT 5", "Top 5 models"),
        ("SELECT * FROM calls LIMIT 5", "Top 5 calls"),
        ("SELECT * FROM feedback LIMIT 5", "Top 5 feedback"),
        
        # Specific data checks
        ("SELECT call_id, name, call_status FROM calls WHERE call_id IS NOT NULL LIMIT 3", "Sample call data"),
        ("SELECT model_id, model_name, client_name FROM models LIMIT 3", "Sample model data"),
        ("SELECT username FROM users WHERE username IS NOT NULL LIMIT 3", "Sample user data"),
        
        # Check for non-null important fields
        ("SELECT COUNT(*) FROM calls WHERE call_id IS NOT NULL", "Calls with call_id"),
        ("SELECT COUNT(*) FROM calls WHERE call_transcription IS NOT NULL", "Calls with transcription"),
        ("SELECT COUNT(*) FROM calls WHERE call_metadata IS NOT NULL", "Calls with metadata"),
        
        # Date-based queries (if you have recent data)
        ("SELECT COUNT(*) FROM calls WHERE call_started_at > datetime('now', '-30 days')", "Recent calls (SQLite format)"),
    ]
    
    # Run PostgreSQL-specific queries (for PostgreSQL datetime format)
    postgres_specific_queries = [
        ("SELECT COUNT(*) FROM calls WHERE call_started_at > NOW() - INTERVAL '30 days'", "Recent calls (PostgreSQL format)"),
        ("SELECT call_id, call_metadata::text FROM calls WHERE call_metadata IS NOT NULL LIMIT 2", "Calls with JSON metadata"),
    ]
    
    # Run standard comparison queries
    for query, description in test_queries:
        try:
            run_query_on_both_dbs(query, description)
        except Exception as e:
            print(f"❌ Error running query '{description}': {e}")
    
    # Run PostgreSQL-specific queries separately
    print(f"\n🔍 PostgreSQL-Specific Queries")
    print("=" * 80)
    
    postgres_engine = create_engine(postgres_url)
    for query, description in postgres_specific_queries:
        print(f"\n{description}:")
        try:
            with postgres_engine.connect() as conn:
                result = conn.execute(text(query)).fetchall()
                if result:
                    for i, row in enumerate(result):
                        print(f"  Row {i+1}: {list(row)}")
                else:
                    print("  📭 No data returned")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Summary
    print(f"\n📋 MIGRATION VERIFICATION SUMMARY")
    print("=" * 80)
    print("If the row counts match and sample data looks similar,")
    print("your migration was successful!")
    print("\nNext steps:")
    print("1. Update your .env.local file: DB_TYPE=postgresql")
    print("2. Restart your application")
    print("3. Test your API endpoints")

if __name__ == "__main__":
    main()
# #migration.py

#!/usr/bin/env python3
"""
Robust migration script with foreign key handling
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path="/app/backend/db_test/.env.local")

def create_tables_direct():
    """
    Create tables using direct SQL commands with proper constraints
    """
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise ValueError("POSTGRES_URL environment variable is required")
    
    engine = create_engine(postgres_url, pool_size=10, max_overflow=20, pool_recycle=3600)
    
    print("Creating tables in PostgreSQL using direct SQL...")
    print(f"Using database: {postgres_url.split('@')[1] if '@' in postgres_url else 'hidden'}")
    
    # SQL commands to create tables - ORDER MATTERS for foreign keys
    create_tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS models (
            model_id VARCHAR(255) PRIMARY KEY,
            model_name VARCHAR(255) NOT NULL,
            client_name VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS calls (
            id SERIAL PRIMARY KEY,
            call_id VARCHAR(255),
            model_id VARCHAR(255) REFERENCES models(model_id) ON DELETE SET NULL,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            name VARCHAR(255),
            call_from VARCHAR(50),
            call_to VARCHAR(50),
            call_type VARCHAR(50),
            call_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            call_duration FLOAT,
            call_ended_at TIMESTAMP,
            call_status VARCHAR(50) DEFAULT 'NA',
            call_metadata JSONB,
            transfer_agent_name VARCHAR(255),
            transfer_reason VARCHAR(500),
            transfer_time TIMESTAMP,
            call_summary TEXT,
            call_transcription TEXT,
            call_recording_url VARCHAR(500),
            call_conversation_quality JSONB,
            call_entity JSONB
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            feedback_text TEXT,
            felt_neutral INTEGER,
            response_speed INTEGER,
            interruptions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        try:
            for sql in create_tables_sql:
                print(f"Executing: {sql.strip()[:50]}...")
                conn.execute(text(sql))
            
            trans.commit()
            print("✅ All tables created successfully!")
            
            # Verify tables were created
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
            tables = [row[0] for row in result.fetchall()]
            print(f"Created tables: {tables}")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error creating tables: {e}")
            raise

def create_default_records(postgres_session):
    """
    Create default records for users and models to handle foreign key references
    """
    print("Creating default records for foreign key references...")
    
    try:
        # Create default user (id=0) if it doesn't exist
        result = postgres_session.execute(text("SELECT id FROM users WHERE id = 0")).fetchone()
        if not result:
            postgres_session.execute(text("""
                INSERT INTO users (id, username, password) 
                VALUES (0, 'default_user', 'default_password')
                ON CONFLICT (id) DO NOTHING
            """))
            print("✅ Created default user (id=0)")
        
        # Reset sequence to ensure future users start from id=1
        postgres_session.execute(text("SELECT setval('users_id_seq', GREATEST(1, (SELECT MAX(id) FROM users)), false)"))
        
        # Create default models for common model_ids found in calls
        # First, get all unique model_ids from SQLite
        sqlite_path = os.getenv("SQLITE_DB_PATH", "/app/backend/db_test/test.db")
        sqlite_url = f"sqlite:///{sqlite_path}"
        sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        
        with sqlite_engine.connect() as sqlite_conn:
            try:
                result = sqlite_conn.execute(text("SELECT DISTINCT model_id FROM calls WHERE model_id IS NOT NULL")).fetchall()
                model_ids = [row[0] for row in result]
                print(f"Found model_ids in SQLite: {model_ids}")
                
                for model_id in model_ids:
                    # Check if model already exists
                    existing = postgres_session.execute(text("SELECT model_id FROM models WHERE model_id = :model_id"), 
                                                      {"model_id": str(model_id)}).fetchone()
                    if not existing:
                        postgres_session.execute(text("""
                            INSERT INTO models (model_id, model_name, client_name) 
                            VALUES (:model_id, :model_name, :client_name)
                            ON CONFLICT (model_id) DO NOTHING
                        """), {
                            "model_id": str(model_id), 
                            "model_name": f"Default Model {model_id}", 
                            "client_name": "Default Client"
                        })
                        print(f"✅ Created default model (id={model_id})")
                        
            except Exception as e:
                print(f"Note: Could not read model_ids from SQLite calls table: {e}")
                # Create some common default models
                default_models = [
                    ("1", "Default Model 1", "Default Client"),
                    ("2", "Default Model 2", "Default Client"),
                    ("default", "Default Model", "Default Client")
                ]
                
                for model_id, model_name, client_name in default_models:
                    existing = postgres_session.execute(text("SELECT model_id FROM models WHERE model_id = :model_id"), 
                                                      {"model_id": model_id}).fetchone()
                    if not existing:
                        postgres_session.execute(text("""
                            INSERT INTO models (model_id, model_name, client_name) 
                            VALUES (:model_id, :model_name, :client_name)
                            ON CONFLICT (model_id) DO NOTHING
                        """), {"model_id": model_id, "model_name": model_name, "client_name": client_name})
                        print(f"✅ Created default model (id={model_id})")
        
        postgres_session.commit()
        print("✅ Default records created successfully!")
        
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Error creating default records: {e}")
        raise

def migrate_data():
    """
    Robust migration that handles foreign key constraints properly
    """
    # Database connections
    sqlite_path = os.getenv("SQLITE_DB_PATH", "/app/backend/db_test/test.db")
    sqlite_url = f"sqlite:///{sqlite_path}"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise ValueError("POSTGRES_URL environment variable is required")
    
    postgres_engine = create_engine(postgres_url, pool_size=10, max_overflow=20, pool_recycle=3600)
    
    # Test connections
    print("Testing connections...")
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
    
    # Create sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()
    
    try:
        print("Starting ROBUST migration from SQLite to PostgreSQL...")
        
        # Step 1: Create default records for foreign key references
        create_default_records(postgres_session)
        
        # Step 2: Define migration order (parents before children)
        migration_order = [
            ('users', ['id', 'username', 'password']),
            ('models', ['model_id', 'model_name', 'client_name']),
            ('calls', [
                'id', 'call_id', 'model_id', 'user_id', 'name', 'call_from', 'call_to', 
                'call_type', 'call_started_at', 'call_duration', 'call_ended_at', 
                'call_status', 'call_metadata', 'transfer_agent_name', 'transfer_reason', 
                'transfer_time', 'call_summary', 'call_transcription', 'call_recording_url', 
                'call_conversation_quality', 'call_entity'
            ]),
            ('feedback', ['id', 'user_id', 'feedback_text', 'felt_neutral', 'response_speed', 'interruptions'])
        ]
        
        for table_name, expected_columns in migration_order:
            print(f"\n--- Migrating table: {table_name} ---")
            
            # Check if table exists in SQLite
            result = sqlite_session.execute(
                text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            ).fetchone()
            
            if not result:
                print(f"❌ Table {table_name} not found in SQLite, skipping...")
                continue
            
            # Get actual columns from SQLite
            columns_result = sqlite_session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            actual_columns = [col[1] for col in columns_result]
            print(f"SQLite columns: {actual_columns}")
            
            # Check if table exists in PostgreSQL
            pg_table_check = postgres_session.execute(
                text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}'")
            ).fetchone()
            
            if not pg_table_check:
                print(f"❌ Table {table_name} does not exist in PostgreSQL.")
                continue
            
            # Get all data from SQLite table
            sqlite_data = sqlite_session.execute(text(f"SELECT * FROM {table_name}")).fetchall()
            
            if not sqlite_data:
                print(f"No data found in table {table_name}")
                continue
            
            print(f"Found {len(sqlite_data)} rows in {table_name}")
            
            # Clear existing data in PostgreSQL table (except default records for users/models)
            try:
                if table_name in ['calls', 'feedback']:
                    postgres_session.execute(text(f"DELETE FROM {table_name}"))
                elif table_name == 'users':
                    postgres_session.execute(text(f"DELETE FROM {table_name} WHERE id > 0"))
                elif table_name == 'models':
                    # Don't delete default models, but delete any existing non-default ones from previous migrations
                    postgres_session.execute(text(f"DELETE FROM {table_name} WHERE model_name NOT LIKE 'Default Model%'"))
                    
                postgres_session.commit()
                print(f"Cleared existing data from {table_name}")
            except Exception as truncate_error:
                print(f"Warning: Could not clear {table_name}: {truncate_error}")
                postgres_session.rollback()
            
            # Insert data into PostgreSQL with error handling
            success_count = 0
            error_count = 0
            
            for row_num, row in enumerate(sqlite_data, 1):
                # Convert row to dict using actual columns
                row_dict = dict(zip(actual_columns, row))
                
                # Handle special cases for each table
                if table_name == 'calls':
                    # Handle JSON columns
                    for json_col in ['call_metadata', 'call_conversation_quality', 'call_entity']:
                        if json_col in row_dict and row_dict[json_col]:
                            if isinstance(row_dict[json_col], str):
                                try:
                                    parsed = json.loads(row_dict[json_col])
                                    row_dict[json_col] = json.dumps(parsed)
                                except json.JSONDecodeError:
                                    row_dict[json_col] = '{}'
                            elif isinstance(row_dict[json_col], dict):
                                row_dict[json_col] = json.dumps(row_dict[json_col])
                            else:
                                row_dict[json_col] = '{}'
                        elif json_col in row_dict:
                            row_dict[json_col] = None
                    
                    # Handle foreign key references
                    if 'model_id' in row_dict and row_dict['model_id']:
                        # Check if model exists, if not create it
                        model_exists = postgres_session.execute(
                            text("SELECT model_id FROM models WHERE model_id = :model_id"), 
                            {"model_id": str(row_dict['model_id'])}
                        ).fetchone()
                        
                        if not model_exists:
                            try:
                                postgres_session.execute(text("""
                                    INSERT INTO models (model_id, model_name, client_name) 
                                    VALUES (:model_id, :model_name, :client_name)
                                    ON CONFLICT (model_id) DO NOTHING
                                """), {
                                    "model_id": str(row_dict['model_id']), 
                                    "model_name": f"Auto-created Model {row_dict['model_id']}", 
                                    "client_name": "Auto-created Client"
                                })
                                postgres_session.commit()
                                print(f"  ℹ️  Auto-created model {row_dict['model_id']}")
                            except Exception as model_create_error:
                                print(f"  ⚠️  Could not create model {row_dict['model_id']}: {model_create_error}")
                                row_dict['model_id'] = None
                    
                    # Ensure user_id exists or set to 0 (default user)
                    if 'user_id' in row_dict and row_dict['user_id'] is not None:
                        if row_dict['user_id'] != 0:
                            user_exists = postgres_session.execute(
                                text("SELECT id FROM users WHERE id = :user_id"), 
                                {"user_id": row_dict['user_id']}
                            ).fetchone()
                            if not user_exists:
                                print(f"  ⚠️  User {row_dict['user_id']} doesn't exist, setting to default user (0)")
                                row_dict['user_id'] = 0
                
                elif table_name == 'feedback':
                    # Handle feedback user_id
                    if 'user_id' in row_dict and row_dict['user_id'] is not None:
                        user_exists = postgres_session.execute(
                            text("SELECT id FROM users WHERE id = :user_id"), 
                            {"user_id": row_dict['user_id']}
                        ).fetchone()
                        if not user_exists:
                            print(f"  ⚠️  User {row_dict['user_id']} doesn't exist, setting to default user (0)")
                            row_dict['user_id'] = 0
                
                # Handle datetime fields
                datetime_fields = ['call_started_at', 'call_ended_at', 'transfer_time', 'created_at']
                for dt_field in datetime_fields:
                    if dt_field in row_dict and row_dict[dt_field]:
                        if isinstance(row_dict[dt_field], str):
                            try:
                                dt = datetime.fromisoformat(row_dict[dt_field].replace('Z', '+00:00'))
                                row_dict[dt_field] = dt.isoformat()
                            except:
                                pass
                
                # Remove None values for optional fields
                filtered_dict = {k: v for k, v in row_dict.items() if v is not None}
                
                # Build INSERT query with conflict handling
                if filtered_dict:
                    columns = ', '.join(filtered_dict.keys())
                    placeholders = ', '.join([f":{key}" for key in filtered_dict.keys()])
                    
                    # Handle ID conflicts for tables with auto-incrementing IDs
                    if table_name in ['users', 'calls', 'feedback'] and 'id' in filtered_dict:
                        # Use ON CONFLICT for tables with potential ID conflicts
                        query = f"""
                            INSERT INTO {table_name} ({columns}) 
                            VALUES ({placeholders})
                            ON CONFLICT (id) DO UPDATE SET
                            {', '.join([f"{col} = EXCLUDED.{col}" for col in filtered_dict.keys() if col != 'id'])}
                        """
                    else:
                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    
                    try:
                        postgres_session.execute(text(query), filtered_dict)
                        success_count += 1
                        if success_count % 10 == 0 or success_count == len(sqlite_data):
                            print(f"  ✅ Processed {success_count}/{len(sqlite_data)} rows")
                    except Exception as e:
                        error_count += 1
                        print(f"  ❌ Error inserting row {row_num}: {str(e)[:100]}...")
                        postgres_session.rollback()
                        # Start new transaction
                        postgres_session.begin()
                        continue
            
            postgres_session.commit()
            print(f"✅ Successfully migrated {success_count}/{len(sqlite_data)} rows to {table_name}")
            if error_count > 0:
                print(f"⚠️  {error_count} rows had errors and were skipped")
        
        print("\n🎉 ROBUST Migration completed successfully!")
        
        # Verify the migration worked
        print("\n📊 Final Verification:")
        with postgres_engine.connect() as conn:
            for table in ['users', 'models', 'calls', 'feedback']:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    print(f"  {table}: {result[0]} rows")
                except Exception as e:
                    print(f"  {table}: Error - {e}")
        
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python robust_migrate.py [create_tables|migrate_data]")
        print("Commands:")
        print("  create_tables - Create tables in PostgreSQL")
        print("  migrate_data  - Migrate data from SQLite to PostgreSQL")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create_tables":
        create_tables_direct()
    elif command == "migrate_data":
        migrate_data()
    else:
        print("Invalid command. Use 'create_tables' or 'migrate_data'")
        sys.exit(1)
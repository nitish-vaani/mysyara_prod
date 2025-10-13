#!/usr/bin/env python3
"""
Fix PostgreSQL sequences after migration
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/app/backend/db_test/.env.local")

def fix_postgres_sequences():
    """
    Fix PostgreSQL sequences to start from the correct values after migration
    """
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise ValueError("POSTGRES_URL environment variable is required")
    
    engine = create_engine(postgres_url, pool_size=5, max_overflow=10)
    
    print("🔧 Fixing PostgreSQL sequences after migration...")
    
    # List of tables with auto-incrementing primary keys
    tables_with_sequences = [
        ('users', 'users_id_seq'),
        ('calls', 'calls_id_seq'), 
        ('feedback', 'feedback_id_seq')
    ]
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for table_name, sequence_name in tables_with_sequences:
                print(f"\n📊 Fixing sequence for table: {table_name}")
                
                # Get the current maximum ID from the table
                max_id_result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")).fetchone()
                max_id = max_id_result[0] if max_id_result else 0
                
                # Get current sequence value
                current_seq_result = conn.execute(text(f"SELECT last_value FROM {sequence_name}")).fetchone()
                current_seq = current_seq_result[0] if current_seq_result else 0
                
                print(f"  Current max ID in {table_name}: {max_id}")
                print(f"  Current sequence value: {current_seq}")
                
                # Set sequence to max_id + 1
                new_seq_value = max_id + 1
                conn.execute(text(f"SELECT setval('{sequence_name}', {new_seq_value}, false)"))
                
                # Verify the fix
                verify_result = conn.execute(text(f"SELECT last_value FROM {sequence_name}")).fetchone()
                verify_seq = verify_result[0] if verify_result else 0
                
                print(f"  ✅ Updated sequence to: {verify_seq}")
                print(f"  Next ID will be: {new_seq_value}")
            
            trans.commit()
            print(f"\n🎉 All sequences fixed successfully!")
            
            # Test that new inserts will work
            print(f"\n🧪 Testing sequence functionality...")
            for table_name, sequence_name in tables_with_sequences:
                next_val_result = conn.execute(text(f"SELECT nextval('{sequence_name}')")).fetchone()
                next_val = next_val_result[0] if next_val_result else 0
                print(f"  {table_name}: Next available ID = {next_val}")
                
                # Reset the sequence back (we just tested it)
                conn.execute(text(f"SELECT setval('{sequence_name}', {next_val - 1}, true)"))
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error fixing sequences: {e}")
            raise

def main():
    print("🔧 PostgreSQL Sequence Fixer")
    print("=" * 50)
    print("This script fixes auto-increment sequences after data migration")
    print("=" * 50)
    
    try:
        fix_postgres_sequences()
        print(f"\n✅ SUCCESS: Your database is now ready for new records!")
        print(f"You can now run your APIs and insert new data without ID conflicts.")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    main()
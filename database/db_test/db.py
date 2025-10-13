#db.py

from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, DisconnectionError
import sqlite3
from datetime import datetime
import logging
import json
import os
from .database_config import get_database_url, get_engine_args, get_db_type

# Database configuration
DATABASE_URL = get_database_url()
ENGINE_ARGS = get_engine_args()
DB_TYPE = get_db_type()

logger = logging.getLogger("call-logger")
logging.basicConfig(level=logging.INFO)

# Create engine with appropriate arguments
engine = create_engine(DATABASE_URL, **ENGINE_ARGS)

# Add connection event handlers for PostgreSQL resilience
if DB_TYPE == "postgresql":
    @event.listens_for(engine, "connect")
    def set_postgresql_settings(dbapi_connection, connection_record):
        """Set PostgreSQL-specific connection settings"""
        try:
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SET statement_timeout = '60s'")
                cursor.execute("SET lock_timeout = '30s'")
                cursor.execute("SET idle_in_transaction_session_timeout = '60s'")
            logger.debug("PostgreSQL connection settings applied")
        except Exception as e:
            logger.warning(f"Could not set PostgreSQL settings: {e}")

    @event.listens_for(engine, "checkout")
    def test_connection_on_checkout(dbapi_connection, connection_record, connection_proxy):
        """Test connection health before use"""
        try:
            with dbapi_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            logger.debug("Connection health check passed")
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            # Invalidate the connection so a new one will be created
            connection_proxy._invalidate_on_error = True
            raise

    @event.listens_for(engine, "invalidate")
    def on_connection_invalidate(dbapi_connection, connection_record, exception):
        """Log when connections are invalidated"""
        logger.info(f"Connection invalidated due to: {exception}")

# Session configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def execute_with_retry(func, max_retries=3, *args, **kwargs):
    """
    Execute database function with retry logic for connection issues
    """
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (OperationalError, DisconnectionError) as e:
            if attempt == max_retries - 1:  # Last attempt
                logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                raise
            
            # Check if it's a connection issue
            if any(phrase in str(e).lower() for phrase in [
                'ssl connection has been closed',
                'connection closed',
                'server closed the connection',
                'connection was forcibly closed',
                'connection reset'
            ]):
                logger.warning(f"Connection issue detected (attempt {attempt + 1}/{max_retries}): {e}")
                continue
            else:
                # Not a connection issue, don't retry
                raise
        except Exception as e:
            # Non-connection errors, don't retry
            logger.error(f"Non-connection error: {e}")
            raise

# Dependency to get DB session with retry logic
def get_db():
    """
    Dependency function to get database session with connection resilience
    """
    db = SessionLocal()
    try:
        # Test the connection
        db.execute(text("SELECT 1"))
        yield db
    except (OperationalError, DisconnectionError) as e:
        logger.warning(f"Database connection issue in get_db: {e}")
        db.rollback()
        db.close()
        # Create a new session and try again
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            yield db
        except Exception as retry_error:
            logger.error(f"Failed to establish database connection: {retry_error}")
            db.rollback()
            raise
    except Exception as e:
        logger.error(f"Database error in get_db: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session():
    """
    Direct function to get a database session with connection testing
    Remember to close it when done!
    """
    db = SessionLocal()
    try:
        # Test the connection
        db.execute(text("SELECT 1"))
        return db
    except (OperationalError, DisconnectionError):
        # Connection issue, try with a new session
        db.close()
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # This will raise if still failing
        return db

def fix_postgres_sequences():
    """
    Fix PostgreSQL sequences to prevent ID conflicts
    """
    if DB_TYPE != "postgresql":
        return  # Only needed for PostgreSQL
    
    def _fix_sequences():
        with engine.connect() as conn:
            # Fix sequences for tables with auto-incrementing IDs
            tables_with_sequences = [
                ('users', 'users_id_seq'),
                ('calls', 'calls_id_seq'), 
                ('feedback', 'feedback_id_seq')
            ]
            
            for table_name, sequence_name in tables_with_sequences:
                try:
                    # Get max ID and set sequence accordingly
                    max_id_result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")).fetchone()
                    max_id = max_id_result[0] if max_id_result else 0
                    
                    # Set sequence to max_id + 1
                    conn.execute(text(f"SELECT setval('{sequence_name}', {max_id + 1}, false)"))
                    
                except Exception as seq_error:
                    logger.warning(f"Could not fix sequence for {table_name}: {seq_error}")
            
            conn.commit()
            logger.info("PostgreSQL sequences synchronized")
    
    try:
        execute_with_retry(_fix_sequences)
    except Exception as e:
        logger.warning(f"Could not fix PostgreSQL sequences: {e}")

def ensure_default_records():
    """
    Ensure default records exist for foreign key references with retry logic
    """
    def _ensure_defaults():
        db = SessionLocal()
        try:
            from . import models  # Import here to avoid circular imports
            
            # Ensure default user exists
            default_user = db.query(models.User).filter(models.User.id == 0).first()
            if not default_user:
                default_user = models.User(
                    id=0,
                    username="default_user",
                    password="default_password"
                )
                db.add(default_user)
                logger.info("Created default user")
            
            # Ensure at least one default model exists
            default_model = db.query(models.Model).filter(models.Model.model_id == "default").first()
            if not default_model:
                default_model = models.Model(
                    model_id="default",
                    model_name="Default Model",
                    client_name="Default Client"
                )
                db.add(default_model)
                logger.info("Created default model")
            
            db.commit()
        finally:
            db.close()
    
    try:
        execute_with_retry(_ensure_defaults)
    except Exception as e:
        logger.error(f"Error ensuring default records: {e}")

def get_call_by_room(room_name: str):
    """
    Get call information by room name using SQLAlchemy ORM with retry logic
    """
    def _get_call():
        db = SessionLocal()
        try:
            from . import models  # Import here to avoid circular imports
            
            call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if call:
                return {
                    "id": call.id,
                    "call_id": call.call_id,
                    "model_id": call.model_id,
                    "user_id": call.user_id,
                    "name": call.name,
                    "call_from": call.call_from,
                    "call_to": call.call_to,
                    "call_type": call.call_type,
                    "started_at": call.call_started_at.isoformat() if call.call_started_at else None,
                    "ended_at": call.call_ended_at.isoformat() if call.call_ended_at else None,
                    "status": call.call_status,
                    "duration": call.call_duration,
                    "metadata": call.call_metadata,
                    "transfer_agent_name": call.transfer_agent_name,
                    "transfer_reason": call.transfer_reason,
                    "transfer_time": call.transfer_time.isoformat() if call.transfer_time else None,
                    "call_summary": call.call_summary,
                    "call_transcription": call.call_transcription,
                    "call_recording_url": call.call_recording_url,
                    "call_conversation_quality": call.call_conversation_quality,
                    "call_entity": call.call_entity
                }
            return None
        finally:
            db.close()
    
    try:
        return execute_with_retry(_get_call)
    except Exception as e:
        logger.error(f"Error fetching call by room {room_name}: {e}")
        return None

def insert_call_start(room_name: str, agent_id: str, status: str, metadata: dict = None, 
                      name: str = None, call_from: str = None, call_to: str = None,
                      call_type: str = "Incoming", user_id: int = 0):
    """Insert a new row into the DB when a call starts using SQLAlchemy ORM with retry logic."""
    
    def _insert_call():
        from . import models  # Import here to avoid circular imports
        
        BASE_URL = "http://sbi.vaaniresearch.com:1244"
        call_transcription = f"{BASE_URL}/api/transcript/{room_name}"
        call_recording_url = f"{BASE_URL}/api/recording/{room_name}"

        db = SessionLocal()
        try:
            # Ensure default records exist
            ensure_default_records()
            
            # Check if call already exists to avoid duplicates
            existing_call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if existing_call:
                logger.info(f"Call {room_name} already exists, skipping insert")
                return existing_call.id

            # Validate foreign key references
            validated_user_id = user_id
            validated_model_id = agent_id
            
            # Check if user exists
            if user_id is not None and user_id != 0:
                user_exists = db.query(models.User).filter(models.User.id == user_id).first()
                if not user_exists:
                    logger.warning(f"User {user_id} doesn't exist, using default user (0)")
                    validated_user_id = 0
            
            # Check if model exists, create if it doesn't
            if agent_id:
                model_exists = db.query(models.Model).filter(models.Model.model_id == agent_id).first()
                if not model_exists:
                    # Create the model automatically
                    new_model = models.Model(
                        model_id=agent_id,
                        model_name=f"Auto-created Model {agent_id}",
                        client_name="Auto-created Client"
                    )
                    db.add(new_model)
                    db.flush()  # Flush to get the model available for the call
                    logger.info(f"Auto-created model {agent_id}")

            new_call = models.Call(
                call_id=room_name,
                model_id=validated_model_id,
                call_started_at=datetime.utcnow(),
                call_status=status,
                call_metadata=metadata or {},
                name=name,
                call_from=call_from,
                call_to=call_to,
                call_type=call_type,
                user_id=validated_user_id,
                call_transcription=call_transcription,
                call_recording_url=call_recording_url
            )
            
            db.add(new_call)
            db.commit()
            db.refresh(new_call)
            logger.info(f"Logged start of call for room '{room_name}' with agent '{agent_id}'.")
            return new_call.id
        finally:
            db.close()
    
    try:
        return execute_with_retry(_insert_call)
    except Exception as e:
        # If it's a sequence issue, try to fix it and retry once
        if "duplicate key value violates unique constraint" in str(e) and "pkey" in str(e):
            logger.warning("Detected sequence issue, attempting to fix...")
            try:
                fix_postgres_sequences()
                # Retry the insert one more time
                return execute_with_retry(_insert_call)
            except Exception as retry_error:
                logger.error(f"Failed to fix and retry: {retry_error}")
        
        logger.error(f"Failed to log call start: {e}")
        return None

def insert_call_end(room_name: str, status: str = "ended"):
    """Update the DB when the call ends or fails using SQLAlchemy ORM with retry logic."""
    
    def _insert_call_end():
        from . import models  # Import here to avoid circular imports
        
        db = SessionLocal()
        try:
            call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if not call:
                logger.error(f"No call found with call_id '{room_name}'.")
                return False
            
            call.call_ended_at = datetime.utcnow()
            call.call_status = status
            
            # Calculate duration if both start and end times exist
            if call.call_started_at and call.call_ended_at:
                duration = (call.call_ended_at - call.call_started_at).total_seconds()
                call.call_duration = duration
            
            db.commit()
            logger.info(f"Updated call end for room '{room_name}' with status '{status}'.")
            return True
        finally:
            db.close()
    
    try:
        return execute_with_retry(_insert_call_end)
    except Exception as e:
        logger.error(f"Failed to log call end: {e}")
        return False

def update_call_status(room_name: str, status: str):
    """Update the status of a call using SQLAlchemy ORM with retry logic."""
    
    def _update_status():
        from . import models  # Import here to avoid circular imports
        
        db = SessionLocal()
        try:
            call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if not call:
                logger.error(f"No call found with call_id '{room_name}'.")
                return False
            
            if call.call_status == "ended":
                logger.error(f"Call with call_id '{room_name}' has already ended. Cannot update status.")
                return False
            
            call.call_status = status
            db.commit()
            logger.info(f"Updated call status for room '{room_name}' to '{status}'.")
            return True
        finally:
            db.close()
    
    try:
        return execute_with_retry(_update_status)
    except Exception as e:
        logger.error(f"Failed to update call status: {e}")
        return False

def update_call_transfer_info(room_name: str, agent_name: str, reason: str):
    """Update the transfer info for a call using SQLAlchemy ORM with retry logic."""
    
    def _update_transfer():
        from . import models  # Import here to avoid circular imports
        
        db = SessionLocal()
        try:
            call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if not call:
                logger.error(f"No call found with call_id '{room_name}'.")
                return False
            
            if call.call_status == "ended":
                logger.error(f"Call with call_id '{room_name}' has already ended. Cannot update transfer info.")
                return False

            call.transfer_agent_name = agent_name
            call.transfer_reason = reason
            call.transfer_time = datetime.utcnow()
            
            db.commit()
            logger.info(f"Updated transfer info for room '{room_name}' to agent '{agent_name}'.")
            return True
        finally:
            db.close()
    
    try:
        return execute_with_retry(_update_transfer)
    except Exception as e:
        logger.error(f"Failed to update transfer info: {e}")
        return False

def update_call_summary(room_name: str, summary: str):
    """Update the call summary using SQLAlchemy ORM with retry logic."""
    
    def _update_summary():
        from . import models
        
        db = SessionLocal()
        try:
            call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if not call:
                logger.error(f"No call found with call_id '{room_name}'.")
                return False
            
            call.call_summary = summary
            db.commit()
            logger.info(f"Updated call summary for room '{room_name}'.")
            return True
        finally:
            db.close()
    
    try:
        return execute_with_retry(_update_summary)
    except Exception as e:
        logger.error(f"Failed to update call summary: {e}")
        return False

def update_call_quality(room_name: str, quality_data: dict):
    """Update the call conversation quality using SQLAlchemy ORM with retry logic."""
    
    def _update_quality():
        from . import models
        
        db = SessionLocal()
        try:
            call = db.query(models.Call).filter(models.Call.call_id == room_name).first()
            if not call:
                logger.error(f"No call found with call_id '{room_name}'.")
                return False
            
            call.call_conversation_quality = quality_data
            db.commit()
            logger.info(f"Updated call quality for room '{room_name}'.")
            return True
        finally:
            db.close()
    
    try:
        return execute_with_retry(_update_quality)
    except Exception as e:
        logger.error(f"Failed to update call quality: {e}")
        return False

def get_all_calls(limit: int = 100, offset: int = 0):
    """Get all calls with pagination using SQLAlchemy ORM with retry logic."""
    
    def _get_calls():
        from . import models
        
        db = SessionLocal()
        try:
            calls = db.query(models.Call).offset(offset).limit(limit).all()
            return [
                {
                    "id": call.id,
                    "call_id": call.call_id,
                    "model_id": call.model_id,
                    "user_id": call.user_id,
                    "name": call.name,
                    "call_from": call.call_from,
                    "call_to": call.call_to,
                    "call_type": call.call_type,
                    "started_at": call.call_started_at.isoformat() if call.call_started_at else None,
                    "ended_at": call.call_ended_at.isoformat() if call.call_ended_at else None,
                    "status": call.call_status,
                    "duration": call.call_duration,
                    "metadata": call.call_metadata
                }
                for call in calls
            ]
        finally:
            db.close()
    
    try:
        return execute_with_retry(_get_calls)
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return []

# Initialize database with default records on import
def init_db():
    """Initialize database with default records and fix sequences"""
    try:
        ensure_default_records()
        fix_postgres_sequences()  # Fix sequences after ensuring default records
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

if __name__ == "__main__":
    # Test the database configuration
    print(f"Using database: {DATABASE_URL}")
    print(f"Database type: {DB_TYPE}")
    
    # Initialize database
    init_db()
    
    # Test connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Uncomment to test functions
    import uuid
    # Generate a unique room name for testing
    room_name = f"Test_Room_{uuid.uuid4().hex[:8]}"

    call_id = insert_call_start(room_name, "test_model", "started", 
                      {"key": "value"}, "Test User",
                      "+919798601253", "+917055888820"
                      ) 
    print(f"Call started with ID: {call_id}")
    if call_id:
        print(f"✅ Created call with ID: {call_id}")
        print("✅ Database is working correctly!")
    else:
        print("❌ Failed to create call")
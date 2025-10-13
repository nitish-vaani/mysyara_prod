# #database_config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/app/.env.local")

def get_database_url():
    """
    Get the appropriate database URL based on DB_TYPE environment variable
    """
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    if db_type == "postgresql":
        postgres_url = os.getenv("POSTGRES_URL")
        if not postgres_url:
            raise ValueError("POSTGRES_URL environment variable is required when DB_TYPE=postgresql")
        return postgres_url
    
    elif db_type == "sqlite":
        sqlite_path = os.getenv("SQLITE_DB_PATH", "./backend/test.db")
        return f"sqlite:///{sqlite_path}"
    
    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}. Use 'sqlite' or 'postgresql'")

def get_engine_args():
    """
    Get database engine arguments based on database type with connection resilience
    """
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    if db_type == "postgresql":
        return {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,  # KEY FOR NEON AUTO-RECOVERY
            "pool_recycle": 300,    # Recycle every 5 minutes
            "connect_args": {
                "connect_timeout": 60,
                "application_name": "fastapi_livekit_app",
                "sslmode": "require",
            },
            "echo": False
        }
    elif db_type == "sqlite":
        return {
            "connect_args": {"check_same_thread": False},
            "echo": False
        }
    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}")

def get_db_type():
    """
    Get the current database type
    """
    return os.getenv("DB_TYPE", "sqlite").lower()
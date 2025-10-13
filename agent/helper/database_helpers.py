"""
Database operation helpers.
Handles all database-related operations and optimizations.
"""

from typing import Dict, Any
from database.db_manager import insert_call_start_optimized, insert_call_end_optimized
from .logging_config import get_logger

logger = get_logger(__name__)

async def insert_call_start_async(room_name: str, agent_name: str, status: str, 
                                dial_info: Dict[str, Any], name: str, call_from: str, 
                                call_to: str, call_type: str, user_id: int) -> str:
    """Async wrapper for insert_call_start using optimized approach"""
    try:
        operation_id = await insert_call_start_optimized(
            room_name, agent_name, status, dial_info, name, call_from, call_to, call_type, user_id
        )
        logger.info(f"Queued call start recording: {operation_id}")
        return operation_id
    except Exception as e:
        logger.error(f"Failed to queue call start recording: {e}")
        raise

async def insert_call_end_async(room_name: str, end_reason: str) -> str:
    """Async wrapper for insert_call_end using optimized approach"""
    try:
        operation_id = await insert_call_end_optimized(room_name, end_reason)
        logger.info(f"Queued call end recording: {operation_id} - {end_reason}")
        return operation_id
    except Exception as e:
        logger.error(f"Failed to queue call end recording: {e}")
        raise
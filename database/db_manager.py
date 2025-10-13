#db_manager.py

import asyncio
import logging
from typing import Optional
import time
from .db_test.db import insert_call_start, insert_call_end

logger = logging.getLogger("db-manager")

class DatabaseOperationManager:
    """Manages database operations with better error handling and queuing"""
    
    def __init__(self, max_workers: int = 3, retry_attempts: int = 2):
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts
        self.operation_queue = asyncio.Queue()
        self.workers_started = False
        
    async def start_workers(self):
        """Start background workers to process DB operations"""
        if not self.workers_started:
            for i in range(self.max_workers):
                asyncio.create_task(self._worker(f"db-worker-{i}"))
            self.workers_started = True
            logger.info(f"Started {self.max_workers} database workers")
    
    async def _worker(self, worker_name: str):
        """Background worker to process database operations"""
        while True:
            try:
                operation = await self.operation_queue.get()
                await self._execute_with_retry(operation)
                self.operation_queue.task_done()
            except Exception as e:
                logger.error(f"{worker_name} error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_with_retry(self, operation: dict):
        """Execute database operation with retry logic"""
        func = operation['func']
        args = operation['args']
        kwargs = operation['kwargs']
        operation_id = operation['id']
        
        for attempt in range(self.retry_attempts):
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
                
                if result:
                    logger.debug(f"DB operation {operation_id} succeeded")
                    return result
                else:
                    logger.warning(f"DB operation {operation_id} returned False")
                    
            except Exception as e:
                logger.error(f"DB operation {operation_id} attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(1)  # Simple 1-second retry delay
        
        logger.error(f"DB operation {operation_id} failed after all attempts")
    
    async def queue_operation(self, func, *args, **kwargs) -> str:
        """Queue a database operation for async execution"""
        operation_id = f"{func.__name__}_{int(time.time() * 1000)}"
        
        operation = {
            'id': operation_id,
            'func': func,
            'args': args,
            'kwargs': kwargs
        }
        
        await self.operation_queue.put(operation)
        return operation_id

# Global instance
db_manager = DatabaseOperationManager()

async def insert_call_start_optimized(*args, **kwargs):
    """Optimized call start insertion with queuing"""
    await db_manager.start_workers()
    return await db_manager.queue_operation(insert_call_start, *args, **kwargs)

async def insert_call_end_optimized(room_name: str, status: str):
    """Optimized call end insertion with queuing"""
    await db_manager.start_workers()
    return await db_manager.queue_operation(insert_call_end, room_name, status)
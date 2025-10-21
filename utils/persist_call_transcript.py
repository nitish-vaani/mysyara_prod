import asyncio
import aiofiles
import os 
from datetime import datetime
from .utils import get_month_year_as_string
from database.connectors.s3 import S3Connector
from database.connectors.azure_conn import BlobConnector
from livekit.agents import ConversationItemAddedEvent
from backend.openai_eval import evaluate_call_success
from database.db_test.db import update_call_success_status
import logging

logger = logging.getLogger(__name__)

def __persist_call_transacription(session, roomname, where, s3_folder_name):
    log_queue = asyncio.Queue()
    conversation_transcript = []  # Store transcript for evaluation

    @session.on("conversation_item_added")
    def on_conversation_item_added(event: ConversationItemAddedEvent):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if event.item.role == 'user':
            log_entry = f"[{timestamp}] USER: {event.item.text_content}. \n interrupted: {event.item.interrupted}\n\n"
            log_queue.put_nowait(log_entry)
            conversation_transcript.append(f"USER: {event.item.text_content}")
            
        if event.item.role == 'assistant':
            log_entry = f"[{timestamp}] AGENT: {event.item.text_content}. \n interrupted: {event.item.interrupted}\n\n"
            log_queue.put_nowait(log_entry)
            conversation_transcript.append(f"AGENT: {event.item.text_content}")

    filename = f"{roomname}.txt"

    async def write_transcription():
        async with aiofiles.open(filename, "w") as f:
            while True:
                msg = await log_queue.get()
                if msg is None:
                    break
                await f.write(msg)
        
        # After transcript is written, evaluate call success
        if conversation_transcript:
            try:
                full_transcript = "\n".join(conversation_transcript)
                logger.info(f"Evaluating call success for room: {roomname}")
                
                success_eval = await evaluate_call_success(full_transcript)
                
                if success_eval["status_code"] == 200:
                    update_call_success_status(roomname, success_eval["status"])
                    logger.info(f"Call success evaluated: {success_eval['status']} for room {roomname}")
                else:
                    logger.warning(f"Failed to evaluate call success for room {roomname}: {success_eval.get('error')}")
                    # Set as Undetermined if evaluation fails
                    update_call_success_status(roomname, "Undetermined")
            except Exception as e:
                logger.error(f"Error evaluating call success for room {roomname}: {e}")
                # Don't fail transcript persistence if evaluation fails
                try:
                    update_call_success_status(roomname, "Undetermined")
                except Exception as db_error:
                    logger.error(f"Failed to update call status to Undetermined: {db_error}")
        
        # Handle file storage based on 'where' parameter
        if where == 'both':
            s3_connector = S3Connector(os.getenv("AWS_BUCKET"))
            s3_key = f"transcripts/{s3_folder_name}/{get_month_year_as_string()}/{filename}"
            s3_url = await s3_connector.upload_file_async(filename, s3_key)
        elif where == 's3':
            s3_connector = S3Connector(os.getenv("AWS_BUCKET"))
            s3_key = f"transcripts/{s3_folder_name}/{get_month_year_as_string()}/{filename}"
            s3_url = await s3_connector.upload_file_async(filename, s3_key)
            if s3_url:
                os.remove(filename)  # Delete local file after upload
        elif where == 'azure':
            # print 3 line space
            # print("\n\n\n")
            # print("\n"*3)
            # print("Uploading to Azure Blob Storage")
            # print("\n\n\n")

            azure_connector = BlobConnector(os.getenv("AZURE_CONTAINER_NAME"))
            # using azure_blob path similar to s3 path for consistency
            # print("\n"*3, azure_connector, "\n========"*3)

            blob_path = f"transcripts/{s3_folder_name}/{get_month_year_as_string()}/{filename}"

            # return await azure_connector.upload_file_async(filename, blob_path)
            azure_url = await azure_connector.upload_file_async(filename, blob_path)
            if azure_url:
                # print(f"azure_url: {azure_url}")
                os.remove(filename) # Delete local file after upload
        elif where == 'local':
            pass  # file is already written to local with filename "roomname.txt"
        
    write_task = asyncio.create_task(write_transcription())

    async def finish_queue():
        log_queue.put_nowait(None)
        await write_task

    return finish_queue
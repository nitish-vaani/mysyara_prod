import asyncio
import aiofiles
import os 
from datetime import datetime
from .utils import get_month_year_as_string
from database.connectors.s3 import S3Connector
from livekit.agents import ConversationItemAddedEvent

def __persist_call_transacription(session, roomname, where, s3_folder_name):
    log_queue = asyncio.Queue()

    @session.on("conversation_item_added")
    def on_conversation_item_added(event: ConversationItemAddedEvent):
        # print(
        #     f"Conversation item added from {event.item.role}: {event.item.text_content}. interrupted: {event.item.interrupted}"
        # )
        if event.item.role == 'user':
            log_queue.put_nowait(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] USER: {event.item.text_content}. \n interrupted: {event.item.interrupted}\n\n"
            )
        if event.item.role == 'assistant':
            log_queue.put_nowait(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AGENT: {event.item.text_content}. \n interrupted: {event.item.interrupted}\n\n"
            )

    filename = f"{roomname}.txt"

    async def write_transcription():
        async with aiofiles.open(filename, "w") as f:
            while True:
                msg = await log_queue.get()
                if msg is None:
                    break
                await f.write(msg)
        if where == 'both':
            s3_connector = S3Connector(os.getenv("AWS_BUCKET"))
            s3_key = f"transcripts/{s3_folder_name}/{get_month_year_as_string()}/{filename}"
            s3_url = await s3_connector.upload_file_async(filename, s3_key)
        elif where == 's3':
            s3_connector = S3Connector(os.getenv("AWS_BUCKET"))
            s3_key = f"transcripts/{s3_folder_name}/{get_month_year_as_string()}/{filename}"
            s3_url = await s3_connector.upload_file_async(filename, s3_key)
            if s3_url:
                os.remove(filename)  # Delete local file after upload (optional)
        elif where == 'local':
            pass # file is already written to local with filename "roomname.txt"
        
    write_task = asyncio.create_task(write_transcription())

    async def finish_queue():
        log_queue.put_nowait(None)
        await write_task

    return finish_queue
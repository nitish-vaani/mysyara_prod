"""
Transcript management and conversation tracking.
Handles conversation logging and transcript persistence.
"""

from datetime import datetime
from typing import Dict, Any
from livekit.agents import ConversationItemAddedEvent
from utils.persist_call_transcript import __persist_call_transacription as persist_call_transcription
from .logging_config import get_transcript_logger

transcript_logger = get_transcript_logger()

class TranscriptManager:
    """Manages conversation transcripts and logging"""
    
    def __init__(self):
        self.conversation_transcript = ""
    
    def setup_transcript_persistence(self, session, room_name: str, config: Dict[str, Any]):
        """Setup transcript persistence if enabled in config"""
        if not config["store_transcription"]['switch']:
            return None
            
        return persist_call_transcription(
            session, room_name, 
            config["store_transcription"]['where'], 
            config['client_name']
        )
    
    def create_conversation_handler(self):
        """Create conversation item added event handler"""
        def on_conversation_item_added(event: ConversationItemAddedEvent):
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            if event.item.role == 'user':
                transcript_logger.info(f"[{timestamp}] USER: {event.item.text_content}")
                self.conversation_transcript += f"\n[{timestamp}] USER: {event.item.text_content}\n"
            elif event.item.role == 'assistant':
                transcript_logger.info(f"[{timestamp}] AGENT: {event.item.text_content}")
                self.conversation_transcript += f"\n[{timestamp}] AGENT: {event.item.text_content}\n"
        
        return on_conversation_item_added
    
    def get_transcript(self) -> str:
        """Get the current conversation transcript"""
        return self.conversation_transcript
    
    def clear_transcript(self):
        """Clear the conversation transcript"""
        self.conversation_transcript = ""

# Global transcript manager instance
transcript_manager = TranscriptManager()
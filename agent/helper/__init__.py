"""
Helper package for Mysyara agent.
Contains modular utilities for configuration, logging, AI models, call handling, and more.
"""

from .config_manager import config_manager
from .logging_config import setup_logging, get_logger, get_transcript_logger
from .ai_models import get_openai_llm, get_tts, get_stt_instance, get_vad_instance
from .call_handlers import CallState, handle_outbound_sip_call, handle_inbound_call, get_disconnect_reason
from .database_helpers import insert_call_start_async, insert_call_end_async
from .session_helpers import (prewarm_session, create_agent_session, setup_background_audio, 
                             setup_audio_recording, get_room_input_options)
from .transcript_manager import transcript_manager
from .agent_class import MysyaraAgent, create_mysyara_agent
from .entrypoint_handler import handle_entrypoint
from .data_entities import UserData
from .rag_connector import enrich_with_rag

__all__ = [
    # Config management
    'config_manager',
    
    # Logging
    'setup_logging', 'get_logger', 'get_transcript_logger',
    
    # AI Models
    'get_openai_llm', 'get_tts', 'get_stt_instance', 'get_vad_instance',
    
    # Call handling
    'CallState', 'handle_outbound_sip_call', 'handle_inbound_call', 'get_disconnect_reason',
    
    # Database operations
    'insert_call_start_async', 'insert_call_end_async',
    
    # Session helpers
    'prewarm_session', 'create_agent_session', 'setup_background_audio', 
    'setup_audio_recording', 'get_room_input_options',
    
    # Transcript management
    'transcript_manager',
    
    # Agent class
    'MysyaraAgent', 'create_mysyara_agent',
    
    # Entrypoint handler
    'handle_entrypoint',

    # Data entities
    'UserData',

    # RAG connector
    'enrich_with_rag',
]
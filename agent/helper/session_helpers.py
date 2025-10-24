"""
Session and agent setup helpers.
Handles session configuration, background audio, and recording setup.
"""

import os
from typing import Dict, Any
from livekit import api
from livekit.agents import (AudioConfig, BackgroundAudioPlayer, BuiltinAudioClip, 
                           AgentSession, RoomInputOptions)
from livekit.plugins import noise_cancellation
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.agents import llm, stt, tts
from .ai_models import get_openai_llm, get_tts, get_stt_instance, get_vad_instance, get_llm_instance, get_azure_llm
from .logging_config import get_logger
from .data_entities import UserData
from .config_manager import config_manager
from utils.utils import get_month_year_as_string

# Load configuration
config = config_manager.config
logger = get_logger(__name__)

def prewarm_session(proc):
    """Prewarm function for session initialization"""
    proc.userdata["bg_audio_config"] = {
        "ambient": [AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=1)],
        "thinking": [
            AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.2),
            AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING2, volume=0.2),
        ],
    }

def create_agent_session(userdata: UserData, config: Dict[str, Any], agent_config: Dict[str, Any]=None) -> AgentSession:
    """Create and configure an agent session with all required components"""
    primary_stt_provider = config['STT']['primary_provider']
    secondary_stt_provider = config['STT']['secondary_provider']
    primary_stt_model = config['STT']['primary_model']
    secondary_stt_model = config['STT']['secondary_model']

    primary_tts_provider = config['TTS']['primary_provider']
    secondary_tts_provider = config['TTS']['secondary_provider']
    primary_tts_model = config['TTS']['primary_model']
    secondary_tts_model = config['TTS']['secondary_model']
    
    primary_llm_provider = config['LLM']['primary_provider']
    secondary_llm_provider = config['LLM']['secondary_provider']
    primary_llm_model = config['LLM']['primary_model']
    secondary_llm_model = config['LLM']['secondary_model']

    # Get AI model instances
    # llm_instance = get_azure_llm()
    # llm_instance = get_openai_llm()
    llm_instance = get_llm_instance(primary_llm_provider, secondary_llm_provider, primary_llm_model, secondary_llm_model)
    tts_instance = get_tts(config, voice_config=agent_config if agent_config else None)
    stt_instance = get_stt_instance()
    vad_instance = get_vad_instance()
    
    # Create session with all components
    if config['STT']['primary_provider'] == 'assemblyai': #this can throw issues as not all stt will support turn detection
        session = AgentSession[UserData](
            stt=stt.FallbackAdapter(stt_instance),
            # llm=llm_instance,
            llm=llm.FallbackAdapter(llm_instance),
            tts=tts.FallbackAdapter(tts_instance),
            vad=vad_instance,
            turn_detection="stt",
            # turn_detection=EnglishModel(),
            userdata=userdata
        )
    else:
        session = AgentSession[UserData](
            stt=stt.FallbackAdapter(stt_instance),
            llm=llm_instance,
            # llm=llm.FallbackAdapter(llm_instance),
            tts=tts.FallbackAdapter(tts_instance),
            vad=vad_instance,
            # turn_detection=EnglishModel(),
            userdata=userdata
        )
    
    logger.info("Agent session created successfully")
    return session

async def setup_background_audio(config: Dict[str, Any], room, session: AgentSession) -> BackgroundAudioPlayer:
    """Setup background audio if enabled in config"""
    _ambient_sound = None
    _thinking_sound = None
    if (not config.get("bg_office_noise")) and (not config.get("bg_thinking_sound")):
        return None
    
    if config.get("bg_office_noise", False):
        _ambient_sound = AudioConfig(BuiltinAudioClip.OFFICE_AMBIENCE, volume=0.7)

    if config.get("bg_thinking_sound", False):
        _thinking_sound = [
                AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING, volume=0.2),
                AudioConfig(BuiltinAudioClip.KEYBOARD_TYPING2, volume=0.2),
            ]
        
    try:
        bg_audio = BackgroundAudioPlayer(
            # play office ambience sound looping in the background
            ambient_sound=_ambient_sound,
            # play keyboard typing sound when the agent is thinking
            thinking_sound=_thinking_sound,
        )
        await bg_audio.start(room=room, agent_session=session)
        logger.info("Background audio started successfully")
        return bg_audio
    except Exception as e:
        logger.warning(f"Failed to start background audio: {e}")
        return None

async def setup_audio_recording(config: Dict[str, Any], room_name: str):
    """Setup audio recording if enabled in config"""
    if not config.get("record_audio", False):
        logger.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        logger.info("Recording is not set")
        logger.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        return

    path = f"recordings/ogg/{config['client_name']}/{get_month_year_as_string()}"
    if config['audio_record_location']=="s3":  
        try:
            req = api.RoomCompositeEgressRequest(
                room_name=room_name,
                layout="speaker",
                audio_only=True,
                file_outputs=[
                    api.EncodedFileOutput(
                        file_type=api.EncodedFileType.OGG,
                        filepath=f"{path}/{room_name}.ogg",
                        s3=api.S3Upload(
                            access_key=os.getenv("AWS_ACCESS_KEY"),
                            secret=os.getenv("AWS_SECRET_KEY"),
                            region=os.getenv("AWS_REGION"),
                            bucket=os.getenv("AWS_BUCKET"),
                        ),
                    )
                ],
            )
            logger.info(f"Starting recording for room {room_name}")
            lkapi = api.LiveKitAPI()
            await lkapi.egress.start_room_composite_egress(req)
            logger.info("Audio recording started successfully")
        except Exception as e:
            logger.warning(f"Failed to start recording: {e}")

    elif config["audio_record_location"]=="azure":  
        try:
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            container_name = os.getenv("AZURE_CONTAINER_NAME")
            
            if not connection_string or not container_name:
                logger.error("Azure credentials not found in environment")
                return
            
            conn_parts = {}
            for part in connection_string.split(';'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    conn_parts[key] = value
            
            account_name = conn_parts.get('AccountName', '')
            account_key = conn_parts.get('AccountKey', '')
            
            if not account_name or not account_key:
                logger.error("Could not parse AccountName or AccountKey from connection string")
                return
            
            logger.info(f"Using Azure account: {account_name}, container: {container_name}")
            
            path = f"recordings/ogg/{config['client_name']}/{get_month_year_as_string()}"

            req = api.RoomCompositeEgressRequest(
                room_name=room_name,
                layout="speaker",
                audio_only=True,
                file_outputs=[
                    api.EncodedFileOutput(
                        file_type=api.EncodedFileType.OGG,
                        filepath=f"{path}/{room_name}.ogg",
                        azure=api.AzureBlobUpload(
                            account_name=account_name,
                            account_key=account_key,
                            container_name=container_name,
                        ),
                    )
                ],
            )
            logger.info(f"Starting OGG recording for room {room_name}")
            lkapi = api.LiveKitAPI()
            await lkapi.egress.start_room_composite_egress(req)
            logger.info("Audio recording started successfully")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")

def get_room_input_options(mode: str) -> RoomInputOptions:
    """Get appropriate room input options based on mode"""
    if mode == "SIP":
        return RoomInputOptions(
            noise_cancellation=noise_cancellation.BVCTelephony(),
        )
    else:  # Console mode
        return RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        )
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
from .ai_models import get_openai_llm, get_tts, get_stt_instance, get_vad_instance
from .logging_config import get_logger
from .data_entities import UserData

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

# def create_agent_session(userdata: UserData, config: Dict[str, Any]) -> AgentSession:
#     """Create and configure an agent session with all required components"""
#     # Get AI model instances
#     llm_instance = get_openai_llm()
#     tts_instance = get_tts(config)
#     stt_instance = get_stt_instance()
#     vad_instance = get_vad_instance()
    
#     # Create session with all components
#     session = AgentSession[UserData](
#         stt=stt_instance,
#         llm=llm_instance,
#         tts=tts_instance,
#         vad=vad_instance,
#         turn_detection=EnglishModel(),
#         userdata=userdata
#     )
    
#     logger.info("Agent session created successfully")
#     return session
def create_agent_session(userdata: UserData, config: Dict[str, Any], agent_config: Dict[str, Any]=None) -> AgentSession:
    """Create and configure an agent session with all required components"""
    # Get AI model instances
    llm_instance = get_openai_llm()
    tts_instance = get_tts(config, voice_config=agent_config if agent_config else None)
    stt_instance = get_stt_instance()
    vad_instance = get_vad_instance()
    
    # Create session with all components
    session = AgentSession[UserData](
        stt=stt_instance,
        llm=llm_instance,
        tts=tts_instance,
        vad=vad_instance,
        turn_detection=EnglishModel(),
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
        return
        
    try:
        req = api.RoomCompositeEgressRequest(
            room_name=room_name,
            layout="speaker",
            audio_only=True,
            segment_outputs=[
                api.SegmentedFileOutput(
                    filename_prefix=f"{room_name}",
                    playlist_name=f"{room_name}-playlist.m3u8",
                    live_playlist_name=f"{room_name}-live-playlist.m3u8",
                    segment_duration=5,
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
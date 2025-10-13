"""
AI model configuration and initialization.
Handles LLM, TTS, and other AI model setup.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from livekit.plugins import elevenlabs, deepgram, openai, cartesia, aws, silero
from .config_manager import config_manager
from .logging_config import get_logger

logger = get_logger(__name__)
config = config_manager.config
def get_openai_llm():
    """Get properly configured OpenAI LLM"""
    api_key = config_manager.get_openai_api_key()
    
    try:
        # For project-specific keys, we might need to handle differently
        if api_key.startswith("sk-proj-"):
            logger.info("Using project-specific OpenAI API key")
        
        if config['llm'] == 'cerebras':
            llm_instance = openai.LLM.with_cerebras(
                 model=config['model'],
                 api_key=api_key
            )
        else:
            llm_instance = openai.LLM(
                # model="gpt-3.5-turbo",  # More reliable and supported model
                model="gpt-4o",  # Use gpt-4o for better performance
                api_key=api_key
            )
        
        logger.info("Successfully created OpenAI LLM instance")
        return llm_instance
        
    except Exception as e:
        logger.error(f"Failed to create OpenAI LLM: {e}")
        raise

def get_tts(config: Dict[str, Any], voice_config: Dict[str, Any] = None):
    """Get configured TTS instance based on config"""
    which_tts = config["TTS"]
    which_voice=voice_config.get("voice", "default") if voice_config else "default"

    if which_tts == "cartesia":
        david = "da69d796-4603-4419-8a95-293bfc5679eb"
        help_desk = "39b376fc-488e-4d0c-8b37-e00b72059fdd"
        customer_service = "2a4d065a-ac91-4203-a015-eb3fc3ee3365"
        Devansh = "1259b7e3-cb8a-43df-9446-30971a46b8b0"

        def get_voice(voice_name: str):
            voices = {
                "david": david,
                "help_desk": help_desk,
                "customer_service": customer_service,
                "devansh": Devansh,
                "default": help_desk,
            }
            return voices.get(voice_name.lower(), Devansh)
        
        def manipulate_speed(list_view):
            import random
            # choose a random value from the list and return it
            if not list_view:   # handle empty list safely
                return None
            return random.choice(list_view)


        return cartesia.TTS(
            model="sonic-2-2025-03-07",
            # voice=which_voice if which_voice != "default" else Devansh,
            voice=get_voice(which_voice),
            speed=-0.15,
            language="en",
            emotion=["positivity:highest", "curiosity:highest"],
        ) 
    
    if which_tts == "aws":
        return aws.TTS()
    if which_tts == "elevenlabs":

        #Male Voices
        eric = "9T9vSqRrPPxIs5wpyZfK"

        #Female Voices





        def get_voice(voice_name: str):
            voices = {
                "eric": eric,
                "default": eric,
            }
            return voices.get(voice_name.lower(), eric)


        @dataclass
        class VoiceSettings:
            stability: float
            similarity_boost: float
            style: float | None = None
            speed: float | None = 1.0
            use_speaker_boost: bool | None = False

        voice_setting = VoiceSettings(
            stability=0.5,
            speed=1.05,
            similarity_boost=0.6,
            style=0.0,
            use_speaker_boost=True,
        )
          
        return elevenlabs.TTS(
            model="eleven_flash_v2_5", 
            voice_settings=voice_setting, 
            voice_id=eric
        )
    if which_tts == "deepgram":
        return deepgram.TTS()

def get_stt_instance():

    """Get configured STT instance"""
    from ..prompts.boosted_keywords import keywords_to_boost
    
    return deepgram.STT(
        model="nova-3",  
        language="en", 
        keyterms=keywords_to_boost
    )

def get_vad_instance():
    """Get configured VAD instance"""
    return silero.VAD.load()
# """
# AI model configuration and initialization.
# Handles LLM, TTS, and other AI model setup.
# """

# import os
# import json
# from typing import Dict, Any
# from dataclasses import dataclass
# from livekit.plugins import elevenlabs, deepgram, openai, cartesia, aws, silero, assemblyai
# from .config_manager import config_manager
# from .logging_config import get_logger

# logger = get_logger(__name__)
# config = config_manager.config




# def get_openai_llm(model_name=None):
#     """Get properly configured OpenAI LLM"""
#     api_key = config_manager.get_openai_api_key()
#     model= model_name if model_name is not None else "gpt-5"
#     try:
#         llm_instance = openai.LLM(
#             # model="gpt-3.5-turbo",  # More reliable and supported model
#             model=model,  # Use gpt-4o for better performance
#             api_key=api_key
#         )
#         logger.info("Successfully created OpenAI LLM instance")
#         return llm_instance
        
#     except Exception as e:
#         logger.error(f"Failed to create OpenAI LLM: {e}")
#         raise

# def get_gemini_llm(model_name=None):
#     model = model_name if model_name is not None else "google/gemini-2.5-pro"
#     try:
#     # gemini_model = "google/gemini-2.5-flash-lite"
#         gemini_model = model
#         google_api_key = os.getenv("GOOGLE_API_KEY")
#         missing = [name for name, val in [
#             ("GOOGLE_API_KEY", google_api_key),
#             ("model", gemini_model)
#         ] if not val]
#         if missing:
#             raise ValueError(
#                 "Missing required Gemini settings: " + ", ".join(missing) +
#                 ". Ensure env vars are set and model is specified in engine_config.yaml"
#             )
#         logger.info(f"Initializing Gemini LLM {gemini_model}")
#         # from livekit.agents import inference
#         return inference.LLM(
#             model=gemini_model,
#             # extra_kwargs={
#             #     # "provider": "google",
#             #     "api_key": google_api_key
#             # }
#         )

#     except:
#         logger.error(f"Failed to create Gemini LLM instance: {error}")

# def get_azure_llm(model_name=None):
#     model_name=None
#     try:
#         azure_cfg = config.get("azure", {}) if isinstance(config, dict) else {}
#         azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or azure_cfg.get("endpoint")
#         azure_api_key = os.getenv("AZURE_OPENAI_API_KEY") or azure_cfg.get("api_key")
#         azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION") or azure_cfg.get("api_version")
#         azure_deployment = (
#             os.getenv("AZURE_OPENAI_DEPLOYMENT")
#             or azure_cfg.get("deployment")
#             or config.get("model")
#         )
#         missing = [name for name, val in [
#             ("AZURE_OPENAI_ENDPOINT", azure_endpoint),
#             ("AZURE_OPENAI_API_KEY", azure_api_key),
#             ("AZURE_OPENAI_API_VERSION", azure_api_version),
#             ("AZURE_OPENAI_DEPLOYMENT/model", azure_deployment),
#         ] if not val]
#         if missing:
#             raise ValueError(
#                 "Missing required Azure OpenAI settings: " + ", ".join(missing) +
#                 ". Ensure env vars are set or provide azure.{endpoint, api_key, api_version, deployment} in engine_config.yaml; `model` can serve as deployment."
#             )
#         logger.info("Initializing Azure OpenAI LLM via with_azure using engine_config.yaml settings")
#         return openai.LLM.with_azure(
#             azure_deployment=azure_deployment,
#             azure_endpoint=azure_endpoint,
#             api_key=azure_api_key,
#             api_version=azure_api_version,
#         )
#     except Exception as error:
#         logger.error(f"Failed to create Azure OpenAI LLM instance: {error}")

# def get_llm_instance(primary, secondary, primary_model, secondary_model):
#     primary_llm = config_llm['primary'](primary_model)
#     secondary_llm = config_llm['secondary'](secondary_model)
#     return [primary_llm, secondary_llm]

# config_llm = {
#     "gemini": get_gemini_llm,
#     "openai": get_openai_llm,
#     "azure": get_azure_llm}


# def get_tts(config: Dict[str, Any], voice_config: Dict[str, Any] = None):
#     """Get configured TTS instance based on config"""
#     which_tts = config["TTS"]['primary_provider']
#     which_voice=voice_config.get("voice", "default") if voice_config else "default"

#     if which_tts == "cartesia":
#         david = "da69d796-4603-4419-8a95-293bfc5679eb"
#         help_desk = "39b376fc-488e-4d0c-8b37-e00b72059fdd"
#         customer_service = "2a4d065a-ac91-4203-a015-eb3fc3ee3365"
#         Devansh = "1259b7e3-cb8a-43df-9446-30971a46b8b0"

#         def get_voice(voice_name: str):
#             voices = {
#                 "david": david,
#                 "help_desk": help_desk,
#                 "customer_service": customer_service,
#                 "devansh": Devansh,
#                 "default": help_desk,
#             }
#             return voices.get(voice_name.lower(), Devansh)
        
#         def manipulate_speed(list_view):
#             import random
#             # choose a random value from the list and return it
#             if not list_view:   # handle empty list safely
#                 return None
#             return random.choice(list_view)


#         primary_tts =  cartesia.TTS(
#                             model="sonic-2-2025-03-07",
#                             # voice=which_voice if which_voice != "default" else Devansh,
#                             voice=get_voice(which_voice),
#                             speed=-0.15,
#                             language="en",
#                             emotion=["positivity:highest", "curiosity:highest"],
#                         ) 

#         secondary_tts = deepgram.TTS(model="aura-2-arcas-en")
#         return [primary_tts, secondary_tts]
    
#     if which_tts == "aws":
#         return aws.TTS()
    
#     if which_tts == "elevenlabs":

#         #Male Voices
#         eric = "9T9vSqRrPPxIs5wpyZfK"

#         #Female Voices





#         def get_voice(voice_name: str):
#             voices = {
#                 "eric": eric,
#                 "default": eric,
#             }
#             return voices.get(voice_name.lower(), eric)


#         @dataclass
#         class VoiceSettings:
#             stability: float
#             similarity_boost: float
#             style: float | None = None
#             speed: float | None = 1.0
#             use_speaker_boost: bool | None = False

#         voice_setting = VoiceSettings(
#             stability=0.5,
#             speed=1.05,
#             similarity_boost=0.6,
#             style=0.0,
#             use_speaker_boost=True,
#         )
          
#         primary_tts= elevenlabs.TTS(
#                                     model="eleven_flash_v2_5", 
#                                     voice_settings=voice_setting, 
#                                     voice_id=eric
#                                 )

#         secondary_tts = deepgram.TTS(model="aura-2-arcas-en")
#         return [primary_tts, secondary_tts]
    
#     if which_tts == "deepgram":
#         return deepgram.TTS()

# def get_stt_instance():
#     """Get configured STT instance"""
#     from ..prompts.boosted_keywords import keywords_to_boost
#     which_stt = config["STT"]['primary_provider']

#     if which_stt == 'deepgram':
#         primary_stt = deepgram.STT(
#                             model="nova-3",  
#                             language="en", 
#                             # keyterms=keywords_to_boost
#                         )
#         fallback_stt = assemblyai.STT(
#                             keyterms_prompt=keywords_to_boost,
#                             end_of_turn_confidence_threshold=0.5,
#                             min_end_of_turn_silence_when_confident=160,
#                             max_turn_silence=1280,
#                             format_turns=True
#                         )

#         return [primary_stt, fallback_stt]


        

#     if which_stt == "assemblyai":
#         fallback_stt = deepgram.STT(
#                             model="nova-3",  
#                             language="en", 
#                             keyterms=keywords_to_boost
#                         )
#         primary_stt = assemblyai.STT(
#                             # keyterms_prompt=keywords_to_boost,
#                             end_of_turn_confidence_threshold=0.5,
#                             min_end_of_turn_silence_when_confident=160,
#                             max_turn_silence=1280,
#                             format_turns=True
#                         )

#         return [primary_stt, fallback_stt]

# def get_vad_instance():
#     """Get configured VAD instance"""
#     return silero.VAD.load()








"""
AI model configuration and initialization.
Handles LLM, TTS, and other AI model setup.
"""

import os
import json
from typing import Dict, Any
from dataclasses import dataclass
from livekit.plugins import elevenlabs, deepgram, openai, cartesia, aws, silero, assemblyai
from livekit.agents import inference
from .config_manager import config_manager
from .logging_config import get_logger

logger = get_logger(__name__)
config = config_manager.config


def get_openai_llm(model_name=None):
    """Get properly configured OpenAI LLM"""
    api_key = config_manager.get_openai_api_key()
    model = model_name if model_name is not None else "gpt-4o"
    try:
        llm_instance = openai.LLM(
            model=model,
            api_key=api_key
        )
        logger.info("******************************")
        logger.info(f"Successfully created OpenAI LLM instance: {model}")
        logger.info("******************************")
        return llm_instance

        
    except Exception as e:
        logger.error(f"Failed to create OpenAI LLM: {e}")
        raise


def get_gemini_llm(model_name=None):
    """Get properly configured Gemini LLM"""
    model = model_name if model_name is not None else "google/gemini-2.0-flash-exp"
    
    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        logger.info(f"Initializing Gemini LLM: {model}")
        
        return inference.LLM(
            model=model,
        )
    
    except Exception as e:
        logger.error(f"Failed to create Gemini LLM: {e}")
        raise


def get_azure_llm(model_name=None):
    """Get properly configured Azure OpenAI LLM"""
    model_name=None
    try:
        azure_cfg = config.get("azure", {}) if isinstance(config, dict) else {}
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or azure_cfg.get("endpoint")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY") or azure_cfg.get("api_key")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION") or azure_cfg.get("api_version")
        azure_deployment = (
            model_name or
            os.getenv("AZURE_OPENAI_DEPLOYMENT") or
            azure_cfg.get("deployment") or
            config.get("model")
        )
        
        missing = [name for name, val in [
            ("AZURE_OPENAI_ENDPOINT", azure_endpoint),
            ("AZURE_OPENAI_API_KEY", azure_api_key),
            ("AZURE_OPENAI_API_VERSION", azure_api_version),
            ("AZURE_OPENAI_DEPLOYMENT/model", azure_deployment),
        ] if not val]
        
        if missing:
            raise ValueError(
                "Missing required Azure OpenAI settings: " + ", ".join(missing) +
                ". Ensure env vars are set or provide azure.{endpoint, api_key, api_version, deployment} in engine_config.yaml"
            )
        logger.info("******************************")
        logger.info(f"Initializing Azure OpenAI LLM: {azure_deployment}")
        logger.info("******************************")
        
        return openai.LLM.with_azure(
            azure_deployment=azure_deployment,
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=azure_api_version,
        )


    except Exception as e:
        logger.error(f"Failed to create Azure OpenAI LLM: {e}")
        raise


def get_llm_instance(primary_provider, secondary_provider, primary_model, secondary_model):
    """Get LLM instances with fallback support"""
    config_llm = {
        'gemini': get_gemini_llm,
        'openai': get_openai_llm,
        'azure': get_azure_llm
    }
    
    try:
        if primary_provider not in config_llm:
            raise ValueError(f"Unknown primary LLM provider: {primary_provider}")
        
        primary_llm = config_llm[primary_provider](primary_model)
        logger.info(f"Primary LLM initialized: {primary_provider}")
    except Exception as e:
        logger.error(f"Failed to initialize primary LLM ({primary_provider}): {e}")
        raise
    
    try:
        if secondary_provider not in config_llm:
            raise ValueError(f"Unknown secondary LLM provider: {secondary_provider}")
        
        secondary_llm = config_llm[secondary_provider](secondary_model)
        logger.info(f"Secondary LLM initialized: {secondary_provider}")
    except Exception as e:
        logger.warning(f"Failed to initialize secondary LLM ({secondary_provider}): {e}")
        secondary_llm = None
    
    # Return list with secondary only if it exists
    return [primary_llm, secondary_llm] if secondary_llm else [primary_llm]



def get_tts(config: Dict[str, Any], voice_config: Dict[str, Any] = None):
    """Get configured TTS instance based on config"""
    which_tts = config["TTS"]['primary_provider']
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


        primary_tts =  cartesia.TTS(
                            model="sonic-2-2025-03-07",
                            # voice=which_voice if which_voice != "default" else Devansh,
                            voice=get_voice(which_voice),
                            speed=-0.15,
                            language="en",
                            emotion=["positivity:highest", "curiosity:highest"],
                        ) 

        secondary_tts = deepgram.TTS(model="aura-2-arcas-en")
        return [primary_tts, secondary_tts]
    
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
          
        primary_tts= elevenlabs.TTS(
                                    model="eleven_flash_v2_5", 
                                    voice_settings=voice_setting, 
                                    voice_id=eric
                                )

        secondary_tts = deepgram.TTS(model="aura-2-arcas-en")
        return [primary_tts, secondary_tts]
    
    if which_tts == "deepgram":
        return deepgram.TTS()

def get_stt_instance():
    """Get configured STT instance"""
    from ..prompts.boosted_keywords import keywords_to_boost
    which_stt = config["STT"]['primary_provider']

    if which_stt == 'deepgram':
        logger.info(f"From STT if block")
        primary_stt = deepgram.STT(
                            model="nova-3",  
                            language="en", 
                            # keyterms=keywords_to_boost
                        )
        fallback_stt = assemblyai.STT(
                            keyterms_prompt=keywords_to_boost,
                            end_of_turn_confidence_threshold=0.5,
                            min_end_of_turn_silence_when_confident=160,
                            max_turn_silence=1280,
                            format_turns=True
                        )

        return [primary_stt, fallback_stt]


        

    if which_stt == "assemblyai":
        logger.info(f"From STT 2nd if block")
        fallback_stt = deepgram.STT(
                            model="nova-3",  
                            language="en", 
                            keyterms=keywords_to_boost
                        )
        primary_stt = assemblyai.STT(
                            # keyterms_prompt=keywords_to_boost,
                            end_of_turn_confidence_threshold=0.5,
                            min_end_of_turn_silence_when_confident=160,
                            max_turn_silence=1280,
                            format_turns=True
                        )

        return [primary_stt, fallback_stt]

def get_vad_instance():
    """Get configured VAD instance"""
    return silero.VAD.load()
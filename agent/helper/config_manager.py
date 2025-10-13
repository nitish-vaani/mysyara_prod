"""
Configuration management for the Mysyara agent.
Handles loading and parsing of configuration files and environment variables.
"""

import os
import logging
from dotenv import load_dotenv
from yaml import safe_load
from typing import Dict, Any
logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, env_path: str = "/app/.env.local", config_path: str = "/app/config/engine_config.yaml"):
        self.env_path = env_path
        self.config_path = config_path
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load environment variables and YAML configuration"""
        # Load environment variables
        load_dotenv(dotenv_path=self.env_path)
        
        # Load YAML configuration
        try:
            with open(self.config_path, "r") as file:
                self._config = safe_load(file)
            logger.info(f"Successfully loaded config from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the loaded configuration"""
        # print(self._config)
        return self._config
    
    def get_env_var(self, key: str, default: str = None) -> str:
        """Get environment variable with optional default"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
    
    def get_openai_api_key(self) -> str:
        """Get and validate OpenAI API key"""
        api_key_cerebras = self.get_env_var('CEREBRAS_API_KEY', None)
        api_key = self.get_env_var("OPENAI_API_KEY")
        logger.info(f"OpenAI API Key configured: {api_key[:15]}...{api_key[-4:]}")
        if self.config['llm'] == 'cerebras':
            return api_key_cerebras 
        return api_key
    
    def get_sip_trunk_id(self) -> str:
        """Get SIP outbound trunk ID"""
        return self.get_env_var("SIP_OUTBOUND_TRUNK_ID")

# Global configuration instance
config_manager = ConfigManager()
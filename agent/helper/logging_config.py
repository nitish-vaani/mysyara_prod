"""
Logging configuration for the Mysyara agent.
Centralizes all logging setup and configuration.
"""

import logging

def setup_logging():
    """Configure all loggers for the application"""
    
    # Main agent logger
    logger = logging.getLogger("outbound-caller")
    logger.setLevel(logging.INFO)
    
    # Transcript logger with custom formatting
    transcript_logger = logging.getLogger("transcript")
    transcript_logger.setLevel(logging.INFO)
    transcript_handler = logging.StreamHandler()
    transcript_formatter = logging.Formatter('%(message)s') 
    transcript_handler.setFormatter(transcript_formatter)
    transcript_logger.addHandler(transcript_handler)
    transcript_logger.propagate = False
    
    # Reduce noise from third-party loggers
    noisy_loggers = [
        "openai", "httpx", "httpcore", "livekit", "asyncio",
        "botocore", "boto3", "s3transfer", "urllib3"
    ]
    
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Keep important loggers at INFO level
    important_loggers = ["livekit.agents", "call-logger"]
    for logger_name in important_loggers:
        logging.getLogger(logger_name).setLevel(logging.INFO)
    
    return logger, transcript_logger

def get_logger(name: str = "outbound-caller") -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)

def get_transcript_logger() -> logging.Logger:
    """Get the transcript logger instance"""
    return logging.getLogger("transcript")
"""Logging configuration for PhoneAgent."""

import logging
import os
import sys

def setup_logger(name: str = "phone_agent", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and return a logger with standard formatting.
    
    Args:
        name: Logger name.
        level: Logging level.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

# Default logger
logger = setup_logger()

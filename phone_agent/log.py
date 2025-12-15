"""Logging configuration for PhoneAgent."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(
    name: str = "phone_agent",
    level: int = logging.INFO,
    log_file: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up and return a logger with standard formatting.

    Supports both console and file logging with automatic log rotation.
    File logging path can be configured via PHONE_AGENT_LOG_FILE env var.

    Args:
        name: Logger name.
        level: Logging level.
        log_file: Path to log file (overrides env var if specified).
        max_bytes: Maximum size of each log file before rotation (default: 10MB).
        backup_count: Number of backup log files to keep (default: 5).

    Returns:
        Configured logger instance.

    Environment Variables:
        PHONE_AGENT_LOG_FILE: Path to log file (default: ./logs/phone_agent.log)
        PHONE_AGENT_LOG_LEVEL: Logging level (DEBUG/INFO/WARNING/ERROR, default: INFO)
    """
    logger = logging.getLogger(name)

    # Read log level from env
    log_level_str = os.getenv("PHONE_AGENT_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        # Standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional, with rotation)
        if log_file is None:
            log_file = os.getenv("PHONE_AGENT_LOG_FILE")

        if log_file:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"File logging enabled: {log_file} (max {max_bytes//1024//1024}MB, {backup_count} backups)")

    return logger

# Default logger
logger = setup_logger()

"""Logging configuration and setup."""
from __future__ import annotations

import sys
from pathlib import Path
from loguru import logger

from ..core.config import settings


def setup_logging():
    """Setup application logging configuration."""
    # Remove default logger
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # File logging
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
        compression="gzip"
    )
    
    # Error file logging
    error_log_file = log_file.parent / "errors.log"
    logger.add(
        error_log_file,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 week",
        retention="12 weeks",
        compression="gzip"
    )
    
    logger.info("Logging setup completed")


def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)

"""
Structured logging module for SentraScan Platform.

Uses structlog library with JSON output formatter for consistent, machine-readable logs.
Supports multiple output destinations (stdout, stderr, file) and log levels.
"""

import os
import sys
import structlog
from logging import StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def configure_logging(
    log_level: Optional[str] = None,
    log_dir: Optional[str] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> structlog.BoundLogger:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
        log_dir: Directory for log files. Defaults to /app/logs or ./logs.
        enable_file_logging: Whether to write logs to files.
        enable_console_logging: Whether to write logs to console.
    
    Returns:
        Configured structlog logger instance.
    """
    # Get log level from environment or use default
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Determine log directory
    if log_dir is None:
        if os.path.exists("/app"):
            log_dir = "/app/logs"
        else:
            log_dir = "./logs"
    
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add JSON renderer for structured output
    processors.append(structlog.processors.JSONRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    
    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler (stdout for info and below, stderr for warning and above)
    if enable_console_logging:
        # Info and below go to stdout
        info_handler = StreamHandler(sys.stdout)
        info_handler.setLevel(logging.DEBUG)
        info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
        info_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=processors[:-1],  # All except JSONRenderer
            )
        )
        root_logger.addHandler(info_handler)
        
        # Warning and above go to stderr
        error_handler = StreamHandler(sys.stderr)
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=processors[:-1],
            )
        )
        root_logger.addHandler(error_handler)
    
    # File handlers for different log levels
    if enable_file_logging:
        # Info level file handler
        info_file = log_path / "app-info.log"
        info_file_handler = RotatingFileHandler(
            str(info_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.addFilter(lambda record: record.levelno == logging.INFO)
        info_file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=processors[:-1],
            )
        )
        root_logger.addHandler(info_file_handler)
        
        # Debug level file handler
        debug_file = log_path / "app-debug.log"
        debug_file_handler = RotatingFileHandler(
            str(debug_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
        debug_file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=processors[:-1],
            )
        )
        root_logger.addHandler(debug_file_handler)
        
        # Error level file handler
        error_file = log_path / "app-error.log"
        error_file_handler = RotatingFileHandler(
            str(error_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=processors[:-1],
            )
        )
        root_logger.addHandler(error_file_handler)
    
    # Return configured logger
    return structlog.get_logger()


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name. If None, returns the default logger.
    
    Returns:
        Structlog logger instance.
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


# Initialize logging on module import (lazy initialization)
_logger = None

def _get_default_logger():
    """Get or create default logger (lazy initialization)"""
    global _logger
    if _logger is None:
        _logger = configure_logging()
    return _logger


"""
Structured logging configuration with OTEL hooks
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
from pathlib import Path

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry, default=str)

def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """Setup structured logging"""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with structured format
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    logging.info("Structured logging configured", extra={"level": level})

class Logger:
    """Application logger with context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """Set logging context"""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear logging context"""
        self.context.clear()

    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method"""
        extra = {**self.context, **kwargs}
        getattr(self.logger, level)(message, extra={"extra": extra})

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def exception(self, message: str, **kwargs):
        self._log("exception", message, **kwargs)

def get_logger(name: str) -> Logger:
    """Get logger instance"""
    return Logger(name)
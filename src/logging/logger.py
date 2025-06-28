"""
Logging configuration and setup for the RAG ingestion system.
"""
import logging
import sys
from typing import Optional


class LoggerFactory:
    """Factory for creating and configuring loggers."""
    
    @staticmethod
    def create_logger(name: str, debug: bool = False, log_file: Optional[str] = None) -> logging.Logger:
        """
        Create and configure a logger with the specified settings.
        
        Args:
            name: The name of the logger
            debug: Whether to enable debug logging
            log_file: Optional file path for logging to file
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Avoid adding handlers multiple times
        if logger.handlers:
            return logger
            
        # Set log level
        level = logging.DEBUG if debug else logging.INFO
        logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger


class IngestionLogger:
    """Specialized logger for ingestion operations."""
    
    def __init__(self, debug: bool = False):
        self.logger = LoggerFactory.create_logger("ingestion", debug)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message) 
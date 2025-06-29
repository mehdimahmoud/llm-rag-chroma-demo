import logging
import os
import sys

from typing import Optional

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer, StackInfoRenderer, TimeStamper, format_exc_info
from structlog.stdlib import LoggerFactory as StructlogLoggerFactory


class StructLogConfig:
    """Configuration for structlog with level-based formatting."""

    @staticmethod
    def configure(
        debug: bool = False, json_output: bool = False, log_file: Optional[str] = None
    ):
        """
        Configure structlog with level-based formatting.

        Args:
            debug: Whether to enable debug logging
            json_output: Whether to output JSON format (for production)
            log_file: Optional file path for logging to file
        """
        # Determine processors based on configuration
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            TimeStamper(fmt="iso"),
            StackInfoRenderer(),
            format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        # Add output renderer
        if json_output:
            processors.append(JSONRenderer())
        else:
            processors.append(ConsoleRenderer())

        # Configure structlog
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=StructlogLoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Configure standard library logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.DEBUG if debug else logging.INFO,
        )

        # Add file handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG if debug else logging.INFO)

            # Create file formatter
            if json_output:
                file_formatter = logging.Formatter(
                    "%(message)s"
                )  # JSON is already formatted
            else:
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

            file_handler.setFormatter(file_formatter)

            # Add handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)

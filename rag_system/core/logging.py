"""
Structured logging configuration for the RAG system.

This module provides logging with structured output, performance monitoring,
and correlation IDs.
"""

import logging
import sys
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
    cast,
)

import structlog
from structlog.stdlib import LoggerFactory

# Type alias for structlog processors
StructlogProcessor = Callable[
    [Any, str, MutableMapping[str, Any]],
    Union[Mapping[str, Any], str, bytes, bytearray, Tuple[Any, ...]],
]


def setup_logging(
    log_level: str,
    log_format: str,
    enable_console: bool = True,
    enable_file: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or text)
        enable_console: Enable console logging
        enable_file: Enable file logging
        log_file: Log file path
    """
    if not log_level or not log_format:
        raise ValueError(
            "log_level and log_format must be provided to setup_logging"
        )
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    processors: List[StructlogProcessor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add output formatting
    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structured logger
    """
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


def log_performance(
    logger: structlog.stdlib.BoundLogger, operation: str, **kwargs: Any
) -> None:
    """
    Log performance metrics for operations.

    Args:
        logger: Structured logger instance
        operation: Operation name
        **kwargs: Additional performance metrics
    """
    logger.info("Performance metric", operation=operation, **kwargs)


def log_error(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log errors with structured context.

    Args:
        logger: Structured logger instance
        error: Exception that occurred
        context: Additional context information
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if context:
        error_context.update(context)

    logger.error("Error occurred", **error_context, exc_info=True)

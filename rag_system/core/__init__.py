"""
Core functionality for the RAG system.

This package contains the fundamental components including configuration,
logging, and base classes.
"""

from .config import Settings
from .logging import setup_logging

__all__ = ["Settings", "setup_logging"]

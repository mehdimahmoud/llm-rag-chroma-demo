"""
RAG (Retrieval-Augmented Generation) System.

A production-ready implementation using LangChain and ChromaDB for document
ingestion, vector storage, and intelligent querying.
"""

__version__ = "1.0.0"
__author__ = "Mehdi Khoder"
__email__ = "xxxxxxxxxxxx@gmail.com"

from .core.config import Settings
from .core.logging import setup_logging

__all__ = ["Settings", "setup_logging"]

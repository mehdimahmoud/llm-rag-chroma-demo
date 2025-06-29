"""
Abstract interfaces for the ingestion system.
"""
# Re-export all interfaces for backward compatibility
from .interfaces.document_loader import DocumentLoader
from .interfaces.embedding_generator import EmbeddingGenerator
from .interfaces.ingestion_orchestrator import IngestionOrchestrator
from .interfaces.text_chunker import TextChunker
from .interfaces.text_extractor import TextExtractor
from .interfaces.user_interface import UserInterface
from .interfaces.vector_store import VectorStore

__all__ = [
    "DocumentLoader",
    "TextExtractor",
    "TextChunker",
    "EmbeddingGenerator",
    "VectorStore",
    "UserInterface",
    "IngestionOrchestrator",
]

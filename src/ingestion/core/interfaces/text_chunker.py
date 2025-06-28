"""
Abstract interface for chunking text into smaller pieces.
"""
from abc import ABC, abstractmethod
from typing import List

from ...models.document import DocumentChunk, IngestionConfig


class TextChunker(ABC):
    """Abstract interface for chunking text into smaller pieces."""
    
    @abstractmethod
    def chunk_text(self, text: str, config: IngestionConfig, source_file: str) -> List[DocumentChunk]:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Text to chunk
            config: Ingestion configuration
            source_file: Source filename for the chunks
            
        Returns:
            List of text chunks
        """
        pass 
"""
Abstract interface for generating embeddings from text chunks.
"""
from abc import ABC, abstractmethod
from typing import List

from ...models.document import DocumentChunk


class EmbeddingGenerator(ABC):
    """Abstract interface for generating embeddings from text chunks."""

    @abstractmethod
    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[List[float]]:
        """
        Generate embeddings for text chunks.

        Args:
            chunks: List of text chunks

        Returns:
            List of embeddings (vectors)
        """
        pass

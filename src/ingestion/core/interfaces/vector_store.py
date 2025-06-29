"""
Abstract interface for vector storage operations.
"""
from abc import ABC, abstractmethod
from typing import List

from ...models.document import DocumentChunk


class VectorStore(ABC):
    """Abstract interface for vector storage operations."""

    @abstractmethod
    def add_documents(
        self, chunks: List[DocumentChunk], embeddings: List[List[float]]
    ) -> bool:
        """
        Add documents and their embeddings to the vector store.

        Args:
            chunks: List of document chunks
            embeddings: List of embeddings

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def delete_documents_by_source(self, source: str) -> int:
        """
        Delete all documents with the given source.

        Args:
            source: Source filename

        Returns:
            Number of documents deleted
        """
        pass

    @abstractmethod
    def document_exists(self, source: str) -> bool:
        """
        Check if a document with the given source exists.

        Args:
            source: Source filename

        Returns:
            True if document exists
        """
        pass

    @abstractmethod
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the store.

        Returns:
            Number of documents
        """
        pass

    @abstractmethod
    def get_all_document_sources(self) -> List[str]:
        """
        Get all unique document sources in the collection.

        Returns:
            List of source filenames
        """
        pass

    @abstractmethod
    def clear_all_documents(self) -> int:
        """
        Clear all documents from the vector store.

        Returns:
            Number of documents deleted
        """
        pass

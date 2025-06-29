"""
Abstract interface for extracting text from documents.
"""
from abc import ABC, abstractmethod

from ...models.document import Document


class TextExtractor(ABC):
    """Abstract interface for extracting text from documents."""

    @abstractmethod
    def extract_text(self, document: Document) -> str:
        """
        Extract text from a document.

        Args:
            document: Document to extract text from

        Returns:
            Extracted text
        """
        pass

    @abstractmethod
    def supports_document(self, document: Document) -> bool:
        """
        Check if this extractor supports the given document type.

        Args:
            document: Document to check

        Returns:
            True if the document type is supported
        """
        pass

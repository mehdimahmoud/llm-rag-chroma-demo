"""
Abstract interface for loading documents from various sources.
"""
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from ...models.document import Document, IngestionConfig


class DocumentLoader(ABC):
    """Abstract interface for loading documents from various sources."""
    
    @abstractmethod
    def load_documents(self, config: IngestionConfig) -> List[Document]:
        """
        Load documents from the configured source.
        
        Args:
            config: Ingestion configuration
            
        Returns:
            List of loaded documents
        """
        pass
    
    @abstractmethod
    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this loader supports the given file type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file type is supported
        """
        pass 
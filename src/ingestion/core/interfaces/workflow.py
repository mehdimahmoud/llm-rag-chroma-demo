"""
Abstract interface for ingestion workflows.
"""
from abc import ABC, abstractmethod
from typing import List

from ...core.models.menu_context import MenuContext
from ...models.document import Document, IngestionConfig, IngestionResult


class IngestionWorkflow(ABC):
    """Abstract interface for ingestion workflows."""

    @abstractmethod
    def execute(
        self, documents: List[Document], config: IngestionConfig
    ) -> IngestionResult:
        """
        Execute the complete ingestion workflow.

        Args:
            documents: List of documents to process
            config: Ingestion configuration

        Returns:
            Ingestion result
        """
        pass

    @abstractmethod
    def create_menu_context(self, documents: List[Document]) -> MenuContext:
        """
        Create menu context from documents.

        Args:
            documents: List of documents

        Returns:
            Menu context
        """
        pass

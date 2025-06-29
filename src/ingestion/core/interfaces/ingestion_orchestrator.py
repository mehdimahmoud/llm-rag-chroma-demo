"""
Abstract interface for orchestrating the ingestion process.
"""
from abc import ABC, abstractmethod

from ...models.document import IngestionConfig, IngestionResult


class IngestionOrchestrator(ABC):
    """Abstract interface for orchestrating the ingestion process."""

    @abstractmethod
    def ingest_documents(self, config: IngestionConfig) -> IngestionResult:
        """
        Orchestrate the complete ingestion process.

        Args:
            config: Ingestion configuration

        Returns:
            Ingestion result
        """
        pass

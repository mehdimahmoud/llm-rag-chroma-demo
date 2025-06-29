"""
Abstract interface for building ingestion workflows.
"""
from abc import ABC, abstractmethod
from typing import List

from ...core.interfaces.document_processor import DocumentProcessor
from ...core.interfaces.menu_strategy import MenuStrategy
from ...core.interfaces.workflow import IngestionWorkflow


class WorkflowBuilder(ABC):
    """Abstract interface for building ingestion workflows."""

    @abstractmethod
    def with_menu_strategy(self, strategy: MenuStrategy) -> "WorkflowBuilder":
        """Add a menu strategy to the workflow."""
        pass

    @abstractmethod
    def with_processor_chain(
        self, processors: List[DocumentProcessor]
    ) -> "WorkflowBuilder":
        """Add a processor chain to the workflow."""
        pass

    @abstractmethod
    def with_dependencies(self, **dependencies) -> "WorkflowBuilder":
        """Add dependencies to the workflow."""
        pass

    @abstractmethod
    def build(self) -> IngestionWorkflow:
        """Build and return the configured workflow."""
        pass

from ...models.document import Document, DocumentChunk, IngestionConfig

"""
Abstract interface for document processing pipeline components.
"""


class ProcessingResult:
    """Result of a document processing step."""

    def __init__(
        self, success: bool, data: Optional[object] = None, error: Optional[str] = None
    ):
        self.success = success
        self.data = data
        self.error = error


class DocumentProcessor(ABC):
    """Abstract interface for document processing pipeline components."""

    def __init__(self, next_processor: Optional["DocumentProcessor"] = None):
        self.next_processor = next_processor

    @abstractmethod
    def process(self, document: Document, config: IngestionConfig) -> ProcessingResult:
        """
        Process a document and optionally pass to next processor.

        Args:
            document: Document to process
            config: Ingestion configuration

        Returns:
            Processing result
        """
        pass

    def set_next(self, processor: "DocumentProcessor") -> "DocumentProcessor":
        """Set the next processor in the chain."""
        self.next_processor = processor
        return processor

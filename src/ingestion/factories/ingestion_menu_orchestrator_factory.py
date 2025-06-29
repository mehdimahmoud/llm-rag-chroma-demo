"""
Factory for creating IngestionMenuOrchestrator instances with proper dependency injection.
"""
from typing import Optional
import structlog

from ...ingestion.core.interfaces import UserInterface
from ...chroma.vector_store import ChromaDBVectorStore
from ..orchestrators.ingestion_menu_orchestrator import IngestionMenuOrchestrator
from ..builders.ingestion_menu_builder import IngestionMenuBuilder
from ..services.document_loader import FileSystemDocumentLoader
from ..services.text_extractor_factory import TextExtractorFactory
from ..services.text_chunker import ParagraphTextChunker
from ...embeddings.embedding_generator import SentenceTransformerEmbeddingGenerator
from ...menu.orchestrators.menu_orchestrator import MenuOrchestrator
from ..core.interfaces import DocumentLoader, TextChunker, EmbeddingGenerator


class IngestionMenuOrchestratorFactory:
    """Factory for creating IngestionMenuOrchestrator instances."""
    
    def __init__(self, logger=None):
        """
        Initialize the factory.
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or structlog.get_logger("ingestion_menu_orchestrator_factory")
    
    def create_orchestrator(
        self,
        user_interface: UserInterface,
        vector_store: ChromaDBVectorStore,
        data_directory: str = "data",
        document_loader: Optional[DocumentLoader] = None,
        text_extractor_factory: Optional[TextExtractorFactory] = None,
        text_chunker: Optional[TextChunker] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        menu_builder: Optional[IngestionMenuBuilder] = None,
        menu_orchestrator: Optional[MenuOrchestrator] = None,
    ) -> IngestionMenuOrchestrator:
        """
        Create an IngestionMenuOrchestrator with proper dependency injection.
        
        Args:
            user_interface: User interface service
            vector_store: Vector store service
            data_directory: Directory containing documents to process
            document_loader: Document loader service (optional)
            text_extractor_factory: Text extractor factory (optional)
            text_chunker: Text chunker service (optional)
            embedding_generator: Embedding generator service (optional)
            menu_builder: Menu builder (optional)
            menu_orchestrator: Menu orchestrator (optional)
            
        Returns:
            Configured IngestionMenuOrchestrator instance
        """
        # Create default dependencies if not provided
        if document_loader is None:
            document_loader = FileSystemDocumentLoader(data_directory)
            self.logger.debug("Created default FileSystemDocumentLoader", data_directory=data_directory)
        
        if text_extractor_factory is None:
            text_extractor_factory = TextExtractorFactory(self.logger)
            self.logger.debug("Created default TextExtractorFactory")
        
        if text_chunker is None:
            text_chunker = ParagraphTextChunker()
            self.logger.debug("Created default ParagraphTextChunker")
        
        if embedding_generator is None:
            embedding_generator = SentenceTransformerEmbeddingGenerator()
            self.logger.debug("Created default SentenceTransformerEmbeddingGenerator")
        
        if menu_builder is None:
            menu_builder = IngestionMenuBuilder()
            self.logger.debug("Created default IngestionMenuBuilder")
        
        if menu_orchestrator is None:
            menu_orchestrator = MenuOrchestrator(user_interface, self.logger)
            self.logger.debug("Created default MenuOrchestrator")
        
        # Create and return the orchestrator
        orchestrator = IngestionMenuOrchestrator(
            user_interface=user_interface,
            vector_store=vector_store,
            document_loader=document_loader,
            text_extractor_factory=text_extractor_factory,
            text_chunker=text_chunker,
            embedding_generator=embedding_generator,
            menu_builder=menu_builder,
            menu_orchestrator=menu_orchestrator,
            _logger=self.logger
        )
        
        self.logger.info("Created IngestionMenuOrchestrator with dependency injection")
        return orchestrator
    
    def create_orchestrator_with_defaults(
        self,
        user_interface: UserInterface,
        vector_store: ChromaDBVectorStore,
        data_directory: str = "data"
    ) -> IngestionMenuOrchestrator:
        """
        Create an IngestionMenuOrchestrator with all default dependencies.
        
        Args:
            user_interface: User interface service
            vector_store: Vector store service
            data_directory: Directory containing documents to process
            
        Returns:
            Configured IngestionMenuOrchestrator instance with default dependencies
        """
        return self.create_orchestrator(
            user_interface=user_interface,
            vector_store=vector_store,
            data_directory=data_directory
        ) 
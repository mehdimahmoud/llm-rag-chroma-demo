"""
Example demonstrating dependency injection with IngestionMenuOrchestrator.

This example shows how to:
1. Use the factory for clean dependency injection
2. Mock dependencies for testing
3. Configure different implementations
"""
import structlog
from unittest.mock import Mock, MagicMock

from src.ingestion.factories.ingestion_menu_orchestrator_factory import IngestionMenuOrchestratorFactory
from src.ingestion.core.interfaces import DocumentLoader, TextChunker, EmbeddingGenerator
from src.ingestion.models.document import Document, IngestionConfig
from src.ingestion.models.enums import FileType


def example_with_defaults():
    """Example using the factory with default dependencies."""
    print("=== Example 1: Using Factory with Defaults ===")
    
    # Create factory
    factory = IngestionMenuOrchestratorFactory()
    
    # Mock dependencies (in real usage, these would be actual implementations)
    mock_user_interface = Mock()
    mock_vector_store = Mock()
    
    # Create orchestrator with defaults
    orchestrator = factory.create_orchestrator_with_defaults(
        user_interface=mock_user_interface,
        vector_store=mock_vector_store,
        data_directory="data"
    )
    
    print(f"✅ Created orchestrator with default dependencies")
    print(f"   Document Loader: {type(orchestrator.document_loader).__name__}")
    print(f"   Text Chunker: {type(orchestrator.text_chunker).__name__}")
    print(f"   Embedding Generator: {type(orchestrator.embedding_generator).__name__}")
    print()


def example_with_custom_dependencies():
    """Example using the factory with custom dependencies."""
    print("=== Example 2: Using Factory with Custom Dependencies ===")
    
    # Create factory
    factory = IngestionMenuOrchestratorFactory()
    
    # Create custom mock dependencies
    custom_document_loader = Mock(spec=DocumentLoader)
    custom_text_chunker = Mock(spec=TextChunker)
    custom_embedding_generator = Mock(spec=EmbeddingGenerator)
    
    # Mock dependencies
    mock_user_interface = Mock()
    mock_vector_store = Mock()
    
    # Create orchestrator with custom dependencies
    orchestrator = factory.create_orchestrator(
        user_interface=mock_user_interface,
        vector_store=mock_vector_store,
        document_loader=custom_document_loader,
        text_chunker=custom_text_chunker,
        embedding_generator=custom_embedding_generator
    )
    
    print(f"✅ Created orchestrator with custom dependencies")
    print(f"   Document Loader: {type(orchestrator.document_loader).__name__}")
    print(f"   Text Chunker: {type(orchestrator.text_chunker).__name__}")
    print(f"   Embedding Generator: {type(orchestrator.embedding_generator).__name__}")
    print()


def example_for_testing():
    """Example showing how dependency injection makes testing easier."""
    print("=== Example 3: Testing with Dependency Injection ===")
    
    # Create factory
    factory = IngestionMenuOrchestratorFactory()
    
    # Create test doubles (mocks)
    mock_user_interface = Mock()
    mock_vector_store = Mock()
    mock_document_loader = Mock(spec=DocumentLoader)
    mock_text_chunker = Mock(spec=TextChunker)
    mock_embedding_generator = Mock(spec=EmbeddingGenerator)
    
    # Configure mocks for testing
    test_document = Document(
        file_path="test.txt",
        filename="test.txt",
        file_type=FileType.TXT.value,
        size=100
    )
    
    mock_document_loader.load_documents.return_value = [test_document]
    mock_text_chunker.chunk_text.return_value = ["chunk1", "chunk2"]
    mock_embedding_generator.generate_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
    mock_vector_store.add_documents.return_value = True
    
    # Create orchestrator for testing
    orchestrator = factory.create_orchestrator(
        user_interface=mock_user_interface,
        vector_store=mock_vector_store,
        document_loader=mock_document_loader,
        text_chunker=mock_text_chunker,
        embedding_generator=mock_embedding_generator
    )
    
    print(f"✅ Created orchestrator for testing")
    print(f"   All dependencies are mocks: {all(isinstance(dep, Mock) for dep in [mock_document_loader, mock_text_chunker, mock_embedding_generator])}")
    print(f"   Easy to verify interactions and test behavior")
    print()


def example_hybrid_approach():
    """Example showing hybrid approach - some defaults, some custom."""
    print("=== Example 4: Hybrid Approach ===")
    
    # Create factory
    factory = IngestionMenuOrchestratorFactory()
    
    # Mock dependencies
    mock_user_interface = Mock()
    mock_vector_store = Mock()
    
    # Custom document loader for specific data source
    custom_document_loader = Mock(spec=DocumentLoader)
    custom_document_loader.load_documents.return_value = []
    
    # Use defaults for other dependencies
    orchestrator = factory.create_orchestrator(
        user_interface=mock_user_interface,
        vector_store=mock_vector_store,
        document_loader=custom_document_loader  # Custom
        # text_chunker, embedding_generator, etc. will use defaults
    )
    
    print(f"✅ Created orchestrator with hybrid approach")
    print(f"   Document Loader: Custom ({type(orchestrator.document_loader).__name__})")
    print(f"   Text Chunker: Default ({type(orchestrator.text_chunker).__name__})")
    print(f"   Embedding Generator: Default ({type(orchestrator.embedding_generator).__name__})")
    print()


if __name__ == "__main__":
    print("🚀 Dependency Injection Examples")
    print("=" * 50)
    print()
    
    example_with_defaults()
    example_with_custom_dependencies()
    example_for_testing()
    example_hybrid_approach()
    
    print("🎯 Benefits of Dependency Injection:")
    print("   ✅ Loose coupling between components")
    print("   ✅ Easy to test with mocks")
    print("   ✅ Flexible configuration")
    print("   ✅ Better separation of concerns")
    print("   ✅ Easier to swap implementations") 
"""
Main script for the RAG document ingestion system.
"""
import logging
import sys
from pathlib import Path
from typing import Optional, Set

from .logging.logger import LoggerFactory, IngestionLogger
from .ingestion.models.document import IngestionConfig
from .ingestion.models.enums import FileType
from .ingestion.services.document_loader import FileSystemDocumentLoader
from .ingestion.services.text_extractor_factory import TextExtractorFactory
from .ingestion.services.text_chunker import ParagraphTextChunker
from .ingestion.services.ingestion_orchestrator import DefaultIngestionOrchestrator
from .ingestion.services.user_interface import ConsoleUserInterface
from .embeddings.embedding_generator import SentenceTransformerEmbeddingGenerator
from .chromadb.vector_store import ChromaDBVectorStore


def create_config(file_types: Optional[Set[FileType]] = None, process_all: bool = True) -> IngestionConfig:
    """
    Create ingestion configuration with flexible file type options.
    
    Args:
        file_types: Set of allowed file types (e.g., {FileType.PDF, FileType.TXT})
        process_all: If True, process all supported types; if False, only process specified types
        
    Returns:
        IngestionConfig instance
    """
    data_dir = Path("data")
    
    if file_types is None:
        # Default: process all supported file types
        allowed_types = FileType.get_all_supported()
    else:
        # Process only specified file types
        allowed_types = file_types
    
    return IngestionConfig(
        data_dir=data_dir,
        interactive=True,
        debug=True,
        chunk_min_length=30,
        collection_name="hr_policies",
        allowed_file_types=allowed_types,
        process_all_supported=process_all
    )


def main():
    """Main entry point for the document ingestion system."""
    # Setup logging
    logger_factory = LoggerFactory()
    logger = logger_factory.create_logger("main", debug=True)
    ingestion_logger = IngestionLogger(debug=True)
    
    try:
        logger.info("Starting RAG document ingestion system")
        
        # Configuration examples - choose one:
        
        # Option 1: Process all supported file types
        config = create_config()
        logger.info("Configuration: Processing all supported file types")
        
        # Option 2: Process only PDF files
        # config = create_config(file_types={FileType.PDF}, process_all=False)
        # logger.info("Configuration: Processing PDF files only")
        
        # Option 3: Process only text files
        # config = create_config(file_types={FileType.TXT}, process_all=False)
        # logger.info("Configuration: Processing text files only")
        
        # Option 4: Process specific file types
        # config = create_config(file_types={FileType.PDF, FileType.TXT}, process_all=False)
        # logger.info("Configuration: Processing PDF and text files only")
        
        logger.info(f"Allowed file types: {config.get_allowed_file_types_str()}")
        
        # Initialize services
        logger.info("Initializing services...")
        
        # Document loader
        document_loader = FileSystemDocumentLoader(data_directory="data")
        
        # Text extractor factory
        text_extractor_factory = TextExtractorFactory(logger=ingestion_logger)
        
        # Text chunker
        text_chunker = ParagraphTextChunker()
        
        # Embedding generator
        embedding_generator = SentenceTransformerEmbeddingGenerator()
        
        # Vector store
        vector_store = ChromaDBVectorStore(
            persist_dir="./chroma_db",
            collection_name=config.collection_name,
            logger=ingestion_logger
        )
        
        # User interface
        user_interface = ConsoleUserInterface()
        
        # Ingestion orchestrator
        orchestrator = DefaultIngestionOrchestrator(
            document_loader=document_loader,
            text_extractor_factory=text_extractor_factory,
            text_chunker=text_chunker,
            embedding_generator=embedding_generator,
            vector_store=vector_store,
            user_interface=user_interface
        )
        
        logger.info("All services initialized successfully")
        
        # Run ingestion
        logger.info("Starting document ingestion...")
        result = orchestrator.ingest_documents(config)
        
        # Display results
        print("\n" + "="*50)
        print("INGESTION RESULTS")
        print("="*50)
        print(f"Success: {result.success}")
        print(f"Documents processed: {result.documents_processed}")
        print(f"Chunks ingested: {result.chunks_ingested}")
        
        if result.has_errors:
            print(f"\nErrors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.has_warnings:
            print(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.success:
            print(f"\n✅ Successfully ingested {result.documents_processed} documents with {result.chunks_ingested} chunks")
        else:
            print(f"\n❌ Ingestion failed: {result.errors[0] if result.errors else 'Unknown error'}")
        
        print("="*50)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
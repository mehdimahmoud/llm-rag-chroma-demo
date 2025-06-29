"""
Main script for the RAG document ingestion system.
"""
import os
import sys
from pathlib import Path
from typing import Optional, Set

import structlog

from .chroma.vector_store import ChromaDBVectorStore
from .embeddings.embedding_generator import SentenceTransformerEmbeddingGenerator
from .ingestion.models.document import IngestionConfig
from .ingestion.models.enums import FileType
from .ingestion.orchestrators.ingestion_menu_orchestrator import (
    IngestionMenuOrchestrator,
)
from .ingestion.services.document_loader import FileSystemDocumentLoader
from .ingestion.services.text_chunker import ParagraphTextChunker
from .ingestion.services.text_extractor_factory import TextExtractorFactory
from .ingestion.services.user_interface import ConsoleUserInterface
from .logutils.logger import StructLogConfig


def create_config(
    file_types: Optional[Set[FileType]] = None,
    process_all: bool = True,
    debug: bool = False,
) -> IngestionConfig:
    """
    Create ingestion configuration with flexible file type options.

    Args:
        file_types: Set of allowed file types (e.g., {FileType.PDF, FileType.TXT})
        process_all: If True, process all supported types; if False, only process specified types
        debug: Whether to enable debug mode

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
        debug=debug,
        chunk_min_length=30,
        collection_name="hr_policies",
        allowed_file_types=allowed_types,
        process_all_supported=process_all,
    )


def main():
    """Main entry point for the document ingestion system."""
    # Configuration - set debug mode here
    debug_mode = False  # Set to True for debug output

    # Setup logging with structlog
    StructLogConfig.configure(debug=debug_mode)
    logger = structlog.get_logger("main")
    ingestion_logger = structlog.get_logger("ingestion")

    try:
        logger.info("Starting RAG document ingestion system")

        # Ask user which orchestrator to use
        print("\n" + "=" * 60)
        print("RAG DOCUMENT INGESTION SYSTEM")
        print("=" * 60)
        print("\nChoose orchestrator type:")
        print("1. Generic menu orchestrator (new)")
        print("2. Exit")

        while True:
            choice = input("\nEnter your choice (1-2): ").strip()
            if choice in ["1", "2"]:
                break
            print("Invalid choice. Please enter 1 or 2.")

        if choice == "2":
            logger.info("User chose to exit")
            return

        # Configuration examples - choose one:

        # Option 1: Process all supported file types
        config = create_config(debug=debug_mode)
        logger.info("Configuration: Processing all supported file types")

        # Option 2: Process only PDF files
        # config = create_config(file_types={FileType.PDF}, process_all=False, debug=debug_mode)
        # logger.info("Configuration: Processing PDF files only")

        # Option 3: Process only text files
        # config = create_config(file_types={FileType.TXT}, process_all=False, debug=debug_mode)
        # logger.info("Configuration: Processing text files only")

        # Option 4: Process specific file types
        # config = create_config(file_types={FileType.PDF, FileType.TXT}, process_all=False, debug=debug_mode)
        # logger.info("Configuration: Processing PDF and text files only")

        logger.info(f"Allowed file types: {config.get_allowed_file_types_str()}")

        # Initialize services
        logger.info("Initializing services...")

        # Document loader
        _document_loader = FileSystemDocumentLoader(data_directory="data")

        # Text extractor factory
        _text_extractor_factory = TextExtractorFactory(logger=ingestion_logger)

        # Text chunker
        _text_chunker = ParagraphTextChunker()

        # Embedding generator
        _embedding_generator = SentenceTransformerEmbeddingGenerator()

        # Vector store
        vector_store = ChromaDBVectorStore(
            persist_dir="./chroma_db",
            collection_name=config.collection_name,
            logger=ingestion_logger,
        )

        # User interface
        user_interface = ConsoleUserInterface()

        # Choose orchestrator based on user preference
        logger.info("Using generic menu orchestrator")
        orchestrator = IngestionMenuOrchestrator(
            user_interface=user_interface,
            vector_store=vector_store,
            logger=ingestion_logger,
        )

        # Run generic menu orchestrator
        result = orchestrator.ingest_documents(config)

        # Display results
        print("\n" + "=" * 50)
        print("GENERIC MENU SYSTEM RESULTS")
        print("=" * 50)
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

        print("=" * 50)

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

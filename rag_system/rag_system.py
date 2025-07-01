"""
Main RAG system orchestrator.

This module provides the main interface for the RAG system, coordinating
document ingestion, processing, and querying operations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

# from .core.config import settings
from .core.logging import get_logger
from .ingestion.document_loader import DocumentLoader
from .ingestion.text_processor import TextProcessor
from .ingestion.vector_store import VectorStore

logger = get_logger(__name__)


class RAGSystem:
    """Main RAG system orchestrator."""

    def __init__(self):
        """Initialize the RAG system with all components."""
        logger.info("Initializing RAG system")

        # Initialize components
        self.document_loader = DocumentLoader()
        self.text_processor = TextProcessor()

        # Create embedding function for vector store
        embedding_function = self.text_processor.embedding_model
        print(
            "Has embed_documents: " f"{hasattr(embedding_function, 'embed_documents')}",
        )

        self.vector_store = VectorStore(embedding_function=embedding_function)

        logger.info("RAG system initialized successfully")

    def ingest_documents(
        self, file_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ingest documents into the RAG system.

        Args:
            file_paths: Optional list of specific file paths to process

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info("Starting document ingestion")

        try:
            # Load documents
            if file_paths:
                # Load specific files
                documents = []
                for file_path in file_paths:
                    doc = self.document_loader.load_document(Path(file_path))
                    documents.extend(doc)
            else:
                # Load all documents
                documents = self.document_loader.load_all_documents()

            if not documents:
                logger.warning("No documents found for ingestion")
                return {"status": "no_documents", "documents_processed": 0}

            # Process documents (chunk and embed)
            chunked_docs, embeddings = self.text_processor.process_documents(
                documents,
            )

            # Store in vector database
            doc_ids = self.vector_store.add_documents(chunked_docs, embeddings)

            stats = {
                "status": "success",
                "original_documents": len(documents),
                "chunked_documents": len(chunked_docs),
                "embeddings_generated": len(embeddings),
                "documents_stored": len(doc_ids),
            }

            logger.info("Document ingestion completed", stats=stats)
            return stats

        except Exception as e:
            logger.error("Document ingestion failed", error=str(e))
            raise

    def query(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        include_scores: bool = False,
    ) -> List[Document] | List[tuple[Document, float]]:
        """
        Query the RAG system.

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            include_scores: Whether to include similarity scores

        Returns:
            List of documents or (document, score) tuples
        """
        logger.info("Processing query", query=query, k=k)

        try:
            if include_scores:
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter,
                )
            else:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter,
                )

            logger.info("Query completed", results_count=len(results))
            return results

        except Exception as e:
            logger.error("Query failed", query=query, error=str(e))
            raise

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.

        Returns:
            Dictionary with system statistics
        """
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats()

            # Get file type summary
            file_summary = self.document_loader.get_file_type_summary()

            # Get document sources
            sources = self.vector_store.get_document_sources()

            stats = {
                "vector_store": vector_stats,
                "file_types": file_summary,
                "document_sources": sources,
                "total_sources": len(sources),
            }

            logger.info("System statistics retrieved", stats=stats)
            return stats

        except Exception as e:
            logger.error("Failed to get system statistics", error=str(e))
            raise

    def clear_database(self) -> None:
        """Clear all data from the vector database."""
        logger.info("Clearing vector database")

        try:
            self.vector_store.delete_collection()
            logger.info("Vector database cleared successfully")
            # Re-instantiate VectorStore to ensure a new collection is created and referenced
            self.vector_store = VectorStore(
                embedding_function=self.text_processor.embedding_model
            )
        except Exception as e:
            logger.error("Failed to clear vector database", error=str(e))
            raise

    def get_document_sources(self) -> List[str]:
        """
        Get list of document sources in the database.

        Returns:
            List of source file paths
        """
        return self.vector_store.get_document_sources()

    def get_supported_files(self) -> List[str]:
        """
        Get list of supported files in the data directory.

        Returns:
            List of file paths
        """
        files = self.document_loader.get_supported_files()
        return [str(f) for f in files]

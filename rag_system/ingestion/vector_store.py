"""
Vector store operations for document storage and retrieval.

This module provides a clean interface to ChromaDB for storing and
retrieving document embeddings with metadata.
"""

from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from ..core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Manages vector storage operations using ChromaDB."""

    def __init__(
        self,
        settings,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        embedding_function=None,
    ):
        """
        Initialize the vector store.

        Args:
            settings: Settings instance
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_function: Embedding function for the vector store
        """
        self.settings = settings
        self.persist_directory = str(
            persist_directory or settings.chroma_persist_directory
        )
        self.collection_name = collection_name or settings.collection_name
        self.embedding_function = embedding_function

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Initialize LangChain Chroma wrapper
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
        )

        logger.info(
            "Vector store initialized",
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )

    def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents to add
            embeddings: List of embedding vectors
            ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        if not documents:
            logger.warning("No documents provided for storage")
            return []

        if len(documents) != len(embeddings):
            raise ValueError(
                "Number of documents must match number of embeddings",
            )

        # Generate IDs if not provided
        if ids is None:
            ids = [
                f"doc_{i}_{hash(doc.page_content) % 1000000}"
                for i, doc in enumerate(documents)
            ]

        try:
            # Add documents to vector store
            self.vector_store.add_documents(
                documents=documents,
                ids=ids,
            )

            logger.info(
                "Documents added to vector store",
                document_count=len(documents),
                collection_name=self.collection_name,
            )

            return ids

        except Exception as e:
            logger.error(
                "Failed to add documents to vector store",
                error=str(e),
                document_count=len(documents),
            )
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Perform similarity search.

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of similar documents
        """
        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter,
            )

            logger.info(
                "Similarity search completed",
                query=query,
                results_count=len(results),
                k=k,
            )

            return results

        except Exception as e:
            logger.error("Similarity search failed", query=query, error=str(e))
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with scores.

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter,
            )

            logger.info(
                "Similarity search with scores completed",
                query=query,
                results_count=len(results),
                k=k,
            )

            return results

        except Exception as e:
            logger.error(
                "Similarity search with scores failed",
                query=query,
                error=str(e),
            )
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.client.get_collection(name=self.collection_name)
            count = collection.count()

            stats = {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
            }

            logger.info("Collection statistics retrieved", stats=stats)
            return stats

        except Exception as e:
            logger.error("Failed to get collection statistics", error=str(e))
            raise

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(
                "Collection deleted",
                collection_name=self.collection_name,
            )
        except Exception as e:
            logger.error("Failed to delete collection", error=str(e))
            raise

    def get_document_sources(self) -> List[str]:
        """
        Get list of unique document sources in the collection.

        Returns:
            List of unique source file paths
        """
        try:
            collection = self.client.get_collection(name=self.collection_name)
            results = collection.get(include=["metadatas"])

            sources = set()
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    if metadata and "source" in metadata:
                        sources.add(metadata["source"])

            sources_list = list(sources)
            logger.info(
                "Document sources retrieved",
                source_count=len(sources_list),
            )
            return sources_list

        except Exception as e:
            logger.error("Failed to get document sources", error=str(e))
            raise

"""
ChromaDB implementation of the VectorStore interface.
"""
import contextlib
import os

import chromadb
import structlog

from typing import Any, Dict, List

from ..ingestion.core.interfaces import VectorStore
from ..ingestion.models.document import DocumentChunk


class ChromaDBVectorStore(VectorStore):
    """ChromaDB implementation of the VectorStore interface."""

    def __init__(self, persist_dir: str, collection_name: str, logger=None):
        """
        Initialize ChromaDB vector store.

        Args:
            persist_dir: Directory to persist ChromaDB data
            collection_name: Name of the collection
            logger: Logger instance (structlog logger)
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.logger = structlog.get_logger("chroma_vector_store")

        # Create persist directory if it doesn't exist
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
            self.logger.info("Created ChromaDB directory", persist_dir=persist_dir)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)

        self.logger.info("ChromaDB initialized", collection_name=collection_name)

    def add_documents(
        self, chunks: List[DocumentChunk], embeddings: List[List[float]]
    ) -> bool:
        """
        Add documents and their embeddings to ChromaDB.

        Args:
            chunks: List of document chunks
            embeddings: List of embeddings

        Returns:
            True if successful
        """
        try:
            self.logger.debug("Starting database storage", chunk_count=len(chunks))

            # Prepare data for ChromaDB
            self.logger.debug("Preparing data for ChromaDB storage")
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = [dict(chunk.metadata) for chunk in chunks]

            self.logger.debug(
                "Data prepared",
                id_count=len(ids),
                document_count=len(documents),
                metadata_count=len(metadatas),
            )

            # Suppress ChromaDB warnings during addition
            with open(os.devnull, "w") as devnull:
                with contextlib.redirect_stderr(devnull):
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        embeddings=embeddings,  # type: ignore
                        metadatas=metadatas,  # type: ignore
                    )

            self.logger.debug(
                "Successfully stored chunks in ChromaDB", chunk_count=len(chunks)
            )
            return True

        except Exception as e:
            if "Add of existing embedding ID" in str(e):
                # Suppress this specific ChromaDB warning - it's harmless
                self.logger.debug("Suppressed ChromaDB warning", error=str(e))
                return True
            else:
                self.logger.error("Error adding documents to ChromaDB", error=str(e))
                return False

    def delete_documents_by_source(self, source: str) -> int:
        """
        Delete all documents with the given source.

        Args:
            source: Source filename

        Returns:
            Number of documents deleted
        """
        try:
            self.logger.info("Deleting documents by source", source=source)

            # Get all documents with the given source
            results = self.collection.get(where={"source": source})
            ids_to_delete = results.get("ids", [])

            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                self.logger.info(
                    "Deleted documents", source=source, count=len(ids_to_delete)
                )
                return len(ids_to_delete)
            else:
                self.logger.info("No documents found to delete", source=source)
                return 0

        except Exception as e:
            self.logger.error(
                "Error deleting documents by source", source=source, error=str(e)
            )
            return 0

    def document_exists(self, source: str) -> bool:
        """
        Check if a document with the given source exists.

        Args:
            source: Source filename

        Returns:
            True if document exists
        """
        try:
            results = self.collection.get(where={"source": source})
            exists = len(results.get("ids", [])) > 0
            self.logger.debug(
                "Checked document existence", source=source, exists=exists
            )
            return exists
        except Exception as e:
            self.logger.error(
                "Error checking document existence", source=source, error=str(e)
            )
            return False

    def get_document_count(self) -> int:
        """
        Get the total number of documents in the store.

        Returns:
            Number of documents
        """
        try:
            count = self.collection.count()
            self.logger.debug("Got document count", count=count)
            return count
        except Exception as e:
            self.logger.error("Error getting document count", error=str(e))
            return 0

    def get_all_document_sources(self) -> List[str]:
        """
        Get all unique document sources in the collection.

        Returns:
            List of source filenames
        """
        try:
            results = self.collection.get()
            sources = set()
            metadatas = results.get("metadatas", [])
            if metadatas:
                for metadata in metadatas:
                    if metadata and "source" in metadata:
                        sources.add(metadata["source"])

            source_list = list(sources)
            self.logger.debug("Got all document sources", source_count=len(source_list))
            return source_list
        except Exception as e:
            self.logger.error("Error getting document sources", error=str(e))
            return []

    def clear_all_documents(self) -> int:
        """
        Clear all documents from the vector store.

        Returns:
            Number of documents deleted
        """
        try:
            self.logger.info("Clearing all documents from vector store")
            count_before = self.collection.count()
            # Delete the collection using the client
            self.client.delete_collection(name=self.collection_name)
            # Re-create the collection for further use
            self.collection = self.client.get_or_create_collection(self.collection_name)
            self.logger.info("Cleared all documents", deleted_count=count_before)
            return count_before
        except Exception as e:
            self.logger.error("Error clearing all documents", error=str(e))
            return 0

    def get_collection_state(self) -> Dict[str, Any]:
        """
        Get the current state of the collection for debugging.

        Returns:
            Dictionary with collection state information
        """
        try:
            results = self.collection.get()
            return {
                "count": len(results.get("ids", [])),
                "ids": results.get("ids", []),
                "sources": self.get_all_document_sources(),
            }
        except Exception as e:
            self.logger.error(f"Error getting collection state: {e}")
            return {"count": 0, "ids": [], "sources": []}

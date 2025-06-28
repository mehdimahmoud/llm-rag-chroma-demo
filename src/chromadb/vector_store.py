"""
ChromaDB implementation of the VectorStore interface.
"""
import os
import time
import contextlib
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings

from ..ingestion.core.interfaces import VectorStore
from ..ingestion.models.document import DocumentChunk
from ..logging.logger import IngestionLogger


class ChromaDBVectorStore(VectorStore):
    """ChromaDB implementation of the VectorStore interface."""
    
    def __init__(self, persist_dir: str, collection_name: str, logger: IngestionLogger):
        """
        Initialize ChromaDB vector store.
        
        Args:
            persist_dir: Directory to persist ChromaDB data
            collection_name: Name of the collection
            logger: Logger instance
        """
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.logger = logger
        
        # Create persist directory if it doesn't exist
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
            self.logger.info(f"Created ChromaDB directory: {persist_dir}")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)
        
        self.logger.info(f"ChromaDB initialized with collection: {collection_name}")
    
    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> bool:
        """
        Add documents and their embeddings to ChromaDB.
        
        Args:
            chunks: List of document chunks
            embeddings: List of embeddings
            
        Returns:
            True if successful
        """
        try:
            # Prepare data for ChromaDB
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = [dict(chunk.metadata) for chunk in chunks]  # Convert to dict
            
            # Suppress ChromaDB warnings during addition
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull):
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        embeddings=embeddings,  # type: ignore
                        metadatas=metadatas  # type: ignore
                    )
            
            self.logger.debug(f"Added {len(chunks)} chunks to ChromaDB")
            return True
            
        except Exception as e:
            if "Add of existing embedding ID" in str(e):
                # Suppress this specific ChromaDB warning - it's harmless
                self.logger.debug(f"Suppressed ChromaDB warning: {e}")
                return True
            else:
                self.logger.error(f"Error adding documents to ChromaDB: {e}")
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
            # Get documents with the given source
            results = self.collection.get(where={"source": source})
            
            if not results['ids']:
                return 0
            
            # Suppress ChromaDB warnings during deletion
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stderr(devnull):
                    self.collection.delete(ids=results['ids'])
            
            deleted_count = len(results['ids'])
            self.logger.info(f"Deleted {deleted_count} documents for {source}")
            
            # Add a small delay to ensure deletion completes
            time.sleep(1)
            
            return deleted_count
            
        except Exception as e:
            if "Add of existing embedding ID" in str(e):
                # Suppress this specific ChromaDB warning - it's harmless
                self.logger.debug(f"Suppressed ChromaDB deletion warning for {source}: {e}")
                return 0
            else:
                self.logger.error(f"Error deleting documents for {source}: {e}")
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
            return len(results['ids']) > 0
        except Exception as e:
            self.logger.debug(f"Error checking for existing document {source}: {e}")
            return False
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the store.
        
        Returns:
            Number of documents
        """
        try:
            return self.collection.count()
        except Exception as e:
            self.logger.error(f"Error getting document count: {e}")
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
            metadatas = results.get('metadatas', [])
            if metadatas:
                for metadata in metadatas:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])
            return list(sources)
        except Exception as e:
            self.logger.error(f"Error getting document sources: {e}")
            return []
    
    def get_collection_state(self) -> Dict[str, Any]:
        """
        Get the current state of the collection for debugging.
        
        Returns:
            Dictionary with collection state information
        """
        try:
            results = self.collection.get()
            return {
                'count': len(results.get('ids', [])),
                'ids': results.get('ids', []),
                'sources': self.get_all_document_sources()
            }
        except Exception as e:
            self.logger.error(f"Error getting collection state: {e}")
            return {'count': 0, 'ids': [], 'sources': []} 
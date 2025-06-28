"""
Ingestion orchestrator service for coordinating the complete ingestion process.
"""
import logging
from typing import List

from ..core.interfaces.ingestion_orchestrator import IngestionOrchestrator
from ..core.interfaces.document_loader import DocumentLoader
from ..core.interfaces.text_extractor import TextExtractor
from ..core.interfaces.text_chunker import TextChunker
from ..core.interfaces.embedding_generator import EmbeddingGenerator
from ..core.interfaces.vector_store import VectorStore
from ..core.interfaces.user_interface import UserInterface
from ..models.document import Document, DocumentChunk, IngestionConfig, IngestionResult
from ..models.enums import DeletionChoice, BulkActionChoice, FileActionChoice
from .text_extractor_factory import TextExtractorFactory


logger = logging.getLogger(__name__)


class DefaultIngestionOrchestrator(IngestionOrchestrator):
    """Default implementation of the ingestion orchestrator."""
    
    def __init__(
        self,
        document_loader: DocumentLoader,
        text_extractor_factory: TextExtractorFactory,
        text_chunker: TextChunker,
        embedding_generator: EmbeddingGenerator,
        vector_store: VectorStore,
        user_interface: UserInterface
    ):
        """
        Initialize the ingestion orchestrator.
        
        Args:
            document_loader: Document loader service
            text_extractor_factory: Text extractor factory
            text_chunker: Text chunking service
            embedding_generator: Embedding generation service
            vector_store: Vector store service
            user_interface: User interface service
        """
        self.document_loader = document_loader
        self.text_extractor_factory = text_extractor_factory
        self.text_chunker = text_chunker
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.user_interface = user_interface
        
        logger.debug("Initialized DefaultIngestionOrchestrator")
    
    def ingest_documents(self, config: IngestionConfig) -> IngestionResult:
        """
        Orchestrate the complete ingestion process.
        
        Args:
            config: Ingestion configuration
            
        Returns:
            Ingestion result
        """
        logger.info("Starting document ingestion process")
        
        try:
            # Step 1: Load documents
            documents = self.document_loader.load_documents(config)
            if not documents:
                logger.warning("No documents found to process")
                return IngestionResult(
                    success=False,
                    documents_processed=0,
                    chunks_ingested=0,
                    errors=["No documents found"],
                    warnings=[]
                )
            
            logger.info(f"Loaded {len(documents)} documents")
            
            # Step 2: Handle existing documents
            existing_files = self._get_existing_files(documents)
            if existing_files:
                deletion_choice = self.user_interface.get_deletion_choice(existing_files)
                if deletion_choice == DeletionChoice.ALL.value:
                    self._delete_all_existing_files(existing_files)
                elif deletion_choice == DeletionChoice.ALL_BY_TYPE.value:
                    self._delete_all_files_by_type(existing_files)
                elif deletion_choice == DeletionChoice.SPECIFIC.value:
                    self._delete_specific_files(existing_files)
                elif deletion_choice == DeletionChoice.SKIP.value:
                    logger.info("Skipping deletion of existing files")
            
            # Step 3: Process documents
            processed_documents = 0
            total_chunks = 0
            errors = []
            warnings = []
            
            for document in documents:
                try:
                    # Check if document should be processed
                    if not self._should_process_document(document):
                        continue
                    
                    # Get appropriate text extractor
                    text_extractor = self.text_extractor_factory.get_extractor(document)
                    
                    # Extract text
                    text = text_extractor.extract_text(document)
                    if not text.strip():
                        warnings.append(f"No text extracted from {document.filename}")
                        continue
                    
                    # Chunk text
                    chunks = self.text_chunker.chunk_text(text, config, document.filename)
                    if not chunks:
                        warnings.append(f"No chunks created for {document.filename}")
                        continue
                    
                    # Generate embeddings
                    embeddings = self.embedding_generator.generate_embeddings(chunks)
                    if not embeddings:
                        errors.append(f"Failed to generate embeddings for {document.filename}")
                        continue
                    
                    # Add to vector store
                    if self.vector_store.add_documents(chunks, embeddings):
                        processed_documents += 1
                        total_chunks += len(chunks)
                        logger.info(f"Successfully processed {document.filename} ({len(chunks)} chunks)")
                    else:
                        errors.append(f"Failed to add {document.filename} to vector store")
                
                except Exception as e:
                    error_msg = f"Error processing document {document.filename}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            # Step 4: Return result
            result = IngestionResult(
                success=processed_documents > 0,
                documents_processed=processed_documents,
                chunks_ingested=total_chunks,
                errors=errors,
                warnings=warnings
            )
            
            logger.info(f"Ingestion completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during ingestion process: {e}")
            return IngestionResult(
                success=False,
                documents_processed=0,
                chunks_ingested=0,
                errors=[str(e)],
                warnings=[]
            )
    
    def _get_existing_files(self, documents: List[Document]) -> List[str]:
        """Get list of files that already exist in the vector store."""
        existing_files = []
        for document in documents:
            if self.vector_store.document_exists(document.filename):
                existing_files.append(document.filename)
        return existing_files
    
    def _delete_all_existing_files(self, existing_files: List[str]) -> None:
        """Delete all existing files from the vector store."""
        if self.user_interface.confirm_action(f"Delete all {len(existing_files)} existing files?"):
            total_deleted = 0
            for filename in existing_files:
                deleted_count = self.vector_store.delete_documents_by_source(filename)
                total_deleted += deleted_count
                logger.info(f"Deleted {deleted_count} chunks for {filename}")
            logger.info(f"Total chunks deleted: {total_deleted}")
        else:
            logger.info("Deletion cancelled by user")
    
    def _delete_all_files_by_type(self, existing_files: List[str]) -> None:
        """Delete all files of a specific type from the vector store."""
        # Group files by type
        grouped_files = self.user_interface._group_files_by_type(existing_files)
        
        # Get user choice for which file type to delete
        selected_type = self.user_interface.get_file_type_deletion_choice(grouped_files)
        
        if selected_type in grouped_files:
            files_to_delete = grouped_files[selected_type]
            if self.user_interface.confirm_action(f"Delete all {len(files_to_delete)} {selected_type} files?"):
                total_deleted = 0
                for filename in files_to_delete:
                    deleted_count = self.vector_store.delete_documents_by_source(filename)
                    total_deleted += deleted_count
                    logger.info(f"Deleted {deleted_count} chunks for {filename}")
                logger.info(f"Total chunks deleted for {selected_type}: {total_deleted}")
            else:
                logger.info(f"Deletion of {selected_type} files cancelled by user")
        else:
            logger.warning(f"No files found for type: {selected_type}")
    
    def _delete_specific_files(self, existing_files: List[str]) -> None:
        """Delete specific files based on user choice."""
        print("\nSelect files to delete (enter numbers separated by spaces):")
        for i, filename in enumerate(existing_files, 1):
            print(f"  {i}. {filename}")
        
        try:
            choices = input("Enter file numbers: ").strip().split()
            indices = [int(choice) - 1 for choice in choices if choice.isdigit()]
            
            files_to_delete = [existing_files[i] for i in indices if 0 <= i < len(existing_files)]
            
            if files_to_delete:
                if self.user_interface.confirm_action(f"Delete {len(files_to_delete)} selected files?"):
                    for filename in files_to_delete:
                        deleted_count = self.vector_store.delete_documents_by_source(filename)
                        logger.info(f"Deleted {deleted_count} chunks for {filename}")
                else:
                    logger.info("Deletion cancelled by user")
            else:
                logger.info("No valid files selected for deletion")
        
        except (ValueError, IndexError):
            logger.warning("Invalid selection, skipping deletion")
    
    def _should_process_document(self, document: Document) -> bool:
        """Check if document should be processed based on user choice."""
        if self.vector_store.document_exists(document.filename):
            choice = self.user_interface.get_user_choice(document.filename)
            return choice == FileActionChoice.ADD.value
        return True 
from typing import Optional, Set
import structlog
from ...embeddings.embedding_generator import SentenceTransformerEmbeddingGenerator
from ...menu.core.menu_command import CommandContext, CommandResult, MenuCommand
from ...menu.core.enums import MenuAction, MenuChoice
from ...menu.core.menu_registry import MenuRegistry
from ...menu.orchestrators.menu_orchestrator import MenuOrchestrator
from ...ingestion.builders.ingestion_menu_builder import IngestionMenuBuilder
from ...ingestion.core.enums import FileCategory, IngestionAction
from ...ingestion.core.interfaces import DocumentLoader, EmbeddingGenerator, TextChunker
from ...ingestion.core.interfaces.ingestion_orchestrator import IngestionOrchestrator
from ...ingestion.core.models.menu_context import MenuContext
from ...ingestion.models.document import DocumentChunk, IngestionConfig, IngestionResult
from ...ingestion.services.document_loader import FileSystemDocumentLoader
from ...ingestion.services.text_chunker import ParagraphTextChunker
from ...ingestion.services.text_extractor_factory import TextExtractorFactory


       
class IngestionMenuOrchestrator(IngestionOrchestrator):
    """Ingestion orchestrator using the generic menu system."""

    def __init__(
        self, 
        user_interface, 
        vector_store, 
        document_loader: Optional[DocumentLoader] = None,
        text_extractor_factory: Optional[TextExtractorFactory] = None,
        text_chunker: Optional[TextChunker] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        menu_builder: Optional[IngestionMenuBuilder] = None,
        menu_orchestrator: Optional[MenuOrchestrator] = None,
        _logger = None
    ):
        """
        Initialize the ingestion menu orchestrator with dependency injection.
        
        Args:
            user_interface: User interface service
            vector_store: Vector store service
            document_loader: Document loader service (optional, will create default if not provided)
            text_extractor_factory: Text extractor factory (optional, will create default if not provided)
            text_chunker: Text chunker service (optional, will create default if not provided)
            embedding_generator: Embedding generator service (optional, will create default if not provided)
            menu_builder: Menu builder (optional, will create default if not provided)
            menu_orchestrator: Menu orchestrator (optional, will create default if not provided)
            _logger: Logger instance (optional)
        """
        self.user_interface = user_interface
        self.vector_store = vector_store
        self.logger = _logger or structlog.get_logger("ingestion_menu_orchestrator")
        
        # Use dependency injection or create defaults
        self.document_loader = document_loader or FileSystemDocumentLoader("data")
        self.text_extractor_factory = text_extractor_factory or TextExtractorFactory(self.logger)
        self.text_chunker = text_chunker or ParagraphTextChunker()
        self.embedding_generator = embedding_generator or SentenceTransformerEmbeddingGenerator()
        self.menu_builder = menu_builder or IngestionMenuBuilder()
        self.menu_orchestrator = menu_orchestrator or MenuOrchestrator(user_interface, self.logger)

        # Track processing results
        self.processed_documents = 0
        self.total_chunks = 0
        self.errors = []
        self.warnings = []

    def ingest_documents(self, config: IngestionConfig) -> IngestionResult:
        """Orchestrate the ingestion process using the generic menu system."""
        self.logger.info("Starting ingestion with generic menu system")

        # Track processing results
        processed_documents = 0
        total_chunks = 0
        errors = []
        warnings = []

        try:
            # Build the main menu
            main_menu = self.menu_builder.build_main_menu()

            # Create context factory for the menu orchestrator
            def context_factory():
                return self._create_ingestion_context(config)

            # Override the menu orchestrator's result processing
            original_process_result = self.menu_orchestrator._process_result

            def process_result_with_ingestion_handling(result, context):
                nonlocal processed_documents, total_chunks, errors, warnings

                if getattr(result, "action", None) == MenuAction.CUSTOM_ACTION:
                    action_type = (
                        result.data.get("action_type") if result.data else None
                    )
                    if action_type == IngestionAction.ADD_FILES.value:
                        files = result.data.get("files", [])
                        if files:
                            # Process files for addition
                            self.logger.info(
                                "Starting batch processing", file_count=len(files)
                            )
                            try:
                                # Load documents from the data directory
                                documents = self.document_loader.load_documents(config)
                                selected_docs = [
                                    doc for doc in documents if doc.filename in files
                                ]

                                if selected_docs:
                                    self.logger.info(
                                        "Found documents to process",
                                        document_count=len(selected_docs),
                                    )
                                    # Process each document
                                    for i, doc in enumerate(selected_docs, 1):
                                        self.logger.info(
                                            "Processing file",
                                            file_number=i,
                                            total_files=len(selected_docs),
                                            filename=doc.filename,
                                        )
                                        try:
                                            # Extract text
                                            self.logger.info(
                                                "Extracting text", filename=doc.filename
                                            )
                                            text_extractor = self.text_extractor_factory.get_extractor(
                                                doc
                                            )
                                            text = text_extractor.extract_text(doc)

                                            if text:
                                                self.logger.info(
                                                    "Text extraction successful",
                                                    filename=doc.filename,
                                                    text_length=len(text),
                                                )
                                                # Add to vector store
                                                chunks_added = (
                                                    self._add_document_to_vector_store(
                                                        doc, text, config
                                                    )
                                                )
                                                total_chunks += chunks_added
                                                processed_documents += 1
                                                self.logger.info(
                                                    "File processing complete",
                                                    file_number=i,
                                                    total_files=len(selected_docs),
                                                    filename=doc.filename,
                                                    chunks_added=chunks_added,
                                                )
                                            else:
                                                warnings.append(
                                                    "No text extracted from {doc.filename}"
                                                )
                                                self.logger.warning(
                                                    "No text extracted",
                                                    filename=doc.filename,
                                                )

                                        except Exception as e:
                                            error_msg = "Error processing file {doc.filename}: {e}"
                                            errors.append(error_msg)
                                            self.logger.error(
                                                "Error processing file",
                                                filename=doc.filename,
                                                error=str(e),
                                            )
                                    self.logger.info(
                                        "Batch processing complete",
                                        files_processed=processed_documents,
                                        total_chunks=total_chunks,
                                    )
                                else:
                                    warnings.append(
                                        "No documents found for selected files"
                                    )
                                    self.logger.warning(
                                        "No documents found for selected files"
                                    )

                            except Exception as e:
                                error_msg = "Error loading documents: {e}"
                                errors.append(error_msg)
                                self.logger.error(
                                    "Error loading documents", error=str(e)
                                )
                # Call original method for other actions
                return original_process_result(result, context)

            # Replace the method temporarily
            self.menu_orchestrator._process_result = (
                process_result_with_ingestion_handling
            )

            # Run the menu system
            self.menu_orchestrator.run(main_menu, context_factory)

            # Restore original method
            self.menu_orchestrator._process_result = original_process_result

            # Return the actual processing results
            return IngestionResult(
                success=len(errors) == 0,
                documents_processed=processed_documents,
                chunks_ingested=total_chunks,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            self.logger.error("Error during ingestion", error=str(e))
            return IngestionResult(
                success=False,
                documents_processed=0,
                chunks_ingested=0,
                errors=[str(e)],
                warnings=[],
            )

    def _process_files_for_addition(
        self,
        files_to_add: Set[str],
        context: Optional[CommandContext],
        config: IngestionConfig,
    ):
        """Process files for addition to the database."""
        try:
            self.logger.info("Starting batch processing", file_count=len(files_to_add))

            # Load documents from the data directory
            documents = self.document_loader.load_documents(config)

            # Filter to selected files
            selected_docs = [doc for doc in documents if doc.filename in files_to_add]

            if not selected_docs:
                self.warnings.append("No documents found for selected files")
                self.logger.warning("No documents found for selected files")
                return

            self.logger.info(
                "Found documents to process", document_count=len(selected_docs)
            )

            # Process each document
            for i, doc in enumerate(selected_docs, 1):
                self.logger.info(
                    "Processing file",
                    file_number=i,
                    total_files=len(selected_docs),
                    filename=doc.filename,
                )
                try:
                    # Extract text
                    self.logger.info("Extracting text", filename=doc.filename)
                    text_extractor = self.text_extractor_factory.get_extractor(doc)
                    text = text_extractor.extract_text(doc)

                    if text:
                        self.logger.info(
                            "Text extraction successful",
                            filename=doc.filename,
                            text_length=len(text),
                        )
                        # Add to vector store
                        chunks_added = self._add_document_to_vector_store(
                            doc, text, config
                        )
                        self.total_chunks += chunks_added
                        self.processed_documents += 1
                        self.logger.info(
                            "File processing complete",
                            file_number=i,
                            total_files=len(selected_docs),
                            filename=doc.filename,
                            chunks_added=chunks_added,
                        )
                    else:
                        self.warnings.append("No text extracted from {doc.filename}")
                        self.logger.warning("No text extracted", filename=doc.filename)

                except Exception as e:
                    error_msg = "Error processing {doc.filename}: {e}"
                    self.errors.append(error_msg)
                    self.logger.error(
                        "Error processing file", filename=doc.filename, error=str(e)
                    )

            self.logger.info(
                "Batch processing complete",
                files_processed=self.processed_documents,
                total_chunks=self.total_chunks,
            )

        except Exception as e:
            error_msg = "Error loading documents: {e}"
            self.errors.append(error_msg)
            self.logger.error("Error loading documents", error=str(e))

    def _add_document_to_vector_store(
        self, doc, text: str, config: IngestionConfig
    ) -> int:
        """Helper method to add a document to the vector store with proper chunking and embeddings."""
        try:
            self.logger.info(
                "Starting processing", filename=doc.filename, text_length=len(text)
            )

            # Step 1: Create chunks from the text
            self.logger.info("Step 1: Creating text chunks", filename=doc.filename)
            chunks = self.text_chunker.chunk_text(text, config, doc.filename)

            if not chunks:
                self.logger.warning("No chunks created", filename=doc.filename)
                return 0

            self.logger.info(
                "Step 1 Complete: Chunks created",
                filename=doc.filename,
                chunk_count=len(chunks),
            )

            # Step 2: Generate embeddings for the chunks
            self.logger.info(
                "Step 2: Generating embeddings",
                filename=doc.filename,
                chunk_count=len(chunks),
            )
            embeddings = self.embedding_generator.generate_embeddings(chunks)

            if not embeddings or len(embeddings) != len(chunks):
                self.logger.error(
                    "Failed to generate embeddings",
                    filename=doc.filename,
                    expected_count=len(chunks),
                    actual_count=len(embeddings) if embeddings else 0,
                )
                return 0

            self.logger.info(
                "Step 2 Complete: Embeddings generated",
                filename=doc.filename,
                embedding_count=len(embeddings),
            )

            # Step 3: Add to vector store
            self.logger.info(
                "Step 3: Storing chunks in database",
                filename=doc.filename,
                chunk_count=len(chunks),
            )
            if self.vector_store.add_documents(chunks, embeddings):
                self.logger.info(
                    "Step 3 Complete: Successfully stored chunks",
                    filename=doc.filename,
                    chunk_count=len(chunks),
                )
                return len(chunks)
            else:
                self.logger.error(
                    "Step 3 Failed: Failed to add to vector store",
                    filename=doc.filename,
                )
                return 0

        except Exception as e:
            self.logger.error(
                "Error processing document", filename=doc.filename, error=str(e)
            )
            return 0

    def _discover_local_files(self, config: IngestionConfig) -> Set[str]:
        """Discover files in the local data directory."""
        try:
            documents = self.document_loader.load_documents(config)
            return {doc.filename for doc in documents}
        except Exception as e:
            self.logger.error("Error discovering local files", error=str(e))
            return set()

    def _get_database_files(self) -> Set[str]:
        """Get files currently in the database."""
        try:
            return set(self.vector_store.get_all_document_sources())
        except Exception as e:
            self.logger.error("Error getting database files", error=str(e))
            return set()

    def _create_ingestion_context(self, config: IngestionConfig) -> CommandContext:
        """Create context for the ingestion menu system."""
        context = CommandContext()

        try:
            # Discover local files
            local_files = self._discover_local_files(config)
            self.logger.info("Discovered local files", file_count=len(local_files))

            # Get database files
            db_files = self._get_database_files()
            self.logger.info("Found database files", file_count=len(db_files))

            # Categorize files
            files_only_local = local_files - db_files
            files_both = local_files & db_files
            files_only_db = db_files - local_files

            self.logger.info(
                "File categorization",
                files_only_local=len(files_only_local),
                files_both=len(files_both),
                files_only_db=len(files_only_db),
            )

            # Populate context with categorized files
            context.data = {
                FileCategory.NEW_FILES.value: files_only_local,
                FileCategory.EXISTING_FILES.value: files_both,
                FileCategory.ORPHANED_FILES.value: files_only_db,
                "total_files_in_db": len(db_files),
                "total_files_in_local": len(local_files),
            }

            # Add dependencies
            context.user_interface = self.user_interface
            context.vector_store = self.vector_store
            context.logger = self.logger

            # Debug logging
            self.logger.debug(
                "Context created",
                vector_store=context.vector_store,
                self_vector_store=self.vector_store,
            )

            return context

        except Exception as e:
            self.logger.error("Error creating ingestion context", error=str(e))
            return context

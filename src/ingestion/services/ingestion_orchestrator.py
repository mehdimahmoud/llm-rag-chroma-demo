import os
import structlog
from typing import List, Set

from ..core.enums import (AdvancedOptionsMenuChoice,
                          BulkOperationsMenuChoice, FileActionChoice, 
                          FilesInBothPlacesMenuChoice, FilesOnlyInDbMenuChoice, 
                          FileType, MainMenuChoice, NewFilesMenuChoice)
from ..core.interfaces import (DocumentLoader, EmbeddingGenerator,
                              IngestionOrchestrator, TextChunker,
                              UserInterface, VectorStore)
from ..models.document import Document, DocumentChunk, IngestionConfig, IngestionResult
from ..models.enums import DeletionChoice
from .text_extractor_factory import TextExtractorFactory

logger = structlog.get_logger("ingestion_orchestrator")


class DefaultIngestionOrchestrator(IngestionOrchestrator):
    """Default implementation of the ingestion orchestrator."""

    def __init__(
        self,
        document_loader: DocumentLoader,
        text_extractor_factory: TextExtractorFactory,
        text_chunker: TextChunker,
        embedding_generator: EmbeddingGenerator,
        vector_store: VectorStore,
        user_interface: UserInterface,
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

    def _display_grouped_files(self, files: set, header: str):
        if not files:
            return
        print("\n{header}")
        grouped = self.user_interface._group_files_by_type(list(files))
        for file_type, file_list in sorted(grouped.items()):
            print(".{file_type.upper()} files ({len(file_list)}):")
            for i, filename in enumerate(file_list, 1):
                print("  {i}. {filename}")

    def _display_comprehensive_menu(
        self, files_only_local: set, files_both: set, files_only_db: set
    ):
        """Display the comprehensive menu for file management."""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE FILE MANAGEMENT MENU")
        print("=" * 60)

        print("\n📁 LOCAL FILES ONLY ({len(files_only_local)} files):")
        for file in sorted(files_only_local):
            print("   + {file}")

        print("\n📋 FILES IN BOTH PLACES ({len(files_both)} files):")
        for file in sorted(files_both):
            print("   = {file}")

        print("\n🗄️  FILES ONLY IN DATABASE ({len(files_only_db)} files):")
        for file in sorted(files_only_db):
            print("   - {file}")

        print("\n" + "=" * 60)
        print("MENU OPTIONS:")
        print("=" * 60)

        print("\n1. NEW FILES (local only)")
        print("   - Process all new files")
        print("   - Process specific new files")
        print("   - Process new files by type")
        print("   - Skip all new files")

        print("\n2. EXISTING FILES (in both places)")
        print("   - Re-process all existing files")
        print("   - Re-process specific existing files")
        print("   - Re-process existing files by type")
        print("   - Keep all existing files as-is")

        print("\n3. ORPHANED FILES (database only)")
        print("   - Delete all files only in database")
        print("   - Delete specific files only in database")
        print("   - Delete files only in database by type")
        print("   - Keep all files only in database")

        print("\n4. BULK OPERATIONS")
        print("   - Process all files (new + existing)")
        print("   - Clear database and add all local files")
        print("   - Skip all files (do nothing)")

        print("\n5. ADVANCED OPTIONS")
        print("   - Show detailed file comparison")
        print("   - Preview what will be processed")
        print("   - Custom file selection")

        print("\n0. EXIT (cancel all operations)")
        print("\n" + "=" * 60)

    def ingest_documents(self, config: IngestionConfig) -> IngestionResult:
        """
        Orchestrate the complete ingestion process with comprehensive menu.

        Args:
            config: Ingestion configuration

        Returns:
            Ingestion result
        """
        logger.info("Starting document ingestion process")

        try:
            # Step 1: Load documents from local filesystem
            documents = self.document_loader.load_documents(config)
            if not documents:
                logger.warning("No documents found to process")
                return IngestionResult(
                    success=False,
                    documents_processed=0,
                    chunks_ingested=0,
                    errors=["No documents found"],
                    warnings=[],
                )

            logger.info("Found {len(documents)} documents in data folder")

            # Step 2: Get existing files from database
            existing_files_in_db = self.vector_store.get_all_document_sources()
            logger.info("Found {len(existing_files_in_db)} existing files in database")

            # Step 3: Categorize files
            local_filenames = {doc.filename for doc in documents}
            existing_filenames = set(existing_files_in_db)

            files_only_local = local_filenames - existing_filenames
            files_only_db = existing_filenames - local_filenames
            files_both = local_filenames & existing_filenames

            logger.info("Files only in local folder: {len(files_only_local)}")
            logger.info("Files only in database: {len(files_only_db)}")
            logger.info("Files in both places: {len(files_both)}")

            # Step 4: Display comprehensive menu
            self._display_comprehensive_menu(
                files_only_local, files_both, files_only_db
            )

            # Step 5: Get user's main menu choice
            while True:
                try:
                    main_choice = input("Enter your choice (0-5): ").strip()

                    if main_choice == MainMenuChoice.EXIT.value:
                        logger.info("User cancelled all operations")
                        return IngestionResult(
                            success=True,
                            documents_processed=0,
                            chunks_ingested=0,
                            errors=[],
                            warnings=["User cancelled all operations"],
                        )
                    elif main_choice in [
                        MainMenuChoice.PROCESS_NEW_FILES.value,
                        MainMenuChoice.HANDLE_FILES_IN_BOTH_PLACES.value,
                        MainMenuChoice.HANDLE_FILES_ONLY_IN_DB.value,
                        MainMenuChoice.BULK_OPERATIONS.value,
                        MainMenuChoice.ADVANCED_OPTIONS.value,
                    ]:
                        break
                    else:
                        print("Invalid choice. Please enter 0, 1, 2, 3, 4, or 5.")
                except (ValueError, KeyboardInterrupt):
                    print("\nOperation cancelled by user.")
                    return IngestionResult(
                        success=True,
                        documents_processed=0,
                        chunks_ingested=0,
                        errors=[],
                        warnings=["Operation cancelled by user"],
                    )

            # Step 6: Handle user's choice
            files_to_process = set()

            if main_choice == MainMenuChoice.PROCESS_NEW_FILES.value:
                # PROCESS NEW FILES
                files_to_process = self._handle_new_files_menu(files_only_local)
            elif main_choice == MainMenuChoice.HANDLE_FILES_IN_BOTH_PLACES.value:
                # HANDLE FILES IN BOTH PLACES
                files_to_process = self._handle_files_in_both_places_menu(files_both)
            elif main_choice == MainMenuChoice.HANDLE_FILES_ONLY_IN_DB.value:
                # HANDLE FILES ONLY IN DATABASE
                self._handle_files_only_in_db_menu(files_only_db)
            elif main_choice == MainMenuChoice.BULK_OPERATIONS.value:
                # BULK OPERATIONS
                files_to_process = self._handle_bulk_operations_menu(
                    files_only_local, files_both
                )
            elif main_choice == MainMenuChoice.ADVANCED_OPTIONS.value:
                # ADVANCED OPTIONS
                files_to_process = self._handle_advanced_options_menu(
                    files_only_local, files_both, files_only_db
                )

            # Step 7: Process selected files
            if not files_to_process:
                logger.info("No files selected for processing")
                return IngestionResult(
                    success=True,
                    documents_processed=0,
                    chunks_ingested=0,
                    errors=[],
                    warnings=["No files were selected for processing"],
                )

            logger.info("Processing {len(files_to_process)} selected files...")
            self._display_grouped_files(
                files_to_process, "Files selected for processing:"
            )
            print()  # Add blank line for better readability

            # Filter documents to only process selected files
            documents_to_process = [
                doc for doc in documents if doc.filename in files_to_process
            ]

            processed_documents = 0
            total_chunks = 0
            errors = []
            warnings = []

            for i, document in enumerate(documents_to_process, 1):
                try:
                    logger.info("-" * 50)
                    logger.info(
                        "Processing file {i} of {len(documents_to_process)}: {document.filename}"
                    )

                    # Get appropriate text extractor
                    text_extractor = self.text_extractor_factory.get_extractor(document)

                    # Extract text
                    logger.debug("Extracting text from {document.filename}")
                    text = text_extractor.extract_text(document)
                    if not text.strip():
                        warning_msg = "No text extracted from {document.filename}"
                        logger.warning(warning_msg)
                        warnings.append(warning_msg)
                        continue

                    logger.info(
                        "Extracted {len(text)} characters from {document.filename}"
                    )

                    # Chunk text
                    logger.debug("Chunking text from {document.filename}")
                    chunks = self.text_chunker.chunk_text(
                        text, config, document.filename
                    )
                    if not chunks:
                        warning_msg = "No chunks created for {document.filename}"
                        logger.warning(warning_msg)
                        warnings.append(warning_msg)
                        continue

                    logger.info(
                        "Created {len(chunks)} chunks from {document.filename}"
                    )

                    # Generate embeddings
                    logger.debug("Generating embeddings for {document.filename}")
                    embeddings = self.embedding_generator.generate_embeddings(chunks)
                    if not embeddings:
                        error_msg = (
                            "Failed to generate embeddings for {document.filename}"
                        )
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue

                    logger.info("Generated embeddings for {document.filename}")

                    # Add to vector store
                    logger.debug("Adding {document.filename} to vector store")
                    if self.vector_store.add_documents(chunks, embeddings):
                        processed_documents += 1
                        total_chunks += len(chunks)
                        logger.info(
                            "Successfully ingested {document.filename} ({len(chunks)} chunks)"
                        )
                    else:
                        error_msg = "Failed to add {document.filename} to vector store"
                        logger.error(error_msg)
                        errors.append(error_msg)

                except Exception as e:
                    error_msg = "Error processing document {document.filename}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue

            # Step 8: Return result
            result = IngestionResult(
                success=processed_documents > 0,
                documents_processed=processed_documents,
                chunks_ingested=total_chunks,
                errors=errors,
                warnings=warnings,
            )

            logger.info(
                "Ingestion completed: {processed_documents} documents processed, {total_chunks} chunks ingested"
            )
            return result

        except Exception as e:
            logger.error("Error during ingestion process: {e}")
            return IngestionResult(
                success=False,
                documents_processed=0,
                chunks_ingested=0,
                errors=[str(e)],
                warnings=[],
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
        if self.user_interface.confirm_action(
            "Delete all {len(existing_files)} existing files?"
        ):
            total_deleted = 0
            for filename in existing_files:
                deleted_count = self.vector_store.delete_documents_by_source(filename)
                total_deleted += deleted_count
                logger.info("Deleted {deleted_count} chunks for {filename}")
            logger.info("Total chunks deleted: {total_deleted}")
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
            if self.user_interface.confirm_action(
                "Delete all {len(files_to_delete)} {selected_type} files?"
            ):
                total_deleted = 0
                for filename in files_to_delete:
                    deleted_count = self.vector_store.delete_documents_by_source(
                        filename
                    )
                    total_deleted += deleted_count
                    logger.info("Deleted {deleted_count} chunks for {filename}")
                logger.info(
                    "Total chunks deleted for {selected_type}: {total_deleted}"
                )
            else:
                logger.info("Deletion of {selected_type} files cancelled by user")
        else:
            logger.warning("No files found for type: {selected_type}")

    def _delete_specific_files(self, existing_files: List[str]) -> None:
        """Delete specific files based on user choice."""
        print("\nSelect files to delete (enter numbers separated by spaces):")
        for i, filename in enumerate(existing_files, 1):
            print("  {i}. {filename}")

        try:
            choices = input("Enter file numbers: ").strip().split()
            indices = [int(choice) - 1 for choice in choices if choice.isdigit()]

            files_to_delete = [
                existing_files[i] for i in indices if 0 <= i < len(existing_files)
            ]

            if files_to_delete:
                if self.user_interface.confirm_action(
                    "Delete {len(files_to_delete)} selected files?"
                ):
                    for filename in files_to_delete:
                        deleted_count = self.vector_store.delete_documents_by_source(
                            filename
                        )
                        logger.info("Deleted {deleted_count} chunks for {filename}")
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

    def _handle_new_files_menu(self, files_only_local: set) -> set:
        """Handle menu for new files (files only in local folder)."""
        print("\n" + "=" * 50)
        print("PROCESS NEW FILES MENU")
        print("=" * 50)

        print("\n1. Add all new files")
        print("2. Add specific new files")
        print("3. Add new files by type")
        print("4. Skip all new files")
        print("0. Back to main menu")

        while True:
            try:
                choice = input("\nEnter your choice (0-4): ").strip()

                if choice == NewFilesMenuChoice.BACK.value:
                    return set()
                elif choice == NewFilesMenuChoice.ADD_ALL.value:
                    if self.user_interface.confirm_action(
                        "Add all {len(files_only_local)} new files to database?"
                    ):
                        return files_only_local
                    else:
                        return set()
                elif choice == NewFilesMenuChoice.ADD_SPECIFIC.value:
                    selected_files = self.user_interface.get_specific_file_choices(
                        list(files_only_local), FileActionChoice.ADD.value
                    )
                    if selected_files and self.user_interface.confirm_action(
                        "Add {len(selected_files)} selected files to database?"
                    ):
                        return set(selected_files)
                    return set()
                elif choice == NewFilesMenuChoice.ADD_BY_TYPE.value:
                    grouped_files = self.user_interface._group_files_by_type(
                        list(files_only_local)
                    )
                    selected_type = self.user_interface.get_file_type_deletion_choice(
                        grouped_files
                    )
                    if selected_type in grouped_files:
                        type_files = grouped_files[selected_type]
                        if self.user_interface.confirm_action(
                            "Add all {len(type_files)} {selected_type} files to database?"
                        ):
                            return set(type_files)
                    return set()
                elif choice == NewFilesMenuChoice.SKIP_ALL.value:
                    logger.info("User chose to skip all new files")
                    return set()
                else:
                    print("Invalid choice. Please enter 0, 1, 2, 3, or 4.")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return set()

    def _handle_files_in_both_places_menu(self, files_both: set) -> set:
        """Handle menu for files that exist in both local folder and database."""
        print("\n" + "=" * 50)
        print("FILES IN BOTH PLACES MENU")
        print("=" * 50)

        print("\n1. Replace all files in both places")
        print("2. Replace specific files in both places")
        print("3. Replace files in both places by type")
        print("4. Keep all files in both places (skip)")
        print("5. Keep specific files in both places")
        print("6. Keep files in both places by type")
        print("0. Back to main menu")

        while True:
            try:
                choice = input("\nEnter your choice (0-6): ").strip()

                if choice == FilesInBothPlacesMenuChoice.BACK.value:
                    return set()
                elif choice == FilesInBothPlacesMenuChoice.REPLACE_ALL.value:
                    if self.user_interface.confirm_action(
                        "Replace all {len(files_both)} files in both places?"
                    ):
                        # Delete existing files first
                        for filename in files_both:
                            deleted_count = (
                                self.vector_store.delete_documents_by_source(filename)
                            )
                            logger.info(
                                "Deleted {deleted_count} chunks for {filename}"
                            )
                        return files_both
                    return set()
                elif choice == FilesInBothPlacesMenuChoice.REPLACE_SPECIFIC.value:
                    selected_files = self.user_interface.get_specific_file_choices(
                        list(files_both), FileActionChoice.REPLACE.value
                    )
                    if selected_files and self.user_interface.confirm_action(
                        "Replace {len(selected_files)} selected files?"
                    ):
                        # Delete selected files first
                        for filename in selected_files:
                            deleted_count = (
                                self.vector_store.delete_documents_by_source(filename)
                            )
                            logger.info(
                                "Deleted {deleted_count} chunks for {filename}"
                            )
                        return set(selected_files)
                    return set()
                elif choice == FilesInBothPlacesMenuChoice.REPLACE_BY_TYPE.value:
                    grouped_files = self.user_interface._group_files_by_type(
                        list(files_both)
                    )
                    selected_type = self.user_interface.get_file_type_deletion_choice(
                        grouped_files
                    )
                    if selected_type in grouped_files:
                        type_files = grouped_files[selected_type]
                        if self.user_interface.confirm_action(
                            "Replace all {len(type_files)} {selected_type} files?"
                        ):
                            # Delete selected files first
                            for filename in type_files:
                                deleted_count = (
                                    self.vector_store.delete_documents_by_source(
                                        filename
                                    )
                                )
                                logger.info(
                                    "Deleted {deleted_count} chunks for {filename}"
                                )
                            return set(type_files)
                    return set()
                elif choice == FilesInBothPlacesMenuChoice.KEEP_ALL.value:
                    logger.info("User chose to keep all files in both places")
                    return set()
                elif choice == FilesInBothPlacesMenuChoice.KEEP_SPECIFIC.value:
                    selected_files = self.user_interface.get_specific_file_choices(
                        list(files_both), FileActionChoice.KEEP.value
                    )
                    if selected_files:
                        remaining_files = files_both - set(selected_files)
                        if self.user_interface.confirm_action(
                            "Keep {len(selected_files)} files and process {len(remaining_files)} remaining files?"
                        ):
                            return remaining_files
                    return set()
                elif choice == FilesInBothPlacesMenuChoice.KEEP_BY_TYPE.value:
                    grouped_files = self.user_interface._group_files_by_type(
                        list(files_both)
                    )
                    selected_type = self.user_interface.get_file_type_deletion_choice(
                        grouped_files
                    )
                    if selected_type in grouped_files:
                        type_files = grouped_files[selected_type]
                        remaining_files = files_both - set(type_files)
                        if self.user_interface.confirm_action(
                            "Keep all {len(type_files)} {selected_type} files and process {len(remaining_files)} remaining files?"
                        ):
                            return remaining_files
                    return set()
                else:
                    print("Invalid choice. Please enter 0-6.")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return set()

    def _handle_files_only_in_db_menu(self, files_only_db: set) -> None:
        """Handle menu for files that exist only in database."""
        print("\n" + "=" * 50)
        print("FILES ONLY IN DATABASE MENU")
        print("=" * 50)

        print("\n1. Delete all files only in database")
        print("2. Delete specific files only in database")
        print("3. Delete files only in database by type")
        print("4. Keep all files only in database")
        print("0. Back to main menu")

        while True:
            try:
                choice = input("\nEnter your choice (0-4): ").strip()

                if choice == FilesOnlyInDbMenuChoice.BACK.value:
                    return
                elif choice == FilesOnlyInDbMenuChoice.DELETE_ALL.value:
                    if self.user_interface.confirm_action(
                        "Delete all {len(files_only_db)} files only in database?"
                    ):
                        for filename in files_only_db:
                            deleted_count = (
                                self.vector_store.delete_documents_by_source(filename)
                            )
                            logger.info(
                                "Deleted {deleted_count} chunks for {filename}"
                            )
                    return
                elif choice == FilesOnlyInDbMenuChoice.DELETE_SPECIFIC.value:
                    selected_files = self.user_interface.get_specific_file_choices(
                        list(files_only_db), FileActionChoice.DELETE.value
                    )
                    if selected_files and self.user_interface.confirm_action(
                        "Delete {len(selected_files)} selected files from database?"
                    ):
                        for filename in selected_files:
                            deleted_count = (
                                self.vector_store.delete_documents_by_source(filename)
                            )
                            logger.info(
                                "Deleted {deleted_count} chunks for {filename}"
                            )
                    return
                elif choice == FilesOnlyInDbMenuChoice.DELETE_BY_TYPE.value:
                    grouped_files = self.user_interface._group_files_by_type(
                        list(files_only_db)
                    )
                    selected_type = self.user_interface.get_file_type_deletion_choice(
                        grouped_files
                    )
                    if selected_type in grouped_files:
                        type_files = grouped_files[selected_type]
                        if self.user_interface.confirm_action(
                            "Delete all {len(type_files)} {selected_type} files from database?"
                        ):
                            for filename in type_files:
                                deleted_count = (
                                    self.vector_store.delete_documents_by_source(
                                        filename
                                    )
                                )
                                logger.info(
                                    "Deleted {deleted_count} chunks for {filename}"
                                )
                    return
                elif choice == FilesOnlyInDbMenuChoice.KEEP_ALL.value:
                    logger.info("User chose to keep all files only in database")
                    return
                else:
                    print("Invalid choice. Please enter 0-4.")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return

    def _handle_bulk_operations_menu(
        self, files_only_local: set, files_both: set
    ) -> set:
        """Handle bulk operations menu."""
        print("\n" + "=" * 50)
        print("BULK OPERATIONS MENU")
        print("=" * 50)

        print("\n1. Process all files (new + existing)")
        print("2. Clear database and add all local files")
        print("3. Skip all files (do nothing)")
        print("0. Back to main menu")

        while True:
            try:
                choice = input("\nEnter your choice (0-3): ").strip()

                if choice == BulkOperationsMenuChoice.BACK.value:
                    return set()
                elif choice == BulkOperationsMenuChoice.PROCESS_ALL.value:
                    all_files = files_only_local | files_both
                    if self.user_interface.confirm_action(
                        "Process all {len(all_files)} files (new + existing)?"
                    ):
                        return all_files
                    return set()
                elif choice == BulkOperationsMenuChoice.CLEAR_AND_REBUILD.value:
                    if self.user_interface.confirm_action(
                        "Clear entire database and add all local files?"
                    ):
                        # Clear all documents from database
                        self.vector_store.clear_all_documents()
                        logger.info("Cleared all documents from database")
                        return files_only_local | files_both
                    return set()
                elif choice == BulkOperationsMenuChoice.SKIP_ALL.value:
                    logger.info("User chose to skip all files")
                    return set()
                else:
                    print("Invalid choice. Please enter 0-3.")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return set()

    def _handle_advanced_options_menu(
        self, files_only_local: set, files_both: set, files_only_db: set
    ) -> set:
        """Handle advanced options menu."""
        print("\n" + "=" * 50)
        print("ADVANCED OPTIONS MENU")
        print("=" * 50)

        print("\n1. Show detailed file comparison")
        print("2. Preview what will be processed")
        print("3. Custom file selection")
        print("0. Back to main menu")

        while True:
            try:
                choice = input("\nEnter your choice (0-3): ").strip()

                if choice == AdvancedOptionsMenuChoice.BACK.value:
                    return set()
                elif choice == AdvancedOptionsMenuChoice.SHOW_DETAILED_COMPARISON.value:
                    self._show_detailed_file_comparison(
                        files_only_local, files_both, files_only_db
                    )
                    return self._handle_advanced_options_menu(
                        files_only_local, files_both, files_only_db
                    )
                elif choice == AdvancedOptionsMenuChoice.PREVIEW_PROCESSING_PLAN.value:
                    self._preview_processing_plan(
                        files_only_local, files_both, files_only_db
                    )
                    return self._handle_advanced_options_menu(
                        files_only_local, files_both, files_only_db
                    )
                elif choice == AdvancedOptionsMenuChoice.CUSTOM_SELECTION.value:
                    return self._custom_file_selection(files_only_local, files_both)
                else:
                    print("Invalid choice. Please enter 0-3.")
            except (ValueError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return set()

    def _show_detailed_file_comparison(
        self, files_only_local: set, files_both: set, files_only_db: set
    ):
        """Show detailed file comparison."""
        print("\n" + "=" * 60)
        print("DETAILED FILE COMPARISON")
        print("=" * 60)

        print("\nFiles only in local folder ({len(files_only_local)}):")
        for filename in sorted(files_only_local):
            print("  + {filename}")

        print("\nFiles in both places ({len(files_both)}):")
        for filename in sorted(files_both):
            print("  = {filename}")

        print("\nFiles only in database ({len(files_only_db)}):")
        for filename in sorted(files_only_db):
            print("  - {filename}")

        print("\nLegend: + = new file, = = exists in both, - = only in database")
        input("\nPress Enter to continue...")

    def _preview_processing_plan(
        self, files_only_local: set, files_both: set, files_only_db: set
    ):
        """Preview what will be processed."""
        print("\n" + "=" * 60)
        print("PROCESSING PLAN PREVIEW")
        print("=" * 60)

        print(
            "\nThis preview shows what would happen with different processing options:"
        )

        print("\n1. Process all files:")
        print("   - Add {len(files_only_local)} new files")
        print("   - Replace {len(files_both)} existing files")
        print("   - Total: {len(files_only_local) + len(files_both)} files processed")

        print("\n2. Process only new files:")
        print("   - Add {len(files_only_local)} new files")
        print("   - Skip {len(files_both)} existing files")
        print("   - Total: {len(files_only_local)} files processed")

        print("\n3. Clear and rebuild:")
        print("   - Delete {len(files_only_db) + len(files_both)} files from database")
        print(
            "   - Add {len(files_only_local) + len(files_both)} files from local folder"
        )
        print("   - Total: {len(files_only_local) + len(files_both)} files processed")

        input("\nPress Enter to continue...")

    def _custom_file_selection(self, files_only_local: set, files_both: set) -> set:
        """Allow custom file selection."""
        print("\n" + "=" * 50)
        print("CUSTOM FILE SELECTION")
        print("=" * 50)

        all_files = list(files_only_local | files_both)
        if not all_files:
            print("No files available for selection.")
            return set()

        print("\nAvailable files:")
        for i, filename in enumerate(all_files, 1):
            status = "NEW" if filename in files_only_local else "EXISTING"
            print("  {i}. {filename} ({status})")

        print("\nEnter file numbers separated by commas (e.g., 1,3,5)")
        print("Or enter 'all' to select all files")
        print("Or enter 'new' to select only new files")
        print("Or enter 'existing' to select only existing files")

        try:
            choice = input("\nYour selection: ").strip().lower()

            if choice == "all":
                selected_files = all_files
            elif choice == "new":
                selected_files = list(files_only_local)
            elif choice == "existing":
                selected_files = list(files_both)
            else:
                # Parse comma-separated numbers
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected_files = [
                    all_files[i] for i in indices if 0 <= i < len(all_files)
                ]

            if selected_files and self.user_interface.confirm_action(
                "Process {len(selected_files)} selected files?"
            ):
                return set(selected_files)
            return set()

        except (ValueError, IndexError, KeyboardInterrupt):
            print("Invalid selection or operation cancelled.")
            return set()

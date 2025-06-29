"""
Document loader service for loading documents from the data directory.
"""
from pathlib import Path
from typing import List

import structlog

from ..core.interfaces.document_loader import DocumentLoader
from ..models.document import Document, IngestionConfig
from ..models.enums import FileType


class FileSystemDocumentLoader(DocumentLoader):
    """Loads documents from the file system."""

    def __init__(self, data_directory: str = "data"):
        """
        Initialize the document loader.

        Args:
            data_directory: Path to the data directory
        """
        self.data_directory = Path(data_directory)
        self.logger = structlog.get_logger("document_loader")
        self.logger.debug(
            "Initialized FileSystemDocumentLoader",
            data_directory=str(self.data_directory),
        )

    def load_documents(self, config: IngestionConfig) -> List[Document]:
        """
        Load documents from the configured data directory.

        Args:
            config: Ingestion configuration

        Returns:
            List of loaded documents
        """
        self.logger.info("Loading documents", data_directory=str(self.data_directory))
        self.logger.info(
            "Allowed file types", allowed_types=config.get_allowed_file_types_str()
        )

        if not self.data_directory.exists():
            self.logger.warning(
                "Data directory does not exist", data_directory=str(self.data_directory)
            )
            return []

        documents = []

        # Recursively find all files in the data directory
        for file_path in self.data_directory.rglob("*"):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()

                # Check if file type is allowed
                if config.is_file_type_allowed(file_extension):
                    if self.supports_file(file_path):
                        try:
                            document = Document(
                                file_path=str(file_path),
                                filename=file_path.name,
                                file_type=file_extension,
                                size=file_path.stat().st_size,
                            )
                            documents.append(document)
                            self.logger.debug(
                                "Loaded document",
                                filename=file_path.name,
                                file_type=file_extension,
                            )
                        except Exception as e:
                            self.logger.error(
                                "Failed to load document",
                                file_path=str(file_path),
                                error=str(e),
                            )
                    else:
                        self.logger.debug(
                            "Skipping unsupported file",
                            filename=file_path.name,
                            file_type=file_extension,
                        )
                else:
                    self.logger.debug(
                        "Skipping disallowed file type",
                        filename=file_path.name,
                        file_type=file_extension,
                    )

        self.logger.info("Loaded documents", document_count=len(documents))

        # Log summary by file type
        file_types = {}
        for doc in documents:
            file_types[doc.file_type] = file_types.get(doc.file_type, 0) + 1

        for file_type, count in file_types.items():
            self.logger.info("File type summary", file_type=file_type, count=count)

        return documents

    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if the file is supported
        """
        file_extension = file_path.suffix.lower()
        return file_extension in [FileType.PDF.value, FileType.TXT.value]

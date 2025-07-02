"""
Document loading and file type detection.

This module provides document loading capabilities for various
file formats with proper error handling and validation.
"""

from pathlib import Path
from typing import Dict, List, Optional

from langchain_community.document_loaders import (CSVLoader, Docx2txtLoader,
                                                  PyPDFLoader, TextLoader,
                                                  UnstructuredExcelLoader)
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document

from ..core.logging import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Handles loading documents from various file formats."""

    # File type to loader mapping
    LOADER_MAPPING: Dict[str, type[BaseLoader]] = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".docx": Docx2txtLoader,
        ".csv": CSVLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".md": TextLoader,
    }

    def __init__(self, settings, data_directory: Optional[Path] = None):
        """
        Initialize the document loader.

        Args:
            settings: Settings instance
            data_directory: Directory containing documents to load
        """
        self.settings = settings
        self.data_directory = data_directory or settings.data_directory
        self.supported_types = set(settings.supported_file_types)

        logger.info(
            "Document loader initialized",
            data_directory=str(self.data_directory),
            supported_types=list(self.supported_types),
        )

    def get_supported_files(self) -> List[Path]:
        """
        Get list of supported files in the data directory.

        Returns:
            List of file paths for supported file types
        """
        if not self.data_directory.exists():
            logger.warning(
                "Data directory does not exist",
                data_directory=str(self.data_directory),
            )
            return []

        supported_files = []
        for file_path in self.data_directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_types:
                supported_files.append(file_path)

        logger.info(
            "Found supported files",
            file_count=len(supported_files),
            files=[str(f) for f in supported_files],
        )

        return supported_files

    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load a single document from file.

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_suffix = file_path.suffix.lower()
        if file_suffix not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_suffix}")

        if file_suffix not in self.LOADER_MAPPING:
            raise ValueError(
                f"No loader available for file type: {file_suffix}",
            )

        try:
            loader_class = self.LOADER_MAPPING[file_suffix]
            loader = loader_class(str(file_path))
            documents = loader.load()

            # Add metadata
            for doc in documents:
                doc.metadata.update(
                    {
                        "source": str(file_path),
                        "file_type": file_suffix,
                        "file_name": file_path.name,
                    }
                )

            logger.info(
                "Document loaded successfully",
                file_path=str(file_path),
                document_count=len(documents),
            )

            return documents

        except Exception as e:
            logger.error(
                "Failed to load document",
                file_path=str(file_path),
                error=str(e),
            )
            raise

    def load_all_documents(self) -> List[Document]:
        """
        Load all supported documents from the data directory.

        Returns:
            List of all Document objects
        """
        supported_files = self.get_supported_files()
        all_documents = []

        for file_path in supported_files:
            try:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(
                    "Failed to load document, skipping",
                    file_path=str(file_path),
                    error=str(e),
                )
                continue

        logger.info(
            "All documents loaded",
            total_documents=len(all_documents),
            files_processed=len(supported_files),
        )

        return all_documents

    def get_file_type_summary(self) -> Dict[str, int]:
        """
        Get summary of file types in the data directory.

        Returns:
            Dictionary mapping file types to counts
        """
        supported_files = self.get_supported_files()
        type_counts = {}

        for file_path in supported_files:
            file_type = file_path.suffix.lower()
            type_counts[file_type] = type_counts.get(file_type, 0) + 1

        return type_counts

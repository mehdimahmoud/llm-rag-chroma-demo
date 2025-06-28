"""
Document loader service for loading documents from the data directory.
"""
import logging
from pathlib import Path
from typing import List

from ..core.interfaces.document_loader import DocumentLoader
from ..models.document import Document, IngestionConfig
from ..models.enums import FileType


logger = logging.getLogger(__name__)


class FileSystemDocumentLoader(DocumentLoader):
    """Loads documents from the file system."""
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the document loader.
        
        Args:
            data_directory: Path to the data directory
        """
        self.data_directory = Path(data_directory)
        logger.debug(f"Initialized FileSystemDocumentLoader with data directory: {self.data_directory}")
    
    def load_documents(self, config: IngestionConfig) -> List[Document]:
        """
        Load documents from the configured data directory.
        
        Args:
            config: Ingestion configuration
            
        Returns:
            List of loaded documents
        """
        logger.info(f"Loading documents from: {self.data_directory}")
        logger.info(f"Allowed file types: {config.get_allowed_file_types_str()}")
        
        if not self.data_directory.exists():
            logger.warning(f"Data directory does not exist: {self.data_directory}")
            return []
        
        documents = []
        
        # Recursively find all files in the data directory
        for file_path in self.data_directory.rglob('*'):
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
                                size=file_path.stat().st_size
                            )
                            documents.append(document)
                            logger.debug(f"Loaded document: {file_path.name} ({file_extension})")
                        except Exception as e:
                            logger.error(f"Failed to load document {file_path}: {e}")
                    else:
                        logger.debug(f"Skipping unsupported file: {file_path.name} ({file_extension})")
                else:
                    logger.debug(f"Skipping disallowed file type: {file_path.name} ({file_extension})")
        
        logger.info(f"Loaded {len(documents)} documents")
        
        # Log summary by file type
        file_types = {}
        for doc in documents:
            file_types[doc.file_type] = file_types.get(doc.file_type, 0) + 1
        
        for file_type, count in file_types.items():
            logger.info(f"  - {file_type}: {count} files")
        
        return documents
    
    def supports_file(self, file_path: Path) -> bool:
        """
        Check if this loader supports the given file type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file type is supported
        """
        return FileType.is_supported(file_path.suffix.lower()) 
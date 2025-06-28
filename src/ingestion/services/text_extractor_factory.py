"""
Factory for creating appropriate text extractors based on file type.
"""
from typing import List, Optional

from ..core.interfaces import TextExtractor
from ..models.document import Document
from ..models.enums import FileType
from .text_extractor import TextFileExtractor, PDFTextExtractor
from ...logging.logger import IngestionLogger


class TextExtractorFactory:
    """Factory for creating text extractors based on file type."""
    
    def __init__(self, logger: Optional[IngestionLogger] = None):
        """
        Initialize the text extractor factory.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or IngestionLogger()
        self.extractors: List[TextExtractor] = [
            TextFileExtractor(logger),
            PDFTextExtractor(logger)
        ]
    
    def get_extractor(self, document: Document) -> TextExtractor:
        """
        Get the appropriate text extractor for the given document.
        
        Args:
            document: Document to extract text from
            
        Returns:
            Appropriate text extractor
            
        Raises:
            ValueError: If no extractor supports the document type
        """
        for extractor in self.extractors:
            if extractor.supports_document(document):
                self.logger.debug(f"Using {extractor.__class__.__name__} for {document.filename}")
                return extractor
        
        raise ValueError(f"No text extractor found for file type: {document.file_type}")
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(FileType.get_all_supported())
    
    def supports_file_type(self, file_type: str) -> bool:
        """
        Check if the factory supports a given file type.
        
        Args:
            file_type: File extension (e.g., '.pdf', '.txt')
            
        Returns:
            True if the file type is supported
        """
        return FileType.is_supported(file_type) 
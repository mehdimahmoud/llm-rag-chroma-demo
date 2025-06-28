"""
Text extractor implementations for different file types.
"""
from pathlib import Path
from typing import List, Optional
from PyPDF2 import PdfReader

from ..core.interfaces import TextExtractor
from ..models.document import Document
from ..models.enums import FileType
from ...logging.logger import IngestionLogger


class TextFileExtractor(TextExtractor):
    """Text file extractor for .txt files."""
    
    def __init__(self, logger: Optional[IngestionLogger] = None):
        """
        Initialize the text file extractor.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or IngestionLogger()
    
    def extract_text(self, document: Document) -> str:
        """
        Extract text from a text file.
        
        Args:
            document: Document to extract text from
            
        Returns:
            Extracted text
        """
        try:
            self.logger.debug(f"Extracting text from {document.filename}")
            
            # Read the text file
            with open(document.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
                if not text.strip():
                    self.logger.warning(f"No text found in {document.filename}")
                    return ""
                
                self.logger.debug(f"Successfully extracted {len(text)} characters from {document.filename}")
                return text
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {document.filename}: {e}")
            raise
    
    def supports_document(self, document: Document) -> bool:
        """
        Check if this extractor supports the given document type.
        
        Args:
            document: Document to check
            
        Returns:
            True if the document type is supported
        """
        return document.file_type.lower() == FileType.TXT.value


class PDFTextExtractor(TextExtractor):
    """PDF text extractor using PyPDF2."""
    
    def __init__(self, logger: Optional[IngestionLogger] = None):
        """
        Initialize the PDF text extractor.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or IngestionLogger()
    
    def extract_text(self, document: Document) -> str:
        """
        Extract text from a PDF document.
        
        Args:
            document: Document to extract text from
            
        Returns:
            Extracted text
        """
        try:
            self.logger.debug(f"Extracting text from {document.filename}")
            
            # Open and read the PDF
            with open(document.file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                        self.logger.debug(f"Extracted text from page {page_num + 1}")
                    except Exception as e:
                        self.logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                
                # Combine all text parts
                full_text = '\n'.join(text_parts)
                
                if not full_text.strip():
                    self.logger.warning(f"No text extracted from {document.filename}")
                    return ""
                
                self.logger.debug(f"Successfully extracted {len(full_text)} characters from {document.filename}")
                return full_text
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {document.filename}: {e}")
            raise
    
    def supports_document(self, document: Document) -> bool:
        """
        Check if this extractor supports the given document type.
        
        Args:
            document: Document to check
            
        Returns:
            True if the document type is supported
        """
        return document.file_type.lower() == FileType.PDF.value 
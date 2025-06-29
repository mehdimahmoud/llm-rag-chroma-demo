"""
Text extractor implementations for different file types.
"""

import structlog
from pypdf import PdfReader

from ..core.interfaces import TextExtractor
from ..models.document import Document
from ..models.enums import FileType


class TextFileExtractor(TextExtractor):
    """Text file extractor for .txt files."""

    def __init__(self, logger=None):
        """
        Initialize the text file extractor.

        Args:
            logger: Logger instance (structlog logger)
        """
        self.logger = logger or structlog.get_logger("text_file_extractor")

    def extract_text(self, document: Document) -> str:
        """
        Extract text from a text file.

        Args:
            document: Document to extract text from

        Returns:
            Extracted text
        """
        try:
            self.logger.debug("Extracting text from file", filename=document.filename)

            # Read the text file
            with open(document.file_path, "r", encoding="utf-8") as file:
                text = file.read()

                if not text.strip():
                    self.logger.warning(
                        "No text found in file", filename=document.filename
                    )
                    return ""

                self.logger.debug(
                    "Successfully extracted text",
                    filename=document.filename,
                    text_length=len(text),
                )
                return text

        except Exception as e:
            self.logger.error(
                "Error extracting text from file",
                filename=document.filename,
                error=str(e),
            )
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
    """PDF text extractor using pypdf."""

    def __init__(self, logger=None):
        """
        Initialize the PDF text extractor.

        Args:
            logger: Logger instance (structlog logger)
        """
        self.logger = logger or structlog.get_logger("pdf_text_extractor")

    def extract_text(self, document: Document) -> str:
        """
        Extract text from a PDF document.

        Args:
            document: Document to extract text from

        Returns:
            Extracted text
        """
        try:
            self.logger.debug(
                "Extracting text from PDF file", filename=document.filename
            )

            # Open and read the PDF
            with open(document.file_path, "rb") as file:
                pdf_reader = PdfReader(file)

                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                        self.logger.debug(
                            "Extracted text from page",
                            filename=document.filename,
                            page_number=page_num + 1,
                        )
                    except Exception as e:
                        self.logger.warning(
                            "Error extracting text from page",
                            filename=document.filename,
                            page_number=page_num + 1,
                            error=str(e),
                        )

                # Combine all text parts
                full_text = "\n".join(text_parts)

                if not full_text.strip():
                    self.logger.warning(
                        "No text extracted from PDF file", filename=document.filename
                    )
                    return ""

                self.logger.debug(
                    "Successfully extracted text from PDF",
                    filename=document.filename,
                    text_length=len(full_text),
                )
                return full_text

        except Exception as e:
            self.logger.error(
                "Error extracting text from PDF file",
                filename=document.filename,
                error=str(e),
            )
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

"""
Generic PDF generation utilities.

This module provides domain-agnostic utilities for creating PDF documents
from text content, templates, and structured data.
"""
import os
from typing import List, Tuple, Dict, Any
from fpdf import FPDF


class PDFGenerator:
    """Generic PDF generation utility class."""
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize the PDF generator.
        
        Args:
            output_dir: Directory where PDF files will be saved
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_pdf_from_text(self, filename: str, content: str, font_size: int = 12) -> str:
        """
        Create a PDF file from text content.
        
        Args:
            filename: Name of the output PDF file
            content: Text content to include in the PDF
            font_size: Font size for the text
            
        Returns:
            Path to the created PDF file
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=font_size)
        
        for line in content.split("\n"):
            pdf.cell(0, 10, line, ln=1)
        
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        return filepath
    
    def create_pdf_from_template(self, filename: str, template: str, data: Dict[str, Any], font_size: int = 12) -> str:
        """
        Create a PDF file from a template with data substitution.
        
        Args:
            filename: Name of the output PDF file
            template: Template string with placeholders (e.g., {title}, {content})
            data: Dictionary with values to substitute in the template
            font_size: Font size for the text
            
        Returns:
            Path to the created PDF file
        """
        content = template.format(**data)
        return self.create_pdf_from_text(filename, content, font_size)
    
    def create_multiple_pdfs(self, documents: List[Tuple[str, str]], font_size: int = 12) -> List[str]:
        """
        Create multiple PDF files from a list of (filename, content) tuples.
        
        Args:
            documents: List of (filename, content) tuples
            font_size: Font size for the text
            
        Returns:
            List of paths to the created PDF files
        """
        created_files = []
        for filename, content in documents:
            filepath = self.create_pdf_from_text(filename, content, font_size)
            created_files.append(filepath)
        return created_files
    
    def merge_pdfs(self, input_files: List[str], output_filename: str) -> str:
        """
        Merge multiple PDF files into a single PDF.
        
        Args:
            input_files: List of input PDF file paths
            output_filename: Name of the output merged PDF file
            
        Returns:
            Path to the merged PDF file
        """
        # This is a placeholder - would need PyPDF2 or similar for actual merging
        # For now, just return the first file as an example
        if input_files:
            return input_files[0]
        return "" 
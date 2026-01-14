"""
PDF Extractor - Extract text content from PDF files
"""
from pathlib import Path
from typing import Optional


class PDFExtractor:
    """Extract text from PDF files"""
    
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            ImportError: If pypdf is not installed
            ValueError: If the file is not a valid PDF
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF support. "
                "Install it with: pip install pypdf>=3.0.0"
            )
        
        try:
            reader = PdfReader(pdf_path)
            text_parts = []
            
            # Extract text from all pages
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return '\n'.join(text_parts)
        
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

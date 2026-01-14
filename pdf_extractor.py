"""
PDF Text Extractor - Extract text content from PDF files
"""
from pathlib import Path
from typing import Union
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


class PDFExtractor:
    """Extract text from PDF files"""
    
    def __init__(self):
        """Initialize PDF extractor"""
        if PdfReader is None:
            raise ImportError(
                "pypdf library is required for PDF support. "
                "Install it with: pip install pypdf"
            )
    
    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            # Extract text from all pages
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

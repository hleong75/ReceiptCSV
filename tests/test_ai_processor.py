"""
Tests for AI-powered receipt processing
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_processor import AIProcessor, AIExtractedData
from receipt_parser import ReceiptParser


class TestAIProcessor(unittest.TestCase):
    """Test AI processor functionality"""
    
    def test_ai_processor_init_without_key(self):
        """Test AI processor initialization without API key"""
        # Clear any existing API key
        old_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        processor = AIProcessor()
        self.assertFalse(processor.is_enabled())
        
        # Restore key if it existed
        if old_key:
            os.environ['OPENAI_API_KEY'] = old_key
    
    def test_ai_processor_init_with_key(self):
        """Test AI processor initialization with API key"""
        # Skip if openai is not installed
        try:
            import openai
            with patch('openai.OpenAI') as mock_openai:
                processor = AIProcessor(api_key='test-key')
                # Should try to initialize OpenAI client
                mock_openai.assert_called_once_with(api_key='test-key')
        except ImportError:
            self.skipTest("OpenAI library not installed")
    
    def test_extract_receipt_data_disabled(self):
        """Test extraction when AI is disabled"""
        processor = AIProcessor()
        processor.enabled = False
        
        result = processor.extract_receipt_data("Test receipt")
        self.assertIsNone(result)
    
    def test_extract_receipt_data_with_ai(self):
        """Test extraction with AI enabled"""
        # Skip if openai is not installed
        try:
            import openai
        except ImportError:
            self.skipTest("OpenAI library not installed")
            return
        
        # Setup mock
        with patch('openai.OpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '''{
                "date": "2024-03-15",
                "merchant": "Test Store",
                "products": [
                    {"name": "Product A", "quantity": 1.0, "unit_price": 9.99, "subtotal": 9.99}
                ],
                "discounts": [],
                "payments": [{"method": "Card", "amount": 9.99}],
                "total": 9.99,
                "currency": "EUR"
            }'''
            
            mock_client.chat.completions.create.return_value = mock_response
            
            processor = AIProcessor(api_key='test-key')
            
            result = processor.extract_receipt_data("Test receipt text")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.date, "2024-03-15")
            self.assertEqual(result.merchant, "Test Store")
            self.assertEqual(len(result.products), 1)
            self.assertEqual(result.products[0]['name'], "Product A")


class TestReceiptParserWithAI(unittest.TestCase):
    """Test receipt parser with AI integration"""
    
    def test_parser_without_ai(self):
        """Test parser works without AI enabled"""
        parser = ReceiptParser(use_ai=False)
        self.assertIsNone(parser.ai_processor)
        
        text = """2024-03-15
App Store
Application A    1 x 9.99    9.99
Paiement: Apple Pay    9.99
"""
        receipt = parser.parse(text)
        self.assertEqual(receipt.date, "2024-03-15")
        self.assertEqual(receipt.merchant, "App Store")
        self.assertEqual(len(receipt.products), 1)
    
    def test_parser_with_ai_disabled(self):
        """Test parser with AI enabled but no API key"""
        old_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        parser = ReceiptParser(use_ai=True)
        # Should fall back to traditional parsing
        
        text = """2024-03-15
App Store
Application A    1 x 9.99    9.99
"""
        receipt = parser.parse(text)
        self.assertEqual(receipt.date, "2024-03-15")
        
        if old_key:
            os.environ['OPENAI_API_KEY'] = old_key
    
    @patch('receipt_parser.AIProcessor')
    def test_parser_with_ai_fallback(self, mock_ai_class):
        """Test parser falls back to traditional parsing if AI fails"""
        mock_processor = MagicMock()
        mock_processor.is_enabled.return_value = True
        mock_processor.extract_receipt_data.return_value = None  # AI fails
        mock_ai_class.return_value = mock_processor
        
        parser = ReceiptParser(use_ai=True)
        parser.ai_processor = mock_processor
        
        text = """2024-03-15
App Store
Application A    1 x 9.99    9.99
"""
        receipt = parser.parse(text)
        # Should still parse successfully with traditional method
        self.assertEqual(receipt.date, "2024-03-15")
    
    @patch('receipt_parser.AIProcessor')
    def test_parser_discount_type_with_ai(self, mock_ai_class):
        """Test discount type identification with AI"""
        mock_processor = MagicMock()
        mock_processor.is_enabled.return_value = True
        mock_processor.extract_receipt_data.return_value = None
        mock_processor.identify_discount_type.return_value = "Loyalty Reward"
        mock_ai_class.return_value = mock_processor
        
        parser = ReceiptParser(use_ai=True)
        parser.ai_processor = mock_processor
        
        text = """2024-03-15
Store
Product A    10.00
Special Customer Discount    -2.00
"""
        receipt = parser.parse(text)
        # Check if AI-identified discount type is used
        if receipt.products:
            # Discount might be on product or global
            has_discount = (receipt.products[0].discount_type == "Loyalty Reward" or
                          any(dtype == "Loyalty Reward" for dtype, _ in receipt.global_discounts))
            self.assertTrue(has_discount)


class TestAIExtractedData(unittest.TestCase):
    """Test AIExtractedData dataclass"""
    
    def test_ai_extracted_data_defaults(self):
        """Test default values for AIExtractedData"""
        data = AIExtractedData()
        self.assertEqual(data.products, [])
        self.assertEqual(data.discounts, [])
        self.assertEqual(data.payments, [])
        self.assertEqual(data.merchant, "")
        self.assertEqual(data.date, "")
        self.assertEqual(data.total, 0.0)
        self.assertEqual(data.confidence, 0.0)
    
    def test_ai_extracted_data_with_values(self):
        """Test AIExtractedData with values"""
        data = AIExtractedData(
            products=[{"name": "Test", "quantity": 1.0}],
            merchant="Test Store",
            date="2024-03-15",
            confidence=0.9
        )
        self.assertEqual(len(data.products), 1)
        self.assertEqual(data.merchant, "Test Store")
        self.assertEqual(data.confidence, 0.9)


if __name__ == '__main__':
    unittest.main()

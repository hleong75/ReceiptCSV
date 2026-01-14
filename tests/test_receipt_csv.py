"""
Tests for receipt CSV extraction
"""
import unittest
from receipt_parser import ReceiptParser, Product
from csv_generator import CSVGenerator


class TestReceiptParser(unittest.TestCase):
    """Test receipt parsing functionality"""
    
    def setUp(self):
        self.parser = ReceiptParser()
    
    def test_date_extraction_iso_format(self):
        """Test date extraction in YYYY-MM-DD format"""
        text = "2024-03-15\nApp Store"
        receipt = self.parser.parse(text)
        self.assertEqual(receipt.date, "2024-03-15")
    
    def test_date_extraction_european_format(self):
        """Test date extraction in DD/MM/YYYY format"""
        text = "15/12/2023\nAmazon"
        receipt = self.parser.parse(text)
        self.assertEqual(receipt.date, "2023-12-15")
    
    def test_merchant_extraction(self):
        """Test merchant name extraction"""
        text = "2024-03-15\nApp Store\nProduct A    9.99"
        receipt = self.parser.parse(text)
        self.assertEqual(receipt.merchant, "App Store")
    
    def test_product_extraction(self):
        """Test product extraction"""
        text = "Application A    1 x 9.99    9.99"
        receipt = self.parser.parse(text)
        self.assertEqual(len(receipt.products), 1)
        self.assertEqual(receipt.products[0].name, "Application A")
        self.assertEqual(receipt.products[0].quantity, 1.0)
        self.assertEqual(receipt.products[0].unit_price, 9.99)
        self.assertEqual(receipt.products[0].subtotal, 9.99)
    
    def test_payment_method_extraction(self):
        """Test payment method extraction"""
        text = "Paiement: Apple Pay    10.98"
        receipt = self.parser.parse(text)
        self.assertEqual(len(receipt.payment_methods), 1)
        self.assertEqual(receipt.payment_methods[0][0], "Apple Pay")
        self.assertEqual(receipt.payment_methods[0][1], 10.98)
    
    def test_discount_extraction(self):
        """Test discount extraction"""
        text = "Coupon    -2.00"
        receipt = self.parser.parse(text)
        self.assertEqual(len(receipt.global_discounts), 1)
        self.assertEqual(receipt.global_discounts[0][0], "Coupon")
        self.assertEqual(receipt.global_discounts[0][1], 2.00)


class TestCSVGenerator(unittest.TestCase):
    """Test CSV generation functionality"""
    
    def setUp(self):
        self.generator = CSVGenerator()
    
    def test_csv_header(self):
        """Test CSV header generation"""
        from receipt_parser import Receipt
        receipt = Receipt()
        csv_output = self.generator.generate(receipt)
        lines = csv_output.strip().split('\n')
        self.assertTrue(len(lines) >= 1)
        self.assertIn("Date d'achat", lines[0])
    
    def test_csv_separator(self):
        """Test CSV uses semicolon separator"""
        from receipt_parser import Receipt, Product
        receipt = Receipt(
            date="2024-03-15",
            merchant="Test Store",
            products=[Product(name="Product A", quantity=1, unit_price=9.99, subtotal=9.99)]
        )
        csv_output = self.generator.generate(receipt)
        self.assertIn(';', csv_output)
    
    def test_single_product_single_payment(self):
        """Test CSV generation with single product and payment"""
        from receipt_parser import Receipt, Product
        receipt = Receipt(
            date="2024-03-15",
            merchant="App Store",
            products=[Product(name="App A", quantity=1, unit_price=9.99, subtotal=9.99)],
            payment_methods=[("Apple Pay", 9.99)]
        )
        csv_output = self.generator.generate(receipt)
        lines = csv_output.strip().split('\n')
        self.assertEqual(len(lines), 2)  # Header + 1 product
    
    def test_multiple_payment_methods(self):
        """Test CSV generation with multiple payment methods"""
        from receipt_parser import Receipt, Product
        receipt = Receipt(
            date="2024-04-20",
            merchant="Store",
            products=[
                Product(name="Product A", quantity=1, unit_price=14.99, subtotal=14.99),
                Product(name="Product B", quantity=1, unit_price=3.49, subtotal=3.49)
            ],
            payment_methods=[("CB Visa", 12.73), ("PayPal", 4.25)]
        )
        csv_output = self.generator.generate(receipt)
        lines = csv_output.strip().split('\n')
        # Header + (2 products * 2 payment methods) = 5 lines
        self.assertEqual(len(lines), 5)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_receipt_processing(self):
        """Test full receipt processing from text to CSV"""
        receipt_text = """2024-03-15
App Store
Application A    1 x 9.99    9.99
Application B    2.99
Paiement: Apple Pay    12.98
"""
        parser = ReceiptParser()
        generator = CSVGenerator()
        
        receipt = parser.parse(receipt_text)
        csv_output = generator.generate(receipt)
        
        lines = csv_output.strip().split('\n')
        self.assertTrue(len(lines) >= 2)  # At least header + 1 product
        
        # Verify header
        self.assertIn("Date d'achat", lines[0])
        
        # Verify data row exists
        self.assertIn("2024-03-15", lines[1])


if __name__ == '__main__':
    unittest.main()

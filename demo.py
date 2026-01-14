#!/usr/bin/env python3
"""
Demo script showing how to use the receipt CSV extractor
"""

from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator


def demo_simple_receipt():
    """Demo with a simple receipt"""
    print("=" * 60)
    print("DEMO 1: Simple receipt with one payment method")
    print("=" * 60)
    
    receipt_text = """
2024-03-15
App Store
Application A    1 x 9.99    9.99
Application B    2.99
Paiement: Apple Pay    12.98
"""
    
    parser = ReceiptParser()
    generator = CSVGenerator()
    
    receipt = parser.parse(receipt_text)
    csv_output = generator.generate(receipt)
    
    print("\nInput:")
    print(receipt_text)
    print("\nOutput:")
    print(csv_output)


def demo_multiple_payments():
    """Demo with multiple payment methods"""
    print("=" * 60)
    print("DEMO 2: Receipt with multiple payment methods")
    print("=" * 60)
    
    receipt_text = """
2024-04-20
Google Play Store
Abonnement Premium    1 x 14.99    14.99
Jeu Mobile    3.49
Réduction Totale    -1.50
CB Visa    12.73
PayPal    4.25
"""
    
    parser = ReceiptParser()
    generator = CSVGenerator()
    
    receipt = parser.parse(receipt_text)
    csv_output = generator.generate(receipt)
    
    print("\nInput:")
    print(receipt_text)
    print("\nOutput:")
    print(csv_output)
    print("\nNote: Each product is distributed proportionally across payment methods")
    print("      CB Visa paid 75% (12.73/16.98), PayPal paid 25% (4.25/16.98)")


def demo_with_discounts():
    """Demo with product and global discounts"""
    print("=" * 60)
    print("DEMO 3: Receipt with product-specific and global discounts")
    print("=" * 60)
    
    receipt_text = """
2024-06-10
Netflix France
Abonnement Standard    1 x 13.49    13.49
Location Film Premium    4.99
Coupon Nouveau Client    -5.00
Réduction Totale    -2.00
Carte Visa    8.24
PayPal    3.24
"""
    
    parser = ReceiptParser()
    generator = CSVGenerator()
    
    receipt = parser.parse(receipt_text)
    csv_output = generator.generate(receipt)
    
    print("\nInput:")
    print(receipt_text)
    print("\nOutput:")
    print(csv_output)
    print("\nNote: Product discounts are applied to the preceding product")
    print("      Global discounts are distributed proportionally across all products")


if __name__ == '__main__':
    demo_simple_receipt()
    print("\n\n")
    demo_multiple_payments()
    print("\n\n")
    demo_with_discounts()

"""
Example demonstrating AI-powered receipt processing

This script shows how to use the AI processor to handle
noisy OCR output and extract structured data intelligently.

Note: Run from the repository root: python examples/ai_demo.py
"""

import sys
import os

# Add parent directory to path (needed when running from examples/ subdirectory)
# In production, install the package properly instead
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator


def example_traditional_parsing():
    """Example using traditional parsing (no AI)"""
    print("=" * 60)
    print("EXEMPLE 1: Parsing traditionnel (sans IA)")
    print("=" * 60)
    
    receipt_text = """2024-03-15
App Store
Application A    1 x 9.99    9.99
Application B    2.99
Coupon App A    -2.00
Paiement: Apple Pay    10.98
"""
    
    parser = ReceiptParser(use_ai=False)
    generator = CSVGenerator()
    
    receipt = parser.parse(receipt_text)
    csv_output = generator.generate(receipt)
    
    print("\nReçu original:")
    print(receipt_text)
    print("\nRésultat CSV:")
    print(csv_output)


def example_ai_parsing():
    """Example using AI-powered parsing"""
    print("\n" + "=" * 60)
    print("EXEMPLE 2: Parsing avec IA (si clé API disponible)")
    print("=" * 60)
    
    # Simulate noisy OCR output
    noisy_receipt = """2O24-O3-15
App St0re
Applicati0n A    l x 9.99    9.99
Applicati0n B    2.99
C0up0n App A    -2.OO
Paiement: Apple Pay    lO.98
"""
    
    parser = ReceiptParser(use_ai=True)
    generator = CSVGenerator()
    
    if not parser.ai_processor:
        print("\nINFO: IA non disponible (pas de clé API)")
        print("Le système utilisera le parsing traditionnel")
        print("Pour activer l'IA, définir OPENAI_API_KEY")
    else:
        print("\nINFO: IA activée ✓")
    
    receipt = parser.parse(noisy_receipt)
    csv_output = generator.generate(receipt)
    
    print("\nReçu OCR bruité:")
    print(noisy_receipt)
    print("\nRésultat CSV:")
    print(csv_output)


def example_discount_type_detection():
    """Example showing intelligent discount type detection"""
    print("\n" + "=" * 60)
    print("EXEMPLE 3: Identification intelligente des réductions")
    print("=" * 60)
    
    receipt_text = """2024-06-01
Amazon
Livre Python    24.99
Réduction Membres Premium    -5.00
Film Blu-ray    15.99
Offre Black Friday    -3.00
Paiement: Carte Visa    32.98
"""
    
    parser = ReceiptParser(use_ai=True)
    generator = CSVGenerator()
    
    receipt = parser.parse(receipt_text)
    csv_output = generator.generate(receipt)
    
    print("\nReçu avec réductions variées:")
    print(receipt_text)
    print("\nRésultat CSV (types de réductions identifiés):")
    print(csv_output)
    
    if parser.ai_processor:
        print("\n💡 Avec l'IA, les types de réduction sont mieux catégorisés")
    else:
        print("\n💡 Sans IA, détection basique des types de réduction")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("DÉMONSTRATION DES CAPACITÉS IA DE ReceiptCSV")
    print("=" * 60)
    print()
    
    # Check if AI is available
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✓ Clé API OpenAI détectée - IA activée")
    else:
        print("⚠ Pas de clé API OpenAI - Mode traditionnel uniquement")
        print("  Pour activer l'IA:")
        print("  export OPENAI_API_KEY='votre-clé'")
    
    print()
    
    # Run examples
    example_traditional_parsing()
    example_ai_parsing()
    example_discount_type_detection()
    
    print("\n" + "=" * 60)
    print("FIN DES EXEMPLES")
    print("=" * 60)
    print("\nPour plus d'informations, consultez le README.md")


if __name__ == '__main__':
    main()

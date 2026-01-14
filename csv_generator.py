"""
CSV Generator - Generate CSV output from parsed receipts
"""
import csv
from io import StringIO
from typing import List
from receipt_parser import Receipt, Product


class CSVGenerator:
    """Generate CSV from receipt data"""
    
    COLUMNS = [
        "Date d'achat",
        "Nom de l'application / marchand",
        "Nom du produit",
        "Quantité",
        "Prix unitaire",
        "Sous-total produit",
        "Type de réduction",
        "Montant de la réduction",
        "Moyen de paiement",
        "Devise"
    ]
    
    def generate(self, receipt: Receipt) -> str:
        """
        Generate CSV from receipt
        
        Returns CSV content as string with:
        - Semicolon separator
        - One line per product (or per product per payment method if multiple)
        - Proportional distribution for multiple payment methods and global discounts
        """
        output = StringIO()
        writer = csv.writer(output, delimiter=';', lineterminator='\n')
        
        # Write header
        writer.writerow(self.COLUMNS)
        
        # If no payment methods specified, assume one payment for the total
        payment_methods = receipt.payment_methods if receipt.payment_methods else [("", receipt.get_total_with_discounts())]
        
        # Calculate total for proportional distribution
        total = receipt.get_total()
        total_after_discounts = receipt.get_total_with_discounts()
        total_payment = sum(amount for _, amount in payment_methods)
        
        # Distribute global discounts proportionally to products
        products_with_global_discounts = self._apply_global_discounts(receipt)
        
        # Generate rows
        for product in products_with_global_discounts:
            # Calculate product's share after its discounts
            product_after_discount = product.subtotal - product.discount_amount
            
            if len(payment_methods) == 1:
                # Single payment method: one line per product
                row = self._create_row(receipt, product, payment_methods[0][0])
                writer.writerow(row)
            else:
                # Multiple payment methods: one line per product per payment method
                # Distribute the product amount proportionally across payment methods
                for method, method_amount in payment_methods:
                    # Calculate the proportion of this payment method
                    method_ratio = method_amount / total_payment if total_payment > 0 else 0
                    
                    # Create a product with proportional amounts
                    proportional_product = Product(
                        name=product.name,
                        quantity=product.quantity,
                        unit_price=product.unit_price,
                        subtotal=product.subtotal * method_ratio,
                        discount_type=product.discount_type,
                        discount_amount=product.discount_amount * method_ratio
                    )
                    row = self._create_row(receipt, proportional_product, method)
                    writer.writerow(row)
        
        return output.getvalue()
    
    def _apply_global_discounts(self, receipt: Receipt) -> List[Product]:
        """Apply global discounts proportionally to products"""
        products = []
        total = receipt.get_total()
        total_global_discount = sum(amount for _, amount in receipt.global_discounts)
        
        for product in receipt.products:
            # Create a copy of the product
            new_product = Product(
                name=product.name,
                quantity=product.quantity,
                unit_price=product.unit_price,
                subtotal=product.subtotal,
                discount_type=product.discount_type,
                discount_amount=product.discount_amount
            )
            
            # Add proportional global discount
            if total > 0 and total_global_discount > 0:
                product_ratio = product.subtotal / total
                proportional_discount = total_global_discount * product_ratio
                
                if new_product.discount_amount > 0:
                    # Combine with existing discount
                    new_product.discount_amount += proportional_discount
                    if receipt.global_discounts:
                        global_type = receipt.global_discounts[0][0]
                        new_product.discount_type = f"{new_product.discount_type}, {global_type}"
                else:
                    # Set global discount
                    new_product.discount_amount = proportional_discount
                    if receipt.global_discounts:
                        new_product.discount_type = receipt.global_discounts[0][0]
            
            products.append(new_product)
        
        return products
    
    def _create_row(self, receipt: Receipt, product: Product, payment_method: str) -> List[str]:
        """Create a CSV row for a product"""
        return [
            receipt.date,
            receipt.merchant,
            product.name,
            self._format_number(product.quantity),
            self._format_number(product.unit_price),
            self._format_number(product.subtotal),
            product.discount_type,
            self._format_number(product.discount_amount) if product.discount_amount > 0 else "",
            payment_method,
            receipt.currency
        ]
    
    def _format_number(self, value: float) -> str:
        """Format number with . as decimal separator"""
        if value == 0:
            return ""
        # Remove trailing zeros and unnecessary decimal point
        formatted = f"{value:.2f}".rstrip('0').rstrip('.')
        # If it's a whole number, add .0 for clarity, or return as is
        if '.' not in formatted and value != int(value):
            formatted = f"{value:.2f}"
        return formatted

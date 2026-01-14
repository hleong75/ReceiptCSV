"""
Receipt Parser - Extract structured data from receipts
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
try:
    from ai_processor import AIProcessor
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIProcessor = None


@dataclass
class Product:
    """Represents a product on a receipt"""
    name: str
    quantity: float = 1.0
    unit_price: float = 0.0
    subtotal: float = 0.0
    discount_type: str = ""
    discount_amount: float = 0.0


@dataclass
class Receipt:
    """Represents a parsed receipt"""
    date: str = ""  # YYYY-MM-DD format
    merchant: str = ""
    products: List[Product] = field(default_factory=list)
    payment_methods: List[Tuple[str, float]] = field(default_factory=list)  # (method, amount)
    global_discounts: List[Tuple[str, float]] = field(default_factory=list)  # (type, amount)
    currency: str = "EUR"
    
    def get_total(self) -> float:
        """Calculate total before global discounts"""
        return sum(p.subtotal for p in self.products)
    
    def get_total_with_discounts(self) -> float:
        """Calculate total after all discounts"""
        total = self.get_total()
        # Subtract product-level discounts
        total -= sum(p.discount_amount for p in self.products)
        # Subtract global discounts
        total -= sum(amount for _, amount in self.global_discounts)
        return total


class ReceiptParser:
    """Parse receipts from text format"""
    
    def __init__(self, use_ai: bool = True, ai_api_key: Optional[str] = None):
        """
        Initialize receipt parser
        
        Args:
            use_ai: Enable AI-powered enhancement (default: True if API key available)
            ai_api_key: OpenAI API key for AI processing (optional, uses env var if not provided)
        """
        self.ai_processor = None
        if use_ai and AI_AVAILABLE:
            self.ai_processor = AIProcessor(api_key=ai_api_key)
            if not self.ai_processor.is_enabled():
                self.ai_processor = None
    
    def parse(self, text: str, use_ai_fallback: bool = True) -> Receipt:
        """
        Parse receipt text and extract structured data
        
        Expected format (flexible):
        - Date line (various formats)
        - Merchant name
        - Products (name, quantity, price)
        - Discounts
        - Payment methods
        
        Args:
            text: Receipt text to parse
            use_ai_fallback: Use AI to extract data if enabled (default: True)
        """
        receipt = Receipt()
        
        # Try AI extraction first if enabled
        if use_ai_fallback and self.ai_processor:
            ai_data = self.ai_processor.extract_receipt_data(text)
            if ai_data and ai_data.confidence > 0.5:
                # Use AI-extracted data
                receipt = self._convert_ai_to_receipt(ai_data)
                return receipt
        
        # Fallback to traditional parsing
        lines = text.strip().split('\n')
        
        # Parse line by line
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Try to extract date
            if not receipt.date:
                date = self._extract_date(line)
                if date:
                    receipt.date = date
                    i += 1
                    continue
            
            # Try to extract merchant
            if not receipt.merchant and not self._is_product_line(line):
                # First non-date line could be merchant
                if not any(keyword in line.lower() for keyword in ['total', 'subtotal', 'tax', 'payment']):
                    receipt.merchant = line
                    i += 1
                    continue
            
            # Try to extract discount (check before payment - more specific)
            discount = self._extract_discount(line)
            if discount:
                discount_type, amount = discount
                # Check if this is a product-specific discount or global
                # For now, treat standalone discounts as global
                if receipt.products and not self._is_global_discount(line):
                    # Apply to last product
                    last_product = receipt.products[-1]
                    if last_product.discount_amount > 0:
                        # Already has a discount - combine them
                        last_product.discount_amount += amount
                        last_product.discount_type = f"{last_product.discount_type}, {discount_type}"
                    else:
                        # First discount for this product
                        last_product.discount_type = discount_type
                        last_product.discount_amount = amount
                else:
                    receipt.global_discounts.append((discount_type, amount))
                i += 1
                continue
            
            # Try to extract payment method (check after discount)
            if self._is_payment_line(line):
                method, amount = self._extract_payment(line)
                if method:
                    receipt.payment_methods.append((method, amount))
                i += 1
                continue
            
            # Try to extract product
            product = self._extract_product(line)
            if product:
                receipt.products.append(product)
                i += 1
                continue
            
            i += 1
        
        return receipt
    
    def _extract_date(self, line: str) -> Optional[str]:
        """Extract date from line and convert to YYYY-MM-DD"""
        # Try various date formats
        patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{2})-(\d{2})-(\d{4})',  # DD-MM-YYYY
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})',  # DD Month YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if pattern == patterns[0]:  # Already in correct format
                    return match.group(0)
                elif pattern in [patterns[1], patterns[2]]:  # DD/MM/YYYY or DD-MM-YYYY
                    day, month, year = match.groups()
                    return f"{year}-{month}-{day}"
                elif pattern == patterns[3]:  # DD Month YYYY
                    day, month_name, year = match.groups()
                    month_map = {
                        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                    }
                    month = month_map.get(month_name[:3].lower(), '01')
                    return f"{year}-{month}-{day.zfill(2)}"
        
        return None
    
    def _is_product_line(self, line: str) -> bool:
        """Check if line contains product information"""
        # Look for price patterns
        return bool(re.search(r'\d+[.,]\d{2}', line))
    
    def _extract_product(self, line: str) -> Optional[Product]:
        """Extract product from line"""
        # Try AI-enhanced extraction first if available
        if self.ai_processor:
            # For now, we'll use traditional parsing
            # AI enhancement can be added for specific edge cases
            pass
        
        # Pattern: Product name [quantity x] unit_price [subtotal]
        # Examples:
        # "Product A    1 x 10.00    10.00"
        # "Product B    2.5 x 5.00   12.50"
        # "Product C    15.00"
        
        # Try to find prices (with , or . as decimal separator)
        prices = re.findall(r'(\d+)[.,](\d{2})', line)
        if not prices:
            return None
        
        # Convert prices to float
        price_values = [float(f"{p[0]}.{p[1]}") for p in prices]
        
        # Try to extract quantity
        quantity_match = re.search(r'(\d+(?:[.,]\d+)?)\s*x', line, re.IGNORECASE)
        quantity = float(quantity_match.group(1).replace(',', '.')) if quantity_match else 1.0
        
        # Extract product name
        if quantity_match:
            # If there's a quantity, name is everything before it
            name = line[:quantity_match.start()].strip()
        else:
            # Otherwise, name is everything before the first price
            name_match = re.match(r'(.+?)(?=\d+[.,]\d{2})', line)
            name = name_match.group(1).strip() if name_match else line.split()[0]
        
        # Determine unit price and subtotal
        if len(price_values) >= 2:
            unit_price = price_values[0]
            subtotal = price_values[-1]
        elif len(price_values) == 1:
            subtotal = price_values[0]
            # Calculate unit price from subtotal and quantity
            # If quantity is 0 or invalid, use subtotal as unit price
            if quantity > 0:
                unit_price = subtotal / quantity
            else:
                # Edge case: quantity is 0, treat it as 1
                unit_price = subtotal
                quantity = 1.0
        else:
            return None
        
        return Product(
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
    
    def _is_payment_line(self, line: str) -> bool:
        """Check if line contains payment method information"""
        payment_keywords = [
            'carte', 'card', 'visa', 'mastercard', 'cb',
            'apple pay', 'paypal', 'espèces', 'cash',
            'solde', 'balance', 'crédit', 'credit',
            'paiement', 'payment', 'payé', 'paid'
        ]
        return any(keyword in line.lower() for keyword in payment_keywords)
    
    def _extract_payment(self, line: str) -> Tuple[Optional[str], float]:
        """Extract payment method and amount"""
        # Extract amount
        prices = re.findall(r'(\d+)[.,](\d{2})', line)
        if not prices:
            return None, 0.0
        
        amount = float(f"{prices[-1][0]}.{prices[-1][1]}")
        
        # Extract method name (everything before the amount)
        price_str = f"{prices[-1][0]}{'.' if '.' in line else ','}{prices[-1][1]}"
        method = line.split(price_str)[0].strip()
        # Clean up common prefixes
        method = re.sub(r'^(paiement|payment|payé|paid)\s*[:;]?\s*', '', method, flags=re.IGNORECASE).strip()
        
        return method, amount
    
    def _extract_discount(self, line: str) -> Optional[Tuple[str, float]]:
        """Extract discount information"""
        discount_keywords = [
            'réduction', 'reduction', 'remise', 'discount',
            'coupon', 'promo', 'promotion', 'crédit', 'credit',
            'rabais', 'offre'
        ]
        
        if not any(keyword in line.lower() for keyword in discount_keywords):
            return None
        
        # Extract amount (must have negative sign for discounts)
        # Check for negative sign first
        has_negative = '-' in line
        if not has_negative:
            return None  # Discounts must be negative
        
        prices = re.findall(r'-?\s*(\d+)[.,](\d{2})', line)
        if not prices:
            return None
        
        amount = float(f"{prices[-1][0]}.{prices[-1][1]}")
        # Amount should always be positive (absolute value)
        amount = abs(amount)
        
        # Determine discount type - use AI if available for better categorization
        discount_type = "Réduction"
        if self.ai_processor:
            ai_type = self.ai_processor.identify_discount_type(line)
            if ai_type:
                discount_type = ai_type
        else:
            # Traditional keyword matching
            for keyword in discount_keywords:
                if keyword in line.lower():
                    discount_type = keyword.capitalize()
                    break
        
        return discount_type, amount
    
    def _is_global_discount(self, line: str) -> bool:
        """Check if discount is global (not product-specific)"""
        # Global discounts usually contain words like "total", "order", "facture"
        global_keywords = ['total', 'order', 'facture', 'commande']
        return any(keyword in line.lower() for keyword in global_keywords)
    
    def _convert_ai_to_receipt(self, ai_data) -> Receipt:
        """
        Convert AI-extracted data to Receipt object
        
        Args:
            ai_data: AIExtractedData object from AI processor
            
        Returns:
            Receipt object
        """
        receipt = Receipt(
            date=ai_data.date,
            merchant=ai_data.merchant,
            currency=ai_data.currency if hasattr(ai_data, 'currency') else "EUR"
        )
        
        # Convert products
        for prod_dict in ai_data.products:
            product = Product(
                name=prod_dict.get('name', ''),
                quantity=float(prod_dict.get('quantity', 1.0)),
                unit_price=float(prod_dict.get('unit_price', 0.0)),
                subtotal=float(prod_dict.get('subtotal', 0.0))
            )
            receipt.products.append(product)
        
        # Convert discounts
        for disc_dict in ai_data.discounts:
            discount_type = disc_dict.get('type', 'Discount')
            amount = float(disc_dict.get('amount', 0.0))
            product_index = disc_dict.get('product_index', None)
            
            if product_index is not None and 0 <= product_index < len(receipt.products):
                # Product-specific discount
                receipt.products[product_index].discount_type = discount_type
                receipt.products[product_index].discount_amount = amount
            else:
                # Global discount
                receipt.global_discounts.append((discount_type, amount))
        
        # Convert payment methods
        for pay_dict in ai_data.payments:
            method = pay_dict.get('method', '')
            amount = float(pay_dict.get('amount', 0.0))
            receipt.payment_methods.append((method, amount))
        
        return receipt

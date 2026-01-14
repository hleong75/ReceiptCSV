"""
AI Processor - Intelligent post-OCR data extraction using AI
"""
import re
import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AIExtractedData:
    """Represents data extracted by AI from receipt text"""
    products: List[Dict[str, Any]] = None
    discounts: List[Dict[str, Any]] = None
    payments: List[Dict[str, Any]] = None
    merchant: str = ""
    date: str = ""
    total: float = 0.0
    currency: str = "EUR"
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.products is None:
            self.products = []
        if self.discounts is None:
            self.discounts = []
        if self.payments is None:
            self.payments = []


class AIProcessor:
    """
    AI-powered receipt data processor
    
    Uses AI to intelligently extract and structure receipt data,
    particularly useful for noisy OCR output or complex receipt formats.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize AI processor
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model: Model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.enabled = bool(self.api_key)
        
        # Try to import OpenAI library if enabled
        if self.enabled:
            try:
                import openai
                self.openai = openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                self.enabled = False
                self.openai = None
                self.client = None
    
    def is_enabled(self) -> bool:
        """Check if AI processing is enabled"""
        return self.enabled
    
    def extract_receipt_data(self, text: str) -> Optional[AIExtractedData]:
        """
        Extract receipt data using AI
        
        Args:
            text: Raw receipt text (potentially from OCR)
            
        Returns:
            AIExtractedData object with extracted information, or None if AI is disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Create prompt for AI extraction
            prompt = self._create_extraction_prompt(text)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured data from receipts. "
                                 "Extract product names, prices, quantities, discounts, payment methods, "
                                 "merchant name, and date. Return data in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = response.choices[0].message.content
            return self._parse_ai_response(result)
            
        except Exception as e:
            # If AI fails, return None (will fallback to traditional parsing)
            logger.warning(f"AI processing failed: {e}")
            return None
    
    def enhance_product_detection(self, line: str, context: List[str]) -> Optional[Dict[str, Any]]:
        """
        Use AI to enhance product detection from a single line
        
        Args:
            line: Line of text that might contain product information
            context: Surrounding lines for context
            
        Returns:
            Dictionary with product information or None
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Analyze this line from a receipt and extract product information if present.
Context (previous lines):
{chr(10).join(context[-3:]) if context else 'None'}

Line to analyze:
{line}

Extract:
- Product name
- Quantity (default 1 if not specified)
- Unit price
- Total/subtotal price
- Any discount mentioned

Return JSON with keys: name, quantity, unit_price, subtotal, has_product (boolean).
If no product is found, set has_product to false."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying products in receipt text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            if result.get('has_product', False):
                return result
            return None
            
        except Exception as e:
            logger.debug(f"AI product detection failed: {e}")
            return None
    
    def identify_discount_type(self, text: str) -> Optional[str]:
        """
        Use AI to identify the type of discount from text
        
        Args:
            text: Discount line text
            
        Returns:
            Discount type (e.g., "Coupon", "Promotion", "Loyalty") or None
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Identify the type of discount from this text:
"{text}"

Common types: Coupon, Promotion, Promo, Loyalty, Seasonal Sale, Clearance, Bundle Discount, Employee Discount, etc.

Return JSON with key "discount_type" containing a single word or short phrase."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing retail discounts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get('discount_type', None)
            
        except Exception as e:
            logger.debug(f"AI discount type identification failed: {e}")
            return None
    
    def extract_price_from_noisy_text(self, text: str) -> Optional[float]:
        """
        Extract price from noisy OCR text using AI
        
        Args:
            text: Potentially noisy text containing a price
            
        Returns:
            Extracted price as float or None
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Extract the price/monetary amount from this text (which may contain OCR errors):
"{text}"

Common OCR errors:
- O (letter) vs 0 (zero)
- l (lowercase L) vs 1 (one)
- S vs 5
- Comma vs period for decimals

Return JSON with key "price" as a number (use period as decimal separator).
If no price found, return {{"price": null}}."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at correcting OCR errors in prices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            price = result.get('price', None)
            
            if price is not None:
                return float(price)
            return None
            
        except Exception as e:
            logger.debug(f"AI price extraction failed: {e}")
            return None
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create prompt for full receipt extraction"""
        return f"""Extract all information from this receipt:

{text}

Return JSON with this structure:
{{
    "date": "YYYY-MM-DD format",
    "merchant": "Store/merchant name",
    "products": [
        {{
            "name": "Product name",
            "quantity": 1.0,
            "unit_price": 9.99,
            "subtotal": 9.99
        }}
    ],
    "discounts": [
        {{
            "type": "Coupon/Promotion/etc",
            "amount": 2.00,
            "product_index": null or index of product it applies to
        }}
    ],
    "payments": [
        {{
            "method": "Payment method name",
            "amount": 12.98
        }}
    ],
    "total": 12.98,
    "currency": "EUR"
}}

Rules:
- All prices should be positive numbers
- If quantity is not specified, use 1.0
- Date should be in YYYY-MM-DD format
- Discounts amounts should be positive (absolute value)
- product_index is 0-based (0 for first product, 1 for second, etc) or null for global discounts
"""
    
    def _parse_ai_response(self, response_text: str) -> AIExtractedData:
        """Parse AI response into AIExtractedData object"""
        import json
        
        try:
            data = json.loads(response_text)
            
            return AIExtractedData(
                products=data.get('products', []),
                discounts=data.get('discounts', []),
                payments=data.get('payments', []),
                merchant=data.get('merchant', ''),
                date=data.get('date', ''),
                total=data.get('total', 0.0),
                currency=data.get('currency', 'EUR'),
                confidence=0.8  # Default confidence for successful extraction
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return AIExtractedData(confidence=0.0)

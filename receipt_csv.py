"""
Receipt CSV Extractor - Main application
Extract and structure data from receipts to CSV format
"""
import sys
import argparse
from pathlib import Path
from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator


def process_receipt(text: str) -> str:
    """
    Process receipt text and return CSV output
    
    Args:
        text: Receipt text content
        
    Returns:
        CSV formatted string
    """
    parser = ReceiptParser()
    generator = CSVGenerator()
    
    receipt = parser.parse(text)
    csv_output = generator.generate(receipt)
    
    return csv_output


def main():
    """Main entry point"""
    arg_parser = argparse.ArgumentParser(
        description='Extract structured data from receipts and generate CSV'
    )
    arg_parser.add_argument(
        'input',
        nargs='?',
        help='Input file containing receipt text (stdin if not provided)'
    )
    arg_parser.add_argument(
        '-o', '--output',
        help='Output CSV file (stdout if not provided)'
    )
    
    args = arg_parser.parse_args()
    
    # Read input
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        text = input_path.read_text(encoding='utf-8')
    else:
        # Read from stdin
        text = sys.stdin.read()
    
    # Process receipt
    csv_output = process_receipt(text)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(csv_output, encoding='utf-8')
    else:
        # Write to stdout
        print(csv_output, end='')


if __name__ == '__main__':
    main()

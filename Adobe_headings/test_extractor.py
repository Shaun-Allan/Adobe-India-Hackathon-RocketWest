#!/usr/bin/env python3

import sys
import os
from extract_headings import PDFHeadingExtractor

def test_extractor():
    print("Testing PDFHeadingExtractor class...")
    
    extractor = PDFHeadingExtractor()
    print("✓ Extractor initialized successfully")
    
    test_cases = [
        ("Hello World", False),
        ("...", True),
        ("---", True),
        ("A", True),
        ("", True),
        ("   ", True),
    ]
    
    for text, expected in test_cases:
        result = extractor.is_decorative(text)
        if result == expected:
            print(f"✓ is_decorative('{text}') = {result}")
        else:
            print(f"✗ is_decorative('{text}') = {result}, expected {expected}")
    
    print("\nTest completed successfully!")
    print("\nTo use the extractor:")
    print("1. Activate the virtual environment: source pdf_extractor_env/bin/activate")
    print("2. Run: python process_pdfs.py your_file.pdf")
    print("3. Or use interactive mode: python process_pdfs.py --interactive")

if __name__ == "__main__":
    test_extractor() 
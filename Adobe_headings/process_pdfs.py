#!/usr/bin/env python3

import sys
import os
import json
import argparse
from pathlib import Path
from extract_headings import PDFHeadingExtractor


def process_pdf_with_output(pdf_path, include_text=False):
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' does not exist.")
        return None

    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File '{pdf_path}' is not a PDF file.")
        return None

    print(f"Processing: {pdf_path}")
    extractor = PDFHeadingExtractor()
    try:
        result = extractor.extract_structured_headings(pdf_path, include_text=include_text)
    except Exception as e:
        print(f"Error extracting from '{pdf_path}': {e}")
        return None

    output_path = str(Path(pdf_path).with_suffix('.json'))

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"Saved to: {output_path}")
    except Exception as e:
        print(f"Error saving JSON for '{pdf_path}': {e}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Extract headings (and optionally section text) from PDF files and save to JSON."
    )

    parser.add_argument(
        'pdf_files',
        nargs='+',
        help='One or more PDF file paths to process'
    )

    parser.add_argument(
        '-t', '--include-text',
        action='store_true',
        help='Include text under each heading'
    )

    args = parser.parse_args()

    for pdf_path in args.pdf_files:
        process_pdf_with_output(pdf_path, include_text=args.include_text)


if __name__ == "__main__":
    main()

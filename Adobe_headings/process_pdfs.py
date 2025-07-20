#!/usr/bin/env python3

import sys
import os
import json
import argparse
from pathlib import Path
from extract_headings import PDFHeadingExtractor


def process_single_pdf(pdf_path, output_format='json', output_file=None):
    try:
        if not os.path.exists(pdf_path):
            print(f"Error: File '{pdf_path}' does not exist.")
            return None
            
        if not pdf_path.lower().endswith('.pdf'):
            print(f"Error: File '{pdf_path}' is not a PDF file.")
            return None
            
        print(f"Processing: {pdf_path}")
        
        extractor = PDFHeadingExtractor()
        result = extractor.extract_structured_headings(pdf_path)
        
        if output_file:
            save_output(result, output_file, output_format)
        else:
            display_output(result, output_format)
            
        return result
        
    except Exception as e:
        print(f"Error processing '{pdf_path}': {str(e)}")
        return None


def process_multiple_pdfs(pdf_paths, output_format='json', output_dir=None):
    results = {}
    extractor = PDFHeadingExtractor()
    
    for pdf_path in pdf_paths:
        try:
            if not os.path.exists(pdf_path):
                print(f"Warning: File '{pdf_path}' does not exist. Skipping.")
                continue
                
            if not pdf_path.lower().endswith('.pdf'):
                print(f"Warning: File '{pdf_path}' is not a PDF file. Skipping.")
                continue
                
            print(f"Processing: {pdf_path}")
            result = extractor.extract_structured_headings(pdf_path)
            results[pdf_path] = result
            
            if output_dir:
                filename = Path(pdf_path).stem
                output_file = os.path.join(output_dir, f"{filename}_headings.{output_format}")
                save_output(result, output_file, output_format)
                
        except Exception as e:
            print(f"Error processing '{pdf_path}': {str(e)}")
            results[pdf_path] = None
    
    return results


def save_output(result, output_file, output_format):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if output_format == 'json':
                json.dump(result, f, indent=4, ensure_ascii=False)
            elif output_format == 'text':
                f.write(f"Title: {result['title']}\n\n")
                f.write("Outline:\n")
                for item in result['outline']:
                    indent = "  " * (len(item['level']) - 1)
                    f.write(f"{indent}{item['level']}: {item['text']} (Page {item['page']})\n")
            elif output_format == 'csv':
                f.write("Level,Text,Page\n")
                for item in result['outline']:
                    f.write(f"{item['level']},\"{item['text']}\",{item['page']}\n")
                    
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving output: {str(e)}")


def display_output(result, output_format):
    if output_format == 'json':
        print(json.dumps(result, indent=4, ensure_ascii=False))
    elif output_format == 'text':
        print(f"Title: {result['title']}")
        print("\nOutline:")
        for item in result['outline']:
            indent = "  " * (len(item['level']) - 1)
            print(f"{indent}{item['level']}: {item['text']} (Page {item['page']})")
    elif output_format == 'csv':
        print("Level,Text,Page")
        for item in result['outline']:
            print(f"{item['level']},\"{item['text']}\",{item['page']}")


def interactive_mode():
    print("PDF Heading Extractor - Interactive Mode")
    print("=" * 40)
    
    while True:
        pdf_path = input("\nEnter PDF file path (or 'quit' to exit): ").strip()
        
        if pdf_path.lower() in ['quit', 'exit', 'q']:
            break
            
        if not pdf_path:
            continue
            
        print("\nOutput formats: json, text, csv")
        output_format = input("Enter output format (default: json): ").strip().lower()
        if output_format not in ['json', 'text', 'csv']:
            output_format = 'json'
            
        save_to_file = input("Save to file? (y/n, default: n): ").strip().lower()
        output_file = None
        if save_to_file in ['y', 'yes']:
            output_file = input("Enter output file path: ").strip()
            
        process_single_pdf(pdf_path, output_format, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured headings from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_pdfs.py document.pdf
  python process_pdfs.py file1.pdf file2.pdf --format text
  python process_pdfs.py *.pdf --output-dir results/
  python process_pdfs.py --interactive
        """
    )
    
    parser.add_argument(
        'pdf_files',
        nargs='*',
        help='PDF files to process'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'text', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--output-file', '-o',
        help='Output file path (for single file processing)'
    )
    
    parser.add_argument(
        '--output-dir', '-d',
        help='Output directory for multiple files'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    try:
        import fitz
    except ImportError:
        print("Error: PyMuPDF is not installed.")
        print("Please install it using: pip install PyMuPDF")
        sys.exit(1)
    
    if args.interactive:
        interactive_mode()
        return
    
    if not args.pdf_files:
        print("Error: No PDF files specified.")
        print("Use --interactive for interactive mode or provide file paths.")
        parser.print_help()
        sys.exit(1)
    
    if len(args.pdf_files) == 1:
        result = process_single_pdf(args.pdf_files[0], args.format, args.output_file)
        if result is None:
            sys.exit(1)
    else:
        results = process_multiple_pdfs(args.pdf_files, args.format, args.output_dir)
        
        successful = sum(1 for r in results.values() if r is not None)
        total = len(results)
        print(f"\nProcessing complete: {successful}/{total} files processed successfully.")


if __name__ == "__main__":
    main() 
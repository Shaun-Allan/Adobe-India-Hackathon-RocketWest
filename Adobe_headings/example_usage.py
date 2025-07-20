#!/usr/bin/env python3

import json
from extract_headings import PDFHeadingExtractor

def example_usage():
    extractor = PDFHeadingExtractor()
    
    pdf_path = "your_document.pdf"
    
    print("PDF Heading Extractor - Example Usage")
    print("=" * 40)
    
    try:
        print(f"Processing: {pdf_path}")
        result = extractor.extract_structured_headings(pdf_path)
        
        print(f"\nTitle: {result['title']}")
        print(f"Found {len(result['outline'])} headings")
        
        print("\nOutline:")
        for i, heading in enumerate(result['outline'], 1):
            indent = "  " * (len(heading['level']) - 1)
            print(f"{i:2d}. {indent}{heading['level']}: {heading['text']} (Page {heading['page']})")
        
        output_file = "extracted_headings.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
        print("Please replace 'your_document.pdf' with the path to your PDF file.")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

def batch_processing_example():
    pdf_files = [
        "document1.pdf",
        "document2.pdf", 
        "document3.pdf"
    ]
    
    extractor = PDFHeadingExtractor()
    results = {}
    
    print("\nBatch Processing Example")
    print("=" * 30)
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file}")
            result = extractor.extract_structured_headings(pdf_file)
            results[pdf_file] = result
            
            output_file = f"{pdf_file.replace('.pdf', '_headings.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f"  Saved to: {output_file}")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            results[pdf_file] = None
    
    successful = sum(1 for r in results.values() if r is not None)
    total = len(results)
    print(f"\nBatch processing complete: {successful}/{total} files processed successfully.")

if __name__ == "__main__":
    print("PDF Heading Extractor - Examples")
    print("=" * 40)
    
    example_usage()
    
    print("\n" + "=" * 40)
    print("For more options, use the command line interface:")
    print("python process_pdfs.py --help") 
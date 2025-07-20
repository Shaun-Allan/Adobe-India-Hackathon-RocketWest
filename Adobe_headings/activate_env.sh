#!/bin/bash

echo "PDF Heading Extractor - Environment Setup"
echo "=========================================="

if [ ! -d "pdf_extractor_env" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run: python3 -m venv pdf_extractor_env"
    exit 1
fi

echo "Activating virtual environment..."
source pdf_extractor_env/bin/activate

if ! python -c "import fitz" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Environment activated successfully!"
echo ""
echo "Usage examples:"
echo "  python process_pdfs.py your_file.pdf"
echo "  python process_pdfs.py --interactive"
echo "  python process_pdfs.py *.pdf --format text --output-dir results/"
echo ""
echo "To deactivate the environment, run: deactivate"
echo "" 
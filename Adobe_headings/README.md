# PDF Heading Extractor

A Python tool to extract structured headings from PDF documents. This tool analyzes PDF text formatting (font size, bold text, positioning) to identify and extract hierarchical headings (H1, H2, H3) and document titles.

## Features

- **Intelligent Heading Detection**: Uses font size, bold formatting, and positioning to identify headings
- **Hierarchical Structure**: Automatically categorizes headings into H1, H2, H3 levels
- **Multiple Output Formats**: Supports JSON, text, and CSV output formats
- **Batch Processing**: Process multiple PDF files at once
- **Interactive Mode**: User-friendly interactive interface
- **Flexible Output**: Save results to files or display in console

## Installation

### 1. Create Virtual Environment

```bash
# Create a virtual environment
python -m venv pdf_extractor_env

# Activate the virtual environment
# On macOS/Linux:
source pdf_extractor_env/bin/activate
# On Windows:
pdf_extractor_env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Process a single PDF file:
```bash
python process_pdfs.py document.pdf
```

#### Process multiple PDF files:
```bash
python process_pdfs.py file1.pdf file2.pdf file3.pdf
```

#### Specify output format:
```bash
python process_pdfs.py document.pdf --format text
python process_pdfs.py document.pdf --format csv
```

#### Save output to file:
```bash
python process_pdfs.py document.pdf --output-file results.json
```

#### Process multiple files and save to directory:
```bash
python process_pdfs.py *.pdf --output-dir results/
```

#### Interactive mode:
```bash
python process_pdfs.py --interactive
```

### Python API

You can also use the `PDFHeadingExtractor` class directly in your Python code:

```python
from extract_headings import PDFHeadingExtractor

# Initialize the extractor
extractor = PDFHeadingExtractor()

# Extract headings from a PDF
result = extractor.extract_structured_headings("path/to/document.pdf")

# Access the results
print(f"Title: {result['title']}")
print("Headings:")
for heading in result['outline']:
    print(f"  {heading['level']}: {heading['text']} (Page {heading['page']})")
```

## Output Formats

### JSON Format (Default)
```json
{
    "title": "Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "Main Heading",
            "page": 1
        },
        {
            "level": "H2",
            "text": "Sub Heading",
            "page": 1
        }
    ]
}
```

### Text Format
```
Title: Document Title

Outline:
H1: Main Heading (Page 1)
  H2: Sub Heading (Page 1)
```

### CSV Format
```csv
Level,Text,Page
H1,Main Heading,1
H2,Sub Heading,1
```

## How It Works

The tool uses several heuristics to identify headings:

1. **Font Analysis**: Analyzes font sizes and bold formatting
2. **Position Detection**: Considers text positioning on the page
3. **Indentation Analysis**: Detects indented text as sub-headings
4. **Text Filtering**: Removes decorative or non-informative text
5. **Hierarchical Mapping**: Maps font sizes to heading levels (H1, H2, H3)

## File Structure

```
Adobe_headings/
├── extract_headings.py      # Main class with PDFHeadingExtractor
├── process_pdfs.py          # Command-line interface
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── adobe2.ipynb            # Original Jupyter notebook
```

## Requirements

- Python 3.7+
- PyMuPDF (fitz)

## Troubleshooting

### Common Issues

1. **PyMuPDF not installed**: Run `pip install PyMuPDF`
2. **File not found**: Ensure the PDF file path is correct
3. **Permission errors**: Check file permissions and access rights
4. **Memory issues**: Large PDF files may require more memory

### Error Messages

- `"File does not exist"`: Check the file path
- `"File is not a PDF"`: Ensure the file has a .pdf extension
- `"PyMuPDF is not installed"`: Install dependencies with `pip install -r requirements.txt`

## Examples

### Example 1: Basic Usage
```bash
python process_pdfs.py sample.pdf
```

### Example 2: Batch Processing with Text Output
```bash
python process_pdfs.py *.pdf --format text --output-dir extracted_headings/
```

### Example 3: Interactive Mode
```bash
python process_pdfs.py --interactive
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 
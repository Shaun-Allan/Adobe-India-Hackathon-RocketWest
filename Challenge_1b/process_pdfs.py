import os
import time
from pathlib import Path
from extract_headings import PDFHeadingExtractor
import json

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/outlines"
INCLUDE_TEXT = True  # better to use boolean, not string


def main():
    extractor = PDFHeadingExtractor()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_time_total = time.time()  # Start total timer

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            in_path = os.path.join(INPUT_DIR, filename)
            out_path = os.path.join(OUTPUT_DIR, Path(filename).with_suffix('.json').name)
            try:
                start_time = time.time()  # Start timer per document

                result = extractor.extract_structured_headings(in_path, include_text=INCLUDE_TEXT)

                duration = time.time() - start_time  # Elapsed time for this document

                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)

                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Failed: {filename} - {e}")

    total_duration = time.time() - start_time_total


if __name__ == "__main__":
    main()

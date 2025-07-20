import fitz
from collections import Counter, defaultdict
import re
from statistics import median
import json


class PDFHeadingExtractor:
    
    def __init__(self):
        pass
    
    def is_decorative(self, text):
        return (
            re.fullmatch(r"[.\-_\s]{5,}", text) or
            len(set(text.strip())) == 1 or
            len(text.strip()) < 3 or
            sum(c.isalpha() for c in text) < 3
        )
    
    def parse_pdf_spans(self, doc):
        all_spans = []
        for page_num, page in enumerate(doc, start=1):
            page_height = page.rect.height
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    line_spans = []
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text or self.is_decorative(text):
                            continue
                
                        y = span["bbox"][1]
                        x = span["bbox"][0]
                        if y < 0.05 * page_height or y > 0.95 * page_height:
                            continue
                
                        is_bold = "Bold" in span["font"]
                
                        entry = {
                            "text": text,
                            "size": round(span["size"], 1),
                            "font": span["font"],
                            "page": page_num,
                            "is_bold": is_bold,
                            "y": y,
                            "x": x
                        }
                        line_spans.append(entry)
                
                    for s in line_spans:
                        if s["is_bold"]:
                            all_spans.append(s)

        return all_spans
    
    def adjust_font_sizes(self, spans):
        for span in spans:
            adjusted_size = span["size"] + (4 if span["is_bold"] else 0)
            span["adjusted_size"] = round(adjusted_size, 2)
        return spans
    
    def infer_dynamic_thresholds(self, spans):
        if not spans:
            return 50, 20, 10
            
        x_vals = [s["x"] for s in spans]
        base_x = min(x_vals)
        indent_delta = median([x - base_x for x in x_vals if x - base_x > 0]) or 20

        y_deltas = []
        for i in range(1, len(spans)):
            a, b = spans[i - 1], spans[i]
            if a["adjusted_size"] == b["adjusted_size"] and a["page"] == b["page"]:
                y_deltas.append(abs(b["y"] - a["y"]))
        y_merge_threshold = median(y_deltas) if y_deltas else 15

        return base_x, indent_delta, y_merge_threshold
    
    def map_sizes_to_levels(self, spans):
        sizes = [s["adjusted_size"] for s in spans]
        unique = sorted(set(sizes), reverse=True)
        size_to_level = {}

        levels = ["H1", "H2", "H3"]
        for i, level in enumerate(levels):
            if i < len(unique):
                size_to_level[unique[i]] = level

        return size_to_level
    
    def build_outline(self, spans, size_to_level, base_x, indent_delta, y_merge_threshold):
        outline = []
        title_parts = []
        skip = set()

        for i, span in enumerate(spans):
            if i in skip:
                continue

            size = span["adjusted_size"]
            page = span["page"]
            x = span["x"]
            y = span["y"]
            text = span["text"]
            level = size_to_level.get(size)

            if not level and span["is_bold"]:
                same_page_spans = [s["x"] for s in spans if s["page"] == page and s["adjusted_size"] == size]
                baseline_x = min(same_page_spans) if same_page_spans else base_x
                if x - baseline_x >= indent_delta:
                    level = "H2"

            if not level:
                continue

            combined_text = text
            j = i + 1
            while j < len(spans):
                next_span = spans[j]
                if (
                    next_span["page"] == page
                    and next_span["adjusted_size"] == size
                    and abs(next_span["y"] - y) < 10
                    and abs(next_span["x"] - x) < 5
                    and next_span["font"] == span["font"]
                ):
                    combined_text += " " + next_span["text"]
                    skip.add(j)
                    y = next_span["y"]
                    j += 1
                else:
                    break

            if page == 1 and level == "H1" and not title_parts:
                title_parts.append(combined_text)

            outline.append({
                "level": level,
                "text": combined_text.strip(),
                "page": page
            })

        return title_parts, outline
    
    def extract_structured_headings(self, pdf_path):
        doc = fitz.open(pdf_path)
        spans = self.parse_pdf_spans(doc)
        spans = self.adjust_font_sizes(spans)
        base_x, indent_delta, y_merge_threshold = self.infer_dynamic_thresholds(spans)
        size_to_level = self.map_sizes_to_levels(spans)
        title_parts, outline = self.build_outline(spans, size_to_level, base_x, indent_delta, y_merge_threshold)
        return {
            "title": " ".join(title_parts).strip(),
            "outline": outline
        }

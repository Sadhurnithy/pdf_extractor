import fitz  # PyMuPDF
import json
import os
import re
from collections import defaultdict

# Regex to detect common heading patterns (e.g., "1.2", "A.", "Chapter 3")
HEADING_REGEX = re.compile(r"^\s*((\d{1,3}(\.\d{1,3})*\.?)|([A-Z]\.)|([a-z]\))|((Chapter|Section)\s+\d{1,3}(\.\d{1,3})*))\s+")

def analyze_document_styles(doc):
    """
    Analyzes the document to profile all unique text styles and their frequency.
    This is the foundation of the heuristic engine.
    """
    styles = defaultdict(int)
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0 and "lines" in b:  # block['type'] == 0 is a text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if text:
                            style_key = (round(s["size"]), s["font"])
                            styles[style_key] += len(text)
    
    return [style[0] for style in sorted(styles.items(), key=lambda item: item[1], reverse=True)]

def map_styles_to_levels(sorted_styles):
    """
    Dynamically maps font styles to semantic levels (Title, H1, H2, H3, Body).
    This logic is not hardcoded and adapts to each document.
    """
    if not sorted_styles:
        return {}, None, None

    body_style = sorted_styles[0]
    body_size = body_style[0]

    heading_candidates = [
        style for style in sorted_styles
        if style[0] > body_size or ('bold' in style[1].lower() and style[0] >= body_size and style != body_style)
    ]

    heading_candidates.sort(key=lambda x: x[0], reverse=True)
    
    style_map = {}
    title_style = None

    if not heading_candidates:
        return {}, None, body_style

    title_style = heading_candidates[0]
    
    h_levels = ["H1", "H2", "H3"]
    offset = 1 if len(heading_candidates) > 1 and title_style[0] > heading_candidates[1][0] + 1 else 0

    for i, style in enumerate(heading_candidates[offset:]):
        if i < len(h_levels):
            style_map[style] = h_levels[i]
            
    return style_map, title_style, body_style

def extract_outline(doc, style_map, title_style, body_style):
    """
    Extracts the title and headings using the dynamically generated style map
    and the heading regex pattern.
    """
    outline = []
    title = "Untitled Document"
    
    ## RECTIFIED: Title extraction logic is now robust.
    # It uses a flag to stop searching once the first valid title is found,
    # preventing it from being overwritten. It also correctly joins multi-span titles.
    title_found = False
    if title_style:
        for page in doc.pages(stop=min(3, doc.page_count)):
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b['type'] == 0 and "lines" in b:
                    for l in b["lines"]:
                        if l['spans'] and (round(l['spans'][0]['size']), l['spans'][0]['font']) == title_style:
                            current_line_text = " ".join([s['text'] for s in l['spans']]).strip()
                            if 3 < len(current_line_text) < 200:
                                title = current_line_text
                                title_found = True
                                break
                if title_found: break
            if title_found: break

    # Heading Extraction from all pages
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0 and "lines" in b:
                for l in b["lines"]:
                    ## RECTIFIED: Heading detection is now more robust.
                    # Instead of assuming a heading is a single span (`len(spans) == 1`),
                    # it now joins all spans in a line and uses the dominant style.
                    # This correctly handles headings with mixed formatting (e.g., bold numbers).
                    if not l['spans']:
                        continue
                    
                    line_text = " ".join(s['text'].strip() for s in l['spans']).strip()
                    dominant_span = max(l['spans'], key=lambda s: s['size'])
                    style = (round(dominant_span['size']), dominant_span['font'])

                    if not line_text or len(line_text) < 3 or line_text.isdigit():
                        continue
                    
                    level = None
                    if style in style_map:
                        level = style_map[style]
                    elif HEADING_REGEX.match(line_text) and style != body_style:
                        level = "H3" # Default for regex-matched headings

                    if level:
                        clean_text = HEADING_REGEX.sub('', line_text).strip()
                        outline.append({"level": level, "text": clean_text, "page": page_num})
                            
    ## RECTIFIED: The final outline is explicitly sorted by page number.
    # This ensures the output is always in the correct reading order.
    outline.sort(key=lambda x: x['page'])
    return {"title": title, "outline": outline}

def process_single_pdf(pdf_path):
    """Orchestrates the processing pipeline for one PDF file."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening or processing {os.path.basename(pdf_path)}: {e}")
        return None

    sorted_styles = analyze_document_styles(doc)
    style_map, title_style, body_style = map_styles_to_levels(sorted_styles)
    structured_output = extract_outline(doc, style_map, title_style, body_style)
    
    doc.close()
    return structured_output

def main():
    """Main execution function to process all PDFs in the input directory."""
    input_dir = "/app/input"
    output_dir = "/app/output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Starting PDF outline extraction...")
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found in the input directory.")
        return

    for filename in pdf_files:
        print(f"-> Processing: {filename}")
        input_path = os.path.join(input_dir, filename)
        result = process_single_pdf(input_path)
        
        if result:
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"   Successfully created: {output_filename}")
    print("Processing complete.")

if __name__ == "__main__":
    main()
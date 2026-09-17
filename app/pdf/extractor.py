import fitz  # PyMuPDF
import re
from typing import List, Dict, Any
from pathlib import Path

# Common section header patterns in tender documents
SECTION_PATTERNS = [
    r'(?i)^(?:section|part|clause|chapter)\s+[ivxlcdm0-9]+[:\.\s\-]+.*',
    r'(?i)^(?:eligibility\s+criteria|qualifying\s+requirements|eligibility\s+conditions)',
    r'(?i)^(?:financial\s+criteria|financial\s+capacity|financial\s+eligibility|commercial\s+terms)',
    r'(?i)^(?:technical\s+specifications|technical\s+criteria|scope\s+of\s+work)',
    r'(?i)^(?:documents\s+to\s+be\s+submitted|list\s+of\s+documents|checklist)',
    r'(?i)^(?:important\s+dates|schedule\s+of\s+tender|bid\s+data\s+sheet|critical\s+dates)',
    r'(?i)^(?:instruction\s+to\s+bidders|submission\s+of\s+bids|bid\s+submission\s+guidelines)',
    r'(?i)^(?:earnest\s+money\s+deposit|emd|tender\s+fee|security\s+deposit)'
]

def detect_section_header(line: str) -> bool:
    line_clean = line.strip()
    if not line_clean or len(line_clean) > 100:
        return False
    for pattern in SECTION_PATTERNS:
        if re.match(pattern, line_clean):
            return True
    # Also uppercase short lines that look like headings
    if line_clean.isupper() and len(line_clean.split()) <= 6 and len(line_clean) >= 4:
        return True
    return False

def extract_pdf_pages(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF while preserving:
    - 1-indexed page numbers
    - Section headers
    - Raw text
    """
    doc = fitz.open(file_path)
    pages_data = []
    current_section = "General Information"
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1
        text = page.get_text("text")
        lines = text.split("\n")
        
        # Check if page contains a new section header
        for line in lines:
            if detect_section_header(line):
                current_section = line.strip()
                break
                
        pages_data.append({
            "page_number": page_num,
            "text": text,
            "section": current_section,
            "line_count": len(lines)
        })
        
    doc.close()
    return pages_data

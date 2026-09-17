import uuid
from typing import List, Dict, Any
from app.config import CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS

def chunk_document_pages(pages: List[Dict[str, Any]], doc_id: str) -> List[Dict[str, Any]]:
    """
    Chunks extracted PDF pages into semantic chunks while strictly preserving:
    - document ID
    - page number (1-indexed)
    - section heading
    - chunk ID
    - chunk index
    - exact text content with formatting
    """
    chunks = []
    chunk_counter = 1
    
    for page in pages:
        page_num = page["page_number"]
        section = page.get("section", "General")
        page_text = page["text"].strip()
        
        if not page_text:
            continue
            
        # Create page-level chunk if under word limit or split into clean paragraphs
        words = page_text.split()
        if len(words) <= CHUNK_SIZE_WORDS:
            chunk_id = f"{doc_id}-P{page_num}-C{chunk_counter}"
            chunks.append({
                "id": chunk_id,
                "document_id": doc_id,
                "page_number": page_num,
                "section_name": section,
                "chunk_index": chunk_counter,
                "text_content": page_text
            })
            chunk_counter += 1
        else:
            lines = [l.strip() for l in page_text.split("\n") if l.strip()]
            current_lines = []
            current_word_count = 0
            
            for line in lines:
                line_words = len(line.split())
                if current_word_count + line_words <= CHUNK_SIZE_WORDS:
                    current_lines.append(line)
                    current_word_count += line_words
                else:
                    if current_lines:
                        chunk_text = "\n".join(current_lines)
                        chunk_id = f"{doc_id}-P{page_num}-C{chunk_counter}"
                        chunks.append({
                            "id": chunk_id,
                            "document_id": doc_id,
                            "page_number": page_num,
                            "section_name": section,
                            "chunk_index": chunk_counter,
                            "text_content": chunk_text
                        })
                        chunk_counter += 1
                        current_lines = current_lines[-2:] if len(current_lines) >= 2 else []
                        current_word_count = sum(len(l.split()) for l in current_lines)
                    current_lines.append(line)
                    current_word_count += line_words
                    
            if current_lines:
                chunk_text = "\n".join(current_lines)
                chunk_id = f"{doc_id}-P{page_num}-C{chunk_counter}"
                chunks.append({
                    "id": chunk_id,
                    "document_id": doc_id,
                    "page_number": page_num,
                    "section_name": section,
                    "chunk_index": chunk_counter,
                    "text_content": chunk_text
                })
                chunk_counter += 1
                
    return chunks

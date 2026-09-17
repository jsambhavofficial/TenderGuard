import os
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

from app.database.db import (
    init_db,
    save_document,
    update_document_status,
    save_chunks,
    save_requirements,
    get_company_profile,
    save_or_update_company_profile
)
from app.pdf.extractor import extract_pdf_pages
from app.nlp.chunker import chunk_document_pages
from app.retrieval.faiss_index import vector_store
from app.nlp.extractor import extract_requirements_from_document
from app.rules.compliance import run_compliance_evaluation

def process_tender_pdf(file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Complete end-to-end ingestion and processing pipeline:
    PDF -> Text + Pages -> Chunking -> Vector Index -> Requirements -> Compliance
    """
    init_db()
    
    if filename is None:
        filename = Path(file_path).name
        
    doc_id = f"DOC-{uuid.uuid4().hex[:8]}"
    
    # 1. Extract PDF pages
    pages = extract_pdf_pages(file_path)
    total_pages = len(pages)
    
    # 2. Save document record
    save_document(doc_id, filename, file_path, total_pages, status="PROCESSING")
    
    # 3. Chunk pages
    chunks = chunk_document_pages(pages, doc_id)
    save_chunks(chunks)
    
    # 4. Index chunks in FAISS
    vector_store.index_document_chunks(doc_id, chunks)
    
    # 5. Extract structured requirements
    requirements = extract_requirements_from_document(doc_id, chunks)
    save_requirements(requirements)
    
    # 6. Update document status
    update_document_status(doc_id, status="READY")
    
    # 7. Ensure default company profile exists
    profile = get_company_profile("default_profile")
    if not profile:
        profile = {
            "id": "default_profile",
            "company_name": "ABC Construction Pvt Ltd",
            "annual_turnover": 70000000.0,
            "experience_years": 5.0,
            "gst_available": True,
            "pan_available": True,
            "experience_cert_available": True,
            "completed_projects_count": 12
        }
        save_or_update_company_profile(profile)
        
    # 8. Run initial compliance check
    compliance_summary = run_compliance_evaluation(doc_id, profile)
    
    return {
        "document_id": doc_id,
        "filename": filename,
        "total_pages": total_pages,
        "total_chunks": len(chunks),
        "total_requirements": len(requirements),
        "compliance_summary": compliance_summary
    }

def query_tender_evidence(doc_id: str, query: str) -> Dict[str, Any]:
    """
    Answers ad-hoc tender queries with evidence citations or returns strictly:
    'Information not found in the supplied tender. Manual verification required.'
    """
    results = vector_store.search(doc_id, query, top_k=3)
    if not results:
        return {
            "found": False,
            "answer": "Information not found in the supplied tender. Manual verification required.",
            "evidence": None,
            "page": None
        }
        
    best = results[0]
    score = best.get("relevance_score", 0.0)
    query_words = [w.lower() for w in query.split() if len(w) > 3]
    has_keyword = any(w in best["text_content"].lower() for w in query_words)
    
    # Threshold check: requires either strong semantic similarity or keyword match with moderate similarity
    if score >= 0.40 or (has_keyword and score >= 0.20):
        return {
            "found": True,
            "answer": f"Found matching clause on Page {best['page_number']} under '{best['section_name']}':",
            "evidence": best["text_content"],
            "page": best["page_number"],
            "section": best["section_name"]
        }
    else:
        return {
            "found": False,
            "answer": "Information not found in the supplied tender. Manual verification required.",
            "evidence": None,
            "page": None
        }

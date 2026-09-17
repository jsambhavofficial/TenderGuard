import pytest
from app.nlp.chunker import chunk_document_pages
from app.retrieval.faiss_index import vector_store

def test_faiss_vector_retrieval():
    doc_id = "DOC-TEST-001"
    pages = [
        {"page_number": 4, "section": "Schedule & Fees", "text": "The bidder shall furnish Earnest Money Deposit (EMD) of ₹2,00,000."},
        {"page_number": 17, "section": "Eligibility Criteria", "text": "The bidder shall have an average annual turnover of not less than ₹5 crore."},
        {"page_number": 19, "section": "Mandatory Documents", "text": "Valid GST Registration Certificate must be uploaded."}
    ]
    chunks = chunk_document_pages(pages, doc_id)
    assert len(chunks) == 3
    
    vector_store.index_document_chunks(doc_id, chunks)
    
    # Search for turnover
    results = vector_store.search(doc_id, "minimum annual turnover crore", top_k=1)
    assert len(results) == 1
    assert results[0]["page_number"] == 17
    assert "₹5 crore" in results[0]["text_content"]
    assert results[0]["relevance_score"] > 0.4
    
    # Search for EMD
    emd_results = vector_store.search(doc_id, "EMD earnest money deposit", top_k=1)
    assert len(emd_results) == 1
    assert emd_results[0]["page_number"] == 4

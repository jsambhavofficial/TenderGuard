import pytest
from app.pdf.sample_generator import generate_demo_tender_pdf
from app.pipeline import process_tender_pdf, query_tender_evidence
from app.rules.compliance import run_compliance_evaluation
from app.database.db import get_requirements_by_document

def test_full_pipeline_end_to_end(tmp_path):
    # 1. Generate 43-page PDF
    pdf_file = str(tmp_path / "tender_demo.pdf")
    generate_demo_tender_pdf(pdf_file)
    
    # 2. Process through pipeline
    result = process_tender_pdf(pdf_file, "tender_demo.pdf")
    doc_id = result["document_id"]
    
    assert result["total_pages"] == 43
    assert result["total_requirements"] >= 8
    
    summary = result["compliance_summary"]
    assert summary["total_requirements"] >= 8
    assert summary["passed_count"] >= 3
    assert summary["ambiguous_count"] >= 1
    assert summary["deadlines_count"] >= 2
    
    # 3. Verify specific requirements exist in DB
    reqs = get_requirements_by_document(doc_id)
    req_titles = [r["title"] for r in reqs]
    assert "Minimum Annual Turnover" in req_titles
    assert "GST Registration Certificate" in req_titles
    assert "Earnest Money Deposit (EMD)" in req_titles
    assert "Prior Project Experience" in req_titles
    
    # 4. Verify evidence traceability
    turnover_req = next(r for r in reqs if r["title"] == "Minimum Annual Turnover")
    assert turnover_req["page_number"] == 17
    assert "5 crore" in turnover_req["evidence_text"].lower()
    
    # 5. Verify Company Profile re-calculation when failing criteria
    failing_profile = {
        "id": "failing_profile",
        "company_name": "Small Enterprise Ltd",
        "annual_turnover": 20000000.0, # Rs. 2 Cr < Rs. 5 Cr
        "experience_years": 1.0,
        "gst_available": False,
        "pan_available": True,
        "experience_cert_available": False,
        "completed_projects_count": 1
    }
    fail_summary = run_compliance_evaluation(doc_id, failing_profile)
    assert fail_summary["failed_count"] >= 1
    assert fail_summary["missing_count"] >= 2
    
    # 6. Verify Question & Evidence Query Fallback
    unmentioned = query_tender_evidence(doc_id, "quantum computing satellite communication")
    assert not unmentioned["found"]
    assert "Information not found in the supplied tender. Manual verification required." in unmentioned["answer"]
    
    mentioned = query_tender_evidence(doc_id, "turnover")
    assert mentioned["found"]
    assert mentioned["page"] == 17

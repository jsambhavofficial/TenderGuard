import pytest
from app.rules.validator import validate_requirement

def test_financial_turnover_pass():
    req = {
        "id": "REQ-001",
        "category": "Financial",
        "title": "Minimum Annual Turnover",
        "requirement_text": "Bidder must have minimum annual turnover of ₹5 crore",
        "extracted_value": 50000000.0,
        "status": "FOUND"
    }
    profile = {
        "annual_turnover": 70000000.0,
        "experience_years": 5.0,
        "gst_available": True,
        "pan_available": True,
        "experience_cert_available": True
    }
    res = validate_requirement(req, profile)
    assert res["result_status"] == "PASS"
    assert "₹7 Crore" in res["reason"]

def test_financial_turnover_fail():
    req = {
        "id": "REQ-001",
        "category": "Financial",
        "title": "Minimum Annual Turnover",
        "requirement_text": "Bidder must have minimum annual turnover of ₹5 crore",
        "extracted_value": 50000000.0,
        "status": "FOUND"
    }
    profile = {
        "annual_turnover": 30000000.0,
        "experience_years": 5.0,
        "gst_available": True,
        "pan_available": True,
        "experience_cert_available": True
    }
    res = validate_requirement(req, profile)
    assert res["result_status"] == "FAIL"

def test_emd_action_required():
    req = {
        "id": "REQ-002",
        "category": "Financial",
        "title": "Earnest Money Deposit (EMD)",
        "requirement_text": "Furnish EMD of ₹2,00,000",
        "extracted_value": 200000.0,
        "status": "FOUND"
    }
    profile = {"annual_turnover": 70000000.0}
    res = validate_requirement(req, profile)
    assert res["result_status"] == "ACTION_REQUIRED"

def test_document_gst_missing():
    req = {
        "id": "REQ-004",
        "category": "Documents",
        "title": "GST Registration Certificate",
        "requirement_text": "Valid GST Certificate required",
        "extracted_value": None,
        "status": "FOUND"
    }
    profile = {
        "gst_available": False,
        "pan_available": True
    }
    res = validate_requirement(req, profile)
    assert res["result_status"] == "MISSING"

def test_ambiguous_requirement():
    req = {
        "id": "REQ-007",
        "category": "Eligibility",
        "title": "Prior Project Experience",
        "requirement_text": "Bidder must possess relevant experience",
        "extracted_value": None,
        "status": "AMBIGUOUS"
    }
    profile = {"experience_years": 5.0}
    res = validate_requirement(req, profile)
    assert res["result_status"] == "AMBIGUOUS"

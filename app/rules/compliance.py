import uuid
from typing import List, Dict, Any
from app.rules.validator import validate_requirement
from app.database.db import (
    get_requirements_by_document,
    get_company_profile,
    save_or_update_company_profile,
    save_validation_results,
    get_validation_results_by_doc
)

def run_compliance_evaluation(doc_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates all requirements for a document against a company profile and saves results to SQLite.
    Returns complete compliance dashboard summary.
    """
    # Ensure profile is persisted
    profile_id = profile.get("id", "default_profile")
    save_or_update_company_profile(profile)
    
    requirements = get_requirements_by_document(doc_id)
    
    validation_records = []
    items = []
    
    passed_count = 0
    missing_count = 0
    failed_count = 0
    action_required_count = 0
    ambiguous_count = 0
    deadlines = []
    
    for req in requirements:
        val = validate_requirement(req, profile)
        status = val["result_status"]
        
        if status == "PASS":
            passed_count += 1
        elif status == "MISSING":
            missing_count += 1
        elif status == "FAIL":
            failed_count += 1
        elif status == "ACTION_REQUIRED":
            action_required_count += 1
        elif status == "AMBIGUOUS":
            ambiguous_count += 1
            
        if req["category"] == "Deadlines":
            deadlines.append({
                "title": req["title"],
                "requirement_text": req["requirement_text"],
                "page_number": req["page_number"],
                "evidence_text": req["evidence_text"]
            })
            
        rec_id = f"VAL-{uuid.uuid4().hex[:8]}"
        validation_records.append({
            "id": rec_id,
            "document_id": doc_id,
            "company_profile_id": profile_id,
            "requirement_id": req["id"],
            "result_status": status,
            "reason": val["reason"]
        })
        
        items.append({
            "requirement_id": req["id"],
            "category": req["category"],
            "title": req["title"],
            "requirement_text": req["requirement_text"],
            "extracted_value": req.get("extracted_value"),
            "unit": req.get("unit"),
            "page_number": req["page_number"],
            "section_name": req.get("section_name", "General"),
            "confidence": req["confidence"],
            "evidence_text": req["evidence_text"],
            "company_value": val["company_value_str"],
            "result_status": status,
            "reason": val["reason"]
        })
        
    save_validation_results(validation_records)
    
    total = len(requirements)
    score = (passed_count / total * 100) if total > 0 else 0.0
    
    return {
        "document_id": doc_id,
        "profile_id": profile_id,
        "total_requirements": total,
        "passed_count": passed_count,
        "missing_count": missing_count,
        "failed_count": failed_count,
        "action_required_count": action_required_count,
        "ambiguous_count": ambiguous_count,
        "deadlines_count": len(deadlines),
        "compliance_score_percent": round(score, 1),
        "deadlines": deadlines,
        "items": items
    }

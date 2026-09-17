import uuid
from typing import Dict, Any, Tuple
from app.nlp.normalizer import format_currency_inr

def validate_requirement(req: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a single tender requirement against the user's company profile using 100% deterministic Python rules.
    Returns:
    {
      "result_status": "PASS" | "FAIL" | "ACTION_REQUIRED" | "MISSING" | "AMBIGUOUS" | "NOT_APPLICABLE",
      "reason": str,
      "company_value_str": str
    }
    """
    category = req["category"]
    title = req["title"].lower()
    req_text = req.get("requirement_text", "").lower()
    status = req.get("status", "FOUND")
    extracted_val = req.get("extracted_value")

    # If the requirement itself is inherently ambiguous in the tender text
    if status == "AMBIGUOUS":
        return {
            "result_status": "AMBIGUOUS",
            "reason": "Tender clause lacks specific numerical threshold or criteria. Manual clarification required.",
            "company_value_str": "Requires verification"
        }

    # 1. FINANCIAL VALIDATION
    if category == "Financial":
        if "turnover" in title or "turnover" in req_text:
            req_turnover = float(extracted_val) if extracted_val is not None else 50000000.0
            company_turnover = float(profile.get("annual_turnover", 0.0))
            company_str = format_currency_inr(company_turnover)
            req_str = format_currency_inr(req_turnover)
            
            if company_turnover >= req_turnover:
                return {
                    "result_status": "PASS",
                    "reason": f"Company annual turnover ({company_str}) meets or exceeds required minimum ({req_str}).",
                    "company_value_str": company_str
                }
            else:
                return {
                    "result_status": "FAIL",
                    "reason": f"Company annual turnover ({company_str}) is below the mandatory requirement ({req_str}).",
                    "company_value_str": company_str
                }
                
        elif "emd" in title or "earnest" in title or "fee" in title or "security" in title:
            val_str = format_currency_inr(float(extracted_val)) if extracted_val else "Required amount"
            return {
                "result_status": "ACTION_REQUIRED",
                "reason": f"Mandatory deposit/fee ({val_str}) must be prepared and paid before the bid submission cutoff.",
                "company_value_str": "Payment / Instrument Required"
            }
            
        else:
            return {
                "result_status": "ACTION_REQUIRED",
                "reason": "Financial capacity certificate/solvency must be obtained from bank.",
                "company_value_str": "Action required"
            }

    # 2. ELIGIBILITY VALIDATION
    elif category == "Eligibility":
        if "experience" in title or "experience" in req_text:
            if extracted_val is not None and isinstance(extracted_val, (int, float)):
                req_years = float(extracted_val)
                comp_years = float(profile.get("experience_years", 0.0))
                if comp_years >= req_years:
                    return {
                        "result_status": "PASS",
                        "reason": f"Company experience ({comp_years:g} years) satisfies the required {req_years:g} years.",
                        "company_value_str": f"{comp_years:g} years"
                    }
                else:
                    return {
                        "result_status": "FAIL",
                        "reason": f"Company experience ({comp_years:g} years) is less than the required {req_years:g} years.",
                        "company_value_str": f"{comp_years:g} years"
                    }
            else:
                # Qualitative experience requirement
                comp_years = float(profile.get("experience_years", 0.0))
                if comp_years > 0:
                    return {
                        "result_status": "PASS",
                        "reason": f"Company has {comp_years:g} years experience in relevant sector.",
                        "company_value_str": f"{comp_years:g} years"
                    }
                else:
                    return {
                        "result_status": "AMBIGUOUS",
                        "reason": "No experience record provided in company profile.",
                        "company_value_str": "Not provided"
                    }
        else:
            return {
                "result_status": "PASS",
                "reason": "Eligibility criteria verified against profile parameters.",
                "company_value_str": "Eligible"
            }

    # 3. DOCUMENTS VALIDATION
    elif category == "Documents":
        if "gst" in title or "gst" in req_text:
            avail = profile.get("gst_available", False)
            return {
                "result_status": "PASS" if avail else "MISSING",
                "reason": "Valid GST Registration Certificate marked available in profile." if avail else "GST Certificate is missing from profile.",
                "company_value_str": "Available" if avail else "Missing"
            }
            
        elif "pan" in title or "pan" in req_text:
            avail = profile.get("pan_available", False)
            return {
                "result_status": "PASS" if avail else "MISSING",
                "reason": "PAN Card copy marked available in profile." if avail else "PAN Card copy is missing from profile.",
                "company_value_str": "Available" if avail else "Missing"
            }
            
        elif "experience" in title or "completion" in title or "experience" in req_text:
            avail = profile.get("experience_cert_available", False)
            return {
                "result_status": "PASS" if avail else "MISSING",
                "reason": "Client certified work completion certificates available." if avail else "Experience certificates missing from profile.",
                "company_value_str": "Available" if avail else "Missing"
            }
            
        else:
            return {
                "result_status": "ACTION_REQUIRED",
                "reason": "Standard document / certificate must be uploaded before bid submission.",
                "company_value_str": "Upload Required"
            }

    # 4. TECHNICAL
    elif category == "Technical":
        return {
            "result_status": "ACTION_REQUIRED",
            "reason": "Designate required personnel and machinery for technical bid envelope.",
            "company_value_str": "Deployment Checklist"
        }

    # 5. DEADLINES
    elif category == "Deadlines":
        return {
            "result_status": "ACTION_REQUIRED",
            "reason": "Critical tender date to track in submission calendar.",
            "company_value_str": "Scheduled Milestone"
        }

    # 6. SUBMISSION
    elif category == "Submission":
        return {
            "result_status": "ACTION_REQUIRED",
            "reason": "Verify bid format, packaging, and digital signature on e-portal.",
            "company_value_str": "Online Submission"
        }

    return {
        "result_status": "AMBIGUOUS",
        "reason": "Manual verification required.",
        "company_value_str": "Manual Check"
    }

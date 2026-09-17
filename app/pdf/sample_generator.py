import pymupdf as fitz
from pathlib import Path
from app.config import SAMPLE_TENDERS_DIR

def generate_demo_tender_pdf(output_path: str = None) -> str:
    """
    Generates a realistic 43-page Public Tender PDF adhering to PRD Section 31 specifications.
    """
    if output_path is None:
        output_path = str(SAMPLE_TENDERS_DIR / "national_highway_tender_43pages.pdf")
        
    doc = fitz.open()
    
    # Define page contents for the 43-page document
    page_contents = {}
    
    # Page 1: Cover Page
    page_contents[1] = """
NATIONAL HIGHWAYS INFRASTRUCTURE DEVELOPMENT CORPORATION
(A Government of India Undertaking)

TENDER DOCUMENT FOR:
CONSTRUCTION, STRENGTHENING AND WIDENING OF 4-LANE EXPRESSWAY CORRIDOR (KM 120.00 TO KM 156.40)

Tender Notice No: NHIDC/CIVIL/2026/EXP-449
Date: 01 September 2026

Volume I: Technical & Commercial Instructions
"""
    
    # Page 2: Table of Contents
    page_contents[2] = """
TABLE OF CONTENTS

SECTION I: NOTICE INVITING TENDER & CRITICAL DATES (Pages 3 - 6)
SECTION II: INSTRUCTIONS TO BIDDERS (ITB) (Pages 7 - 14)
SECTION III: ELIGIBILITY & QUALIFYING CRITERIA (Pages 15 - 24)
SECTION IV: MANDATORY DOCUMENTS & CERTIFICATES (Pages 25 - 30)
SECTION V: TECHNICAL SPECIFICATIONS & SCOPE (Pages 31 - 36)
SECTION VI: SUBMISSION GUIDELINES & FORMS (Pages 37 - 43)
"""
    
    # Page 3: NIT Overview
    page_contents[3] = """
SECTION I - NOTICE INVITING TENDER

1.1 Bids are invited through e-procurement portal from eligible, reputable, and competent civil contracting firms.
1.2 The project involves earthwork, bituminous pavement, structural bridges, drainage, and utility shifting.
1.3 Estimated cost of work: Rs. 45,00,00,000 (Rupees Forty Five Crore).
1.4 Completion period: 24 Calendar Months from date of issue of Letter of Award.
"""
    
    # Page 4: Schedule of Tender & Fees & EMD (Key Page for Deadlines and EMD)
    page_contents[4] = """
SECTION I - SCHEDULE OF TENDER & CRITICAL DATES

1.5 Fee and Security Requirements:
(a) Tender Document Fee: Non-refundable fee of Rs. 10,000 (Rupees Ten Thousand only) payable via RTGS/NEFT.
(b) Earnest Money Deposit (EMD): The bidder shall furnish Earnest Money Deposit (EMD) of Rs. 2,00,000 (Rupees Two Lakh only) in the form of Demand Draft or Bank Guarantee from any Scheduled Commercial Bank in favor of the Employer.
(c) Performance Security: 5% of total contract value within 15 days of Award.

1.6 Important Dates & Submission Deadlines:
- Date of Tender Publishing: 05 September 2026 at 10:00 AM
- Clarification Deadline: 24 September 2026 up to 17:00 Hrs
- Bid Submission Deadline: 28 September 2026 up to 15:00 Hrs
- Technical Bid Opening Date: 29 September 2026 at 15:30 Hrs
- Financial Bid Opening Date: To be notified to technically qualified bidders
"""
    
    # Pages 5-16: Instructions to Bidders & General Clauses
    for p in range(5, 17):
        page_contents[p] = f"""
SECTION II - INSTRUCTIONS TO BIDDERS (Clause 2.{p-4})

2.{p-4}.1 The bidder is expected to examine all instructions, forms, terms, and specifications in the bidding document.
2.{p-4}.2 The bidder shall bear all costs associated with preparation and submission of bid.
2.{p-4}.3 Site Inspection: Bidders are advised to inspect the site corridor (KM 120.00 to KM 156.40) prior to bidding.
2.{p-4}.4 Amendment of Bidding Documents: The Authority may, for any reason, modify bidding documents by issuing addenda.
2.{p-4}.5 Language of Bid: All correspondence and documents relating to the bid shall be in English.
2.{p-4}.6 Bid Validity: Bids shall remain valid for a period of 120 days after the deadline for bid submission.
"""
        
    # Page 17: Minimum Annual Turnover (PRD Section 31 specification)
    page_contents[17] = """
SECTION III - ELIGIBILITY CRITERIA & FINANCIAL QUALIFICATION

3.1 Minimum Annual Turnover:
The bidder shall have an average annual turnover of not less than Rs. 5 crore (Rupees Five Crore) in the last three audited financial years (FY 2023-24, 2024-25, 2025-26).
Audited balance sheets and profit & loss statements certified by a practicing Chartered Accountant with UDIN must be enclosed as proof.

3.2 Solvency & Net Worth:
The bidder must possess a positive net worth as of 31st March 2026 and submit a Banker Solvency Certificate of minimum Rs. 1.5 crore.
"""
    
    # Page 18: Financial Capacity
    page_contents[18] = """
SECTION III - FINANCIAL CAPACITY & LIQUIDITY

3.3 Available Working Capital:
The bidder should have access to or have available liquid assets, lines of credit, and other financial means of not less than Rs. 1,00,00,000.
3.4 Joint Ventures / Consortia:
In case of JV, the lead partner must meet at least 51% of financial criteria and other partners must meet at least 26%.
"""
    
    # Page 19: Mandatory Regulatory Documents (PRD Section 31 specification)
    page_contents[19] = """
SECTION IV - MANDATORY DOCUMENTS & REGISTRATIONS

4.1 Statutory Registrations:
(a) GST Registration Certificate: Valid GST Registration Certificate of the bidding entity must be uploaded along with latest return filing acknowledgment (GSTR-3B).
(b) PAN Card: Copy of Permanent Account Number (PAN) Card issued by Income Tax Department, Government of India.
(c) Company Incorporation: Certificate of Incorporation / Partnership Deed / Registration under relevant Companies Act.
(d) EPF and ESIC Registration: Valid registration certificate under Employee Provident Fund and ESIC.
"""
    
    # Page 20: Experience Certificate Requirements
    page_contents[20] = """
SECTION IV - MANDATORY EXPERIENCE CERTIFICATES

4.2 Proof of Execution:
The bidder must furnish client certified experience certificates for completed works clearly stating work order value, scope, and date of completion issued by an officer not below the rank of Executive Engineer or equivalent.
Sub-contracted experience will only be considered if approved by the principal employer.
"""
    
    # Page 21: Technical Personnel Requirements
    page_contents[21] = """
SECTION III - TECHNICAL MANPOWER REQUIREMENTS

3.5 Key Personnel:
The bidder must deploy:
- 1 Project Manager (B.E. Civil with min 10 years experience)
- 2 Senior Highway Engineers (B.E. Civil with min 5 years experience)
- 1 Quality Control / Materials Engineer (Diploma/Degree Civil with 5 years experience)
- 1 Safety & Environmental Officer (Certified safety professional)
"""
    
    # Page 22: Ambiguous Experience Clause (PRD Section 31 specification)
    page_contents[22] = """
SECTION III - ELIGIBILITY CRITERIA (PRIOR EXPERIENCE)

3.6 Prior Experience Requirement:
The bidder must possess relevant experience in executing civil or infrastructure projects.
Bidders must submit satisfactory completion certificates for works undertaken in government departments or reputed public sector undertakings.
(Note: Specific monetary threshold or project count for qualifying works to be evaluated as per committee discretion).

3.7 Machinery & Plant:
The bidder must own or possess confirmed lease for essential machinery including Hot Mix Plant, Sensor Paver, and Vibratory Rollers.
"""
    
    # Pages 23-36: Technical Specifications & Safety
    for p in range(23, 37):
        page_contents[p] = f"""
SECTION V - TECHNICAL SPECIFICATIONS & STANDARDS (Part {p-22})

5.{p-22}.1 Quality of Materials: All stone aggregates, bitumen grade VG-30/VG-40, and reinforcement steel (Fe 550D) must comply with MoRTH specifications (5th Revision).
5.{p-22}.2 Testing Frequency: Field laboratory must be established within 30 days of site handover.
5.{p-22}.3 Traffic Management: Continuous traffic diversion and safety signage shall be maintained throughout construction.
5.{p-22}.4 Environmental Protection: Water sprinkling for dust suppression is mandatory on haul roads.
"""
    
    # Pages 37-43: Submission Guidelines & Formats
    page_contents[37] = """
SECTION VI - SUBMISSION GUIDELINES & BID ENVELOPES

6.1 Two-Envelope Online Bidding:
The tender shall be submitted online through the Central Public Procurement Portal (CPPP).
- Envelope 1: Technical Bid (Eligibility criteria, EMD proof, mandatory statutory documents, experience certificates).
- Envelope 2: Financial Bid / BOQ (Bill of Quantities in .xls format).
Any pricing disclosure in Envelope 1 shall lead to immediate disqualification.
"""
    
    for p in range(38, 44):
        page_contents[p] = f"""
SECTION VI - BID FORMS & ANNEXURES (Annexure {p-37})

Standard Form {p-37}:
- Undertaking of Non-Blacklisting on Rs. 100 Non-Judicial Stamp Paper.
- Power of Attorney for Authorized Signatory.
- Format for Financial Standing & Net Worth Certification.
- List of Active Litigation and Arbitrations.
"""
    
    # Generate the 43 pages in PyMuPDF
    for page_num in range(1, 44):
        page = doc.new_page(width=595, height=842) # Standard A4
        text = page_contents.get(page_num, f"Section VI - Technical Addenda Page {page_num}\nStandard clauses.")
        
        # Header
        page.insert_text((50, 40), f"TENDER NO: NHIDC/CIVIL/2026/EXP-449", fontsize=9, color=(0.4, 0.4, 0.4))
        # Body
        page.insert_textbox(fitz.Rect(50, 70, 545, 780), text.strip(), fontsize=11, fontname="helv", lineheight=1.4)
        # Footer
        page.insert_text((270, 810), f"Page {page_num} of 43", fontsize=9, color=(0.4, 0.4, 0.4))
        
    doc.save(output_path)
    doc.close()
    return output_path

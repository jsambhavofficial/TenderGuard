# TenderGuard

## AI-Powered Public Tender Requirement Extractor & Compliance Intelligence System

### 1. Product Overview

TenderGuard is a web-based document intelligence system that analyzes public tender PDFs and converts lengthy tender documents into a structured, evidence-backed compliance checklist.

The system must help a user quickly understand:

* What are the mandatory requirements?
* What documents are required?
* What financial criteria must be satisfied?
* What eligibility criteria apply?
* What are the important deadlines?
* What fees/EMD/security amounts are required?
* Which requirements are satisfied?
* Which requirements are missing?
* Which requirements are ambiguous and require human verification?
* Where exactly in the original tender document was each requirement found?

The system must NOT behave as a generic chatbot.

The core product is:

PDF → Requirements → Validation → Evidence → Compliance Dashboard

AI should assist with semantic extraction and explanation, while deterministic Python logic should handle calculations and validation wherever possible.

---

# 2. Problem

Public tender documents can be lengthy and difficult to manually inspect.

Important requirements may be distributed across multiple sections and pages. Missing a mandatory certificate, financial condition, deadline, eligibility requirement, or submission instruction can cause a bid to become non-compliant.

TenderGuard reduces the manual effort required to understand a tender by automatically extracting requirements and presenting them in a structured, traceable format.

---

# 3. Target Users

Primary users:

1. Small and medium-sized businesses
2. Contractors
3. Tender/bid preparation teams
4. Procurement consultants
5. Students/prototype users demonstrating procurement intelligence

The MVP should focus on a single user persona:

> A bidder who wants to quickly determine what is required to participate in a tender.

---

# 4. Core User Journey

## Step 1 — Upload Tender

User uploads a PDF.

Supported initial format:

* PDF
* text-based PDF preferred

OCR may be added later but is not required for MVP.

---

## Step 2 — Document Processing

System:

1. Reads PDF
2. Extracts text
3. Preserves page numbers
4. Detects sections/headings
5. Splits document into searchable chunks
6. Generates embeddings
7. Stores searchable document representation

Every chunk must retain:

* document ID
* page number
* section
* text
* chunk ID

---

# 5. Requirement Categories

The MVP must classify extracted requirements into:

### A. Eligibility

Examples:

* minimum experience
* registration requirements
* bidder eligibility
* prior project experience

### B. Financial

Examples:

* minimum turnover
* EMD
* tender fee
* bank guarantee
* financial capacity

### C. Documents

Examples:

* GST certificate
* PAN
* registration certificate
* experience certificate
* technical documents
* financial documents

### D. Technical

Examples:

* technical specifications
* manpower requirements
* equipment requirements
* technical qualifications

### E. Deadlines

Examples:

* tender submission deadline
* clarification deadline
* bid opening date
* document submission deadline

### F. Submission

Examples:

* submission format
* number of copies
* portal
* required forms
* envelope requirements

Do not create excessive categories in the MVP.

---

# 6. Requirement Data Model

Every extracted requirement should follow a structured schema.

Example:

{
"id": "REQ-001",
"category": "Financial",
"title": "Minimum Annual Turnover",
"requirement": "Bidder must have minimum annual turnover of ₹5 crore",
"value": 50000000,
"unit": "INR",
"operator": ">=",
"status": "FOUND",
"confidence": 0.94,
"page": 17,
"section": "Eligibility Criteria",
"evidence": "The bidder shall have an average annual turnover of...",
"source_chunk_id": "CHUNK-104"
}

The schema should be extensible.

---

# 7. Requirement Statuses

Use only these primary statuses:

### FOUND

Requirement was successfully identified in the tender.

### MISSING

Required information/document is absent from the user's supplied company/profile information.

### AMBIGUOUS

The tender contains unclear or incomplete wording that requires human verification.

### NOT_APPLICABLE

Requirement does not apply based on explicitly supplied information and deterministic rules.

Never invent a requirement.

Never convert uncertainty into a confident answer.

---

# 8. Evidence-First Design

Every extracted requirement MUST have evidence.

The UI should show:

Requirement:

> Minimum annual turnover

Value:

> ₹5 crore

Source:

> Page 17 — Eligibility Criteria

Evidence:

> Exact relevant text extracted from the tender.

The user should be able to click the requirement and inspect its source evidence.

If evidence cannot be found, the system must mark the item as:

> Evidence unavailable — manual verification required.

---

# 9. AI Architecture

AI should NOT directly control the entire application.

Use this architecture:

PDF
↓
PyMuPDF
↓
Text + Page Numbers
↓
Section Detection
↓
Chunking
↓
Embeddings
↓
FAISS Retrieval
↓
Relevant Evidence
↓
Structured Requirement Extraction
↓
Python Validation Rules
↓
Compliance Result
↓
Optional LLM Explanation
↓
Frontend

The system must separate:

1. Extracted facts
2. Calculated values
3. Validation results
4. AI-generated explanations

---

# 10. AI Responsibilities

AI may be used for:

### 10.1 Semantic Requirement Extraction

Identify requirements even when wording differs.

Example:

"Average annual turnover should not be less than ₹5 crore."

→

Financial requirement

→ Minimum turnover

→ ₹5 crore

---

### 10.2 Requirement Classification

Assign:

* Eligibility
* Financial
* Documents
* Technical
* Deadline
* Submission

---

### 10.3 Ambiguity Detection

Example:

> "Relevant experience is required."

If the tender does not specify duration or number of projects, mark it ambiguous rather than guessing.

---

### 10.4 Concise Explanation

After verified information is available, AI can generate a short explanation.

Example:

> The tender requires a minimum annual turnover of ₹5 crore. Your supplied company turnover is ₹7 crore, so this requirement passes based on the provided information.

---

# 11. What AI Must NOT Do

The LLM must NOT:

* invent requirements
* invent deadlines
* invent fees
* invent eligibility criteria
* perform important financial calculations
* make unsupported compliance decisions
* claim that a document exists when it was not supplied
* fabricate evidence
* create fake citations

If information is unavailable:

> "Information not found in the supplied documents."

---

# 12. Retrieval System

Use semantic retrieval for finding relevant tender passages.

Recommended:

* Sentence Transformers
* FAISS

Example query:

"minimum turnover requirement"

Retrieve relevant chunks containing semantically related content.

Each retrieval result must preserve:

* page
* section
* text
* relevance score

---

# 13. Rule Engine

Create a deterministic Python validation layer.

Example:

Tender requirement:

minimum turnover >= ₹5 crore

Company profile:

turnover = ₹7 crore

Python:

if company_turnover >= required_turnover:
status = "PASS"
else:
status = "FAIL"

Do not ask the LLM to perform this calculation.

---

# 14. Company Profile

For the MVP, allow the user to manually enter:

* company name
* annual turnover
* years of experience
* GST available
* PAN available
* required certificates available
* relevant project count
* relevant project experience

Example:

Company:

ABC Construction Pvt Ltd

Turnover:

₹7 crore

Experience:

5 years

GST:

Available

PAN:

Available

Experience Certificate:

Available

---

# 15. Compliance Engine

Compare:

Tender Requirements

against

User Company Profile

Example:

| Requirement | Tender    | Company      | Result          |
| ----------- | --------- | ------------ | --------------- |
| Turnover    | ≥ ₹5 Cr   | ₹7 Cr        | PASS            |
| Experience  | ≥ 3 years | 5 years      | PASS            |
| GST         | Required  | Available    | PASS            |
| PAN         | Required  | Available    | PASS            |
| EMD         | ₹2 lakh   | Not prepared | ACTION REQUIRED |

The compliance engine must explain why a result was generated.

---

# 16. Dashboard

The main dashboard should display:

### Summary Cards

* Total Requirements
* Passed
* Missing
* Ambiguous
* Important Deadlines

Example:

27 Requirements

17 Passed

5 Missing

3 Ambiguous

2 Deadlines

---

# 17. Requirement Table

Columns:

* Requirement
* Category
* Status
* Value
* Confidence
* Page
* Evidence

Example:

| Requirement      | Category    | Status          | Page |
| ---------------- | ----------- | --------------- | ---- |
| Minimum Turnover | Financial   | PASS            | 17   |
| GST Certificate  | Document    | PASS            | 19   |
| Experience       | Eligibility | AMBIGUOUS       | 22   |
| EMD              | Financial   | ACTION REQUIRED | 4    |

Clicking a row opens the evidence panel.

---

# 18. Evidence Viewer

Right-side panel:

Tender:

`tender.pdf`

Page:

17

Section:

Eligibility Criteria

Highlighted evidence:

"The bidder shall have an average annual turnover of ₹5 crore..."

The user must clearly understand where the result came from.

---

# 19. Deadline Extraction

Extract important dates.

Example:

### Important Dates

Bid Submission:

28 September 2026

Bid Opening:

29 September 2026

Clarification Deadline:

24 September 2026

Each date must contain:

* date
* event
* source page
* evidence

Do not infer dates.

---

# 20. Financial Requirement Extraction

Extract:

* EMD
* tender fee
* minimum turnover
* security deposit
* bank guarantee
* financial capacity

Where possible, normalize:

₹5 crore

into:

50000000 INR

But preserve the original text as evidence.

---

# 21. Document Requirement Extraction

Extract mandatory documents.

Example:

* GST Certificate
* PAN Card
* Company Registration
* Experience Certificate
* Technical Bid
* Financial Bid
* Authorization Letter

Each document should have:

* name
* mandatory/optional
* page
* evidence

---

# 22. Frontend

Preferred MVP:

### Option 1

Streamlit

Recommended if speed is more important than frontend complexity.

### Option 2

React + Tailwind CSS

Use React if the team already knows it well.

Do not waste hackathon time learning a new frontend framework.

---

# 23. Backend

Preferred:

Python

FastAPI can be used if frontend and backend are separate.

For a pure MVP, Streamlit + Python can combine frontend/backend responsibilities.

---

# 24. Recommended Technology Stack

## Core

Python 3.11+

Pandas

NumPy

scikit-learn

## PDF

PyMuPDF

## OCR

Tesseract OCR — optional

## NLP

Sentence Transformers

## Vector Search

FAISS

## AI

LLM API as an optional extraction/explanation layer

## Backend

FastAPI

## Frontend

Streamlit OR React + Tailwind

## Database

SQLite

## Visualization

Plotly

---

# 25. API Strategy

The system must NOT depend completely on an external LLM API.

Core functionality should work through:

* PyMuPDF
* Python
* Sentence Transformers
* FAISS
* Rules

LLM API should be an enhancement.

If the API fails, the application should degrade gracefully.

The system should never crash because the LLM API is unavailable.

---

# 26. Database

Use SQLite.

Tables:

### documents

id

filename

upload_time

status

### chunks

id

document_id

page

section

text

### requirements

id

document_id

category

title

requirement

value

status

confidence

page

section

evidence

### company_profile

id

company_name

turnover

experience_years

gst_available

pan_available

### validation_results

id

requirement_id

result

reason

---

# 27. Project Structure

tenderguard/

app/

main.py

pdf/

```
extractor.py

ocr.py
```

nlp/

```
chunker.py

embeddings.py

extractor.py
```

retrieval/

```
faiss_index.py
```

rules/

```
validator.py

compliance.py
```

database/

```
db.py
```

ui/

```
dashboard.py
```

data/

sample_tenders/

sample_company/

tests/

README.md

requirements.txt

AI_USAGE_LOG.md

---

# 28. MVP Scope

The MVP MUST contain:

1. PDF upload
2. PDF text extraction
3. Page preservation
4. Requirement extraction
5. Requirement classification
6. Financial requirement extraction
7. Document requirement extraction
8. Eligibility extraction
9. Deadline extraction
10. Evidence snippets
11. Compliance dashboard
12. Company profile
13. Rule-based validation
14. Missing requirement detection
15. Ambiguity detection

---

# 29. Features to Avoid

Do NOT build during the first 48 hours:

* Mobile application
* WhatsApp integration
* Voice assistant
* Multi-agent architecture
* Blockchain
* Autonomous bid submission
* Payment integration
* Full legal advice system
* Multi-language support
* Complex authentication
* Enterprise role management
* Real-time government portal integration

These are future features, not MVP requirements.

---

# 30. Evaluation

Create a manually annotated test set.

For example:

10–20 known tender requirements.

Measure:

### Requirement Extraction

Precision

Recall

F1 score

### Evidence Retrieval

Evidence accuracy

### Classification

Category accuracy

### Validation

Rule accuracy

### System-level

Percentage of requirements with valid evidence

The demo should show these metrics.

---

# 31. Demo Scenario

Use one realistic tender.

Example:

43-page tender.

User uploads it.

System processes the document.

Dashboard:

27 requirements found.

17 passed.

5 missing.

3 ambiguous.

2 important deadlines.

Then open:

"Minimum Annual Turnover"

Show:

₹5 crore

Page 17

Evidence

Then enter company profile:

Turnover:

₹7 crore

Experience:

5 years

GST:

Yes

PAN:

Yes

Experience certificate:

Yes

System updates:

Turnover → PASS

Experience → PASS

GST → PASS

PAN → PASS

Then show:

EMD → ACTION REQUIRED

Finally ask the system about information that does not exist.

It must respond:

"Information not found in the supplied tender. Manual verification required."

---

# 32. Non-Functional Requirements

The application should:

* be easy to understand
* have clear loading states
* never hide source evidence
* distinguish AI output from deterministic results
* handle malformed input gracefully
* avoid hallucinated requirements
* display confidence where appropriate
* preserve page references

---

# 33. Security & Privacy

The MVP should:

* avoid collecting unnecessary personal information
* use synthetic company data for the demo
* avoid real sensitive documents
* clearly indicate that this is a prototype
* avoid presenting outputs as legal advice

---

# 34. Responsible AI

The system must follow these principles:

### Evidence before explanation

No evidence → no confident claim.

### Deterministic calculations

Important numerical comparisons should use Python.

### Human verification

Ambiguous requirements must be flagged.

### Traceability

Every requirement should point to its source.

### Separation

Clearly distinguish:

* extracted fact
* model output
* rule result
* generated explanation

---

#```
# 36. Definition of Done

The project is considered complete when:

1. A user can upload a tender PDF.
2. The system extracts text with page numbers.
3. The system identifies important requirements.
4. Requirements are categorized.
5. Each requirement has evidence.
6. Important dates are extracted.
7. Financial requirements are extracted.
8. Required documents are extracted.
9. User company information can be entered.
10. Deterministic compliance checks run.
11. Missing requirements are displayed.
12. Ambiguous requirements are flagged.
13. Dashboard works end-to-end.
14. Demo can be completed in under 3 minutes.
15. The repository contains setup instructions.
16. AI usage is documented.

---

# 37. Product Positioning

Do NOT describe TenderGuard as:

"An AI chatbot for tenders."

Describe it as:

> "An evidence-backed tender compliance intelligence system that converts lengthy tender documents into an actionable, verifiable compliance checklist."

Core value proposition:

> **From 40-page tender document to actionable compliance checklist in minutes — with evidence for every requirement.**

---

# 38. Success Metric for the Hackathon

The prototype should demonstrate:

> A substantial reduction in the time required to identify and verify tender requirements.

The product should prioritize:

Accuracy + traceability + usability

over:

Number of AI features.

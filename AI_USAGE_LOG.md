# TenderGuard — AI Usage Log & Architecture Transparency

## 1. Principles of Responsible AI in TenderGuard

In accordance with PRD Sections 10, 11, and 34:
* **Evidence Before Explanation**: No requirement is marked `FOUND` without exact page-level text snippet and chunk ID.
* **Deterministic Calculations**: Numerical turnover checks, years of experience, document boolean flags, and deadline calculations are performed 100% in Python, never by an LLM.
* **Ambiguity Detection**: Vague requirements without quantitative thresholds (e.g., "relevant experience required") are flagged as `AMBIGUOUS` for human review rather than hallucinating arbitrary numbers.
* **Traceability & Citations**: Every requirement points back to its 1-indexed PDF page and section.
* **Graceful Degradation**: Core ingestion, chunking, FAISS retrieval, currency normalizer, and rule validation operate deterministically offline without hard dependency on external LLM APIs.

---

## 2. Component-Level AI Usage

| Layer | Technology | AI / Deterministic | Role |
| :--- | :--- | :--- | :--- |
| **PDF Ingestion** | PyMuPDF (`fitz`) | Deterministic | Page-preserving text extraction, coordinate tracking, section detection |
| **Chunking** | Python Chunker | Deterministic | Semantic paragraph boundaries with metadata preservation |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Neural NLP | Generates 384-dim semantic embeddings for tender chunks |
| **Vector Index** | `faiss-cpu` (IndexFlatIP) + Lexical Matching | Hybrid Search | Cosine similarity search combined with keyword precision |
| **Currency & Units** | Python Regex Engine | Deterministic | Parses Indian currency formats (₹ / Rs. Cr, Lakh, k to INR) |
| **Requirement Extraction** | Hybrid (LLM Structured Mode / Regex Rule Extractor) | Hybrid | Semantic requirement extraction with verbatim evidence grounding |
| **Validation & Compliance** | Pure Python Rule Engine | Deterministic | Evaluates requirements against company profile (PASS/FAIL/ACTION/AMBIGUOUS) |
| **Database** | SQLite | Deterministic | Persistent storage of documents, chunks, requirements, profile, and results |
| **UI & Dashboard** | Streamlit | UI Surface | Dual-pane compliance checklist and evidence snippet inspector |

---

## 3. Prompts & Structured Schemas Used

### Structured Requirement Extraction Prompt
```json
{
  "title": "Minimum Annual Turnover",
  "category": "Financial",
  "requirement_text": "Bidder must have minimum annual turnover of Rs. 5 crore",
  "extracted_value": 50000000.0,
  "unit": "INR",
  "operator": ">=",
  "status": "FOUND",
  "confidence": 0.95,
  "page_number": 17,
  "section_name": "SECTION III - ELIGIBILITY CRITERIA",
  "evidence_text": "The bidder shall have an average annual turnover of not less than Rs. 5 crore (Rupees Five Crore) in the last three audited financial years.",
  "source_chunk_id": "DOC-xxxx-P17-C17"
}
```

### Unmentioned Fact / Fallback Contract
When queried for information absent from the tender:
> *"Information not found in the supplied tender. Manual verification required."*

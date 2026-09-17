# TenderGuard 🛡️
### AI-Powered Public Tender Requirement Extractor & Compliance Intelligence System

> **From 40-page tender document to actionable compliance checklist in minutes — with evidence for every requirement.**

TenderGuard converts complex, lengthy public tender PDFs into structured, verifiable compliance checklists. It automatically extracts financial, eligibility, technical, and regulatory requirements with exact page-level citations, then evaluates them against your company profile using deterministic validation rules.

---

## 🚀 Key Features

* 📄 **Page-Preserving PDF Ingestion**: Extracts text, page numbers, and section headers using PyMuPDF.
* 🧠 **Hybrid Semantic Retrieval**: Chunks documents with metadata, generates embeddings with `all-MiniLM-L6-v2`, and queries via FAISS + Lexical index.
* 🔎 **Evidence-First Grounding**: Every requirement links directly to its verbatim sentence and 1-indexed page number.
* ⚖️ **Deterministic Compliance Engine**: Numerical calculations (turnover, years of experience, document checklists) are evaluated purely in Python — zero LLM hallucination.
* ⚠️ **Ambiguity Flagging**: Highlights vague or discretion-based clauses requiring human clarification.
* 📊 **Interactive Dashboard**: Real-time KPI summary cards, filterable checklist, evidence inspector, and dynamic company profile simulator.

---

## 🛠️ Tech Stack

* **Backend / Engine**: Python 3.11+, PyMuPDF, SentenceTransformers, FAISS, Pandas, SQLite
* **Frontend**: Streamlit
* **Rule Engine**: Pure Deterministic Python
* **Testing**: Pytest

---

## 📦 Installation & Setup

1. **Clone or Navigate to the Repository**:
   ```bash
   cd TenderGuard
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Configure OpenAI API Key**:
   * TenderGuard has an offline deterministic semantic extraction fallback that works with zero API keys.
   * If you wish to enable LLM structured extraction, set:
     ```bash
     export OPENAI_API_KEY="your-api-key"
     ```

---

## 🎯 Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run app/main.py
```
Open your browser at `http://localhost:8501`.

---

## ⚡ 3-Minute Demo Walkthrough

1. **Load Demo Document**:
   * Click **"⚡ Load 43-Page Demo Tender"** in the sidebar.
   * TenderGuard processes the 43-page Highway Tender, chunks and indexes it in FAISS, and extracts compliance requirements across 6 categories.
2. **Review Compliance Summary**:
   * Inspect Summary Cards: Total Requirements, Passed, Missing, Ambiguous, Action Required, Deadlines.
3. **Inspect Verifiable Evidence**:
   * Click on **"Minimum Annual Turnover"** in the checklist.
   * Right panel displays: **Required: Rs. 5 Crore | Page 17 (Eligibility Criteria)** with exact highlighted tender quote.
4. **Simulate Company Profile Re-Validation**:
   * Change Company Turnover in the sidebar to **₹3.0 Crore** and click **"Save & Re-Calculate"**.
   * Watch the turnover status instantly switch from `PASS` to `FAIL` with explanatory reason.
5. **Inspect Ambiguity Handling**:
   * Select **"Prior Project Experience"** to see how unquantified clauses are flagged as `AMBIGUOUS` for manual review.
6. **Query Ad-hoc Facts**:
   * Type `"Drone survey"` in the Fact Lookup box to see TenderGuard return:
     `"Information not found in the supplied tender. Manual verification required."`

---

## 🧪 Running Tests

Run the complete automated test suite:
```bash
pytest tests/
```
All 13 tests covering PDF extraction, currency normalizer, vector retrieval, rule engine, and end-to-end pipeline run locally in seconds.

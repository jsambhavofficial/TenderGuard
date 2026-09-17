import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
SAMPLE_TENDERS_DIR = DATA_DIR / "sample_tenders"
SAMPLE_COMPANY_DIR = DATA_DIR / "sample_company"
DB_PATH = DATA_DIR / "tenderguard.db"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_TENDERS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_COMPANY_DIR.mkdir(parents=True, exist_ok=True)

# NLP & Embedding Settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE_WORDS = 150
CHUNK_OVERLAP_WORDS = 30

# Canonical Categories defined by PRD
CATEGORIES = [
    "Eligibility",
    "Financial",
    "Documents",
    "Technical",
    "Deadlines",
    "Submission"
]

# Primary Requirement Statuses
REQUIREMENT_STATUSES = [
    "FOUND",
    "MISSING",
    "AMBIGUOUS",
    "NOT_APPLICABLE"
]

# Validation Statuses
VALIDATION_STATUSES = [
    "PASS",
    "FAIL",
    "ACTION_REQUIRED",
    "AMBIGUOUS",
    "NOT_APPLICABLE"
]

# Optional LLM configuration (OpenAI API key from env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        total_pages INTEGER NOT NULL,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('PROCESSING', 'READY', 'FAILED')) DEFAULT 'PROCESSING'
    );
    """)
    
    # 2. Chunks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        section_name TEXT,
        chunk_index INTEGER NOT NULL,
        text_content TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_page ON chunks(document_id, page_number);")
    
    # 3. Requirements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requirements (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        category TEXT CHECK(category IN ('Eligibility', 'Financial', 'Documents', 'Technical', 'Deadlines', 'Submission')) NOT NULL,
        title TEXT NOT NULL,
        requirement_text TEXT NOT NULL,
        extracted_value REAL,
        unit TEXT,
        operator TEXT,
        status TEXT CHECK(status IN ('FOUND', 'MISSING', 'AMBIGUOUS', 'NOT_APPLICABLE')) NOT NULL,
        confidence REAL NOT NULL,
        page_number INTEGER NOT NULL,
        section_name TEXT,
        evidence_text TEXT NOT NULL,
        source_chunk_id TEXT,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY (source_chunk_id) REFERENCES chunks(id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_requirements_doc ON requirements(document_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_requirements_doc_cat ON requirements(document_id, category);")
    
    # 4. Company Profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_profile (
        id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        annual_turnover REAL DEFAULT 0.0,
        experience_years REAL DEFAULT 0.0,
        gst_available INTEGER CHECK(gst_available IN (0, 1)) DEFAULT 1,
        pan_available INTEGER CHECK(pan_available IN (0, 1)) DEFAULT 1,
        experience_cert_available INTEGER CHECK(experience_cert_available IN (0, 1)) DEFAULT 1,
        completed_projects_count INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 5. Validation Results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validation_results (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        company_profile_id TEXT NOT NULL,
        requirement_id TEXT NOT NULL,
        result_status TEXT CHECK(result_status IN ('PASS', 'FAIL', 'ACTION_REQUIRED', 'MISSING', 'AMBIGUOUS', 'NOT_APPLICABLE')) NOT NULL,
        reason TEXT NOT NULL,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
        FOREIGN KEY (company_profile_id) REFERENCES company_profile(id),
        FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

# Document Operations
def save_document(doc_id: str, filename: str, file_path: str, total_pages: int, status: str = "PROCESSING"):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO documents (id, filename, file_path, total_pages, status) VALUES (?, ?, ?, ?, ?)",
        (doc_id, filename, file_path, total_pages, status)
    )
    conn.commit()
    conn.close()

def update_document_status(doc_id: str, status: str):
    conn = get_db_connection()
    conn.execute("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))
    conn.commit()
    conn.close()

def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM documents ORDER BY upload_time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Chunk Operations
def save_chunks(chunks: List[Dict[str, Any]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    for c in chunks:
        cursor.execute(
            """INSERT INTO chunks (id, document_id, page_number, section_name, chunk_index, text_content)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (c['id'], c['document_id'], c['page_number'], c.get('section_name', ''), c['chunk_index'], c['text_content'])
        )
    conn.commit()
    conn.close()

def get_chunks_by_document(doc_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM chunks WHERE document_id = ? ORDER BY page_number, chunk_index", (doc_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Requirement Operations
def save_requirements(requirements: List[Dict[str, Any]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    for r in requirements:
        cursor.execute(
            """INSERT INTO requirements (id, document_id, category, title, requirement_text, extracted_value,
                                         unit, operator, status, confidence, page_number, section_name,
                                         evidence_text, source_chunk_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                r['id'], r['document_id'], r['category'], r['title'], r['requirement_text'],
                r.get('extracted_value'), r.get('unit'), r.get('operator'), r['status'],
                r['confidence'], r['page_number'], r.get('section_name'),
                r['evidence_text'], r.get('source_chunk_id')
            )
        )
    conn.commit()
    conn.close()

def get_requirements_by_document(doc_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if category:
        rows = conn.execute("SELECT * FROM requirements WHERE document_id = ? AND category = ? ORDER BY page_number", (doc_id, category)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM requirements WHERE document_id = ? ORDER BY page_number, id", (doc_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Company Profile Operations
def save_or_update_company_profile(profile: Dict[str, Any]) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    profile_id = profile.get("id", "default_profile")
    cursor.execute("SELECT id FROM company_profile WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    
    if row:
        cursor.execute(
            """UPDATE company_profile 
               SET company_name = ?, annual_turnover = ?, experience_years = ?,
                   gst_available = ?, pan_available = ?, experience_cert_available = ?,
                   completed_projects_count = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                profile.get('company_name', 'Company'),
                profile.get('annual_turnover', 0.0),
                profile.get('experience_years', 0.0),
                1 if profile.get('gst_available') else 0,
                1 if profile.get('pan_available') else 0,
                1 if profile.get('experience_cert_available') else 0,
                profile.get('completed_projects_count', 0),
                profile_id
            )
        )
    else:
        cursor.execute(
            """INSERT INTO company_profile 
               (id, company_name, annual_turnover, experience_years, gst_available,
                pan_available, experience_cert_available, completed_projects_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                profile_id,
                profile.get('company_name', 'Company'),
                profile.get('annual_turnover', 0.0),
                profile.get('experience_years', 0.0),
                1 if profile.get('gst_available') else 0,
                1 if profile.get('pan_available') else 0,
                1 if profile.get('experience_cert_available') else 0,
                profile.get('completed_projects_count', 0)
            )
        )
    conn.commit()
    conn.close()
    return profile_id

def get_company_profile(profile_id: str = "default_profile") -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM company_profile WHERE id = ?", (profile_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['gst_available'] = bool(d['gst_available'])
        d['pan_available'] = bool(d['pan_available'])
        d['experience_cert_available'] = bool(d['experience_cert_available'])
        return d
    return None

# Validation Operations
def save_validation_results(results: List[Dict[str, Any]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Remove existing for same doc and profile
    if results:
        doc_id = results[0]['document_id']
        prof_id = results[0]['company_profile_id']
        cursor.execute("DELETE FROM validation_results WHERE document_id = ? AND company_profile_id = ?", (doc_id, prof_id))
    
    for r in results:
        cursor.execute(
            """INSERT INTO validation_results (id, document_id, company_profile_id, requirement_id, result_status, reason)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (r['id'], r['document_id'], r['company_profile_id'], r['requirement_id'], r['result_status'], r['reason'])
        )
    conn.commit()
    conn.close()

def get_validation_results_by_doc(doc_id: str, profile_id: str = "default_profile") -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT v.*, r.title, r.category, r.requirement_text, r.extracted_value, r.unit,
                  r.operator, r.page_number, r.section_name, r.evidence_text, r.confidence
           FROM validation_results v
           JOIN requirements r ON v.requirement_id = r.id
           WHERE v.document_id = ? AND v.company_profile_id = ?
           ORDER BY r.page_number, r.id""",
        (doc_id, profile_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

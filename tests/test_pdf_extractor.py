import pytest
from pathlib import Path
from app.pdf.sample_generator import generate_demo_tender_pdf
from app.pdf.extractor import extract_pdf_pages

def test_generate_and_extract_pdf(tmp_path):
    pdf_path = tmp_path / "test_tender.pdf"
    generated_path = generate_demo_tender_pdf(str(pdf_path))
    assert Path(generated_path).exists()
    
    pages = extract_pdf_pages(generated_path)
    assert len(pages) == 43
    
    # Check Page 1
    assert pages[0]["page_number"] == 1
    assert "NATIONAL HIGHWAYS" in pages[0]["text"]
    
    # Check Page 4 (Deadlines & EMD)
    assert pages[3]["page_number"] == 4
    assert "2,00,000" in pages[3]["text"]
    assert "28 September 2026" in pages[3]["text"]
    
    # Check Page 17 (Turnover Rs. 5 Cr)
    assert pages[16]["page_number"] == 17
    assert "5 crore" in pages[16]["text"]
    
    # Check Page 19 (GST and PAN)
    assert pages[18]["page_number"] == 19
    assert "GST Registration Certificate" in pages[18]["text"]
    assert "PAN Card" in pages[18]["text"]
    
    # Check Page 22 (Ambiguous Experience)
    assert pages[21]["page_number"] == 22
    assert "relevant experience in executing" in pages[21]["text"]

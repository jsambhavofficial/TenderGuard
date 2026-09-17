import pytest
from app.nlp.normalizer import normalize_indian_currency, normalize_years, format_currency_inr

def test_normalize_crore():
    assert normalize_indian_currency("₹5 crore") == 50000000.0
    assert normalize_indian_currency("Rs. 5.5 Cr") == 55000000.0
    assert normalize_indian_currency("5 Crores") == 50000000.0

def test_normalize_lakh():
    assert normalize_indian_currency("₹2,00,000") == 200000.0
    assert normalize_indian_currency("2 lakh") == 200000.0
    assert normalize_indian_currency("25 Lacs") == 2500000.0

def test_normalize_thousand():
    assert normalize_indian_currency("₹10,000") == 10000.0
    assert normalize_indian_currency("50 thousand") == 50000.0

def test_normalize_years():
    assert normalize_years("5 years") == 5.0
    assert normalize_years("min 3 yrs") == 3.0
    assert normalize_years("no duration") is None

def test_format_currency_inr():
    assert format_currency_inr(50000000.0) == "₹5 Crore"
    assert format_currency_inr(200000.0) == "₹2 Lakh"
    assert format_currency_inr(10000.0) == "₹10,000"

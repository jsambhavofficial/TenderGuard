import re
from typing import Optional

def normalize_indian_currency(text: str) -> Optional[float]:
    """
    Normalizes text representations of Indian currency into floating point INR values.
    Examples:
    - 'Rs. 5 crore' or '₹5 crore' or 'Rs 5 Cr' or '5 Crores' -> 50000000.0
    - 'Rs. 2,00,000' or '₹2,00,000' or '2 lakh' or '2 Lacs' -> 200000.0
    - 'Rs. 10,000' or '10 thousand' -> 10000.0
    - 'Rs. 45,00,00,000' -> 450000000.0
    """
    if not text:
        return None
    
    clean = text.lower().replace(',', '').replace('₹', '').replace('rs.', '').replace('rs', '').replace('inr', '').replace('?', '').strip()
    
    # 1. Check Crore
    cr_match = re.search(r'([\d\.]+)\s*(?:crore|cr|crores)', clean)
    if cr_match:
        try:
            return float(cr_match.group(1)) * 10_000_000.0
        except ValueError:
            pass
            
    # 2. Check Lakh / Lac
    lakh_match = re.search(r'([\d\.]+)\s*(?:lakh|lac|lakhs|lacs)', clean)
    if lakh_match:
        try:
            return float(lakh_match.group(1)) * 100_000.0
        except ValueError:
            pass
            
    # 3. Check Thousand / k
    k_match = re.search(r'([\d\.]+)\s*(?:thousand|k)', clean)
    if k_match:
        try:
            return float(k_match.group(1)) * 1_000.0
        except ValueError:
            pass
            
    # 4. Plain numeric extraction
    num_match = re.search(r'([\d\.]+)', clean)
    if num_match:
        try:
            return float(num_match.group(1))
        except ValueError:
            pass
            
    return None

def normalize_years(text: str) -> Optional[float]:
    """
    Normalizes experience requirements like '5 years' or 'min 3 yrs' into float.
    """
    if not text:
        return None
    match = re.search(r'([\d\.]+)\s*(?:years?|yrs?)', text.lower())
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None

def format_currency_inr(val: float) -> str:
    """
    Formats an INR number into Indian numbering system string (e.g. ₹5 Crore or ₹2 Lakh).
    """
    if val >= 10_000_000:
        cr = val / 10_000_000
        return f"₹{cr:g} Crore" if cr == int(cr) else f"₹{cr:.2f} Crore"
    elif val >= 100_000:
        lakh = val / 100_000
        return f"₹{lakh:g} Lakh" if lakh == int(lakh) else f"₹{lakh:.2f} Lakh"
    elif val >= 1_000:
        return f"₹{val:,.0f}"
    else:
        return f"₹{val:,.0f}"

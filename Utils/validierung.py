import re
from datetime import datetime

def is_valid_email(value: str) -> bool:
    if not value.strip():
        return True  # empty is allowed
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()) is not None

def is_valid_phone(value: str) -> bool: # +49123456789 or 0123456789
    v = value.strip()
    if not v:
        return True
    if re.fullmatch(r"\+49\d{5,}$", v):
        return True
    if re.fullmatch(r"0\d{5,}$", v):
        return True
    return False

def parse_de_date(value: str):
    v = value.strip()
    if not v:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    return None

def fmt_de_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return value
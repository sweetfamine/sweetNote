import re
from datetime import datetime

def is_valid_email(value: str) -> bool:
    if not value.strip():
        return True  # leer zulassen (falls optional)
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()) is not None

def is_valid_phone(value: str) -> bool:
    v = value.strip()
    if not v:
        return True
    if not re.match(r"^\+?[0-9\s().-]{6,}$", v):
        return False
    return sum(c.isdigit() for c in v) >= 6

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
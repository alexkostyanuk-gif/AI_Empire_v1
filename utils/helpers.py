
import re

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).lower()

def extract_ordinal(text: str):
    """Return zero-based index for phrases like 'первая/вторая/третья/четвёртая/пятая' or '1-я/2-я/3-я' etc."""
    t = normalize_text(text)
    mapping = {
        "первая": 0, "1": 0, "1-я": 0, "1й": 0, "1-ая": 0,
        "вторая": 1, "2": 1, "2-я": 1, "2й": 1, "2-ая": 1,
        "третья": 2, "3": 2, "3-я": 2, "3й": 2, "3-ья": 2,
        "четвертая": 3, "четвёртая": 3, "4": 3, "4-я": 3,
        "пятая": 4, "5": 4, "5-я": 4,
        "последняя": -1
    }
    for k, idx in mapping.items():
        if k in t:
            return idx
    return None

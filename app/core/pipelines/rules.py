import re
from app.db.session import SessionLocal
from app.db.models import ScamPattern

# Genuine banks and agencies often include these warnings; scammers rarely do.
WARNING_PHRASES = [
    "jangan kongsi", "jangan berikan", "jangan dedahkan",
    "never share", "do not share", "don't share"
]

def _has_word(keyword: str, text: str) -> bool:
    """Whole-word match, so 'tac' does not fire inside 'contact' or 'attached'."""
    return re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text) is not None

def check_rules(text: str) -> tuple[int, list[str]]:
    # Use a context manager to prevent session leaks
    with SessionLocal() as db:
        patterns = db.query(ScamPattern).all()

    score = 0
    reasons = []
    text_lower = text.lower()
    matched_types = set()
    
    for p in patterns:
        if _has_word(p.keyword, text_lower):
            score += p.weight
            matched_types.add(p.scam_type)
            reasons.append(f"Contains suspicious {p.scam_type} keyword: '{p.keyword}'")
            
    is_warning = any(w in text_lower for w in WARNING_PHRASES)
    
    if is_warning and score:
        # Looks like a genuine "never share your TAC" reminder: cut the score, no combo bonus
        score = max(0, score - 40)
        reasons = ["Message warns you not to share codes, which genuine messages often do."]
    else:
        # Combination bonuses
        if "impersonation" in matched_types and "otp" in matched_types:
            score += 30
            reasons.append("Authority impersonation combined with TAC/OTP request.")
        if "job" in matched_types and ("telegram" in text_lower or "whatsapp" in text_lower):
            score += 25
            reasons.append("Job offer combined with Telegram/WhatsApp contact.")
            
    return min(score, 100), reasons
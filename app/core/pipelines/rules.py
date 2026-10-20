from app.db.session import SessionLocal
from app.db.models import ScamPattern

def check_rules(text: str) -> tuple[int, list[str]]:
    db = SessionLocal()
    patterns = db.query(ScamPattern).all()
    db.close()
    
    score = 0
    reasons = []
    text_lower = text.lower()
    matched_types = set()
    
    for p in patterns:
        if p.keyword in text_lower:
            score += p.weight
            matched_types.add(p.scam_type)
            reasons.append(f"Contains suspicious {p.scam_type} keyword: '{p.keyword}'")
            
    # Combination bonuses
    if "impersonation" in matched_types and "otp" in matched_types:
        score += 30
        reasons.append("Authority impersonation combined with TAC/OTP request.")
    if "job" in matched_types and ("telegram" in text_lower or "whatsapp" in text_lower):
        score += 25
        reasons.append("Job offer combined with Telegram/WhatsApp contact.")
        
    return min(score, 100), reasons
import hashlib
from app.db.session import SessionLocal
from app.db.models import MuleEntity, UserReport

def hash_value(val: str) -> str:
    return hashlib.sha256(val.encode('utf-8')).hexdigest()

def check_mules(entities: dict) -> tuple[int, list[str]]:
    max_score = 0
    reasons = []
    
    items_to_check = entities.get("accounts", []) + entities.get("phones", [])
    
    if not items_to_check:
        return 0, []

    # Use a context manager to prevent session leaks
    with SessionLocal() as db:
        for item in items_to_check:
            h = hash_value(item)
            
            # 1. Exact DB match: Score 100
            hit = db.query(MuleEntity).filter(MuleEntity.value_hash == h).first()
            if hit:
                max_score = 100
                reasons.append(f"Entity {hit.value_masked} found in official mule records.")
                continue
                
            # 2. User reports: Score 85 if >= 3
            report_count = db.query(UserReport).filter(UserReport.value_hash == h).count()
            if report_count >= 3:
                max_score = max(max_score, 85)
                reasons.append(f"Entity flagged by {report_count} user reports.")
                
    return max_score, reasons
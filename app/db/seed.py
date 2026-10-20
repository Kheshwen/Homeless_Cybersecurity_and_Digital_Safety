import json
import csv
import hashlib
from datetime import datetime
from app.config import DATA_DIR
from app.db.session import engine, SessionLocal
from app.db.models import Base, ScamPattern, MuleEntity

def hash_value(val: str) -> str:
    """Returns a SHA-256 hash of the normalized value."""
    return hashlib.sha256(val.encode('utf-8')).hexdigest()

def mask_value(val: str) -> str:
    """Returns the masked string keeping only the last 4 digits."""
    return f"****{val[-4:]}" if len(val) >= 4 else val

def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed Scam Patterns
    if db.query(ScamPattern).count() == 0:
        with open(DATA_DIR / "scam_phrases.json", "r", encoding="utf-8-sig") as f:
            phrases = json.load(f)
            for p in phrases:
                pattern = ScamPattern(**p)
                db.add(pattern)
        db.commit()

    # Seed Mule Entities
    if db.query(MuleEntity).count() == 0:
        with open(DATA_DIR / "seed_mules.csv", "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_val = row["value_raw"]
                entity = MuleEntity(
                    type=row["type"],
                    value_hash=hash_value(raw_val),
                    value_masked=mask_value(raw_val),
                    source=row["source"],
                    report_count=5, # High enough to trigger alerts
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow()
                )
                db.add(entity)
        db.commit()
    
    db.close()

if __name__ == "__main__":
    run_seed()
    print("Database seeded successfully.")
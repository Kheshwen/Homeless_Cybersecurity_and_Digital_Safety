import time
from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.db.session import get_db
from app.db.models import CheckLog, UserReport
from app.core.analyzer import analyze
from app.schemas import Verdict
from pydantic import BaseModel

router = APIRouter()

class ReportRequest(BaseModel):
    value: str
    entity_type: str
    scam_type: str

@router.post("/api/check", response_model=Verdict)
async def check_message(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    lang: Optional[str] = Form("ms"),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    # Note: Image OCR is built in Phase 5. For now, we process the text.
    input_text = text or ""
    verdict = analyze(input_text, lang)
    
    # Log the check
    latency = int((time.time() - start_time) * 1000)
    log_entry = CheckLog(
        channel="web",
        input_type="image" if image else "text",
        verdict=verdict.level,
        score=verdict.score,
        latency_ms=latency
    )
    db.add(log_entry)
    db.commit()
    
    return verdict

@router.post("/api/report")
def report_scam(report: ReportRequest, db: Session = Depends(get_db)):
    import hashlib
    value_hash = hashlib.sha256(report.value.encode('utf-8')).hexdigest()
    
    new_report = UserReport(
        entity_type=report.entity_type,
        value_hash=value_hash,
        scam_type=report.scam_type,
        reporter_hash="web_user" # Simplified for MVP
    )
    db.add(new_report)
    db.commit()
    
    count = db.query(UserReport).filter(UserReport.value_hash == value_hash).count()
    return {"ok": True, "report_count": count}

@router.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(CheckLog).count()
    danger = db.query(CheckLog).filter(CheckLog.verdict == "DANGER").count()
    caution = db.query(CheckLog).filter(CheckLog.verdict == "CAUTION").count()
    safe = db.query(CheckLog).filter(CheckLog.verdict == "SAFE").count()
    
    return {
        "total_checks": total,
        "verdict_split": {"DANGER": danger, "CAUTION": caution, "SAFE": safe}
    }
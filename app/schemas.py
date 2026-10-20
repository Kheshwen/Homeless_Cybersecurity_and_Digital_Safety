from pydantic import BaseModel
from typing import List, Dict, Optional

class CheckRequest(BaseModel):
    text: Optional[str] = ""
    image: Optional[str] = None
    lang: Optional[str] = "ms"

class Verdict(BaseModel):
    level: str
    score: int
    scam_type: str
    reasons: List[str]
    entities: Dict[str, List[str]]
    advice: str
    lang: str
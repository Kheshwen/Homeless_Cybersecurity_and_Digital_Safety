from app.core.extractor import extract_entities
from app.core.pipelines.mule_lookup import check_mules
from app.core.pipelines.rules import check_rules
from app.core.pipelines.url_check import check_urls
from app.core.scoring import calculate_final_score
from app.schemas import Verdict

def analyze(text: str, lang: str = "ms") -> Verdict:
    # Stage 1: Extraction
    entities = extract_entities(text)
    
    # Stages 2-4: Run checking pipelines
    mule_score, mule_reasons = check_mules(entities)
    rule_score, rule_reasons = check_rules(text)
    url_score, url_reasons = check_urls(entities.get("urls", []))
    
    # Phase 4 (LLM) is bypassed for now to ensure the deterministic fallback works
    llm_score = 0 
    
    # Score Fusion
    final_score, level = calculate_final_score(mule_score, url_score, rule_score, llm_score)
    
    # Combine reasons and prioritize hard evidence
    all_reasons = mule_reasons + url_reasons + rule_reasons
    
    # Generate action advice based on verdict and language
    advice = "Do not install or pay. Call NSRC at 997 if you already paid." if lang == "en" else "Jangan install atau bayar. Hubungi NSRC di 997 jika sudah bayar."
    if level == "SAFE":
         advice = "Looks safe, but always verify the source." if lang == "en" else "Kelihatan selamat, tetapi sentiasa semak sumbernya."
         
    # Basic scam type detection from rules (will be improved by LLM later)
    scam_type = "other"
    if "apk" in text.lower() or "install" in text.lower():
        scam_type = "malware"
    elif "kerja" in text.lower() or "commission" in text.lower():
        scam_type = "job"
    
    return Verdict(
        level=level,
        score=final_score,
        scam_type=scam_type,
        reasons=all_reasons[:2], # Keep it to 1-2 reasons for zero jargon UX
        entities=entities,
        advice=advice,
        lang=lang
    )
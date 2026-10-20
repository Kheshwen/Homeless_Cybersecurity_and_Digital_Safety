from app.core.extractor import extract_entities
from app.core.pipelines.mule_lookup import check_mules
from app.core.pipelines.rules import check_rules
from app.core.pipelines.url_check import check_urls
from app.core.pipelines.llm_intent import get_llm_intent
from app.core.scoring import calculate_final_score
from app.schemas import Verdict

def analyze(text: str, lang: str = "ms") -> Verdict:
    # Stage 1: Extraction
    entities = extract_entities(text)
    
    # Stages 2-4: Run deterministic checking pipelines
    mule_score, mule_reasons = check_mules(entities)
    rule_score, rule_reasons = check_rules(text)
    url_score, url_reasons = check_urls(entities.get("urls", []))
    
    # Stage 5: Tier 4 LLM Intent (Only if score is 20-80)
    llm_score = 0
    llm_data = {}
    if 20 <= rule_score <= 80:
        llm_score, llm_data = get_llm_intent(text)
    
    # Score Fusion
    final_score, level = calculate_final_score(mule_score, url_score, rule_score, llm_score)
    
    # Combine reasons and prioritize hard evidence
    all_reasons = mule_reasons + url_reasons + rule_reasons
    
    # If the LLM provided a reason and no hard evidence fired, use the LLM reason
    if not all_reasons and llm_data:
        reason_key = f"reason_{lang}"
        if reason_key in llm_data:
            all_reasons.append(llm_data[reason_key])
            
    # Default scam type detection from rules or LLM
    scam_type = llm_data.get("scam_type", "other")
    if "apk" in text.lower() or "install" in text.lower():
        scam_type = "malware"
    elif "kerja" in text.lower() or "commission" in text.lower():
        scam_type = "job"
        
    # Generate action advice based on verdict and language
    if level == "SAFE":
         advice = "Looks safe, but always verify the source." if lang == "en" else "Kelihatan selamat, tetapi sentiasa semak sumbernya."
    elif level == "CAUTION":
         advice = "Proceed with caution. Do not share personal info." if lang == "en" else "Berhati-hati. Jangan kongsi maklumat peribadi."
    else:
         advice = "Do not install or pay. Call NSRC at 997 if you already paid." if lang == "en" else "Jangan install atau bayar. Hubungi NSRC di 997 jika sudah bayar."

    return Verdict(
        level=level,
        score=final_score,
        scam_type=scam_type,
        reasons=all_reasons[:2],
        entities=entities,
        advice=advice,
        lang=lang
    )
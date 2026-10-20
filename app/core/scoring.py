def calculate_final_score(mule_score: int, url_score: int, rules_score: int, llm_score: int = 0) -> tuple[int, str]:
    """
    S = max(S_mule, S_url, 0.6 * S_rules + 0.4 * S_llm)
    """
    blended_soft_score = (0.6 * rules_score) + (0.4 * llm_score)
    final_score = int(max(mule_score, url_score, blended_soft_score))
    
    if final_score >= 70:
        verdict = "DANGER"
    elif final_score >= 35:
        verdict = "CAUTION"
    else:
        verdict = "SAFE"
        
    return final_score, verdict
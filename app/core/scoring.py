def calculate_final_score(mule_score: int, url_score: int, rules_score: int,
                          llm_score: int | None = None) -> tuple[int, str]:
    """
    With AI:     S = max(S_mule, S_url, 0.6 * S_rules + 0.4 * S_llm)
    Without AI:  S = max(S_mule, S_url, S_rules)   (llm_score=None, e.g. the AI call failed)
    """
    if llm_score is None:
        soft_score = rules_score
    else:
        soft_score = (0.6 * rules_score) + (0.4 * llm_score)
    final_score = int(max(mule_score, url_score, soft_score))

    # A weak link signal plus a weak keyword signal is more suspicious together than apart
    if url_score > 0 and rules_score > 0:
        final_score = max(final_score, min(100, url_score + rules_score))

    if final_score >= 70:
        verdict = "DANGER"
    elif final_score >= 35:
        verdict = "CAUTION"
    else:
        verdict = "SAFE"

    return final_score, verdict

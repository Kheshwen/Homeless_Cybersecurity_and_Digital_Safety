from app.core.scoring import calculate_final_score


def test_mule_hit_is_danger():
    assert calculate_final_score(100, 0, 0, 0) == (100, "DANGER")


def test_soft_scores_blend():
    score, level = calculate_final_score(0, 0, 50, 50)
    assert score == 50 and level == "CAUTION"


def test_nothing_found_is_safe():
    assert calculate_final_score(0, 0, 0, 0) == (0, "SAFE")


def test_without_ai_uses_rules_score_alone():
    # AI unavailable (None): a strong keyword score must not be shrunk
    assert calculate_final_score(0, 0, 40, None) == (40, "CAUTION")


def test_weak_link_plus_weak_keyword_is_caution():
    assert calculate_final_score(0, 25, 20, None)[1] == "CAUTION"

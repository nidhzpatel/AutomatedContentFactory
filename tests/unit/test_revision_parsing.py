from backend.flows.main_flow import _parse_critique, _parse_fact_check_response


def test_parse_critique_full_response():
    text = (
        "CLARITY: 6.5\n"
        "ENGAGEMENT: 5\n"
        "APPROVED: NO\n"
        "SUGGESTIONS:\n"
        "- Strengthen the introduction\n"
        "- Add concrete examples\n"
        "2. Fix conclusion"
    )
    critique = _parse_critique(text, ["fallback"])
    assert critique.clarity_score == 6.5
    assert critique.engagement_score == 5.0
    assert critique.approved is False
    assert "Strengthen the introduction" in critique.suggestions
    assert "Add concrete examples" in critique.suggestions
    assert "Fix conclusion" in critique.suggestions


def test_parse_critique_empty_text_falls_back_to_approved():
    critique = _parse_critique("", ["fallback"])
    assert critique.approved is True
    assert critique.clarity_score == 9.0
    assert critique.suggestions == ["fallback"]


def test_parse_critique_garbage_falls_back_to_approved():
    critique = _parse_critique("The article is nice but could be better.", ["fallback"])
    assert critique.approved is True
    assert critique.suggestions == ["fallback"]


def test_parse_critique_scores_clamped_to_range():
    text = "CLARITY: 42\nENGAGEMENT: -3\nAPPROVED: YES\n"
    critique = _parse_critique(text, [])
    assert critique.clarity_score == 10.0
    assert critique.engagement_score == 0.0
    assert critique.approved is True


def test_parse_critique_derives_approval_from_scores_when_missing():
    text = "CLARITY: 5\nENGAGEMENT: 9\n"
    critique = _parse_critique(text, [])
    assert critique.approved is False  # clarity below 7 threshold
    text = "CLARITY: 8\nENGAGEMENT: 7.5\n"
    critique = _parse_critique(text, [])
    assert critique.approved is True


def test_parse_fact_check_full_response():
    text = (
        "VERDICT: FAIL\n"
        "CLAIMS:\n"
        "- [VERIFIED] Python 3.12 was released in October 2023\n"
        "- [UNVERIFIED] This tool guarantees 1000% proven returns\n"
    )
    items, passed = _parse_fact_check_response(text)
    assert passed is False
    assert len(items) == 2
    assert items[0].is_verified is True
    assert items[1].is_verified is False
    assert "1000% proven" in items[1].statement


def test_parse_fact_check_empty_returns_no_verdict():
    items, passed = _parse_fact_check_response("")
    assert items == []
    assert passed is None


def test_parse_fact_check_garbage_returns_no_verdict():
    items, passed = _parse_fact_check_response("Everything looks mostly fine to me.")
    assert items == []
    assert passed is None

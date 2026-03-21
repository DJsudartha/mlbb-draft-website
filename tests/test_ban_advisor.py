from backend.services.modeling.advisor_pipeline import advise_bans


def test_advise_bans_uses_local_semantic_advisor():
    payload = advise_bans(team="blue", top_k=2)
    assert "recommendation" in payload
    assert "advisor" in payload
    assert payload["advisor"]["uses_llm"] is False
    assert payload["advisor"]["provider"] == "local-semantic"
    assert payload["advisor"]["model"]
    assert payload["advisor"]["advice"]
    assert "retrieved_principles" in payload["advisor"]
    assert payload["advisor"]["advice"].splitlines()[0].startswith("Ban ")

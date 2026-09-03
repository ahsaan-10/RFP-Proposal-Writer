import json
from pathlib import Path

from app.profile import OrgProfile, RateCardItem
from app.agent.prompts import extract_system, write_system, pricing_system

EXAMPLE = Path(__file__).resolve().parents[2] / "profile.example.json"


def test_defaults_work_without_a_profile_file():
    p = OrgProfile()
    assert p.proposal_sections[0] == "Executive Summary"
    assert "No rate card configured" in p.rate_card_text()


def test_example_profile_parses():
    p = OrgProfile(**json.loads(EXAMPLE.read_text(encoding="utf-8")))
    assert p.name and p.rate_card and p.services


def test_rate_card_text_includes_currency_and_rules():
    p = OrgProfile(currency="EUR",
                   rate_card=[RateCardItem(item="Senior engineer", unit="day", amount=1800)],
                   pricing_rules=["Never discount below 10 percent."])
    text = p.rate_card_text()
    assert "EUR 1,800 per day" in text
    assert "Rule: Never discount below 10 percent." in text


def test_prompts_carry_the_profile_not_hard_coded_branding():
    p = OrgProfile(name="Acme Industrial", description="a civil engineering contractor",
                   services=["bridge inspection"], proposal_sections=["Summary", "Method"],
                   requirement_categories=["scope", "safety"])
    assert "Acme Industrial" in write_system(p)
    assert "bridge inspection" in write_system(p)
    assert "scope|safety" in extract_system(p)
    assert "Acme Industrial" in pricing_system(p)

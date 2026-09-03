"""Organization profile — the one place the system is told who it writes for.

Nothing company-specific is hard-coded in the agent, the prompts, or the pricing
node. Everything is read from a JSON profile (default: profile.json at the repo
root, overridable with ORG_PROFILE_PATH). If no profile file exists, a neutral
default is used so the system still runs end to end out of the box.
"""
import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from .config import settings

DEFAULT_SECTIONS = [
    "Executive Summary", "Understanding of Requirements", "Proposed Approach",
    "Relevant Experience", "Team & Process", "Pricing Summary",
]
DEFAULT_CATEGORIES = ["scope", "technical", "commercial", "compliance", "general"]


class RateCardItem(BaseModel):
    item: str
    unit: str = "unit"          # day | hour | project | seat | licence | unit
    amount: float
    note: str = ""


class OrgProfile(BaseModel):
    """Who the proposals are written for, and on what commercial terms."""
    name: str = "Our Organization"
    description: str = "a professional services provider"
    tone: str = "professional, confident, concise"
    currency: str = "USD"
    services: list[str] = Field(default_factory=list)
    differentiators: list[str] = Field(default_factory=list)
    proposal_sections: list[str] = Field(default_factory=lambda: list(DEFAULT_SECTIONS))
    requirement_categories: list[str] = Field(default_factory=lambda: list(DEFAULT_CATEGORIES))
    rate_card: list[RateCardItem] = Field(default_factory=list)
    pricing_rules: list[str] = Field(default_factory=list)

    def services_text(self) -> str:
        return ", ".join(self.services) if self.services else "services described in the corpus"

    def sections_text(self) -> str:
        return ", ".join(self.proposal_sections)

    def categories_text(self) -> str:
        return "|".join(self.requirement_categories)

    def rate_card_text(self) -> str:
        if not self.rate_card and not self.pricing_rules:
            return ("No rate card configured. Price only from retrieved precedents, "
                    "and flag every line for human review in the note field.")
        lines = [f"- {i.item}: {self.currency} {i.amount:,.0f} per {i.unit}"
                 f"{' — ' + i.note if i.note else ''}" for i in self.rate_card]
        lines += [f"- Rule: {r}" for r in self.pricing_rules]
        return "\n".join(lines)


def _resolve(path_str: str) -> Path:
    """Find the profile whether the app is launched from the repo root, from
    backend/, or from /app inside the container."""
    candidate = Path(path_str)
    if candidate.is_absolute():
        return candidate
    for base in (Path.cwd(), *Path(__file__).resolve().parents):
        if (base / candidate).is_file():
            return base / candidate
    return candidate


@lru_cache(maxsize=1)
def load_profile() -> OrgProfile:
    path = _resolve(settings.org_profile_path)
    if path.is_file():
        return OrgProfile(**json.loads(path.read_text(encoding="utf-8")))
    return OrgProfile()

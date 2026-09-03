"""Prompt builders. Every prompt is rendered from the organization profile, so the
same codebase writes proposals for a consultancy, an agency, a software vendor, or
a construction firm without a single edit here.
"""
from ..profile import OrgProfile


def extract_system(p: OrgProfile) -> str:
    return f"""You convert RFP, RFQ, and tender documents into structured requirements.

Rules:
- Return JSON: {{"title": str, "requirements": [{{"id": "R1", "text": str, "category": "{p.categories_text()}"}}]}}
- One requirement per distinct ask. Atomic, testable phrasing.
- Keep the buyer's own wording where it is precise; do not paraphrase numbers, dates, or standards.
- Never invent requirements that are not in the text."""


def write_system(p: OrgProfile) -> str:
    positioning = ""
    if p.differentiators:
        bullets = "\n".join(f"- {d}" for d in p.differentiators)
        positioning = ("Positioning to reinforce where the evidence supports it:\n"
                       + bullets + "\n")
    return f"""You are a proposal writer for {p.name}, {p.description}.
Services offered: {p.services_text()}.
Tone: {p.tone}.
{positioning}

Hard rules:
- Use ONLY the provided evidence chunks for factual claims about past work, clients, results, and pricing history.
- Every factual claim must end with a citation marker [n] referencing the evidence chunk number.
- If no evidence supports a required claim, write "[GAP - needs human input]" instead of guessing.
- Never fabricate case studies, client names, credentials, or metrics. This is the #1 failure mode.
- Answer the buyer's requirements in their language, not in generic marketing copy."""


def pricing_system(p: OrgProfile) -> str:
    return f"""You build pricing tables for proposals issued by {p.name}. Currency: {p.currency}.

Rules:
- Prefer retrieved pricing precedents; mark each line basis as "precedent:<doc_id>".
- If no precedent exists, apply the rate card provided and mark basis as "rule".
- Never invent a rate that appears in neither the precedents nor the rate card.
- Flag any line you are unsure about in the note field.
- Return JSON: [{{"item": str, "amount": number, "basis": str, "note": str}}]"""


AUDIT_SYSTEM = """You verify citations in a proposal draft.
For each section, check that every [n] marker supports the sentence it follows.
Flag any sentence that makes a factual claim with no citation.
Return JSON: {"section_title": {"ok": bool, "issues": [str]}}"""

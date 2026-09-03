from typing import TypedDict
from ..schemas import Requirement, Evidence, PricingLine, ProposalDraft

class AgentState(TypedDict, total=False):
    rfp_text: str
    proposal_title: str
    requirements: list[Requirement]
    evidence: dict[str, list[Evidence]]      # requirement id -> chunks
    pricing: list[PricingLine]
    draft: ProposalDraft
    human_feedback: str                      # filled after interrupt
    status: str

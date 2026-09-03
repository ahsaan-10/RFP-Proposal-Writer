"""LangGraph agent: extract -> retrieve -> price -> write -> [INTERRUPT for human] -> export.

Human-in-the-loop: the graph interrupts before finalize. The reviewer edits the draft
and/or leaves feedback, then the run is resumed with Command(resume=...).
"""
import json
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from ..llm import chat, chat_json
from ..schemas import Requirement, ProposalDraft, ProposalSection, PricingLine
from ..retrieval.hybrid import retrieve
from ..profile import load_profile
from .prompts import extract_system, write_system, pricing_system, AUDIT_SYSTEM
from .state import AgentState

def extract_requirements(state: AgentState) -> dict:
    out = chat_json(extract_system(load_profile()), f"RFP document:\n\n{state['rfp_text'][:24000]}")
    reqs = [Requirement(**r) for r in out.get("requirements", [])]
    return {"requirements": reqs,
            "proposal_title": out.get("title", "Untitled Proposal"),
            "status": "requirements_extracted"}

def retrieve_evidence(state: AgentState) -> dict:
    evidence = {r.id: retrieve(r.text) for r in state["requirements"]}
    return {"evidence": evidence, "status": "evidence_retrieved"}

def build_pricing(state: AgentState) -> dict:
    seen, precedents = set(), []
    for evs in state["evidence"].values():
        for e in evs:
            if e.doc_id not in seen:
                seen.add(e.doc_id)
                precedents.append(f"[doc:{e.doc_id}] {e.filename}\n{e.text[:800]}")
    profile = load_profile()
    lines = chat_json(pricing_system(profile),
        f"Requirements:\n{json.dumps([r.model_dump() for r in state['requirements']], indent=2)}\n\n"
        f"Pricing precedents:\n" + "\n---\n".join(precedents[:8]) +
        f"\n\nRate card (use when no precedent applies):\n{profile.rate_card_text()}")
    rows = lines if isinstance(lines, list) else lines.get("lines", [])
    return {"pricing": [PricingLine(**l) for l in rows], "status": "priced"}

def write_proposal(state: AgentState) -> dict:
    flat, n = [], 1
    for rid, evs in state["evidence"].items():
        for e in evs[:4]:
            flat.append((n, rid, e)); n += 1
    evidence_block = "\n\n".join(
        f"[{i}] (req {rid}, source: {e.filename} > {e.heading})\n{e.text[:1200]}"
        for i, rid, e in flat)
    feedback = state.get("human_feedback", "")
    profile = load_profile()
    out = chat_json(write_system(profile),
        f"Proposal title: {state['proposal_title']}\n\n"
        f"Requirements:\n{json.dumps([r.model_dump() for r in state['requirements']], indent=2)}\n\n"
        f"Evidence chunks (cite as [n]):\n{evidence_block}\n\n"
        f"Pricing:\n{json.dumps([p.model_dump() for p in state['pricing']], indent=2)}\n\n"
        + (f"Reviewer feedback to incorporate: {feedback}\n\n" if feedback else "")
        + 'Return JSON: {"sections": [{"title": str, "body": str, "citations": [int]}]}. '
        f"Use exactly these sections, in this order: {profile.sections_text()}.")
    draft = ProposalDraft(
        title=state["proposal_title"],
        sections=[ProposalSection(**s) for s in out.get("sections", [])],
        pricing=state["pricing"])
    audit = chat_json(AUDIT_SYSTEM,
        f"Draft:\n{json.dumps([s.model_dump() for s in draft.sections], indent=2)}\n\n"
        f"Evidence:\n{evidence_block}")
    draft.citation_audit = audit if isinstance(audit, dict) else {}
    return {"draft": draft, "status": "awaiting_approval"}

def human_approval(state: AgentState) -> dict:
    """Interrupt point. The API layer resumes with {'approved': bool, 'feedback': str, 'edited_sections': [...]}"""
    decision = interrupt({"draft": state["draft"].model_dump()})
    if decision.get("edited_sections"):
        state["draft"].sections = [ProposalSection(**s) for s in decision["edited_sections"]]
    if not decision.get("approved"):
        return {"human_feedback": decision.get("feedback", ""), "status": "revision_requested"}
    return {"status": "approved"}

def finalize(state: AgentState) -> dict:
    return {"status": "done"}

def route_after_approval(state: AgentState) -> str:
    return "finalize" if state["status"] == "approved" else "write_proposal"

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("extract_requirements", extract_requirements)
    g.add_node("retrieve_evidence", retrieve_evidence)
    g.add_node("build_pricing", build_pricing)
    g.add_node("write_proposal", write_proposal)
    g.add_node("human_approval", human_approval)
    g.add_node("finalize", finalize)
    g.add_edge(START, "extract_requirements")
    g.add_edge("extract_requirements", "retrieve_evidence")
    g.add_edge("retrieve_evidence", "build_pricing")
    g.add_edge("build_pricing", "write_proposal")
    g.add_edge("write_proposal", "human_approval")
    g.add_conditional_edges("human_approval", route_after_approval,
                            {"finalize": "finalize", "write_proposal": "write_proposal"})
    g.add_edge("finalize", END)
    return g

checkpointer = MemorySaver()   # swap for PostgresSaver in production
graph = build_graph().compile(checkpointer=checkpointer)

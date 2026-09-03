"""API surface: documents, proposal runs (start/resume/status), export."""
import uuid
from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from langgraph.types import Command
from ..db import connect, init_db
from ..agent.graph import graph
from ..export.docx_export import draft_to_docx
from ..ingestion.pipeline import parse_file
import tempfile, pathlib

router = APIRouter()

class ResumeRequest(BaseModel):
    approved: bool
    feedback: str = ""
    edited_sections: list[dict] | None = None

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/documents")
def list_documents():
    init_db()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, filename, industry, service_type, year, outcome FROM documents ORDER BY ingested_at DESC")
        cols = ["id", "filename", "industry", "service_type", "year", "outcome"]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@router.post("/proposals")
async def start_proposal(file: UploadFile):
    """Upload an RFP (PDF/DOCX/TXT) and start the agent graph. Runs until the human-approval interrupt."""
    suffix = pathlib.Path(file.filename or "rfp.txt").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = pathlib.Path(tmp.name)
    try:
        rfp_text = parse_file(tmp_path)
    except ValueError as e:
        raise HTTPException(400, str(e))
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"rfp_text": rfp_text, "status": "started"}, config)
    return {"thread_id": thread_id, "status": "awaiting_approval"}

@router.get("/proposals/{thread_id}")
def proposal_status(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    snap = graph.get_state(config)
    if not snap.values:
        raise HTTPException(404, "Unknown thread_id")
    draft = snap.values.get("draft")
    return {
        "thread_id": thread_id,
        "status": snap.values.get("status"),
        "requirements": [r.model_dump() for r in snap.values.get("requirements", [])],
        "draft": draft.model_dump() if draft else None,
        "interrupted": bool(snap.next),
    }

@router.post("/proposals/{thread_id}/resume")
def resume_proposal(thread_id: str, req: ResumeRequest):
    """Human decision: approve (finish) or reject with feedback (loop back to the writer)."""
    config = {"configurable": {"thread_id": thread_id}}
    snap = graph.get_state(config)
    if not snap.values:
        raise HTTPException(404, "Unknown thread_id")
    graph.invoke(Command(resume=req.model_dump()), config)
    return proposal_status(thread_id)

@router.get("/proposals/{thread_id}/export")
def export_docx(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    snap = graph.get_state(config)
    draft = snap.values.get("draft") if snap.values else None
    if not draft:
        raise HTTPException(404, "No draft for this thread_id")
    data = draft_to_docx(draft)
    return Response(content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{draft.title or "proposal"}.docx"'})

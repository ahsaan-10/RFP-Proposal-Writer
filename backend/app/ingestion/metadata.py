"""Metadata from sidecar files (authoritative) with an LLM fallback for bare docs."""
import json
from pathlib import Path
from ..schemas import DocMetadata
from ..llm import chat_json
from ..profile import load_profile

def load_metadata(path: Path, text_preview: str) -> DocMetadata:
    sidecar = path.with_suffix(path.suffix + ".meta.json")
    if sidecar.exists():
        data = json.loads(sidecar.read_text())
        data.setdefault("doc_id", path.stem)
        data.setdefault("filename", path.name)
        return DocMetadata(**data)
    profile = load_profile()
    hint = ("Known service types: " + profile.services_text() + ". "
            "Use one of these when it fits; otherwise use your own short label.")
    data = chat_json(
        "You extract metadata from business documents.",
        "From this document excerpt, return JSON with keys "
        "industry, service_type, year (int or null), outcome (won|lost|unknown). "
        + hint + chr(10) + chr(10) + text_preview[:3000])
    return DocMetadata(doc_id=path.stem, filename=path.name, **data)

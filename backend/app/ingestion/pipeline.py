"""parse -> chunk (by section) -> embed -> store with metadata."""
from pathlib import Path
from pypdf import PdfReader
from docx import Document as Docx
from ..db import connect
from ..llm import embed
from ..schemas import DocMetadata
from .chunker import chunk_document
from .metadata import load_metadata

def parse_file(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".pdf":
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    if suf == ".docx":
        return "\n".join(p.text for p in Docx(str(path)).paragraphs)
    if suf in (".md", ".txt"):
        return path.read_text(errors="ignore")
    raise ValueError(f"Unsupported file type: {path.name}")

def ingest_file(path: Path, conn) -> DocMetadata:
    text = parse_file(path)
    meta = load_metadata(path, text)
    chunks = chunk_document(meta.doc_id, text)
    vectors = embed([c.text for c in chunks])
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO documents (id, filename, industry, service_type, year, outcome) "
            "VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET "
            "filename=EXCLUDED.filename, industry=EXCLUDED.industry, "
            "service_type=EXCLUDED.service_type, year=EXCLUDED.year, outcome=EXCLUDED.outcome",
            (meta.doc_id, meta.filename, meta.industry, meta.service_type, meta.year, meta.outcome))
        cur.execute("DELETE FROM chunks WHERE doc_id = %s", (meta.doc_id,))
        cur.executemany(
            "INSERT INTO chunks (doc_id, heading, text, token_count, embedding) "
            "VALUES (%s,%s,%s,%s,%s)",
            [(c.doc_id, c.heading, c.text, c.token_count, v) for c, v in zip(chunks, vectors)])
    return meta

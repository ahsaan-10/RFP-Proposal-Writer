"""CLI: python -m app.ingestion.run_ingest /corpus"""
import sys
from pathlib import Path
from ..db import init_db, connect
from .pipeline import ingest_file

def main():
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "/corpus")
    init_db()
    files = [p for p in sorted(folder.iterdir())
             if p.suffix.lower() in (".pdf", ".docx", ".md", ".txt")]
    if not files:
        print(f"No documents found in {folder}. Add PDF/DOCX/MD/TXT files and re-run.")
        return
    with connect() as conn:
        for f in files:
            meta = ingest_file(f, conn)
            print(f"ingested  {meta.filename}  [{meta.industry} / {meta.service_type} / {meta.outcome}]")
    print(f"\nDone. {len(files)} documents in the corpus.")

if __name__ == "__main__":
    main()

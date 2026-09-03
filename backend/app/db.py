"""Postgres + pgvector: one database for vectors, full-text, and metadata."""
import psycopg
from .config import settings

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    filename    TEXT NOT NULL,
    industry    TEXT,
    service_type TEXT,
    year        INT,
    outcome     TEXT,
    ingested_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS chunks (
    id          BIGSERIAL PRIMARY KEY,
    doc_id      TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    heading     TEXT,
    text        TEXT NOT NULL,
    token_count INT,
    embedding   vector(1536),
    tsv         tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING gin (tsv);
CREATE INDEX IF NOT EXISTS chunks_doc_idx ON chunks(doc_id);
"""

def connect():
    return psycopg.connect(settings.database_url, autocommit=True)

def init_db():
    with connect() as conn:
        conn.execute(SCHEMA)

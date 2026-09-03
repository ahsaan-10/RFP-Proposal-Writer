"""Hybrid retrieval: pgvector cosine + Postgres full-text (BM25-style ts_rank),
merged with Reciprocal Rank Fusion, then optionally re-ranked (Cohere free tier)."""
from ..db import connect
from ..llm import embed
from ..schemas import Evidence
from ..config import settings

VECTOR_SQL = """
SELECT c.id, c.doc_id, d.filename, c.heading, c.text,
       1 - (c.embedding <=> %s::vector) AS score
FROM chunks c JOIN documents d ON d.id = c.doc_id
ORDER BY c.embedding <=> %s::vector LIMIT %s;
"""
FTS_SQL = """
SELECT c.id, c.doc_id, d.filename, c.heading, c.text,
       ts_rank(c.tsv, plainto_tsquery('english', %s)) AS score
FROM chunks c JOIN documents d ON d.id = c.doc_id
WHERE c.tsv @@ plainto_tsquery('english', %s)
ORDER BY score DESC LIMIT %s;
"""

def _rrf(*rankings: list[Evidence], k: int = 60) -> list[Evidence]:
    scores, pool = {}, {}
    for ranking in rankings:
        for rank, ev in enumerate(ranking):
            scores[ev.chunk_id] = scores.get(ev.chunk_id, 0.0) + 1.0 / (k + rank + 1)
            pool[ev.chunk_id] = ev
    merged = sorted(pool.values(), key=lambda e: scores[e.chunk_id], reverse=True)
    for ev in merged:
        ev.score = scores[ev.chunk_id]
    return merged

def _rerank(query: str, docs: list[Evidence], top_k: int) -> list[Evidence]:
    if not settings.cohere_api_key or not docs:
        return docs[:top_k]
    try:
        import cohere
        client = cohere.Client(settings.cohere_api_key)
        res = client.rerank(model="rerank-english-v3.0", query=query,
                            documents=[d.text for d in docs], top_n=top_k)
        return [docs[r.index] for r in res.results]
    except Exception:
        return docs[:top_k]      # rerank is a nicety, never a failure mode

def retrieve(query: str, top_k: int | None = None,
             industry: str | None = None) -> list[Evidence]:
    top_k = top_k or settings.retrieval_top_k
    vec = embed([query])[0]
    with connect() as conn, conn.cursor() as cur:
        cur.execute(VECTOR_SQL, (vec, vec, top_k * 2))
        vrows = cur.fetchall()
        cur.execute(FTS_SQL, (query, query, top_k * 2))
        frows = cur.fetchall()
    to_ev = lambda r: Evidence(chunk_id=r[0], doc_id=r[1], filename=r[2],
                               heading=r[3] or "", text=r[4], score=float(r[5] or 0))
    merged = _rrf([to_ev(r) for r in vrows], [to_ev(r) for r in frows])
    return _rerank(query, merged, top_k)

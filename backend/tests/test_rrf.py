from app.retrieval.hybrid import _rrf
from app.schemas import Evidence

def ev(i):
    return Evidence(chunk_id=i, doc_id="d", filename="f", text=f"t{i}")

def test_rrf_merges_and_ranks():
    a = [ev(1), ev(2), ev(3)]
    b = [ev(3), ev(1)]
    merged = _rrf(a, b)
    ids = [e.chunk_id for e in merged]
    assert ids[0] == 1            # appears in both, highest combined rank
    assert set(ids) == {1, 2, 3}

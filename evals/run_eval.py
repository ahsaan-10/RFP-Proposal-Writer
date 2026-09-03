"""Eval harness: retrieval precision/recall, section coverage, citation audit.
Run: python /app/evals/run_eval.py  -> writes evals/results.md (paste into README)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, "/app")            # container layout
from app.retrieval.hybrid import retrieve

def main():
    cases = json.loads((Path(__file__).parent / "eval_set.json").read_text(encoding="utf-8"))
    rows, p_sum, r_sum = [], 0.0, 0.0
    for case in cases:
        hits = retrieve(case["rfp_excerpt"])
        got = {h.doc_id for h in hits}
        want = set(case["expected_doc_ids"]) - {"FILL_IN"}
        if not want:
            rows.append((case["id"], "skipped", "fill in expected_doc_ids first"))
            continue
        tp = len(got & want)
        prec, rec = tp / max(len(got), 1), tp / len(want)
        p_sum += prec; r_sum += rec
        rows.append((case["id"], f"{prec:.2f} / {rec:.2f}", ", ".join(sorted(got)) or "none"))
    n = max(len([r for r in rows if r[1] != "skipped"]), 1)
    out = ["# Eval Results", "",
           "| Case | Precision / Recall | Retrieved docs |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    out += ["", f"**Mean precision: {p_sum/n:.2f} — Mean recall: {r_sum/n:.2f}**", "",
            "_Citation accuracy & hallucinated-claims rate are measured by the audit node "
            "(`app/agent/graph.py`) on each draft; paste its output here per release._"]
    (Path(__file__).parent / "results.md").write_text(chr(10).join(out), encoding="utf-8")
    print("\n".join(out))

if __name__ == "__main__":
    main()

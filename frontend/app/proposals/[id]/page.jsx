"use client";
import { useEffect, useState } from "react";
import { getProposal, resumeProposal, exportUrl } from "../../../lib/api";

export default function ReviewPage({ params }) {
  const { id } = params;
  const [data, setData] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { getProposal(id).then(setData).catch(console.error); }, [id]);

  async function decide(approved) {
    setBusy(true);
    try { setData(await resumeProposal(id, { approved, feedback })); }
    finally { setBusy(false); setFeedback(""); }
  }

  if (!data) return <main style={{ padding: 48 }}>Loading…</main>;
  const draft = data.draft;

  return (
    <main style={{ maxWidth: 860, margin: "40px auto", padding: "0 24px" }}>
      <p><a href="/" style={{ color: "#555" }}>← New RFP</a></p>
      <h1 style={{ fontSize: 26 }}>{draft?.title || "Proposal"}</h1>
      <p style={{ color: "#555" }}>Status: <b>{data.status}</b></p>

      <h2 style={{ fontSize: 18, marginTop: 28 }}>Extracted requirements</h2>
      <ul>
        {data.requirements?.map(r => (
          <li key={r.id}><b>{r.id}</b> ({r.category}) — {r.text}</li>
        ))}
      </ul>

      {draft && (<>
        <h2 style={{ fontSize: 18, marginTop: 28 }}>Draft</h2>
        {draft.sections.map((s, i) => (
          <section key={i} style={{ background: "#fff", border: "1px solid #e2e2e2",
                                    borderRadius: 10, padding: 20, marginBottom: 16 }}>
            <h3 style={{ marginTop: 0 }}>{s.title}</h3>
            <p style={{ whiteSpace: "pre-wrap" }}>{s.body}</p>
            {s.citations?.length > 0 &&
              <p style={{ color: "#777", fontSize: 13 }}>Sources: {s.citations.map(c => `[${c}]`).join(" ")}</p>}
          </section>
        ))}

        {draft.pricing?.length > 0 && (<>
          <h2 style={{ fontSize: 18 }}>Pricing</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", background: "#fff" }}>
            <thead><tr>{["Item", "Amount", "Basis", "Note"].map(h =>
              <th key={h} style={{ textAlign: "left", borderBottom: "2px solid #ddd", padding: 8 }}>{h}</th>)}</tr></thead>
            <tbody>{draft.pricing.map((p, i) => (
              <tr key={i}>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{p.item}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>${p.amount.toLocaleString()}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{p.basis}</td>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{p.note}</td>
              </tr>))}</tbody>
          </table>
        </>)}

        <h2 style={{ fontSize: 18, marginTop: 28 }}>Your call</h2>
        <textarea value={feedback} onChange={e => setFeedback(e.target.value)}
          placeholder="Feedback for revision (only needed if you reject)…"
          style={{ width: "100%", minHeight: 80, padding: 10, borderRadius: 8, border: "1px solid #ccc" }} />
        <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
          <button disabled={busy} onClick={() => decide(true)}
            style={{ padding: "10px 20px", background: "#166534", color: "#fff",
                     border: 0, borderRadius: 8, cursor: "pointer" }}>Approve</button>
          <button disabled={busy} onClick={() => decide(false)}
            style={{ padding: "10px 20px", background: "#b91c1c", color: "#fff",
                     border: 0, borderRadius: 8, cursor: "pointer" }}>Revise</button>
          <a href={exportUrl(id)} style={{ marginLeft: "auto", alignSelf: "center" }}>Export DOCX</a>
        </div>
      </>)}
    </main>
  );
}

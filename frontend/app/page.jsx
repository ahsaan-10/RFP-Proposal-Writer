"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { startProposal } from "../lib/api";

export default function Home() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  async function onUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true); setError("");
    try {
      const { thread_id } = await startProposal(file);
      router.push(`/proposals/${thread_id}`);
    } catch (err) {
      setError(String(err)); setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 720, margin: "80px auto", padding: "0 24px" }}>
      <h1 style={{ fontSize: 32, marginBottom: 8 }}>RFP Proposal Writer</h1>
      <p style={{ color: "#555", marginBottom: 32 }}>
        Upload an RFP. The agent extracts requirements, retrieves matching past work,
        drafts a cited proposal, and pauses for your approval.
      </p>
      <label style={{
        display: "block", padding: 48, border: "2px dashed #bbb", borderRadius: 12,
        textAlign: "center", cursor: busy ? "wait" : "pointer", background: "#fff"
      }}>
        {busy ? "Agent is working — extracting, retrieving, drafting…" : "Drop a PDF / DOCX / TXT RFP here, or click to browse"}
        <input type="file" accept=".pdf,.docx,.txt,.md" hidden onChange={onUpload} disabled={busy} />
      </label>
      {error && <p style={{ color: "#b00020", marginTop: 16 }}>{error}</p>}
    </main>
  );
}

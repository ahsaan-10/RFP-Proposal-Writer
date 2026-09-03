const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function startProposal(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/api/proposals`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getProposal(threadId) {
  const res = await fetch(`${API}/api/proposals/${threadId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function resumeProposal(threadId, payload) {
  const res = await fetch(`${API}/api/proposals/${threadId}/resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const exportUrl = (threadId) => `${API}/api/proposals/${threadId}/export`;

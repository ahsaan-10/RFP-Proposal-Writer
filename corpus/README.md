# Corpus

Drop 30-50 of your own documents here (PDF / DOCX / MD / TXT). Anything that carries
evidence of what you have done and what you charge:

- past proposals and bids
- statements of work and contracts
- case studies and reference stories
- pricing sheets, rate cards, quotes
- capability statements, certifications, team bios

Retrieval quality is roughly 70% of this system, so the corpus matters more than the
model choice. Anonymize client names before pushing anything to a public repo.

## Metadata

Add an optional sidecar next to each file, e.g. `platform-migration-2024.pdf.meta.json`:

    {
      "industry": "healthcare",
      "service_type": "data platform migration",
      "year": 2024,
      "outcome": "won"
    }

Sidecars are authoritative. Without one, metadata is inferred by the LLM at ingest
time, using the service list in `profile.json` as a hint.

Then run: `make ingest`

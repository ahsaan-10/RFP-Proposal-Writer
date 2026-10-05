# RFP Proposal Writer

**An LLM workflow for turning an RFP into a proposal draft with retrieved evidence, pricing suggestions, and human review.**

[Demo interface](https://rfp-proposal-writer-dusky.vercel.app) · [Architecture](docs/architecture.md) · [Deployment](docs/DEPLOY.md)

## The problem it addresses

Proposal writing involves reading requirements, finding relevant past work, assembling pricing, and keeping claims tied to evidence. This prototype brings those steps into one reviewable workflow.

## What it does

1. Accepts an RFP as PDF, DOCX, or TXT and extracts requirements.
2. Retrieves relevant evidence from an ingested document corpus using vector search and PostgreSQL full-text search, merged with reciprocal rank fusion.
3. Drafts pricing using retrieved precedents and a configurable rate card.
4. Generates proposal sections with citation references and an LLM citation audit.
5. Pauses the LangGraph workflow for review; rejection with feedback returns to drafting.
6. Provides a DOCX export endpoint.

Business identity, services, proposal sections, pricing rules, and tone come from `profile.json`, rather than a company hardcoded in the application.

## Implementation status

The review interrupt and revision loop are implemented. **The current export endpoint does not check approval status**, so workflow review is not yet a server-enforced export restriction. Graph checkpoints use `MemorySaver` and do not survive a process restart. Citation auditing is model-assisted and does not guarantee factual correctness.

The hosted link exposes the frontend. End-to-end generation requires a working API, PostgreSQL with pgvector, an ingested corpus, and a configured model provider.

## Stack

| Layer | Technology |
| --- | --- |
| Workflow | Python, LangGraph |
| Model access | Claude or OpenAI through a client abstraction |
| Retrieval | PostgreSQL, pgvector, full-text search, reciprocal rank fusion; optional Cohere reranking |
| API | FastAPI |
| Interface | Next.js, React |
| Documents | pypdf, python-docx |

## Run locally

Prerequisites: Docker with Compose for the container setup; a configured model API key for real generation.

```bash
git clone https://github.com/ahsaan-10/RFP-Proposal-Writer.git
cd RFP-Proposal-Writer
cp .env.example .env
cp profile.example.json profile.json
```

Edit `.env` for the selected model and embedding providers, and personalize `profile.json`. Then:

```bash
docker compose up --build
```

Place sample or anonymized documents in `corpus/`, then run ingestion from another terminal:

```bash
docker compose exec backend python -m app.ingestion.run_ingest /corpus
```

Open the frontend at `http://localhost:3000`; the API runs at `http://localhost:8000`.

For Windows without Docker, configure a PostgreSQL instance supporting the `vector` extension and use:

```powershell
Copy-Item .env.example .env
Copy-Item profile.example.json profile.json
.\scripts\dev.ps1 test
.\scripts\dev.ps1 ingest
.\scripts\dev.ps1
```

The helper expects Python 3.11 through the Windows `py` launcher. Start the frontend in a separate terminal using `npm install` and `npm run dev` from `frontend/`.

## Evaluation

```bash
docker compose exec backend pytest -q
docker compose exec backend python /app/evals/run_eval.py
```

The previous README reported retrieval recall of 1.00 and precision of 0.33 on a five-document corpus with deterministic stub embeddings. These figures describe a small pipeline exercise; they do not measure semantic retrieval quality. Citation accuracy and hallucinated-claim rate were not measured. Re-run the harness with real embeddings and representative documents before reporting model quality.

## Repository map

```text
backend/app/
  ingestion/    Document parsing, section chunking, metadata, storage
  retrieval/    Hybrid retrieval and evidence ranking
  agent/        Workflow graph, prompts, and state
  api/          Upload, status, review, and export routes
  export/       DOCX generation
backend/tests/  Chunking, profile, and rank-fusion checks
frontend/       Upload and review interface
evals/          Retrieval evaluation set and runner
corpus/         Source-document instructions
docs/           Architecture and deployment guide
scripts/        Windows development helper
profile.json    Business-specific configuration
```

## A short walkthrough

Use sample documents, upload an RFP, inspect extracted requirements and draft citations, request a revision, and show the resulting DOCX. Describe the review interrupt and export restriction separately when presenting the prototype.

# Architecture

```
                 ┌─────────────────────────── Docker Compose ───────────────────────────┐
                 │                                                                      │
 Browser         │   Next.js (3000)        FastAPI (8000)          Postgres 16          │
   │    upload   │      │  POST /proposals      │                    + pgvector          │
   └────────────►│      └──────────────────────►│                     + full-text (tsv)  │
                 │                              │                            ▲         │
                 │        LangGraph agent graph │  embed / query             │         │
                 │                              ▼                            │         │
                 │   extract ─► retrieve ─► price ─► write ─► [INTERRUPT] ─► finalize   │
                 │   requirements   hybrid     rules +   section-   human    DOCX      │
                 │   (JSON)         vector+    pricing   by-section approval export    │
                 │                  FTS+RRF    precedents + citations edit/resume       │
                 │                                                                      │
                 └──────────────────────────────────────────────────────────────────────┘

LLM: Claude or GPT behind a thin client abstraction (app/llm.py) — swap via LLM_PROVIDER.
Evals: evals/run_eval.py measures retrieval precision/recall; the audit node checks citations.
```

Profile: every prompt, the section list, the requirement taxonomy, and the fallback
rate card are rendered from `profile.json` (app/profile.py). The graph itself carries
no company-specific text.

# Deploy

Three free tiers: Neon for Postgres, Render for the API, Vercel for the UI.
Total cost is zero until you add LLM tokens.

## 1. Database (Neon)

1. Sign in at neon.tech and create a project. Any region near you is fine.
2. Copy the pooled connection string. It looks like
   `postgresql://USER:PASSWORD@ep-xxx-pooler.REGION.aws.neon.tech/neondb?sslmode=require`
3. Nothing else to do. The app runs `CREATE EXTENSION IF NOT EXISTS vector` and creates
   its tables on first boot, and Neon permits both.

## 2. Backend (Render)

1. Push this repo to GitHub.
2. Render dashboard: New > Blueprint, select the repo. `render.yaml` is detected.
3. Set the two secrets it asks for:
   - `DATABASE_URL` = the Neon string from step 1
   - `ALLOWED_ORIGINS` = your Vercel URL (set it after step 3, redeploy is instant)
4. Deploy. Health check is `/api/health`, which returns `{"ok": true}`.

Free instances sleep after 15 minutes idle, so the first request after a pause takes
about 30 seconds. Say so in your demo video rather than letting a reviewer wonder.

## 3. Frontend (Vercel)

1. Vercel: Add New > Project, import the same repo.
2. Set **Root Directory** to `frontend`. Framework preset is detected as Next.js.
3. Add one environment variable:
   `NEXT_PUBLIC_API_URL` = your Render URL, e.g. `https://rfp-backend.onrender.com`
4. Deploy, then paste the resulting URL back into Render's `ALLOWED_ORIGINS`.

## 4. Load the corpus

Ingestion runs from your machine against the same Neon database, so you never need a
shell on the free Render instance:

```powershell
# from the repo root, with .env pointing DATABASE_URL at Neon
.venv\Scripts\python.exe -m app.ingestion.run_ingest ..\corpus   # run inside backend```

## 5. Add an LLM key when you have one

Set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY` with `LLM_PROVIDER=openai`) in Render, and
switch `EMBEDDING_PROVIDER` to `openai` for real semantic embeddings. Re-run ingestion
after that switch: stub and OpenAI vectors are not comparable, so the old rows must be
re-embedded.

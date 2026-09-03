.PHONY: up ingest eval test
up:        ; docker compose up --build
ingest:    ; docker compose exec backend python -m app.ingestion.run_ingest /corpus
eval:      ; docker compose exec backend python /app/evals/run_eval.py
test:      ; docker compose exec backend pytest -q

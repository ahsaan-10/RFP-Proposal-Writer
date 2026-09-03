# Local development without Docker.
#   .\scripts\dev.ps1            start the API on http://localhost:8000
#   .\scripts\dev.ps1 ingest     load .\corpus into the database in .env
#   .\scripts\dev.ps1 test       run the backend test suite
param([string]$Task = "api")

$root = Split-Path $PSScriptRoot -Parent
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    py -3.11 -m venv (Join-Path $root ".venv")
    & $py -m pip install -q -r (Join-Path $root "backend\requirements.txt")
}
Push-Location (Join-Path $root "backend")
switch ($Task) {
    "ingest" { & $py -m app.ingestion.run_ingest ..\corpus }
    "test"   { & $py -m pytest tests -q }
    default  { & $py -m uvicorn app.main:app --reload --port 8000 }
}
Pop-Location

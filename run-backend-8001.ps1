Set-Location "$PSScriptRoot\backend"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item .env.example .env }
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8001

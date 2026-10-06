Set-Location "$PSScriptRoot\backend"
if (-not (Test-Path ".venv")) { py -3.12 -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item .env.example .env }
alembic upgrade head
python -m uvicorn app.main:app --reload

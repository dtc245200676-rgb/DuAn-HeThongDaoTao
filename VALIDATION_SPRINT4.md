# Validation Report — Sprint 4 full integration

- Backend: `python -m pytest -q` — **36 passed** in 23.75s after the migration/configuration adjustments.
- `python -m compileall -q app alembic` — PASS.
- Frontend TypeScript/TSX syntax transpile check — **50 files, 0 syntax errors**.
- Full `npm run build` could not be confirmed in the packaging environment because npm dependency installation timed out; Vite and local TypeScript packages were unavailable afterward. Run `npm install` and `npm run build` on the target Windows machine before merging to GitHub.
- Full MySQL test SQL is provided at `database/SPRINT4_FULL_DATABASE_TEST.sql`; it creates a separate test DB, adds Sprint 4 tables, sample schedule/attendance/absence data, and sets Alembic version to `20261013_0004`.
- The migration's academic holiday index is declared only once, and Sprint 4 model indexes are represented in the migration.
- Important: import SQL only into a new/empty test database. Backend `.env.example` defaults to that isolated database.

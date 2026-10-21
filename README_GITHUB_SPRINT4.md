# BASE Sprint 4 — GitHub handoff

This folder is the shared BASE for Sprint 4. It contains the Sprint 1–3 project plus the shared Sprint 4 infrastructure, migration, models/schemas/helpers, and registered route/page placeholders.

## Recommended Git workflow

1. In the team's GitHub repository, fetch/pull the latest `develop`.
2. Create a branch named `sprint4-base` from `develop`.
3. Copy the **contents of this folder** into the root of the cloned repository (do not copy this enclosing folder as a nested project).
4. Review `Changes`; make sure no `.env` secrets or local machine files are included.
5. Run the backend tests from `backend`:
   ```powershell
   python -m pytest
   ```
6. Commit and push `sprint4-base`, then open a Pull Request with:
   - base: `develop`
   - compare: `sprint4-base`
7. Merge the BASE before any member branches are created.
8. After the BASE is merged, each member creates a branch from the latest `develop`, copies only their assigned package's `overlay/` contents into the repository root, tests, and opens a Pull Request back to `develop`.

## Important

- Do not push Sprint 4 work directly to `main`.
- Do not let feature branches independently change shared migration/model/schema/router-registration files unless the team agrees first.
- Run `alembic upgrade head` against a backed-up development database when updating the database.
- The package's validation notes report 27 backend tests passing for the BASE. Run the tests locally to confirm in your environment.
- Frontend build was not fully confirmed in the packaging environment. Run `npm install` (or `npm ci`) and `npm run build` inside `frontend` before approving integration.

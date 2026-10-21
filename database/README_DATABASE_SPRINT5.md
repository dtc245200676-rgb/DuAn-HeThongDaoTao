# Database Sprint 5

Import `SPRINT5_FULL_DATABASE_TEST.sql` into phpMyAdmin on a local MySQL 8 instance. It creates and uses `he_thong_dao_tao_sprint5_test`; it does not drop existing databases.

Import only once into a new test database. The SQL includes Sprint 1–4 schema/data and Sprint 5 tables for assignments, target classes, per-student deadline extensions and versioned submissions.

If using Alembic instead of the complete SQL, set `DATABASE_URL` in `backend/.env` and run `python -m alembic upgrade head` from `backend`.

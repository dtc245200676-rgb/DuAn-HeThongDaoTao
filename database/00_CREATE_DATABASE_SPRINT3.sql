-- Sprint 3 test database bootstrap.
-- Chỉ tạo database. Schema đầy đủ được tạo/cập nhật bằng Alembic.
CREATE DATABASE IF NOT EXISTS he_thong_dao_tao
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE he_thong_dao_tao;

-- Sau khi chạy file này:
-- cd backend
-- python -m alembic upgrade head
-- python -m scripts.create_admin --email admin@gmail.com --password Admin123 --name "Quản trị viên"

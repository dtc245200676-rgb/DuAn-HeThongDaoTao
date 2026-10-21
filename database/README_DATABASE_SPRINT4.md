# Database Sprint 4 — hướng dẫn test

## Dùng file SQL duy nhất
Import `SPRINT4_FULL_DATABASE_TEST.sql` vào phpMyAdmin/MySQL. File này tạo database `he_thong_dao_tao_sprint4_test`, chứa schema + dữ liệu demo Sprint 1–4, và đặt `alembic_version` ở `20261013_0004`.

**Chỉ import vào database test mới/trống.** Không import lại lần thứ hai vào cùng database vì các bảng đã tồn tại. Không xóa database dự án cũ `he_thong_dao_tao`.

Sau khi import, kiểm tra `backend/.env` có `DATABASE_URL=mysql+pymysql://root:@localhost:3306/he_thong_dao_tao_sprint4_test?charset=utf8mb4`. Nếu MySQL của bạn có mật khẩu, điền mật khẩu thực tế vào URL.

Tài khoản test: `admin@gmail.com / Admin123`, `manager@gmail.com / Manager123`, `admissions@gmail.com / Admissions123`, `teacher@gmail.com / Teacher123`, `student@gmail.com / Student123`.

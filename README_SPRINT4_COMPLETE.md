# Sprint 4 hoàn chỉnh — Hệ thống quản lý đào tạo CodeGym

Bản tích hợp đầy đủ Sprint 1–4, dựa trên BASE Sprint 4 và mã triển khai 9 phần việc Sprint 4.

## Nội dung Sprint 4

- **S4-01A:** Sinh thời khóa biểu tự động, preview và xác nhận lưu.
- **S4-01B:** Quản lý ngày nghỉ lễ để bộ sinh lịch bỏ qua.
- **S4-02:** Phát hiện xung đột phòng học/giảng viên và kiểm soát ghi đè.
- **S4-03:** Sửa, dời hoặc hủy buổi học; lưu lịch sử và thông báo.
- **S4-04:** Lịch tuần/tháng và bộ lọc.
- **S4-05:** Học viên xem lịch học cá nhân.
- **S4-06:** Bảo lưu, chuyển lớp, thôi học, kích hoạt lại và lịch sử.
- **S4-07:** Điểm danh 4 trạng thái, lịch sử thay đổi.
- **S4-08:** Đơn xin phép vắng, duyệt/từ chối và cập nhật điểm danh theo kết quả.

## Cấu trúc

- `backend/`: FastAPI, SQLAlchemy, Alembic, 36 backend tests.
- `frontend/`: React, TypeScript, Vite.
- `database/SPRINT4_FULL_DATABASE_TEST.sql`: schema và dữ liệu test cho Sprint 1–4.
- `run-backend-8001.ps1`, `run-frontend-5173.ps1`: scripts chạy trên Windows PowerShell.

## Cài đặt và chạy trên Windows

### 1. Import SQL

1. Bật MySQL trong XAMPP.
2. Mở `http://localhost/phpmyadmin`.
3. Vào **Import** và chọn `database/SPRINT4_FULL_DATABASE_TEST.sql`.
4. Chạy import. File tạo database riêng `he_thong_dao_tao_sprint4_test`; không đụng đến database `he_thong_dao_tao` cũ. Chỉ import vào database test mới/trống.

### 2. Backend

Từ thư mục gốc của dự án mở PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
# Nếu MySQL có mật khẩu, sửa DATABASE_URL trong backend/.env trước khi chạy
.\run-backend-8001.ps1
```

Backend dùng `http://127.0.0.1:8001`; docs tại `http://127.0.0.1:8001/docs`. Script cài requirements, chạy Alembic và khởi động Uvicorn. SQL đã đặt migration version là `20261013_0004`, nên Alembic sẽ không tạo trùng bảng.

### 3. Frontend

Mở terminal PowerShell thứ hai ở thư mục gốc:

```powershell
.\run-frontend-5173.ps1
```

Mở `http://localhost:5173/login`. `frontend/.env.example` dùng `VITE_API_BASE_URL=http://127.0.0.1:8001`.

## Tài khoản test

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Quản trị viên | `admin@gmail.com` | `Admin123` |
| Quản lý đào tạo | `manager@gmail.com` | `Manager123` |
| Tuyển sinh | `admissions@gmail.com` | `Admissions123` |
| Giảng viên | `teacher@gmail.com` | `Teacher123` |
| Học viên | `student@gmail.com` | `Student123` |

Các tài khoản chỉ dùng cho database test local; không dùng mật khẩu này ở môi trường thật.

## Kiểm tra trước khi đưa lên GitHub

Backend đã chạy `python -m pytest -q`: **36 passed**. Python compileall: PASS. Build frontend chưa thể xác nhận trong môi trường đóng gói do npm dependency không tải xong; sau khi `npm install` trên máy của bạn, hãy chạy `npm run build` trước khi merge.

```powershell
cd backend
python -m pytest -q
cd ../frontend
npm install
npm run build
```

Nếu Frontend build báo lỗi, hãy sửa trước khi tạo PR. Không commit file `.env`, mật khẩu MySQL hoặc token bí mật.

## Git workflow

1. Push/merge BASE Sprint 4 vào `develop`.
2. Tích hợp các thay đổi đã kiểm thử, không merge trực tiếp feature vào `main`.
3. Chạy test backend và build frontend.
4. Tạo PR `release/sprint4-complete` → `develop`.
5. Sau khi test tích hợp đạt, tạo PR `develop` → `main`.

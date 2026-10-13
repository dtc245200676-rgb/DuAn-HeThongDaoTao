# Hướng dẫn test Sprint 2 hoàn chỉnh

## 1. Nội dung bản này
Bản này đã ghép toàn bộ code của 9 thành viên Sprint 2 lên nền Sprint 1 hoàn chỉnh.

Các nhiệm vụ có trong bản ghép:
- S2-01 Import người dùng từ Excel
- S2-02 Chỉnh sửa hồ sơ cá nhân
- S2-03 Ảnh đại diện
- S2-04 Quản lý chương trình đào tạo
- S2-05 Quản lý môn học
- S2-06 Gắn môn / lộ trình / môn tiên quyết
- S2-07 Quản lý buổi học
- S2-08 Form đăng ký tư vấn
- S2-09 Quản lý Lead
- S2-10 Phân công Lead
- S2-11 Tìm kiếm / lọc Lead

## 2. Database MySQL để test
File nên import:

`database/sprint2_full_mysql.sql`

**Lưu ý:** file này có lệnh `DROP DATABASE IF EXISTS he_thong_dao_tao`, nên sẽ xóa database `he_thong_dao_tao` hiện tại rồi tạo lại sạch. Nếu database cũ còn dữ liệu cần giữ, hãy Export/backup trước.

### Import bằng phpMyAdmin
1. Backup database cũ nếu cần.
2. Chọn tab **Import** ở trang chính phpMyAdmin (không cần tạo database trước).
3. Chọn file `database/sprint2_full_mysql.sql`.
4. Bấm **Import / Go**.
5. Sau khi import thành công sẽ có database `he_thong_dao_tao` chứa cả Sprint 1 + Sprint 2.

### Tài khoản test có sẵn
- System Admin: `admin@gmail.com` / `Admin123`
- Training Manager: `manager@gmail.com` / `Manager123`
- Admissions: `admissions@gmail.com` / `Admissions123`

Database cũng có sẵn một chương trình `FS01`, 3 môn mẫu và 2 Lead để test nhanh.

## 3. Chạy backend ở cổng 8001
Mở PowerShell tại thư mục project:

```powershell
cd backend
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload --port 8001
```

Hoặc chạy script:

```powershell
.\run-backend-8001.ps1
```

Swagger:

`http://127.0.0.1:8001/docs`

Backend health:

`http://127.0.0.1:8001/health`

Nếu tài khoản MySQL `root` của bạn có password, sửa `backend/.env`, ví dụ:

```env
DATABASE_URL=mysql+pymysql://root:MAT_KHAU_MYSQL@localhost:3306/he_thong_dao_tao?charset=utf8mb4
```

## 4. Chạy frontend
Mở terminal khác:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run build
npm run dev
```

Hoặc:

```powershell
.\run-frontend-5173.ps1
```

Frontend:

`http://localhost:5173`

File `.env.example` đã trỏ frontend tới backend Sprint 2 ở cổng 8001:

```env
VITE_API_BASE_URL=http://127.0.0.1:8001
```

## 5. Kiểm tra nhanh từng nhóm chức năng

### Sprint 1 regression
- Đăng nhập / đăng xuất
- Forgot/Reset password
- Change password
- RBAC
- User CRUD
- Multi-role
- Lock/Unlock account

### S2-01 Import Excel
- Tải file mẫu
- Preview
- Validate từng dòng
- Import dòng hợp lệ

### S2-02 / S2-03 Profile
- Sửa họ tên/SĐT/ngày sinh/địa chỉ
- Upload JPG/PNG <= 2MB
- Crop/avatar thumbnail

### S2-04 đến S2-07 Training
- CRUD chương trình
- CRUD môn học
- Gắn môn vào chương trình
- Kéo thả thứ tự
- Môn tiên quyết
- Quản lý buổi học
- Clone buổi học

### S2-08 Consultation
Mở `/consultation` khi chưa đăng nhập và gửi form tư vấn.

### S2-09 đến S2-11 Lead
Dùng `manager@gmail.com` để test quản lý/phân công Lead và dùng `admissions@gmail.com` để test quyền chỉ xem Lead được giao.

## 6. Kết quả kiểm tra trước khi đóng gói
- Python compile: PASS.
- Backend: 18 tests PASS.
- 9 overlay thành viên đã được đối chiếu với bản ghép: 30/30 file nhiệm vụ khớp, không thiếu file.
- Frontend `npm run build` chưa xác nhận được trong môi trường đóng gói do quá trình tải npm dependency bị timeout. Trên máy Windows cần chạy `npm install` và `npm run build` trước khi chốt Sprint 2.

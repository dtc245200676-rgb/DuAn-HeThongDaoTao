# HƯỚNG DẪN TEST VÀ CHỐT SPRINT 3

## 1. Tạo nhánh tích hợp cuối
```powershell
git checkout develop
git pull origin develop
git status
git checkout -b release/sprint3-complete
```

## 2. Chuẩn bị MySQL/XAMPP
Bật MySQL trong XAMPP.

Tạo database bằng phpMyAdmin hoặc chạy:
```sql
CREATE DATABASE IF NOT EXISTS he_thong_dao_tao
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Trong `backend/.env` dùng ví dụ:
```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/he_thong_dao_tao?charset=utf8mb4
FRONTEND_URL=http://localhost:5173
```

## 3. Backend
```powershell
cd backend
python -m pip install -r requirements.txt
python -m alembic current
python -m alembic upgrade head
python -m alembic current
python -m pytest
```

Kết quả mong đợi của bộ code đóng gói: `27 passed`.

Tạo/cập nhật admin test:
```powershell
python -m scripts.create_admin --email admin@gmail.com --password Admin123 --name "Quản trị viên"
```

Chạy backend:
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Kiểm tra:
- http://127.0.0.1:8001/health
- http://127.0.0.1:8001/docs

## 4. Frontend
Mở PowerShell thứ hai:
```powershell
cd frontend
npm ci
npm run build
npm run dev
```

Nếu `npm ci` lỗi do môi trường local/package-lock, dùng:
```powershell
npm install
npm run build
npm run dev
```

Frontend: http://127.0.0.1:5173

## 5. Checklist Sprint 3
Test lần lượt:
1. Login admin.
2. Lead Funnel chuyển trạng thái lead.
3. Lead Care tạo interaction/reminder.
4. Chuyển lead Closed thành Student.
5. Tìm/xem/sửa Student Records.
6. Tạo lớp từ chương trình đào tạo.
7. Ghi danh học viên vào lớp.
8. Xem Class Overview.
9. Gán Teacher/Assistant vào môn của lớp.
10. Tạo/sửa phòng và gán phòng cho lớp.

## 6. Nếu có sửa lỗi cuối
Từ root project:
```powershell
git status
git add .
git commit -m "fix: finalize Sprint 3 integration"
git push -u origin release/sprint3-complete
```

Tạo PR:
- base: `develop`
- compare: `release/sprint3-complete`

Sau khi merge PR và test lại `develop`:
```powershell
git checkout develop
git pull origin develop
cd backend
python -m pytest
cd ../frontend
npm run build
```

## 7. Đưa Sprint 3 hoàn chỉnh lên main
Chỉ làm khi backend test và frontend build đều PASS.

Tạo Pull Request GitHub:
- base: `main`
- compare: `develop`
- title: `Release Sprint 3 - Admissions and Class Management`

Sau khi review, merge PR. Không push trực tiếp code feature vào `main`.

Sau đó đồng bộ local:
```powershell
git checkout main
git pull origin main
git tag sprint3-complete
git push origin sprint3-complete
```

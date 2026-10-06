# Đưa BASE Sprint 1 vào repo DuAn-HeThongDaoTao

## Trạng thái đã chuẩn bị
- Giữ nguyên lịch sử Git và remote của repo hiện tại.
- BASE Sprint 1 đã được chép vào `backend/`, `frontend/`, `database/`.
- Chưa tạo commit mới: trưởng nhóm sẽ tự commit bằng tài khoản Git của mình.
- Backend Python compile: PASS.
- Backend BASE test: PASS (`1 passed`).
- Frontend `npm ci` không hoàn thành trong môi trường đóng gói do cài dependency bị timeout; cần chạy lại trên máy của nhóm.

## Bước 1 — Mở terminal trong thư mục repo
```bash
git status
```
Bạn phải thấy nhiều file BASE đang ở trạng thái modified/untracked.

## Bước 2 — Kiểm tra backend trước khi commit
Windows PowerShell:
```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
cd ..
```
Kỳ vọng BASE: test pass.

## Bước 3 — Kiểm tra frontend
```powershell
cd frontend
npm ci
npm run build
npm run lint
cd ..
```
Chỉ commit khi build/lint không có lỗi nghiêm trọng.

## Bước 4 — Commit BASE lên main
```bash
git checkout main
git add .
git commit -m "chore: initialize Sprint 1 base project"
git push origin main
```

## Bước 5 — Tạo develop từ BASE vừa push
```bash
git checkout -b develop
git push -u origin develop
```

Từ đây không cho thành viên push chức năng trực tiếp vào `main` hoặc `develop`.

## Bước 6 — Thành viên bắt đầu từ develop
Ví dụ Người 2 làm S1-03:
```bash
git clone https://github.com/dtc245200676-rgb/DuAn-HeThongDaoTao.git
cd DuAn-HeThongDaoTao
git checkout develop
git pull origin develop
git checkout -b feature/S1-03-forgot-password
```
Sau đó giải nén gói nhiệm vụ của mình và copy toàn bộ nội dung trong `overlay/` vào đúng gốc repo.

```bash
git status
git add .
git commit -m "S1-03: implement forgot and reset password"
git push -u origin feature/S1-03-forgot-password
```
Tạo Pull Request: `feature/S1-03-forgot-password` → `develop`.

## Quy tắc trước khi merge bất kỳ PR nào
```bash
git checkout feature/<branch-cua-ban>
git fetch origin
git merge origin/develop
```
Sau đó:
1. Resolve conflict nếu có.
2. Chạy backend test.
3. Chạy frontend build/lint.
4. Push lại branch.
5. Chỉ merge PR khi code chạy ổn.

## 9 branch Sprint 1
1. `feature/S1-01-02-auth-core`
2. `feature/S1-03-forgot-password`
3. `feature/S1-04-change-password`
4. `feature/S1-05-rbac`
5. `feature/S1-06-role-navigation`
6. `feature/S1-07-access-denied`
7. `feature/S1-08-user-management`
8. `feature/S1-09-user-roles`
9. `feature/S1-10-account-lock`

## Cuối Sprint 1
Khi 9 PR đã vào `develop` và test tổng PASS:
- tạo PR `develop` → `main`;
- review;
- merge;
- tag nếu muốn, ví dụ `sprint1-complete`.

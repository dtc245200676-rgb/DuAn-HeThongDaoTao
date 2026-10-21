# Sprint 5 Complete With SQL — Premium UI Redesign

## Mục tiêu

Nâng cấp toàn bộ frontend React + Ant Design theo phong cách **Modern University Management Dashboard – Premium SaaS UI**, giữ nguyên backend FastAPI, MySQL, route, AuthContext và logic nghiệp vụ Sprint 1–5.

## Hạng mục đã chỉnh sửa

### Hệ thống giao diện chung
- Thêm `frontend/src/styles/design-system.css` với design tokens màu sắc, spacing, radius, shadow và responsive.
- Viết lại `frontend/src/App.css` để đồng bộ Card, Table, Form, Modal, Button, Tag, Tabs và trạng thái focus/hover.
- Cập nhật `frontend/src/index.css` với typography, scrollbar, selection và reset an toàn.
- Cập nhật Ant Design theme token trong `frontend/src/App.tsx`.

### Layout
- Viết lại `frontend/src/layouts/AppLayout.tsx`.
- Sidebar navy, menu nhóm theo nghiệp vụ, active state rõ ràng.
- Desktop có nút thu gọn sidebar.
- Mobile dùng Drawer.
- Header sticky, breadcrumb theo route, tên trang, avatar, tên và vai trò.
- Menu tài khoản gồm hồ sơ, đổi mật khẩu, đăng xuất.
- Không tạo route giả; toàn bộ menu trỏ tới route thật hiện có.
- Bỏ tên Sprint khỏi nhãn hiển thị để giao diện giống sản phẩm thật hơn, nhưng route và chức năng không đổi.

### Đăng nhập
- Thiết kế lại `LoginPage.tsx` thành layout 2 cột trên desktop.
- Cột giới thiệu sử dụng nội dung mô tả hệ thống, không dùng dữ liệu giả.
- Form đăng nhập giữ nguyên AuthContext và API hiện tại.
- Mobile tự chuyển về form 1 cột.

### Dashboard
- Nâng cấp `DashboardPage.tsx` bằng dữ liệu thật từ user hiện tại: số vai trò, số quyền và trạng thái đổi mật khẩu.
- Truy cập nhanh chỉ hiển thị route người dùng thực sự có quyền truy cập.
- Không thêm số liệu giả về học viên/lớp/lead.

### Hồ sơ cá nhân
- Nâng cấp `ProfilePage.tsx` thành layout profile chuyên nghiệp 2 cột.
- Giữ nguyên upload avatar và form profile.
- Đồng bộ fallback API avatar về port 8001.

### Component dùng chung mới
- `PageHeader.tsx`
- `StatCard.tsx`
- `EmptyState.tsx`
- `LoadingState.tsx`
- `FormSection.tsx`

### Các trang nghiệp vụ
- Toàn bộ Card/Table/Form/Modal/Button trong các trang Sprint 1–5 được áp dụng style chung mới.
- Các tiêu đề có tiền tố S2/S3/S4/S5 được đổi thành tên nghiệp vụ thân thiện; chức năng và API không thay đổi.

## Responsive
- Desktop >= 1200px: sidebar đầy đủ, layout rộng.
- Tablet 768–1199px: spacing thu gọn.
- Mobile < 768px: sidebar chuyển Drawer, form inline chuyển dọc, card/modal/table có overflow an toàn.

## Kiểm thử
- Backend regression test: `39 passed`.
- Python backend không bị chỉnh sửa.
- Frontend syntax check bằng TypeScript parser không phát hiện lỗi cú pháp trong các file UI thay đổi.
- Full `npm run build` trong môi trường đóng gói chưa thể hoàn tất vì quá trình cài npm dependency bị timeout và `node_modules` không được tải đủ. Cần chạy `npm install && npm run build` trên máy phát triển trước khi merge.

## Lệnh kiểm tra trên Windows

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Backend:

```powershell
cd backend
python -m pytest -q
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

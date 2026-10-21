# Patch cải tiến luồng Chăm sóc lead và Phễu tuyển sinh

## Nội dung
- `frontend/src/pages/LeadCarePage.tsx`: tổ chức lại màn chăm sóc lead; hiển thị lịch nhắc đang mở, cảnh báo quá hạn theo số khách hàng duy nhất, hoàn tất lịch nhắc tại bảng, xem lịch sử theo lead và không cho chọn lead đã nhập học.
- `frontend/src/pages/LeadFunnelPage.tsx`: thêm chuyển đổi giữa chế độ **Bảng (Kanban)** và **Danh sách (Table)**; dùng chung bộ lọc; cho phép chuyển trạng thái trong bảng; giữ thao tác kéo thẻ trên bảng và ghi lịch sử qua API hiện có.
- `frontend/src/styles/function-ui.css`: bổ sung style responsive cho bảng phễu và phần chăm sóc lead.
- `backend/app/api/routes/lead_care.py`: ẩn lịch nhắc còn mở của lead đã nhập học, chặn hoàn tất lịch nhắc của lead đã nhập học và kiểm tra nội dung tương tác chỉ có khoảng trắng.
- `backend/tests/test_s3_02_lead_care.py`: bổ sung test lịch nhắc bị ẩn sau khi lead chuyển sang trạng thái đã nhập học.

## Cách áp dụng an toàn
1. Sao lưu các file cùng đường dẫn hiện tại trước khi ghi đè.
2. Giải nén ZIP này vào **thư mục gốc dự án** đang có hai thư mục `frontend` và `backend`, cho phép ghi đè các file trùng tên.
3. Giữ nguyên `.env` của dự án đang chạy; patch không chứa `.env` và không thay đổi database schema.
4. Chạy backend test từ thư mục `backend`:
   ```powershell
   $env:PYTHONPATH = "."
   pytest -q tests/test_s3_01_lead_funnel.py tests/test_s3_02_lead_care.py
   ```
5. Chạy frontend từ thư mục `frontend`:
   ```powershell
   npm install
   npm run build
   npm run dev
   ```
   Chỉ cần `npm install` nếu thư mục `node_modules` của máy bạn thiếu dependencies.

## Kiểm thử trong website
- Vào **Tuyển sinh → Phễu tuyển sinh**: thử chuyển giữa Bảng/Danh sách, tìm kiếm, lọc theo trạng thái/nguồn/người phụ trách, chuyển trạng thái ở danh sách và kéo thẻ giữa các cột.
- Vào **Tuyển sinh → Chăm sóc lead**: chọn lead chưa nhập học, lưu tương tác có/không có lịch gọi lại, xác nhận lịch xuất hiện trong bảng, hoàn tất lịch nhắc và kiểm tra lịch sử.
- Khi lead đã nhập học, lịch nhắc chăm sóc chưa hoàn tất của lead đó sẽ không còn xuất hiện trong bảng lịch gọi lại.

## Phạm vi
Không thay đổi cấu trúc database, endpoint phễu tuyển sinh hiện có, phân quyền hoặc chức năng chuyển lead thành học viên. Backend tests đã chạy thành công trong môi trường kiểm thử: 3 passed. Hai file TSX đã được kiểm tra cú pháp; build frontend đầy đủ cần dependencies frontend được cài hoàn chỉnh trên máy dự án.

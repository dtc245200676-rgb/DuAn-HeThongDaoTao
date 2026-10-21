# Patch cải thiện luồng chăm sóc lead (Sprint 3 — S3-02)

## Phạm vi

Patch này chỉ thay đổi luồng **chăm sóc lead**. Không thay đổi API của các phân hệ khác, không thay đổi cấu trúc bảng SQL và không đưa file `.env`, `node_modules`, `dist` hoặc thông tin bí mật vào gói.

## Các file cần ghi đè

Giải nén ZIP vào **thư mục gốc dự án** để giữ nguyên đường dẫn:

- `backend/app/api/routes/lead_care.py`
- `backend/app/schemas/sprint3.py`
- `backend/tests/test_s3_02_lead_care.py`
- `frontend/src/pages/LeadCarePage.tsx`
- `frontend/src/pages/LeadCarePage.css`

## Thay đổi

1. Thêm API `GET /api/s3/care/leads` trả về danh sách lead còn trong quy trình chăm sóc, tìm kiếm theo tên/số điện thoại/email và giữ giới hạn dữ liệu theo nhân viên tuyển sinh được phân công.
2. Không đưa lead đã nhập học hoặc đã từ chối vào hàng đợi nhắc việc; vẫn giữ lịch sử tương tác để tra cứu.
3. Hàng đợi nhắc việc trả thêm thông tin lead, trạng thái và người phụ trách; có thể hoàn tất lịch nhắc trực tiếp từ hàng đợi.
4. Đếm lead quá hạn theo khách hàng duy nhất để tránh thông báo lặp khi một lead có nhiều lịch nhắc quá hạn.
5. Chuẩn hóa thời gian lưu theo UTC và trả timestamp có hậu tố `Z`, tránh lệch giờ trình bày trên trình duyệt.
6. Nội dung tương tác được trim và từ chối chuỗi chỉ chứa khoảng trắng.
7. Hoàn tất lịch nhắc nhiều lần là thao tác idempotent; không ghi đè thời điểm hoàn tất đầu tiên.
8. Làm lại trang Chăm sóc lead theo luồng: hàng đợi nhắc việc → ghi nhận tương tác → lịch sử chăm sóc.
9. Thêm kiểm thử cho lead đã kết thúc quy trình, tìm kiếm, nội dung rỗng, timestamp UTC và hoàn tất nhắc lặp.

## Database / SQL

Không cần chạy SQL migration vì patch dùng các cột hiện có trong `lead_interactions` và `leads`. Không import lại file `SPRINT5_FULL_DATABASE_TEST.sql` vào database đang sử dụng.

## Kiểm thử Backend đã chạy

Từ thư mục `backend`, chạy:

```powershell
python -m pytest -q tests/test_s3_02_lead_care.py
```

Kiểm thử hồi quy liên quan tuyển sinh:

```powershell
python -m pytest -q tests/test_s3_02_lead_care.py tests/test_s2_09_lead_crud.py tests/test_s2_10_11_assignment_search.py tests/test_s3_01_lead_funnel.py tests/test_s3_03_lead_convert.py
```

Kết quả tại môi trường kiểm tra: **7 passed**.

## Kiểm tra Frontend trên máy phát triển

ZIP Frontend được cung cấp không chứa đầy đủ các package thực thi cần thiết (`vite`, `react`, `typescript`), vì vậy không thể xác nhận build tại môi trường kiểm tra này. Trên máy của bạn, mở terminal tại `frontend` và chạy:

```powershell
npm install
npm run build
```

Nếu build thành công, chạy dự án như thường lệ và kiểm tra `/admissions/care` bằng tài khoản có quyền `leads.view` và `leads.edit`.

## Kịch bản test thủ công

1. Mở **Chăm sóc lead**; danh sách chọn lead không hiển thị lead đã nhập học hoặc từ chối.
2. Chọn một lead đang tư vấn, ghi tương tác với lịch nhắc trong quá khứ.
3. Kiểm tra lịch xuất hiện trong hàng đợi và được đánh dấu quá hạn.
4. Nếu cùng một lead có nhiều lịch quá hạn, cảnh báo chỉ đếm lead đó một lần.
5. Nhấn **Hoàn tất** trong hàng đợi; lịch biến mất khỏi hàng đợi đang mở và lịch sử vẫn còn.
6. Tạo một lịch nhắc trong tương lai; lịch xuất hiện ở trạng thái sắp đến hạn.
7. Đăng nhập bằng nhân viên tuyển sinh khác; chỉ thấy lead được phân công cho tài khoản đó.
8. Chuyển lead sang học viên hoặc từ chối; lịch nhắc cũ không còn xuất hiện trong hàng đợi, nhưng lịch sử tương tác vẫn tra cứu được.

# BASE Sprint 4 từ Sprint 3 hoàn chỉnh

BASE này chứa toàn bộ Sprint 1–3 và hạ tầng dùng chung Sprint 4:

- migration `20261013_0004_sprint4_timetable_attendance.py`
- model lịch học, ngày nghỉ, thông báo, lịch sử trạng thái học viên, điểm danh, đơn xin phép
- schema và helper dùng chung
- router/page placeholder để overlay 9 thành viên có thể merge độc lập
- menu và route frontend đã đăng ký sẵn

## Quy trình
1. Merge BASE vào `develop` trước.
2. 9 thành viên đều branch từ `develop` sau khi BASE đã merge.
3. Mỗi thành viên chỉ copy nội dung `overlay/` của gói mình.
4. Chạy `python -m pytest`, `npm run build`, rồi PR về `develop`.
5. Không sửa file shared nếu không thật sự cần.

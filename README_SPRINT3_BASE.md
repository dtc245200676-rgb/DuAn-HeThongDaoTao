# BASE Sprint 3 từ Sprint 2 hoàn chỉnh

BASE này chứa toàn bộ Sprint 1 + Sprint 2 hoàn chỉnh và **hạ tầng dùng chung của Sprint 3**.

## Hạ tầng đã có sẵn
- Migration `20261013_0003_sprint3_admissions_classes.py`.
- Model dùng chung: lịch sử trạng thái lead, nhật ký chăm sóc, hồ sơ học viên, môn học snapshot theo lớp, ghi danh, phân công giảng viên/trợ giảng, phòng học.
- `TrainingClass` được mở rộng cho mã lớp, ngày khai giảng, sĩ số tối đa, hình thức học, phòng và tiến độ.
- Role `teaching_assistant`.
- Router và page placeholder cho S3-01 → S3-09.
- Các route/menu Sprint 3 đã được đăng ký từ BASE để overlay của 9 người không phải sửa file chung.

## Quy tắc merge để tránh conflict
1. Merge BASE Sprint 3 vào `develop` trước.
2. Cả 9 thành viên tạo branch mới từ `develop` sau khi BASE đã merge.
3. Mỗi người chỉ copy thư mục `overlay/` trong gói của mình vào root repo.
4. Mỗi overlay chỉ thay file riêng của story + test riêng, không sửa `main.py`, `App.tsx`, model, schema hoặc migration.
5. Trước PR: merge `origin/develop`, chạy `python -m pytest` và `npm run build`.

Placeholder trong BASE chỉ giúp project import/build được, **không được tính là hoàn thành story**.

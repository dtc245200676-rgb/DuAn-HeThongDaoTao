# DuAn-HeThongDaoTao

Repo nhóm cho dự án **Hệ thống quản lý đào tạo**.

## Git workflow
- `main`: bản ổn định / BASE.
- `develop`: nhánh tích hợp Sprint.
- Thành viên làm trên `feature/...`, push branch riêng và tạo Pull Request vào `develop`.
- Không push trực tiếp code chức năng lên `main` hoặc `develop`.

## BASE Sprint 1
BASE chứa cấu trúc backend/frontend, database migration, model/schema dùng chung và các placeholder để 9 phần Sprint 1 có thể được ghép theo thứ tự bất kỳ mà không làm vỡ import.

Xem `README_SPLIT.md` để biết phân công và cách ghép 9 phần.

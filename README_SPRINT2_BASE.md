# BASE Sprint 2 từ Sprint 1 hoàn chỉnh

BASE này đã chứa toàn bộ Sprint 1 hoàn chỉnh và phần hạ tầng dùng chung của Sprint 2:
- Model + migration Sprint 2
- Permission dùng chung
- Router/page placeholder để bất kỳ overlay nào merge trước cũng không gây lỗi import/build
- Shared helper/type

Không tính các placeholder là hoàn thành story. Mỗi thành viên phải copy đúng `overlay/` của mình lên branch riêng.

## Luồng
1. Đẩy BASE này lên `develop` sau khi Sprint 1 đã ổn định trên `main`.
2. 9 người tạo branch từ `develop`.
3. Copy `overlay/` của gói được giao vào root repo.
4. Commit/push/PR. Ai push trước cũng được.
5. Trước merge: `git fetch origin` + `git merge origin/develop`, chạy test/build.
6. Test xanh mới merge.

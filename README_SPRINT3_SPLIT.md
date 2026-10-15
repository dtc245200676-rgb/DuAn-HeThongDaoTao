# Sprint 3 — Phiếu tư vấn, nhập học và mở lớp

Nguồn yêu cầu: 9 story / 42 point trong ảnh Sprint 3.

## Phân công 9 thành viên

| Người | Story | Nội dung | Branch gợi ý | File overlay |
|---|---|---|---|---|
| 1 | S3-01 | Bảng phễu lead 6 trạng thái, kéo thả, lịch sử, lý do từ chối | `feature/S3-01-lead-funnel` | `lead_funnel.py`, test S3-01, `LeadFunnelPage.tsx` |
| 2 | S3-02 | Nhật ký gọi/nhắn/gặp, lịch nhắc gọi lại, quá hạn | `feature/S3-02-lead-care-reminders` | `lead_care.py`, test S3-02, `LeadCarePage.tsx` |
| 3 | S3-03 | Chuyển lead Chốt → hồ sơ học viên + tài khoản + activation email | `feature/S3-03-lead-to-student` | `lead_convert.py`, test S3-03, `LeadConvertPage.tsx` |
| 4 | S3-04 | Hồ sơ học viên, tìm kiếm, lớp đang học/lịch sử | `feature/S3-04-student-records` | `student_records.py`, test S3-04, `StudentRecordsPage.tsx` |
| 5 | S3-05 | Mở lớp từ chương trình, vòng đời lớp, snapshot môn | `feature/S3-05-open-classes` | `classes_manage.py`, test S3-05, `ClassManagementPage.tsx` |
| 6 | S3-06 | Ghi danh đơn/hàng loạt, chặn full/trùng, audit | `feature/S3-06-class-enrollment` | `class_enrollments.py`, test S3-06, `ClassEnrollmentPage.tsx` |
| 7 | S3-07 | Danh sách lớp, lọc, sĩ số, tiến độ buổi | `feature/S3-07-class-overview` | `class_overview.py`, test S3-07, `ClassOverviewPage.tsx` |
| 8 | S3-08 | Giảng viên chính + nhiều trợ giảng theo từng môn | `feature/S3-08-class-staff` | `class_staff.py`, test S3-08, `ClassStaffPage.tsx` |
| 9 | S3-09 | Phòng vật lý/online, gán phòng, cảnh báo sức chứa | `feature/S3-09-rooms` | `rooms.py`, test S3-09, `RoomManagementPage.tsx` |

## Thứ tự làm Git

1. Merge `00_BASE_SPRINT3_FROM_SPRINT2` vào `develop` trước.
2. Sau khi BASE đã lên `develop`, 9 người clone/pull `develop` và tạo branch riêng.
3. Mỗi người chỉ copy **nội dung trong `overlay/`** của gói mình vào root repo.
4. Chạy backend test và frontend build rồi mới push/PR vào `develop`.
5. Các overlay không cùng sửa `main.py`, `App.tsx`, model, schema, migration; phần dùng chung đã đặt trong BASE nên giảm tối đa conflict.
6. Sau khi 9 PR merge, test toàn bộ `develop`, rồi mới PR `develop → main` để chốt Sprint 3.

## BASE Sprint 3 chứa gì

- Toàn bộ Sprint 1 + Sprint 2 hoàn chỉnh.
- Migration `20261013_0003_sprint3_admissions_classes.py`.
- Model chung Sprint 3.
- Schema request chung Sprint 3.
- Role `teaching_assistant`.
- Router/page placeholder + đăng ký route/menu dùng chung.
- Fix email login trim ký tự ẩn từ bản test Sprint 2.

## Lưu ý database

Sau khi BASE được merge, máy thành viên đang dùng DB Sprint 2 chạy:

```powershell
cd backend
alembic upgrade head
```

Nên backup MySQL trước khi nâng migration. Không để từng thành viên tự tạo bảng riêng bằng SQL thủ công.

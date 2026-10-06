# BASE Sprint 1 cho nhóm 9 người

Đây là code nền chung. BASE được thiết kế có các router/page placeholder để các gói nhiệm vụ có thể merge theo bất kỳ thứ tự nào mà project vẫn import/build được.

## Đưa BASE lên GitHub lần đầu
```bash
git init
git add .
git commit -m "chore: initialize Sprint 1 base"
git branch -M main
git remote add origin <URL_REPO>
git push -u origin main
git checkout -b develop
git push -u origin develop
```
Sau đó mỗi thành viên clone repo, checkout develop, tạo branch của mình và copy thư mục `overlay` trong gói được giao vào repo.

# Chạy bản Premium UI

## Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Swagger: `http://127.0.0.1:8001/docs`

## Frontend

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Website: `http://localhost:5173/login`

Frontend `.env` nên có:

```env
VITE_API_BASE_URL=http://127.0.0.1:8001
```

## Lưu ý
- Không đổi backend/database khi áp dụng giao diện mới.
- Không commit `frontend/node_modules`, `frontend/dist`, `backend/.env`, `frontend/.env` nếu có thông tin môi trường riêng.
- Nếu `npm run build` báo lỗi dependency, xóa `node_modules` rồi chạy lại `npm install`.

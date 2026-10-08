from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app import models as _models  # load all model metadata, including Sprint 2 tables
from app.api.routes import (
    auth_login_session_router, auth_password_reset_router, auth_change_password_router, auth_activation_router,
    roles_router, users_crud_router, user_roles_router, user_lock_router, import_users_router,
    profile_info_router, profile_avatar_router, training_programs_router, training_subjects_router,
    training_curriculum_router, training_sessions_router, consultation_router, leads_crud_router,
    leads_assignment_search_router,
)
from app.db.database import SessionLocal
from app.db.seed import seed_rbac

@asynccontextmanager
async def lifespan(_: FastAPI):
    db=SessionLocal()
    try:
        seed_rbac(db)
    except Exception as exc:
        print(f"[startup] Chưa thể seed RBAC: {exc}")
        db.rollback()
    finally:
        db.close()
    yield

app=FastAPI(title="He Thong Dao Tao CodeGym - Sprint 2",version="2.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in [
    auth_login_session_router,auth_password_reset_router,auth_change_password_router,auth_activation_router,
    roles_router,users_crud_router,user_roles_router,user_lock_router,import_users_router,
    profile_info_router,profile_avatar_router,training_programs_router,training_subjects_router,
    training_curriculum_router,training_sessions_router,consultation_router,leads_crud_router,
    leads_assignment_search_router,
]: app.include_router(router)
Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/")
def home(): return {"message":"Backend đang hoạt động","sprint":"Sprint 2"}
@app.get("/health")
def health(): return {"status":"ok"}

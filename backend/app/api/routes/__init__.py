from app.api.routes.auth_login_session import router as auth_login_session_router
from app.api.routes.auth_password_reset import router as auth_password_reset_router
from app.api.routes.auth_change_password import router as auth_change_password_router
from app.api.routes.auth_activation import router as auth_activation_router
from app.api.routes.roles import router as roles_router
from app.api.routes.users_crud import router as users_crud_router
from app.api.routes.user_roles import router as user_roles_router
from app.api.routes.user_lock import router as user_lock_router
from app.api.routes.import_users import router as import_users_router
from app.api.routes.profile_info import router as profile_info_router
from app.api.routes.profile_avatar import router as profile_avatar_router
from app.api.routes.training_programs import router as training_programs_router
from app.api.routes.training_subjects import router as training_subjects_router
from app.api.routes.training_curriculum import router as training_curriculum_router
from app.api.routes.training_sessions import router as training_sessions_router
from app.api.routes.consultation import router as consultation_router
from app.api.routes.leads_crud import router as leads_crud_router
from app.api.routes.leads_assignment_search import router as leads_assignment_search_router

__all__ = [
    "auth_login_session_router", "auth_password_reset_router", "auth_change_password_router", "auth_activation_router",
    "roles_router", "users_crud_router", "user_roles_router", "user_lock_router", "import_users_router",
    "profile_info_router", "profile_avatar_router", "training_programs_router", "training_subjects_router",
    "training_curriculum_router", "training_sessions_router", "consultation_router", "leads_crud_router",
    "leads_assignment_search_router",
]

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
from app.api.routes.lead_funnel import router as lead_funnel_router
from app.api.routes.lead_care import router as lead_care_router
from app.api.routes.lead_convert import router as lead_convert_router
from app.api.routes.student_records import router as student_records_router
from app.api.routes.classes_manage import router as classes_manage_router
from app.api.routes.class_enrollments import router as class_enrollments_router
from app.api.routes.class_overview import router as class_overview_router
from app.api.routes.class_staff import router as class_staff_router
from app.api.routes.rooms import router as rooms_router
from app.api.routes.sprint4_common import router as sprint4_common_router
from app.api.routes.timetable_generate import router as timetable_generate_router
from app.api.routes.academic_holidays import router as academic_holidays_router
from app.api.routes.schedule_conflicts import router as schedule_conflicts_router
from app.api.routes.schedule_changes import router as schedule_changes_router
from app.api.routes.schedule_calendar import router as schedule_calendar_router
from app.api.routes.student_schedule import router as student_schedule_router
from app.api.routes.student_status import router as student_status_router
from app.api.routes.attendance import router as attendance_router
from app.api.routes.absence_requests import router as absence_requests_router


__all__ = [
    "auth_login_session_router", "auth_password_reset_router", "auth_change_password_router", "auth_activation_router",
    "roles_router", "users_crud_router", "user_roles_router", "user_lock_router", "import_users_router",
    "profile_info_router", "profile_avatar_router", "training_programs_router", "training_subjects_router",
    "training_curriculum_router", "training_sessions_router", "consultation_router", "leads_crud_router",
    "leads_assignment_search_router", "lead_funnel_router", "lead_care_router", "lead_convert_router",
    "student_records_router", "classes_manage_router", "class_enrollments_router", "class_overview_router",
    "class_staff_router", "rooms_router",
    "sprint4_common_router", "timetable_generate_router", "academic_holidays_router", "schedule_conflicts_router",
    "schedule_changes_router", "schedule_calendar_router", "student_schedule_router", "student_status_router",
    "attendance_router", "absence_requests_router",
]

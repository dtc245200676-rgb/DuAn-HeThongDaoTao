from fastapi import APIRouter

from app.api.routes.sprint5_attendance_matrix import router as attendance_matrix_router
from app.api.routes.sprint5_attendance_warnings import router as attendance_warnings_router
from app.api.routes.sprint5_student_attendance import router as student_attendance_router
from app.api.routes.sprint5_attendance_export import router as attendance_export_router
from app.api.routes.sprint5_assignment_create import router as assignment_create_router
from app.api.routes.sprint5_assignment_list import router as assignment_list_router
from app.api.routes.sprint5_assignment_submission import router as assignment_submission_router
from app.api.routes.sprint5_submission_history import router as submission_history_router
from app.api.routes.sprint5_assignment_review import router as assignment_review_router

router = APIRouter()
for feature_router in (
    attendance_matrix_router, attendance_warnings_router, student_attendance_router, attendance_export_router,
    assignment_create_router, assignment_list_router, assignment_submission_router, submission_history_router,
    assignment_review_router,
):
    router.include_router(feature_router)

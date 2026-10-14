from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import serialize_class
from app.db.database import get_db
from app.models.sprint3 import ClassSubject, ClassSubjectStaff
from app.models.training import TrainingClass

router = APIRouter(prefix="/api/s3/class-overview", tags=["S3-07 Class Overview"])


@router.get("/classes")
def class_overview(
    status: str | None = None,
    program_id: int | None = None,
    teacher_user_id: int | None = None,
    start_from: date | None = None,
    start_to: date | None = None,
    context: AuthContext = Depends(require_permission("training.view")),
    db: Session = Depends(get_db),
):
    stmt = select(TrainingClass).options(selectinload(TrainingClass.program))
    if status:
        stmt = stmt.where(TrainingClass.status == status)
    if program_id:
        stmt = stmt.where(TrainingClass.program_id == program_id)
    if start_from:
        stmt = stmt.where(TrainingClass.expected_start_date >= start_from)
    if start_to:
        stmt = stmt.where(TrainingClass.expected_start_date <= start_to)

    staff_filter = teacher_user_id
    roles = set(context.role_slugs)
    if roles & {"teacher", "teaching_assistant"} and not roles & {"system_admin", "training_manager"}:
        staff_filter = context.user.id
    if staff_filter:
        class_ids = select(ClassSubject.class_id).join(
            ClassSubjectStaff, ClassSubjectStaff.class_subject_id == ClassSubject.id
        ).where(ClassSubjectStaff.user_id == staff_filter)
        stmt = stmt.where(TrainingClass.id.in_(class_ids))

    rows = db.scalars(stmt.order_by(TrainingClass.expected_start_date.desc(), TrainingClass.id.desc())).unique().all()
    items = [serialize_class(db, x) for x in rows]
    return {
        "items": items,
        "total": len(items),
        "quick": {
            "preparing": sum(x["status"] == "preparing" for x in items),
            "studying": sum(x["status"] == "studying" for x in items),
            "completed": sum(x["status"] == "completed" for x in items),
            "cancelled": sum(x["status"] == "cancelled" for x in items),
        },
    }

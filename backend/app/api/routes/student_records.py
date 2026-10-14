from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import serialize_student
from app.db.database import get_db
from app.models.sprint3 import StudentProfile
from app.models.user import User
from app.schemas.sprint3 import StudentUpdate

router = APIRouter(prefix="/api/s3/students", tags=["S3-04 Student Records"])


@router.get("")
def list_students(
    q: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: AuthContext = Depends(require_permission("training.view")),
    db: Session = Depends(get_db),
):
    stmt = select(StudentProfile).join(User, User.id == StudentProfile.user_id).options(selectinload(StudentProfile.user))
    count_stmt = select(func.count(StudentProfile.id)).join(User, User.id == StudentProfile.user_id)
    if q.strip():
        pattern = f"%{q.strip()}%"
        condition = or_(StudentProfile.student_code.like(pattern), User.full_name.like(pattern), User.phone.like(pattern))
        stmt = stmt.where(condition); count_stmt = count_stmt.where(condition)
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.order_by(StudentProfile.id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [serialize_student(db, x) for x in rows], "page": page, "page_size": page_size, "total": total}


@router.get("/{student_id}")
def student_detail(
    student_id: int,
    _: AuthContext = Depends(require_permission("training.view")),
    db: Session = Depends(get_db),
):
    student = db.scalar(select(StudentProfile).where(StudentProfile.id == student_id).options(selectinload(StudentProfile.user)))
    if not student:
        raise HTTPException(404, "Không tìm thấy hồ sơ học viên.")
    return serialize_student(db, student)


@router.put("/{student_id}")
def update_student(
    student_id: int,
    data: StudentUpdate,
    _: AuthContext = Depends(require_permission("training.edit")),
    db: Session = Depends(get_db),
):
    student = db.scalar(select(StudentProfile).where(StudentProfile.id == student_id).options(selectinload(StudentProfile.user)))
    if not student:
        raise HTTPException(404, "Không tìm thấy hồ sơ học viên.")
    payload = data.model_dump(exclude_unset=True)
    for key in ["full_name", "phone", "date_of_birth", "address"]:
        if key in payload:
            setattr(student.user, key, payload.pop(key))
    for key in ["entry_level", "notes"]:
        if key in payload:
            setattr(student, key, payload[key])
    db.commit(); db.refresh(student)
    return serialize_student(db, student)

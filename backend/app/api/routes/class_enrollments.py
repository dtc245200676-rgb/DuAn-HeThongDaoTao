from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import active_enrollment_count, serialize_class
from app.db.database import get_db
from app.models.sprint3 import ClassEnrollment, StudentProfile
from app.models.training import TrainingClass
from app.schemas.sprint3 import EnrollmentBulkCreate

router = APIRouter(prefix="/api/s3/enrollments", tags=["S3-06 Enrollments"])


@router.get("/classes")
def classes(_: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingClass).options(selectinload(TrainingClass.program)).order_by(TrainingClass.id.desc())).all()
    return [serialize_class(db, x) for x in rows]


@router.get("/classes/{class_id}/students")
def class_students(class_id: int, _: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    item = db.get(TrainingClass, class_id)
    if not item:
        raise HTTPException(404, "Không tìm thấy lớp.")
    enrolled_rows = db.scalars(
        select(ClassEnrollment)
        .where(ClassEnrollment.class_id == class_id, ClassEnrollment.status == "active")
        .options(selectinload(ClassEnrollment.student).selectinload(StudentProfile.user), selectinload(ClassEnrollment.enrolled_by))
        .order_by(ClassEnrollment.id)
    ).all()
    enrolled = [{
        "enrollment_id": row.id,
        "student_id": row.student_id,
        "student_code": row.student.student_code,
        "full_name": row.student.user.full_name,
        "email": row.student.user.email,
        "enrolled_at": row.enrolled_at,
        "enrolled_by": row.enrolled_by.full_name if row.enrolled_by else None,
    } for row in enrolled_rows]
    enrolled_ids = {x["student_id"] for x in enrolled}
    available_rows = db.scalars(
        select(StudentProfile).options(selectinload(StudentProfile.user)).order_by(StudentProfile.student_code)
    ).all()
    available = [{"id": x.id, "student_code": x.student_code, "full_name": x.user.full_name, "email": x.user.email}
                 for x in available_rows if x.id not in enrolled_ids]
    return {"enrolled": enrolled, "available": available, "current": len(enrolled), "max_students": item.max_students}


@router.post("/classes/{class_id}")
def enroll_students(
    class_id: int,
    data: EnrollmentBulkCreate,
    context: AuthContext = Depends(require_permission("training.edit")),
    db: Session = Depends(get_db),
):
    item = db.get(TrainingClass, class_id)
    if not item:
        raise HTTPException(404, "Không tìm thấy lớp.")
    if item.status in {"completed", "cancelled"}:
        raise HTTPException(409, "Không thể ghi danh vào lớp đã kết thúc hoặc đã hủy.")
    student_ids = list(dict.fromkeys(data.student_ids))
    students = db.scalars(select(StudentProfile).where(StudentProfile.id.in_(student_ids))).all()
    if len(students) != len(student_ids):
        raise HTTPException(404, "Có học viên không tồn tại.")
    existing = set(db.scalars(
        select(ClassEnrollment.student_id).where(
            ClassEnrollment.class_id == class_id,
            ClassEnrollment.student_id.in_(student_ids),
            ClassEnrollment.status == "active",
        )
    ).all())
    if existing:
        raise HTTPException(409, "Có học viên đã ở trong lớp.")
    current = active_enrollment_count(db, class_id)
    if current + len(student_ids) > item.max_students:
        raise HTTPException(409, f"Lớp chỉ còn {max(item.max_students-current,0)} chỗ trống.")
    rows = [ClassEnrollment(class_id=class_id, student_id=sid, status="active", enrolled_by_user_id=context.user.id) for sid in student_ids]
    db.add_all(rows); db.commit()
    return {"message": "Đã ghi danh học viên.", "count": len(rows), "current_students": current + len(rows), "max_students": item.max_students}


@router.delete("/classes/{class_id}/students/{student_id}")
def remove_student(class_id: int, student_id: int, _: AuthContext = Depends(require_permission("training.edit")), db: Session = Depends(get_db)):
    row = db.scalar(select(ClassEnrollment).where(ClassEnrollment.class_id == class_id, ClassEnrollment.student_id == student_id, ClassEnrollment.status == "active"))
    if not row:
        raise HTTPException(404, "Học viên chưa được ghi danh trong lớp.")
    row.status = "cancelled"; db.commit()
    return {"message": "Đã hủy ghi danh."}

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import role_slugs, serialize_class
from app.db.database import get_db
from app.models.role import Role
from app.models.sprint3 import ClassSubject, ClassSubjectStaff
from app.models.training import Subject, TrainingClass
from app.models.user import User
from app.schemas.sprint3 import ClassStaffAssign

router = APIRouter(prefix="/api/s3/class-staff", tags=["S3-08 Class Staff"])


@router.get("/classes")
def list_classes(_: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingClass).options(selectinload(TrainingClass.program)).order_by(TrainingClass.id.desc())).all()
    return [serialize_class(db, x) for x in rows]


@router.get("/eligible-users")
def eligible_users(
    role: str = Query(pattern="^(teacher|assistant)$"),
    _: AuthContext = Depends(require_permission("training.view")),
    db: Session = Depends(get_db),
):
    slug = "teacher" if role == "teacher" else "teaching_assistant"
    rows = db.scalars(
        select(User).join(User.roles).where(Role.slug == slug, User.is_active.is_(True), User.status == "active").options(selectinload(User.roles)).order_by(User.full_name)
    ).unique().all()
    return [{"id": x.id, "full_name": x.full_name, "email": x.email, "roles": [r.slug for r in x.roles]} for x in rows]


@router.get("/classes/{class_id}/subjects")
def class_subjects(class_id: int, _: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    if not db.get(TrainingClass, class_id):
        raise HTTPException(404, "Không tìm thấy lớp.")
    rows = db.execute(
        select(ClassSubject, Subject)
        .join(Subject, Subject.id == ClassSubject.subject_id)
        .where(ClassSubject.class_id == class_id)
        .order_by(ClassSubject.order_index)
    ).all()
    result = []
    for class_subject, subject in rows:
        staff = db.scalars(
            select(ClassSubjectStaff).where(ClassSubjectStaff.class_subject_id == class_subject.id).options(selectinload(ClassSubjectStaff.user))
        ).all()
        teacher = next((x for x in staff if x.staff_role == "teacher"), None)
        assistants = [x for x in staff if x.staff_role == "assistant"]
        result.append({
            "class_subject_id": class_subject.id,
            "subject_id": subject.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "teacher": {"id": teacher.user.id, "full_name": teacher.user.full_name} if teacher else None,
            "assistants": [{"id": x.user.id, "full_name": x.user.full_name} for x in assistants],
        })
    return result


@router.put("/class-subjects/{class_subject_id}/assign")
def assign_staff(
    class_subject_id: int,
    data: ClassStaffAssign,
    context: AuthContext = Depends(require_permission("training.edit")),
    db: Session = Depends(get_db),
):
    class_subject = db.get(ClassSubject, class_subject_id)
    if not class_subject:
        raise HTTPException(404, "Không tìm thấy môn trong lớp.")
    teacher = db.scalar(select(User).where(User.id == data.teacher_user_id).options(selectinload(User.roles)))
    if not teacher or "teacher" not in role_slugs(teacher):
        raise HTTPException(422, "Giảng viên chính phải có vai trò Giảng viên.")
    assistant_ids = list(dict.fromkeys(data.assistant_user_ids))
    if teacher.id in assistant_ids:
        raise HTTPException(422, "Giảng viên chính không thể đồng thời là trợ giảng của cùng môn.")
    assistants = []
    if assistant_ids:
        assistants = db.scalars(select(User).where(User.id.in_(assistant_ids)).options(selectinload(User.roles))).unique().all()
        if len(assistants) != len(assistant_ids):
            raise HTTPException(404, "Có tài khoản trợ giảng không tồn tại.")
        invalid = [x.full_name for x in assistants if "teaching_assistant" not in role_slugs(x)]
        if invalid:
            raise HTTPException(422, "Chỉ tài khoản có vai trò Trợ giảng mới được phân công trợ giảng.")

    db.execute(delete(ClassSubjectStaff).where(ClassSubjectStaff.class_subject_id == class_subject_id))
    db.add(ClassSubjectStaff(class_subject_id=class_subject_id, user_id=teacher.id, staff_role="teacher", assigned_by_user_id=context.user.id))
    for assistant in assistants:
        db.add(ClassSubjectStaff(class_subject_id=class_subject_id, user_id=assistant.id, staff_role="assistant", assigned_by_user_id=context.user.id))
    db.commit()
    return {"message": "Đã phân công giảng viên và trợ giảng.", "teacher_user_id": teacher.id, "assistant_user_ids": assistant_ids}


@router.get("/my-classes")
def my_classes(context: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    class_ids = select(ClassSubject.class_id).join(ClassSubjectStaff, ClassSubjectStaff.class_subject_id == ClassSubject.id).where(ClassSubjectStaff.user_id == context.user.id)
    rows = db.scalars(select(TrainingClass).where(TrainingClass.id.in_(class_ids)).options(selectinload(TrainingClass.program)).order_by(TrainingClass.id.desc())).unique().all()
    return [serialize_class(db, x) for x in rows]

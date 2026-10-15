from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import active_enrollment_count, serialize_class
from app.db.database import get_db
from app.models.sprint3 import ClassSubject
from app.models.training import ProgramSubject, Subject, TrainingClass, TrainingProgram
from app.schemas.sprint3 import TrainingClassCreate, TrainingClassUpdate

router = APIRouter(prefix="/api/s3/classes-manage", tags=["S3-05 Classes"])

TRANSITIONS = {
    "preparing": {"studying", "cancelled"},
    "studying": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


@router.get("/classes")
def list_classes(_: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingClass).options(selectinload(TrainingClass.program)).order_by(TrainingClass.id.desc())).all()
    return [serialize_class(db, x) for x in rows]


@router.post("/classes")
def create_class(
    data: TrainingClassCreate,
    context: AuthContext = Depends(require_permission("training.edit")),
    db: Session = Depends(get_db),
):
    code = data.code.strip().upper()
    if db.scalar(select(TrainingClass.id).where(TrainingClass.code == code)):
        raise HTTPException(409, "Mã lớp đã tồn tại.")
    program = db.get(TrainingProgram, data.program_id)
    if not program:
        raise HTTPException(404, "Không tìm thấy chương trình đào tạo.")
    item = TrainingClass(
        program_id=program.id,
        name=code,
        code=code,
        expected_start_date=data.expected_start_date,
        max_students=data.max_students,
        delivery_mode=data.delivery_mode,
        status="preparing",
        created_by_user_id=context.user.id,
    )
    db.add(item); db.flush()
    curriculum = db.scalars(
        select(ProgramSubject).where(ProgramSubject.program_id == program.id).order_by(ProgramSubject.order_index)
    ).all()
    for row in curriculum:
        db.add(ClassSubject(
            class_id=item.id,
            subject_id=row.subject_id,
            order_index=row.order_index,
            prerequisite_subject_id=row.prerequisite_subject_id,
        ))
    db.commit(); db.refresh(item)
    item = db.scalar(select(TrainingClass).where(TrainingClass.id == item.id).options(selectinload(TrainingClass.program)))
    result = serialize_class(db, item)
    result["copied_subject_count"] = len(curriculum)
    return result


@router.put("/classes/{class_id}")
def update_class(
    class_id: int,
    data: TrainingClassUpdate,
    _: AuthContext = Depends(require_permission("training.edit")),
    db: Session = Depends(get_db),
):
    item = db.scalar(select(TrainingClass).where(TrainingClass.id == class_id).options(selectinload(TrainingClass.program)))
    if not item:
        raise HTTPException(404, "Không tìm thấy lớp.")
    payload = data.model_dump(exclude_unset=True)
    if "status" in payload and payload["status"] != item.status:
        if payload["status"] not in TRANSITIONS.get(item.status, set()):
            raise HTTPException(409, f"Không thể chuyển trạng thái lớp từ {item.status} sang {payload['status']}.")
    if "max_students" in payload and payload["max_students"] < active_enrollment_count(db, item.id):
        raise HTTPException(409, "Sĩ số tối đa không thể nhỏ hơn số học viên đang ghi danh.")
    for key, value in payload.items():
        setattr(item, key, value)
    db.commit(); db.refresh(item)
    return serialize_class(db, item)


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
    return [{
        "id": cs.id,
        "subject_id": subject.id,
        "code": subject.code,
        "name": subject.name,
        "order_index": cs.order_index,
        "prerequisite_subject_id": cs.prerequisite_subject_id,
        "session_count": subject.session_count,
    } for cs, subject in rows]

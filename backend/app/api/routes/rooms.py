from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint3_common import active_enrollment_count, serialize_class
from app.db.database import get_db
from app.models.sprint3 import TrainingRoom
from app.models.training import TrainingClass
from app.schemas.sprint3 import AssignRoomRequest, RoomCreate, RoomUpdate

router = APIRouter(prefix="/api/s3/rooms", tags=["S3-09 Rooms"])


def room_dict(x: TrainingRoom):
    return {
        "id": x.id, "code": x.code, "name": x.name, "room_type": x.room_type,
        "capacity": x.capacity, "online_url": x.online_url, "is_active": x.is_active,
    }


@router.get("")
def list_rooms(_: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    return [room_dict(x) for x in db.scalars(select(TrainingRoom).order_by(TrainingRoom.code)).all()]


@router.post("")
def create_room(data: RoomCreate, _: AuthContext = Depends(require_permission("training.edit")), db: Session = Depends(get_db)):
    code = data.code.strip().upper()
    if db.scalar(select(TrainingRoom.id).where(TrainingRoom.code == code)):
        raise HTTPException(409, "Mã phòng đã tồn tại.")
    item = TrainingRoom(code=code, name=data.name.strip(), room_type=data.room_type, capacity=data.capacity if data.room_type == "physical" else None, online_url=data.online_url if data.room_type == "online" else None)
    db.add(item); db.commit(); db.refresh(item)
    return room_dict(item)


@router.put("/{room_id}")
def update_room(room_id: int, data: RoomUpdate, _: AuthContext = Depends(require_permission("training.edit")), db: Session = Depends(get_db)):
    item = db.get(TrainingRoom, room_id)
    if not item:
        raise HTTPException(404, "Không tìm thấy phòng.")
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items(): setattr(item, key, value)
    if item.room_type == "physical" and not item.capacity:
        raise HTTPException(422, "Phòng vật lý phải có sức chứa.")
    if item.room_type == "online" and not item.online_url:
        raise HTTPException(422, "Phòng trực tuyến phải có liên kết.")
    db.commit(); db.refresh(item)
    return room_dict(item)


@router.get("/classes")
def list_classes(_: AuthContext = Depends(require_permission("training.view")), db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingClass).options(selectinload(TrainingClass.program)).order_by(TrainingClass.id.desc())).all()
    return [serialize_class(db, x) for x in rows]


@router.put("/classes/{class_id}/assign")
def assign_room(
    class_id: int,
    data: AssignRoomRequest,
    _: AuthContext = Depends(require_permission("training.edit")),
    db: Session = Depends(get_db),
):
    training_class = db.scalar(select(TrainingClass).where(TrainingClass.id == class_id).options(selectinload(TrainingClass.program)))
    if not training_class:
        raise HTTPException(404, "Không tìm thấy lớp.")
    if data.room_id is None:
        training_class.room_id = None; db.commit()
        return {"message": "Đã bỏ gán phòng.", "warning": None, "class": serialize_class(db, training_class)}
    room = db.get(TrainingRoom, data.room_id)
    if not room or not room.is_active:
        raise HTTPException(404, "Không tìm thấy phòng đang hoạt động.")
    training_class.room_id = room.id
    db.commit(); db.refresh(training_class)
    current = active_enrollment_count(db, class_id)
    warning = None
    if room.room_type == "physical" and room.capacity is not None and current > room.capacity:
        warning = f"Cảnh báo: lớp đang có {current} học viên nhưng phòng {room.code} chỉ chứa {room.capacity} chỗ."
    return {"message": "Đã gán phòng cho lớp.", "warning": warning, "class": serialize_class(db, training_class)}

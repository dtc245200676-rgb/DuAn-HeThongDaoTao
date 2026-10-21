from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_permission
from app.api.routes.sprint4_common import primary_teacher_for_class_subject, serialize_schedule, session_conflicts
from app.db.database import get_db
from app.models.sprint3 import ClassSubject
from app.models.sprint4 import AcademicHoliday, ClassScheduleSession, ScheduleChangeHistory
from app.models.training import SubjectSession, TrainingClass
from app.schemas.sprint4 import TimetableGenerateRequest

router = APIRouter(prefix="/api/s4/timetable", tags=["S4-01 Timetable"])


def _lesson_queue(db: Session, class_id: int):
    rows = db.scalars(select(ClassSubject).where(ClassSubject.class_id == class_id).order_by(ClassSubject.order_index)).all()
    result=[]
    for cs in rows:
        lessons=db.scalars(select(SubjectSession).where(SubjectSession.subject_id==cs.subject_id).order_by(SubjectSession.sequence)).all()
        for lesson in lessons:
            result.append((cs,lesson))
    existing=set(db.scalars(select(ClassScheduleSession.subject_session_id).where(ClassScheduleSession.class_id==class_id)).all())
    return [(cs,lesson) for cs,lesson in result if lesson.id not in existing]


def _generate(db: Session, data: TimetableGenerateRequest):
    cl=db.get(TrainingClass,data.class_id)
    if not cl: raise HTTPException(404,"Không tìm thấy lớp.")
    lessons=_lesson_queue(db,cl.id)
    if not lessons: raise HTTPException(409,"Lớp không còn bài học nào chưa được xếp lịch hoặc chưa khai báo bài học cho môn.")
    holiday_dates=set(db.scalars(select(AcademicHoliday.holiday_date)).all())
    current=data.start_date
    result=[]
    guard=0
    for cs,lesson in lessons:
        while True:
            guard+=1
            if guard>4000: raise HTTPException(422,"Không thể tìm đủ ngày học với cấu hình hiện tại.")
            if current.weekday() in data.weekdays and current not in holiday_dates:
                start=datetime.combine(current,data.start_time)
                end=start+timedelta(minutes=data.duration_minutes)
                teacher_id=data.teacher_user_id or primary_teacher_for_class_subject(db,cs.id)
                room_id=data.room_id if data.room_id is not None else cl.room_id
                conflicts=session_conflicts(db,start,end,room_id,teacher_id)
                result.append({"class_subject":cs,"lesson":lesson,"start":start,"end":end,"teacher_id":teacher_id,"room_id":room_id,"conflicts":conflicts})
                current=current+timedelta(days=1)
                break
            current=current+timedelta(days=1)
    return cl,result


@router.get("/classes")
def classes(_:AuthContext=Depends(require_permission("training.view")),db:Session=Depends(get_db)):
    rows=db.scalars(select(TrainingClass).where(TrainingClass.status.in_(["preparing","studying"])).order_by(TrainingClass.code)).all()
    return [{"id":x.id,"code":x.code,"name":x.name} for x in rows]


@router.post("/preview")
def preview(data:TimetableGenerateRequest,_:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    cl,plans=_generate(db,data)
    return {"class_id":cl.id,"class_code":cl.code,"count":len(plans),"sessions":[{
        "class_subject_id":x["class_subject"].id,"subject_session_id":x["lesson"].id,
        "lesson_sequence":x["lesson"].sequence,"lesson_topic":x["lesson"].topic,
        "start_at":x["start"].isoformat(),"end_at":x["end"].isoformat(),"room_id":x["room_id"],
        "teacher_user_id":x["teacher_id"],"conflicts":x["conflicts"]} for x in plans]}


@router.post("/confirm")
def confirm(data:TimetableGenerateRequest,context:AuthContext=Depends(require_permission("training.edit")),db:Session=Depends(get_db)):
    cl,plans=_generate(db,data)
    conflicts=[c for x in plans for c in x["conflicts"]]
    if conflicts and not data.force_override:
        raise HTTPException(409,detail={"message":"Có xung đột giảng viên hoặc phòng. Hãy xử lý trước khi lưu.","conflicts":conflicts})
    if conflicts and data.force_override and not ({"system_admin","training_manager"}&set(context.role_slugs)):
        raise HTTPException(403,"Chỉ Quản lý đào tạo hoặc Quản trị hệ thống được xác nhận ghi đè xung đột.")
    saved=[]
    for x in plans:
        item=ClassScheduleSession(class_id=cl.id,class_subject_id=x["class_subject"].id,subject_session_id=x["lesson"].id,start_at=x["start"],end_at=x["end"],room_id=x["room_id"],teacher_user_id=x["teacher_id"],conflict_override=bool(x["conflicts"]),created_by_user_id=context.user.id)
        db.add(item);db.flush()
        db.add(ScheduleChangeHistory(schedule_session_id=item.id,action="override" if x["conflicts"] else "created",actor_user_id=context.user.id,reason="Xác nhận ghi đè xung đột" if x["conflicts"] else None))
        saved.append(item)
    db.commit()
    return {"message":"Đã lưu thời khóa biểu.","count":len(saved),"sessions":[serialize_schedule(db,x) for x in saved]}

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.lead_common import admissions_only
from app.api.routes.sprint3_common import ensure_lead_access
from app.core.security import utcnow
from app.db.database import get_db
from app.models.lead import Lead
from app.models.sprint3 import LeadInteraction
from app.schemas.sprint3 import LeadInteractionCreate

router = APIRouter(prefix="/api/s3/care", tags=["S3-02 Lead Care"])


def _serialize(row: LeadInteraction):
    now = utcnow()
    return {
        "id": row.id,
        "lead_id": row.lead_id,
        "interaction_type": row.interaction_type,
        "content": row.content,
        "occurred_at": row.occurred_at,
        "reminder_at": row.reminder_at,
        "reminder_completed_at": row.reminder_completed_at,
        "is_overdue": bool(row.reminder_at and not row.reminder_completed_at and row.reminder_at < now),
        "created_by": row.created_by.full_name if row.created_by else None,
        "created_at": row.created_at,
    }


@router.get("/leads/{lead_id}/interactions")
def list_interactions(
    lead_id: int,
    context: AuthContext = Depends(require_permission("leads.view")),
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead.")
    ensure_lead_access(lead, context)
    rows = db.scalars(
        select(LeadInteraction)
        .where(LeadInteraction.lead_id == lead_id)
        .options(selectinload(LeadInteraction.created_by))
        .order_by(LeadInteraction.occurred_at.desc(), LeadInteraction.id.desc())
    ).all()
    return [_serialize(x) for x in rows]


@router.post("/leads/{lead_id}/interactions")
def create_interaction(
    lead_id: int,
    data: LeadInteractionCreate,
    context: AuthContext = Depends(require_permission("leads.edit")),
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead.")
    ensure_lead_access(lead, context)
    if lead.status == "enrolled":
        raise HTTPException(409, "Lead đã nhập học nên không tiếp tục ghi nhật ký chăm sóc.")
    content = data.content.strip()
    if not content:
        raise HTTPException(422, "Nội dung chăm sóc không được để trống.")
    row = LeadInteraction(
        lead_id=lead_id,
        interaction_type=data.interaction_type,
        content=content,
        occurred_at=data.occurred_at or utcnow(),
        reminder_at=data.reminder_at,
        created_by_user_id=context.user.id,
    )
    db.add(row); db.commit(); db.refresh(row)
    row = db.scalar(select(LeadInteraction).where(LeadInteraction.id == row.id).options(selectinload(LeadInteraction.created_by)))
    return _serialize(row)


@router.get("/reminders")
def reminders(
    overdue_only: bool = Query(False),
    context: AuthContext = Depends(require_permission("leads.view")),
    db: Session = Depends(get_db),
):
    stmt = (
        select(LeadInteraction)
        .join(Lead, Lead.id == LeadInteraction.lead_id)
        .where(
            LeadInteraction.reminder_at.is_not(None),
            LeadInteraction.reminder_completed_at.is_(None),
            # Once a lead has enrolled, pending sales follow-ups are no longer actionable.
            Lead.status != "enrolled",
        )
        .options(selectinload(LeadInteraction.created_by), selectinload(LeadInteraction.lead))
    )
    if admissions_only(context):
        stmt = stmt.where(Lead.assignee_user_id == context.user.id)
    if overdue_only:
        stmt = stmt.where(LeadInteraction.reminder_at < utcnow())
    rows = db.scalars(stmt.order_by(LeadInteraction.reminder_at.asc())).all()
    return [dict(_serialize(x), lead_name=x.lead.full_name, lead_phone=x.lead.phone) for x in rows]


@router.patch("/interactions/{interaction_id}/complete-reminder")
def complete_reminder(
    interaction_id: int,
    context: AuthContext = Depends(require_permission("leads.edit")),
    db: Session = Depends(get_db),
):
    row = db.scalar(select(LeadInteraction).where(LeadInteraction.id == interaction_id).options(selectinload(LeadInteraction.lead)))
    if not row:
        raise HTTPException(404, "Không tìm thấy lịch nhắc.")
    ensure_lead_access(row.lead, context)
    if row.lead.status == "enrolled":
        raise HTTPException(409, "Lead đã nhập học; lịch chăm sóc không còn cần xử lý.")
    if not row.reminder_at:
        raise HTTPException(409, "Tương tác này không có lịch nhắc.")
    row.reminder_completed_at = utcnow()
    db.commit(); db.refresh(row)
    return {"message": "Đã hoàn tất lịch nhắc.", "id": row.id, "reminder_completed_at": row.reminder_completed_at}

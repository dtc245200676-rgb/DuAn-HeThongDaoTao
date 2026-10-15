from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, require_permission
from app.api.routes.lead_common import admissions_only, serialize_lead
from app.api.routes.sprint3_common import ensure_lead_access
from app.db.database import get_db
from app.models.lead import Lead
from app.models.sprint3 import LeadStatusHistory
from app.schemas.sprint3 import LEAD_FUNNEL_STATUSES, LeadStatusMove

router = APIRouter(prefix="/api/s3/funnel", tags=["S3-01 Lead Funnel"])

LABELS = {
    "new": "Mới",
    "contacted": "Đã liên hệ",
    "consulting": "Đang tư vấn",
    "trial": "Hẹn học thử",
    "closed": "Chốt",
    "rejected": "Từ chối",
}
LEGACY_ALIASES = {"qualified": "consulting"}


def _bucket(status: str) -> str:
    return LEGACY_ALIASES.get(status, status)


@router.get("")
def get_funnel(
    context: AuthContext = Depends(require_permission("leads.view")),
    db: Session = Depends(get_db),
):
    stmt = select(Lead).options(selectinload(Lead.interested_program), selectinload(Lead.assignee))
    if admissions_only(context):
        stmt = stmt.where(Lead.assignee_user_id == context.user.id)
    leads = db.scalars(stmt.order_by(Lead.updated_at.desc(), Lead.id.desc())).all()
    columns = []
    for status in LEAD_FUNNEL_STATUSES:
        items = [serialize_lead(lead) for lead in leads if _bucket(lead.status) == status]
        columns.append({"status": status, "label": LABELS[status], "count": len(items), "items": items})
    return {"columns": columns}


@router.patch("/leads/{lead_id}/status")
def move_lead(
    lead_id: int,
    data: LeadStatusMove,
    context: AuthContext = Depends(require_permission("leads.edit")),
    db: Session = Depends(get_db),
):
    lead = db.scalar(
        select(Lead)
        .where(Lead.id == lead_id)
        .options(selectinload(Lead.interested_program), selectinload(Lead.assignee))
    )
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead.")
    ensure_lead_access(lead, context)
    if lead.status == "enrolled":
        raise HTTPException(409, "Lead đã nhập học nên không được thay đổi trạng thái.")

    old_status = lead.status
    new_status = data.status
    if old_status == new_status:
        return serialize_lead(lead)

    reason = (data.rejection_reason or "").strip() or None
    lead.status = new_status
    db.add(
        LeadStatusHistory(
            lead_id=lead.id,
            from_status=old_status,
            to_status=new_status,
            reason=reason,
            actor_user_id=context.user.id,
        )
    )
    db.commit()
    db.refresh(lead)
    return serialize_lead(lead)


@router.get("/leads/{lead_id}/history")
def status_history(
    lead_id: int,
    context: AuthContext = Depends(require_permission("leads.view")),
    db: Session = Depends(get_db),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead.")
    ensure_lead_access(lead, context)
    rows = db.scalars(
        select(LeadStatusHistory)
        .where(LeadStatusHistory.lead_id == lead_id)
        .options(selectinload(LeadStatusHistory.actor))
        .order_by(LeadStatusHistory.id.desc())
    ).all()
    return [
        {
            "id": row.id,
            "from_status": row.from_status,
            "to_status": row.to_status,
            "reason": row.reason,
            "actor": row.actor.full_name if row.actor else None,
            "changed_at": row.changed_at,
        }
        for row in rows
    ]

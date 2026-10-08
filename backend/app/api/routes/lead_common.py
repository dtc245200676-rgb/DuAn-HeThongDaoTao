from fastapi import HTTPException
from sqlalchemy import select
from app.models.lead import Lead

def normalize_phone(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if value.strip().startswith("+84") and digits.startswith("84"):
        digits = "0" + digits[2:]
    if len(digits) != 10 or not digits.startswith(("03", "05", "07", "08", "09")):
        raise HTTPException(status_code=422, detail="Số điện thoại Việt Nam không hợp lệ.")
    return digits

def serialize_lead(lead: Lead):
    return {
        "id": lead.id, "full_name": lead.full_name, "phone": lead.phone, "email": lead.email,
        "source": lead.source, "interested_program_id": lead.interested_program_id,
        "interested_program": lead.interested_program.name if lead.interested_program else None,
        "status": lead.status, "assignee_user_id": lead.assignee_user_id,
        "assignee": lead.assignee.full_name if lead.assignee else None, "note": lead.note,
        "created_at": lead.created_at, "updated_at": lead.updated_at,
    }

def duplicate_warning(db, phone: str, exclude_id: int | None = None):
    stmt = select(Lead).where(Lead.phone == phone)
    if exclude_id:
        stmt = stmt.where(Lead.id != exclude_id)
    existing = db.scalar(stmt.order_by(Lead.id.desc()))
    if not existing:
        return None
    return {"lead_id": existing.id, "full_name": existing.full_name, "status": existing.status}

def admissions_only(context) -> bool:
    roles=set(context.role_slugs)
    return "admissions" in roles and not ({"training_manager", "system_admin"} & roles)

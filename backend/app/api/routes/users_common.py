from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User

def serialize_user(user: User) -> dict:
    return {
        "id": user.id, "full_name": user.full_name, "email": user.email, "phone": user.phone,
        "status": user.status, "is_active": user.is_active, "must_change_password": user.must_change_password,
        "needs_handover": user.needs_handover,
        "roles": [{"id": r.id, "slug": r.slug, "name": r.name} for r in user.roles],
        "created_at": user.created_at,
    }

def load_roles(db: Session, slugs: list[str]) -> list[Role]:
    if not slugs: return []
    roles = db.scalars(select(Role).where(Role.slug.in_(set(slugs)))).all()
    if len(roles) != len(set(slugs)):
        raise HTTPException(status_code=400, detail="Có vai trò không tồn tại.")
    return list(roles)

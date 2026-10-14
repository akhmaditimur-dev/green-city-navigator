from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from src.db.models import SessionLocal
from src.auth.models import User, Invitation, LoginHistory
from src.auth.security import generate_invitation_code
from src.auth.deps import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


# --- Схемы ---
class InvitationCreate(BaseModel):
    role: str = "student"
    days: int = 30
    note: Optional[str] = None


class RoleChange(BaseModel):
    role: str


VALID_ROLES = ["student", "teacher", "admin", "superadmin"]


# --- Пользователи ---
@router.get("/users")
def list_users(current: User = Depends(require_role("admin", "superadmin"))):
    session = SessionLocal()
    q = session.query(User).filter_by(is_hidden=False)
    users = q.order_by(User.created_at.desc()).all()
    result = [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
    session.close()
    return result


@router.post("/users/{user_id}/role")
def change_role(
    user_id: int,
    data: RoleChange,
    current: User = Depends(require_role("admin", "superadmin")),
):
    if data.role not in VALID_ROLES:
        raise HTTPException(400, f"Недопустимая роль. Доступны: {VALID_ROLES}")

    # admin не может назначать admin/superadmin
    if current.role == "admin" and data.role in ("admin", "superadmin"):
        raise HTTPException(403, "Админ не может назначать админов и супер-админов")

    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        raise HTTPException(404, "Пользователь не найден")

    if user.username == current.username:
        session.close()
        raise HTTPException(400, "Нельзя менять свою роль")

    user.role = data.role
    session.commit()
    session.close()
    return {"status": "ok", "user_id": user_id, "new_role": data.role}


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        raise HTTPException(404, "Пользователь не найден")
    if user.username == current.username:
        session.close()
        raise HTTPException(400, "Нельзя деактивировать себя")

    user.is_active = False
    session.commit()
    session.close()
    return {"status": "ok", "user_id": user_id, "is_active": False}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        raise HTTPException(404, "Пользователь не найден")

    user.is_active = True
    user.failed_attempts = 0
    user.locked_until = None
    session.commit()
    session.close()
    return {"status": "ok", "user_id": user_id, "is_active": True}


@router.post("/users/{user_id}/unlock")
def unlock_user(
    user_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        raise HTTPException(404, "Пользователь не найден")

    user.failed_attempts = 0
    user.locked_until = None
    session.commit()
    session.close()
    return {"status": "ok", "user_id": user_id}


# --- Приглашения ---
@router.get("/invitations")
def list_invitations(current: User = Depends(require_role("admin", "superadmin"))):
    session = SessionLocal()
    invs = session.query(Invitation).order_by(Invitation.created_at.desc()).all()
    result = []
    for inv in invs:
        created_by_user = session.query(User).filter_by(id=inv.created_by).first() if inv.created_by else None
        result.append({
            "id": inv.id,
            "code": inv.code,
            "role": inv.role,
            "created_by": created_by_user.username if created_by_user else None,
            "used_by": inv.used_by,
            "is_used": inv.used_at is not None,
            "is_expired": inv.expires_at < datetime.utcnow(),
            "expires_at": inv.expires_at.isoformat(),
            "created_at": inv.created_at.isoformat(),
            "link": f"/register?code={inv.code}",
        })
    session.close()
    return result


@router.post("/invitations")
def create_invitation(
    data: InvitationCreate,
    current: User = Depends(require_role("admin", "superadmin")),
):
    if data.role not in VALID_ROLES:
        raise HTTPException(400, f"Недопустимая роль. Доступны: {VALID_ROLES}")

    # admin не может приглашать admin/superadmin
    if current.role == "admin" and data.role in ("admin", "superadmin"):
        raise HTTPException(403, "Админ не может приглашать админов и супер-админов")

    session = SessionLocal()

    # Генерируем уникальный код
    for _ in range(10):
        code = generate_invitation_code()
        if not session.query(Invitation).filter_by(code=code).first():
            break
    else:
        session.close()
        raise HTTPException(500, "Не удалось сгенерировать код")

    inv = Invitation(
        code=code,
        role=data.role,
        created_by=current.id,
        expires_at=datetime.utcnow() + timedelta(days=data.days),
    )
    session.add(inv)
    session.commit()
    session.refresh(inv)

    result = {
        "id": inv.id,
        "code": inv.code,
        "role": inv.role,
        "expires_at": inv.expires_at.isoformat(),
        "link": f"/register?code={inv.code}",
    }
    session.close()
    return result


@router.delete("/invitations/{inv_id}")
def delete_invitation(
    inv_id: int,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    inv = session.query(Invitation).filter_by(id=inv_id).first()
    if not inv:
        session.close()
        raise HTTPException(404, "Приглашение не найдено")
    if inv.used_at:
        session.close()
        raise HTTPException(400, "Нельзя удалить использованное приглашение")

    session.delete(inv)
    session.commit()
    session.close()
    return {"status": "ok", "deleted_id": inv_id}


# --- История входов ---
@router.get("/login-history")
def login_history(
    limit: int = 100,
    current: User = Depends(require_role("admin", "superadmin")),
):
    session = SessionLocal()
    rows = (
        session.query(LoginHistory)
        .order_by(LoginHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    result = [
        {
            "id": r.id,
            "username": r.username,
            "ip_address": r.ip_address,
            "user_agent": r.user_agent,
            "success": r.success,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
    session.close()
    return result
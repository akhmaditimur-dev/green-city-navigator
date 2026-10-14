from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from src.db.models import SessionLocal
from src.auth.models import User, Invitation, LoginHistory
from src.auth.security import (
    hash_password, verify_password, validate_password,
    create_token, decode_token,
    MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES,
)
from src.auth.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Схемы ---
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    code: str
    username: str
    password: str
    full_name: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# --- Вход ---
@router.post("/login")
def login(data: LoginRequest, request: Request):
    session = SessionLocal()
    user = session.query(User).filter_by(username=data.username).first()

    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")[:500]

    if not user:
        session.add(LoginHistory(username=data.username, ip_address=ip, user_agent=ua, success=False))
        session.commit()
        session.close()
        raise HTTPException(401, "Неверный логин или пароль")

    # Проверка блокировки
    if user.locked_until and user.locked_until > datetime.utcnow():
        session.close()
        raise HTTPException(423, f"Аккаунт заблокирован до {user.locked_until.strftime('%H:%M')}")

    if not user.is_active:
        session.close()
        raise HTTPException(403, "Аккаунт деактивирован")

    if not verify_password(data.password, user.password_hash):
        user.failed_attempts = (user.failed_attempts or 0) + 1
        if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_attempts = 0
        session.add(LoginHistory(username=data.username, ip_address=ip, user_agent=ua, success=False))
        session.commit()
        session.close()
        raise HTTPException(401, "Неверный логин или пароль")

    # Успех
    user.failed_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    session.add(LoginHistory(username=data.username, ip_address=ip, user_agent=ua, success=True))
    session.commit()

    token = create_token(user.username, user.role)
    result = {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        },
    }
    session.close()
    return result


# --- Регистрация по приглашению ---
@router.post("/register")
def register(data: RegisterRequest):
    session = SessionLocal()

    # Проверка кода
    inv = session.query(Invitation).filter_by(code=data.code).first()
    if not inv:
        session.close()
        raise HTTPException(400, "Неверный код приглашения")

    if inv.used_at:
        session.close()
        raise HTTPException(400, "Код уже использован")

    if inv.expires_at < datetime.utcnow():
        session.close()
        raise HTTPException(400, "Код истёк")

    # Проверка username
    if session.query(User).filter_by(username=data.username).first():
        session.close()
        raise HTTPException(400, "Логин уже занят")

    # Проверка пароля
    ok, msg = validate_password(data.password)
    if not ok:
        session.close()
        raise HTTPException(400, msg)

    # Создание
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=inv.role,
        is_active=True,
    )
    session.add(user)
    session.flush()

    inv.used_by = user.id
    inv.used_at = datetime.utcnow()

    session.commit()
    token = create_token(user.username, user.role)
    result = {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        },
    }
    session.close()
    return result


# --- Текущий пользователь ---
@router.get("/me")
def me(current: User = Depends(get_current_user)):
    return {
        "id": current.id,
        "username": current.username,
        "full_name": current.full_name,
        "role": current.role,
        "email": current.email,
        "created_at": current.created_at.isoformat() if current.created_at else None,
        "last_login": current.last_login.isoformat() if current.last_login else None,
    }


# --- Смена пароля ---
@router.post("/change-password")
def change_password(data: ChangePasswordRequest, current: User = Depends(get_current_user)):
    session = SessionLocal()
    user = session.query(User).filter_by(id=current.id).first()

    if not verify_password(data.old_password, user.password_hash):
        session.close()
        raise HTTPException(400, "Неверный текущий пароль")

    ok, msg = validate_password(data.new_password)
    if not ok:
        session.close()
        raise HTTPException(400, msg)

    user.password_hash = hash_password(data.new_password)
    session.commit()
    session.close()
    return {"status": "ok", "message": "Пароль изменён"}
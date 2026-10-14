import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt


# --- Конфигурация ---
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "30"))

MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_MINUTES = int(os.getenv("LOCKOUT_MINUTES", "15"))


# --- Пароли ---
def hash_password(password: str) -> str:
    """Хэширует пароль через bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль против хэша."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    Проверяет сложность пароля.
    Возвращает (успех, сообщение).
    """
    if len(password) < 8:
        return False, "Пароль должен быть не менее 8 символов"
    if not any(c.isupper() for c in password):
        return False, "Пароль должен содержать заглавную букву"
    if not any(c.islower() for c in password):
        return False, "Пароль должен содержать строчную букву"
    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать цифру"
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Пароль должен содержать спецсимвол (!@#$%^&*)"
    return True, "OK"


# --- JWT ---
def create_token(username: str, role: str) -> str:
    """Создаёт JWT-токен."""
    expire = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {
        "sub": username,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Декодирует JWT. Возвращает payload или None."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# --- Коды приглашений ---
def generate_invitation_code(length: int = 8) -> str:
    """
    Генерирует код приглашения.
    Без похожих символов: 0/O, 1/l/I.
    """
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.db.models import SessionLocal
from src.auth.models import User
from src.auth.security import decode_token

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Неверный токен")

    username = payload.get("sub")
    if not username:
        raise HTTPException(401, "Неверный токен")

    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()

    if not user or not user.is_active:
        raise HTTPException(401, "Пользователь не найден")

    return user


def require_role(*roles: str):
    def checker(current: User = Depends(get_current_user)) -> User:
        if current.role not in roles:
            raise HTTPException(403, "Недостаточно прав")
        return current
    return checker
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from src.db.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    email = Column(String(200))
    role = Column(String(20), nullable=False, default="student")  # superadmin/admin/teacher/student
    is_active = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)  # для recovery
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False, default="student")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Invitation {self.code} ({self.role})>"


class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    success = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<LoginHistory {self.username} {'OK' if self.success else 'FAIL'}>"
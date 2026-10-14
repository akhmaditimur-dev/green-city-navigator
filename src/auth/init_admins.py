import os
from src.db.models import SessionLocal
from src.auth.models import User
from src.auth.security import hash_password


def init_superadmins():
    """Создаёт супер-админов из .env, если их нет."""
    session = SessionLocal()
    created = []

    # Основной супер-админ
    admin_username = os.getenv("SUPERADMIN_USERNAME", "admin")
    admin_password = os.getenv("SUPERADMIN_PASSWORD")
    admin_fullname = os.getenv("SUPERADMIN_FULLNAME", "Super Admin")

    if admin_password:
        existing = session.query(User).filter_by(username=admin_username).first()
        if not existing:
            user = User(
                username=admin_username,
                password_hash=hash_password(admin_password),
                full_name=admin_fullname,
                role="superadmin",
                is_active=True,
                is_hidden=False,
            )
            session.add(user)
            created.append(admin_username)

    # Резервный супер-админ
    rec_username = os.getenv("RECOVERY_USERNAME", "recovery")
    rec_password = os.getenv("RECOVERY_PASSWORD")
    rec_fullname = os.getenv("RECOVERY_FULLNAME", "Recovery Account")

    if rec_password:
        existing = session.query(User).filter_by(username=rec_username).first()
        if not existing:
            user = User(
                username=rec_username,
                password_hash=hash_password(rec_password),
                full_name=rec_fullname,
                role="superadmin",
                is_active=True,
                is_hidden=True,  # скрытый
            )
            session.add(user)
            created.append(rec_username)

    session.commit()
    session.close()

    if created:
        print(f"✓ Созданы супер-админы: {', '.join(created)}")
    else:
        print("✓ Супер-админы уже существуют")

    return created
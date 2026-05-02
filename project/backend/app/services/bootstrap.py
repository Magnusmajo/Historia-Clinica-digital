from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.security import ROLE_ADMIN, hash_password


def ensure_default_admin(db: Session):
    settings = get_settings()
    if not settings.seed_admin_user:
        return None

    email = settings.default_admin_email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    user = User(
        name=settings.default_admin_name.strip() or "Administrador",
        email=email,
        password_hash=hash_password(settings.default_admin_password),
        role=ROLE_ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

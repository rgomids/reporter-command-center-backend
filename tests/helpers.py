from __future__ import annotations

from sqlalchemy.orm import Session
from app.infra.db.models import UserModel
from app.infra.security.password import hash_password
from app.infra.security.auth_jwt import create_jwt


def seed_user(db: Session, tenant_id: str, user_id: str, email: str, role: str = "admin", password: str = "Pass12345!") -> str:
    db.add(
        UserModel(
            id=user_id,
            tenant_id=tenant_id,
            email=email,
            nome="Tester",
            role=role,
            password_hash=hash_password(password),
            external_id=None,
            personality_override=None,
        )
    )
    db.commit()
    return create_jwt(sub=user_id, tenant_id=tenant_id, role=role)


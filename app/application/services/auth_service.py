from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.errors import AuthorizationError
from app.infra.security.password import verify_password
from app.infra.security.auth_jwt import create_jwt, decode_jwt
from app.infra.repos import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.users = UserRepository(session)

    def login_with_password(self, tenant_id: str, username: str, password: str) -> str:
        row = self.users.get_by_email(tenant_id, username)
        if not row or not verify_password(password, row.password_hash):
            raise AuthorizationError("Invalid credentials")
        return create_jwt(sub=row.id, tenant_id=row.tenant_id, role=row.role)

    def validate_session(self, token: str) -> dict:
        return decode_jwt(token)

    def sso_exchange(self, provider: str, code: str, redirect_uri: str) -> str:
        # Stub: issue limited token
        return create_jwt(sub=f"sso:{provider}:{code}", tenant_id="unknown", role="member")


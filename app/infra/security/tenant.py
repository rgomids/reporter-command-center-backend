from __future__ import annotations

from fastapi import HTTPException
from starlette import status

from app.domain.errors import AuthorizationError


def extract_tenant_id(claims: dict) -> str:
    tenant_id = claims.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no tenant")
    return tenant_id


def enforce_tenant(record_tenant_id: str, token_tenant_id: str) -> None:
    if record_tenant_id != token_tenant_id:
        raise AuthorizationError("Cross-tenant access forbidden")


def has_role(claims: dict, role: str) -> bool:
    return claims.get("role") == role


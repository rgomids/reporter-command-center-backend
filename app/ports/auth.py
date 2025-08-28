from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class AuthPort(ABC):
    @abstractmethod
    def login_with_password(self, tenant_id: str, username: str, password: str) -> str:
        """Return JWT for user within tenant scope on success."""

    @abstractmethod
    def validate_session(self, token: str) -> dict:
        """Validate JWT and return claims."""

    @abstractmethod
    def sso_exchange(self, provider: str, code: str, redirect_uri: str) -> str:
        """Optional SSO exchange to JWT. Provider like 'microsoft' or 'google'."""


class TenantPort(ABC):
    @abstractmethod
    def get_current_tenant_id(self, claims: dict) -> str:
        """Extract tenant id from token claims."""

    @abstractmethod
    def enforce_tenant_scope(self, record_tenant_id: str, token_tenant_id: str) -> None:
        """Raise if token tenant doesn't match record tenant."""

    @abstractmethod
    def user_has_role(self, claims: dict, role: str) -> bool:
        """Return if user has role in tenant."""


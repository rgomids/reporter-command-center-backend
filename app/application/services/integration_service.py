from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.entities import IntegracaoTeams, IntegracaoIA, EventoAuditoria
from app.infra.repos import TeamsIntegrationRepository, AiIntegrationRepository, AuditRepository
from app.adapters.teams.mock import MockTeamsAdapter
from app.domain.errors import ValidationError
from datetime import datetime, timezone


class IntegrationService:
    def __init__(self, session: Session) -> None:
        self.teams_repo = TeamsIntegrationRepository(session)
        self.ai_repo = AiIntegrationRepository(session)
        self.audit = AuditRepository(session)
        self.teams = MockTeamsAdapter()

    def validate_teams(self, tenant_id: str, app_id: str, secret_or_cert: str) -> bool:
        if not app_id or not secret_or_cert:
            raise ValidationError("Credenciais inválidas")
        return self.teams.validate_credentials(tenant_id, app_id, secret_or_cert)

    def save_teams(self, tenant_id: str, app_id: str, secret_ref: str, actor_id: str) -> IntegracaoTeams:
        integ = IntegracaoTeams(tenant_id=tenant_id, app_id=app_id, secret_ref=secret_ref, status="valid")
        self.teams_repo.upsert(integ)
        self.audit.create(
            EventoAuditoria(
                tenant_id=tenant_id,
                id=f"audit:{datetime.now(timezone.utc).timestamp()}",
                actor_id=actor_id,
                tipo="teams_updated",
                detalhes={"app_id": app_id},
                criado_em=datetime.now(timezone.utc),
            )
        )
        return integ

    def save_ai(self, tenant_id: str, provider: str, api_key_ref: str, timeout_seconds: int, actor_id: str) -> IntegracaoIA:
        if timeout_seconds <= 0 or timeout_seconds > 120:
            raise ValidationError("Timeout inválido")
        integ = IntegracaoIA(
            tenant_id=tenant_id, provider=provider, api_key_ref=api_key_ref, timeout_seconds=timeout_seconds
        )
        self.ai_repo.upsert(integ)
        self.audit.create(
            EventoAuditoria(
                tenant_id=tenant_id,
                id=f"audit:{datetime.now(timezone.utc).timestamp()}",
                actor_id=actor_id,
                tipo="ai_updated",
                detalhes={"provider": provider},
                criado_em=datetime.now(timezone.utc),
            )
        )
        return integ


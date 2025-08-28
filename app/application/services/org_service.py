from __future__ import annotations

from datetime import time
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.domain.entities import Organizacao, EventoAuditoria
from app.infra.repos import OrganizationRepository, AuditRepository
from app.domain.errors import ValidationError
from datetime import datetime, timezone


class OrgService:
    def __init__(self, session: Session) -> None:
        self.orgs = OrganizationRepository(session)
        self.audit = AuditRepository(session)

    def get_config(self, tenant_id: str) -> Organizacao | None:
        return self.orgs.get(tenant_id)

    def set_config(
        self,
        tenant_id: str,
        nome: str,
        fuso: str,
        janela_inicio: str,
        janela_fim: str,
        frequencia_horas: int,
        flags_ia: Dict[str, Any],
        pre_prompt: str,
        actor_id: str,
    ) -> Organizacao:
        try:
            ti = time.fromisoformat(janela_inicio)
            tf = time.fromisoformat(janela_fim)
        except ValueError as e:
            raise ValidationError("Formato de hora inválido, use HH:MM:SS") from e
        if frequencia_horas <= 0 or frequencia_horas > 24:
            raise ValidationError("Frequência inválida")
        org = Organizacao(
            tenant_id=tenant_id,
            nome=nome,
            fuso=fuso,
            janela_inicio=ti,
            janela_fim=tf,
            frequencia_horas=frequencia_horas,
            flags_ia=flags_ia,
            pre_prompt=pre_prompt,
        )
        self.orgs.upsert(org)
        self.audit.create(
            EventoAuditoria(
                tenant_id=tenant_id,
                id=f"audit:{datetime.now(timezone.utc).timestamp()}",
                actor_id=actor_id,
                tipo="org_config_updated",
                detalhes={"nome": nome, "fuso": fuso},
                criado_em=datetime.now(timezone.utc),
            )
        )
        return org


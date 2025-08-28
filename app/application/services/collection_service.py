from __future__ import annotations

from datetime import datetime, timezone, timedelta, date
from typing import List

from sqlalchemy.orm import Session

from app.domain.entities import Coleta, Resposta
from app.infra.repos import CollectionRepository, ResponseRepository
from app.domain.errors import ValidationError


class CollectionService:
    def __init__(self, session: Session) -> None:
        self.collections = CollectionRepository(session)
        self.responses = ResponseRepository(session)

    def schedule_tick(self, tenant_id: str, user_id: str, when: datetime) -> Coleta:
        cid = f"c:{tenant_id}:{user_id}:{int(when.timestamp())}"
        c = Coleta(tenant_id=tenant_id, id=cid, usuario_id=user_id, agendada_para=when, status="pending")
        self.collections.create(c)
        return c

    def list_ticks(self, tenant_id: str, limit: int = 100) -> List[Coleta]:
        return self.collections.list_ticks(tenant_id, limit)

    def receive_response(self, tenant_id: str, coleta_id: str, user_id: str, text: str, dedupe_id: str | None) -> Resposta:
        if not text:
            raise ValidationError("Resposta vazia")
        r = Resposta(
            tenant_id=tenant_id,
            id=f"r:{tenant_id}:{int(datetime.now(timezone.utc).timestamp())}",
            coleta_id=coleta_id,
            usuario_id=user_id,
            recebida_em=datetime.now(timezone.utc),
            crua=text,
            tratada=None,
            dedupe_id=dedupe_id,
        )
        self.responses.create(r)
        self.collections.mark_responded(tenant_id, coleta_id)
        return r

    def mark_no_response_if_due(self, tenant_id: str, coleta_id: str, now: datetime | None = None) -> None:
        # Idempotent marking (update if pending and past due)
        self.collections.mark_no_response(tenant_id, coleta_id)

    def list_texts_by_day(self, tenant_id: str, user_id: str, day: date) -> List[str]:
        return self.responses.list_texts_by_day(tenant_id, user_id, day)


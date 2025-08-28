from __future__ import annotations

from typing import List, Optional
from datetime import datetime, date
import json

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.entities import (
    Organizacao,
    Time,
    Usuario,
    IntegracaoTeams,
    IntegracaoIA,
    Coleta,
    Resposta,
    SumarizacaoDiaria,
    EventoAuditoria,
)
from .db import models


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, org: Organizacao) -> None:
        existing = self.session.get(models.OrganizationModel, org.tenant_id)
        if existing:
            existing.nome = org.nome
            existing.fuso = org.fuso
            existing.janela_inicio = org.janela_inicio.isoformat()
            existing.janela_fim = org.janela_fim.isoformat()
            existing.frequencia_horas = org.frequencia_horas
            existing.flags_ia = json.dumps(org.flags_ia)
            existing.pre_prompt = org.pre_prompt
        else:
            self.session.add(
                models.OrganizationModel(
                    tenant_id=org.tenant_id,
                    nome=org.nome,
                    fuso=org.fuso,
                    janela_inicio=org.janela_inicio.isoformat(),
                    janela_fim=org.janela_fim.isoformat(),
                    frequencia_horas=org.frequencia_horas,
                    flags_ia=json.dumps(org.flags_ia),
                    pre_prompt=org.pre_prompt,
                )
            )

    def get(self, tenant_id: str) -> Optional[Organizacao]:
        row = self.session.get(models.OrganizationModel, tenant_id)
        if not row:
            return None
        from datetime import time as dtime

        return Organizacao(
            tenant_id=row.tenant_id,
            nome=row.nome,
            fuso=row.fuso,
            janela_inicio=dtime.fromisoformat(row.janela_inicio),
            janela_fim=dtime.fromisoformat(row.janela_fim),
            frequencia_horas=row.frequencia_horas,
            flags_ia=json.loads(row.flags_ia or "{}"),
            pre_prompt=row.pre_prompt or "",
        )


class TeamRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, team: Time) -> None:
        self.session.add(models.TeamModel(id=team.id, tenant_id=team.tenant_id, nome=team.nome))

    def list(self, tenant_id: str) -> List[Time]:
        rows = self.session.scalars(select(models.TeamModel).where(models.TeamModel.tenant_id == tenant_id)).all()
        return [Time(tenant_id=r.tenant_id, id=r.id, nome=r.nome) for r in rows]

    def get(self, tenant_id: str, team_id: str) -> Optional[Time]:
        row = self.session.get(models.TeamModel, team_id)
        if not row or row.tenant_id != tenant_id:
            return None
        return Time(tenant_id=row.tenant_id, id=row.id, nome=row.nome)

    def update(self, team: Time) -> None:
        row = self.session.get(models.TeamModel, team.id)
        if row and row.tenant_id == team.tenant_id:
            row.nome = team.nome

    def delete(self, tenant_id: str, team_id: str) -> None:
        row = self.session.get(models.TeamModel, team_id)
        if row and row.tenant_id == tenant_id:
            self.session.delete(row)


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: Usuario, password_hash: str) -> None:
        self.session.add(
            models.UserModel(
                id=user.id,
                tenant_id=user.tenant_id,
                email=user.email,
                nome=user.nome,
                role=user.role,
                password_hash=password_hash,
                external_id=user.external_id,
                personality_override=user.personality_override,
            )
        )

    def get_by_email(self, tenant_id: str, email: str) -> Optional[models.UserModel]:
        return self.session.scalar(
            select(models.UserModel).where(models.UserModel.tenant_id == tenant_id, models.UserModel.email == email)
        )

    def get(self, tenant_id: str, user_id: str) -> Optional[Usuario]:
        row = self.session.get(models.UserModel, user_id)
        if not row or row.tenant_id != tenant_id:
            return None
        return Usuario(
            tenant_id=row.tenant_id,
            id=row.id,
            email=row.email,
            nome=row.nome,
            role=row.role,
            external_id=row.external_id,
            personality_override=row.personality_override,
        )

    def update(self, user: Usuario) -> None:
        row = self.session.get(models.UserModel, user.id)
        if row and row.tenant_id == user.tenant_id:
            row.nome = user.nome
            row.role = user.role
            row.external_id = user.external_id
            row.personality_override = user.personality_override

    def delete(self, tenant_id: str, user_id: str) -> None:
        row = self.session.get(models.UserModel, user_id)
        if row and row.tenant_id == tenant_id:
            self.session.delete(row)


class TeamsIntegrationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, integ: IntegracaoTeams) -> None:
        existing = self.session.get(models.TeamsIntegrationModel, integ.tenant_id)
        if existing:
            existing.app_id = integ.app_id
            existing.secret_ref = integ.secret_ref
            existing.status = integ.status
        else:
            self.session.add(
                models.TeamsIntegrationModel(
                    tenant_id=integ.tenant_id,
                    app_id=integ.app_id,
                    secret_ref=integ.secret_ref,
                    status=integ.status,
                )
            )

    def get(self, tenant_id: str) -> Optional[IntegracaoTeams]:
        row = self.session.get(models.TeamsIntegrationModel, tenant_id)
        if not row:
            return None
        return IntegracaoTeams(tenant_id=row.tenant_id, app_id=row.app_id, secret_ref=row.secret_ref, status=row.status)


class AiIntegrationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, integ: IntegracaoIA) -> None:
        existing = self.session.get(models.AiIntegrationModel, integ.tenant_id)
        if existing:
            existing.provider = integ.provider
            existing.api_key_ref = integ.api_key_ref
            existing.timeout_seconds = integ.timeout_seconds
        else:
            self.session.add(
                models.AiIntegrationModel(
                    tenant_id=integ.tenant_id,
                    provider=integ.provider,
                    api_key_ref=integ.api_key_ref,
                    timeout_seconds=integ.timeout_seconds,
                )
            )

    def get(self, tenant_id: str) -> Optional[IntegracaoIA]:
        row = self.session.get(models.AiIntegrationModel, tenant_id)
        if not row:
            return None
        return IntegracaoIA(
            tenant_id=row.tenant_id, provider=row.provider, api_key_ref=row.api_key_ref, timeout_seconds=row.timeout_seconds
        )


class CollectionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, c: Coleta) -> None:
        self.session.add(
            models.CollectionModel(
                id=c.id,
                tenant_id=c.tenant_id,
                usuario_id=c.usuario_id,
                agendada_para=c.agendada_para,
                status=c.status,
            )
        )

    def mark_no_response(self, tenant_id: str, id_: str) -> None:
        row = self.session.get(models.CollectionModel, id_)
        if row and row.tenant_id == tenant_id:
            row.status = "no_response"

    def mark_responded(self, tenant_id: str, id_: str) -> None:
        row = self.session.get(models.CollectionModel, id_)
        if row and row.tenant_id == tenant_id:
            row.status = "responded"

    def list_ticks(self, tenant_id: str, limit: int = 100) -> List[Coleta]:
        rows = self.session.scalars(
            select(models.CollectionModel)
            .where(models.CollectionModel.tenant_id == tenant_id)
            .order_by(models.CollectionModel.agendada_para.desc())
            .limit(limit)
        ).all()
        return [
            Coleta(
                tenant_id=r.tenant_id,
                id=r.id,
                usuario_id=r.usuario_id,
                agendada_para=r.agendada_para,
                status=r.status,
            )
            for r in rows
        ]


class ResponseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, r: Resposta) -> None:
        self.session.add(
            models.ResponseModel(
                id=r.id,
                tenant_id=r.tenant_id,
                coleta_id=r.coleta_id,
                usuario_id=r.usuario_id,
                recebida_em=r.recebida_em,
                crua=r.crua,
                tratada=r.tratada,
                dedupe_id=r.dedupe_id,
            )
        )

    def count_by_user_in_date(self, tenant_id: str, user_id: str, day: date) -> int:
        return self.session.scalar(
            select(func.count(models.ResponseModel.id)).where(
                models.ResponseModel.tenant_id == tenant_id,
                models.ResponseModel.usuario_id == user_id,
                func.date(models.ResponseModel.recebida_em) == day,
            )
        ) or 0

    def list_texts_by_day(self, tenant_id: str, user_id: str, day: date) -> List[str]:
        rows = self.session.scalars(
            select(models.ResponseModel.tratada)
            .where(
                models.ResponseModel.tenant_id == tenant_id,
                models.ResponseModel.usuario_id == user_id,
                func.date(models.ResponseModel.recebida_em) == day,
            )
            .order_by(models.ResponseModel.recebida_em.asc())
        ).all()
        return [r or "" for r in rows]


class DailySummaryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, s: SumarizacaoDiaria) -> None:
        existing = self.session.get(models.DailySummaryModel, s.id)
        if existing:
            existing.resumo = s.resumo
        else:
            self.session.add(
                models.DailySummaryModel(
                    id=s.id,
                    tenant_id=s.tenant_id,
                    data=s.data,
                    usuario_id=s.usuario_id,
                    resumo=s.resumo,
                )
            )


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, e: EventoAuditoria) -> None:
        self.session.add(
            models.AuditEventModel(
                id=e.id,
                tenant_id=e.tenant_id,
                actor_id=e.actor_id,
                tipo=e.tipo,
                detalhes=json.dumps(e.detalhes),
                criado_em=e.criado_em,
            )
        )

    def list(self, tenant_id: str, limit: int = 100) -> list[EventoAuditoria]:
        rows = self.session.scalars(
            select(models.AuditEventModel)
            .where(models.AuditEventModel.tenant_id == tenant_id)
            .order_by(models.AuditEventModel.criado_em.desc())
            .limit(limit)
        ).all()
        return [
            EventoAuditoria(
                tenant_id=r.tenant_id,
                id=r.id,
                actor_id=r.actor_id,
                tipo=r.tipo,
                detalhes=json.loads(r.detalhes or "{}"),
                criado_em=r.criado_em,
            )
            for r in rows
        ]


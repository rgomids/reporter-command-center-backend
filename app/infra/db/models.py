from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Text, Integer, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class OrganizationModel(Base):
    __tablename__ = "organizations"
    tenant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    fuso: Mapped[str] = mapped_column(String(64))
    janela_inicio: Mapped[str] = mapped_column(String(8))
    janela_fim: Mapped[str] = mapped_column(String(8))
    frequencia_horas: Mapped[int] = mapped_column(Integer)
    flags_ia: Mapped[str] = mapped_column(Text, default="{}")
    pre_prompt: Mapped[str] = mapped_column(Text, default="")


class TeamModel(Base):
    __tablename__ = "teams"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    nome: Mapped[str] = mapped_column(String(200))
    __table_args__ = (Index("ix_team_tenant", "tenant_id"),)


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    email: Mapped[str] = mapped_column(String(200))
    nome: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(200))
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    personality_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
        Index("ix_user_tenant", "tenant_id"),
    )


class TeamsIntegrationModel(Base):
    __tablename__ = "teams_integrations"
    tenant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    app_id: Mapped[str] = mapped_column(String(200))
    secret_ref: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))


class AiIntegrationModel(Base):
    __tablename__ = "ai_integrations"
    tenant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    provider: Mapped[str] = mapped_column(String(50))
    api_key_ref: Mapped[str] = mapped_column(String(200))
    timeout_seconds: Mapped[int] = mapped_column(Integer)


class CollectionModel(Base):
    __tablename__ = "collections"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    usuario_id: Mapped[str] = mapped_column(String(64), index=True)
    agendada_para: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20))
    __table_args__ = (
        UniqueConstraint("tenant_id", "usuario_id", "agendada_para", name="uq_coleta_tenant_user_datetime"),
        Index("ix_collection_tenant", "tenant_id"),
    )


class ResponseModel(Base):
    __tablename__ = "responses"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    coleta_id: Mapped[str] = mapped_column(String(64))
    usuario_id: Mapped[str] = mapped_column(String(64))
    recebida_em: Mapped[datetime] = mapped_column(DateTime)
    crua: Mapped[str] = mapped_column(Text)
    tratada: Mapped[str | None] = mapped_column(Text, nullable=True)
    dedupe_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    __table_args__ = (
        UniqueConstraint("tenant_id", "dedupe_id", name="uq_response_dedupe"),
        Index("ix_response_tenant", "tenant_id"),
    )


class DailySummaryModel(Base):
    __tablename__ = "daily_summaries"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    data: Mapped[date] = mapped_column(Date)
    usuario_id: Mapped[str] = mapped_column(String(64))
    resumo: Mapped[str] = mapped_column(Text)
    __table_args__ = (
        UniqueConstraint("tenant_id", "data", "usuario_id", name="uq_summary_tenant_date_user"),
        Index("ix_summary_tenant", "tenant_id"),
    )


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    actor_id: Mapped[str] = mapped_column(String(64))
    tipo: Mapped[str] = mapped_column(String(50))
    detalhes: Mapped[str] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime)
    __table_args__ = (Index("ix_audit_tenant", "tenant_id"),)


from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, Dict, Any, List


@dataclass(slots=True)
class Organizacao:
    tenant_id: str
    nome: str
    fuso: str
    janela_inicio: time
    janela_fim: time
    frequencia_horas: int
    flags_ia: Dict[str, Any] = field(default_factory=dict)
    pre_prompt: str = ""


@dataclass(slots=True)
class Time:
    tenant_id: str
    id: str
    nome: str


@dataclass(slots=True)
class Usuario:
    tenant_id: str
    id: str
    email: str
    nome: str
    role: str  # 'admin' or 'member'
    external_id: Optional[str] = None  # teams id
    personality_override: Optional[str] = None


@dataclass(slots=True)
class PoliticasIA:
    tenant_id: str
    provider: str
    timeout_seconds: int
    max_cost_per_day_cents: int


@dataclass(slots=True)
class IntegracaoTeams:
    tenant_id: str
    app_id: str
    secret_ref: str
    status: str  # 'valid' | 'invalid' | 'pending'


@dataclass(slots=True)
class IntegracaoIA:
    tenant_id: str
    provider: str
    api_key_ref: str
    timeout_seconds: int


@dataclass(slots=True)
class Coleta:
    tenant_id: str
    id: str
    usuario_id: str
    agendada_para: datetime
    status: str  # 'pending' | 'responded' | 'no_response'


@dataclass(slots=True)
class Resposta:
    tenant_id: str
    id: str
    coleta_id: str
    usuario_id: str
    recebida_em: datetime
    crua: str
    tratada: Optional[str] = None
    dedupe_id: Optional[str] = None


@dataclass(slots=True)
class SumarizacaoDiaria:
    tenant_id: str
    id: str
    data: date
    usuario_id: str
    resumo: str


@dataclass(slots=True)
class EventoAuditoria:
    tenant_id: str
    id: str
    actor_id: str
    tipo: str
    detalhes: Dict[str, Any]
    criado_em: datetime


from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class LoginRequest(BaseModel):
    tenant_id: str
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class OrgConfig(BaseModel):
    nome: str
    fuso: str
    janela_inicio: str
    janela_fim: str
    frequencia_horas: int
    flags_ia: Dict[str, Any] = Field(default_factory=dict)
    pre_prompt: str = ""


class TeamsValidateRequest(BaseModel):
    app_id: str
    secret: str


class TeamsSaveRequest(BaseModel):
    app_id: str
    secret_ref: str


class AiSaveRequest(BaseModel):
    provider: str
    api_key_ref: str
    timeout_seconds: int


class TeamDTO(BaseModel):
    id: str
    nome: str


class UserDTO(BaseModel):
    id: str
    email: str
    nome: str
    role: str
    external_id: Optional[str] = None
    personality_override: Optional[str] = None
    password: Optional[str] = None


class ImportPreviewRequest(BaseModel):
    rows: List[List[str]]  # [[email, nome, role]]


class WebhookRequest(BaseModel):
    external_user_id: str
    text: str
    timestamp: str
    event_id: str
    coleta_id: str
    usuario_id: str


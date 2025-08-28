from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from .schemas import OrgConfig
from app.application.services.org_service import OrgService
from app.infra.security.tenant import extract_tenant_id, has_role


router = APIRouter(prefix="/org", tags=["org"])


@router.get("/config", response_model=OrgConfig)
def get_config(db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    org = OrgService(db).get_config(tenant_id)
    if not org:
        raise HTTPException(status_code=404, detail="Org not configured")
    return OrgConfig(
        nome=org.nome,
        fuso=org.fuso,
        janela_inicio=org.janela_inicio.isoformat(),
        janela_fim=org.janela_fim.isoformat(),
        frequencia_horas=org.frequencia_horas,
        flags_ia=org.flags_ia,
        pre_prompt=org.pre_prompt,
    )


@router.put("/config", response_model=OrgConfig)
def set_config(dto: OrgConfig, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    if not has_role(claims, "admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    tenant_id = extract_tenant_id(claims)
    org = OrgService(db).set_config(
        tenant_id,
        dto.nome,
        dto.fuso,
        dto.janela_inicio,
        dto.janela_fim,
        dto.frequencia_horas,
        dto.flags_ia,
        dto.pre_prompt,
        claims.get("sub", "unknown"),
    )
    return OrgConfig(
        nome=org.nome,
        fuso=org.fuso,
        janela_inicio=org.janela_inicio.isoformat(),
        janela_fim=org.janela_fim.isoformat(),
        frequencia_horas=org.frequencia_horas,
        flags_ia=org.flags_ia,
        pre_prompt=org.pre_prompt,
    )


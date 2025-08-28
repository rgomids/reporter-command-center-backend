from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from .schemas import TeamsValidateRequest, TeamsSaveRequest, AiSaveRequest
from app.application.services.integration_service import IntegrationService
from app.infra.security.tenant import extract_tenant_id, has_role


router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/teams/validate")
def teams_validate(dto: TeamsValidateRequest, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    if not has_role(claims, "admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    tenant_id = extract_tenant_id(claims)
    ok = IntegrationService(db).validate_teams(tenant_id, dto.app_id, dto.secret)
    return {"valid": ok}


@router.put("/teams")
def teams_save(dto: TeamsSaveRequest, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    if not has_role(claims, "admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    tenant_id = extract_tenant_id(claims)
    integ = IntegrationService(db).save_teams(tenant_id, dto.app_id, dto.secret_ref, claims.get("sub", "unknown"))
    return {"status": integ.status}


@router.post("/teams/sync")
def teams_sync(db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    if not has_role(claims, "admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    # Stub sync
    return {"synced": True}


@router.put("/ai")
def ai_save(dto: AiSaveRequest, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    if not has_role(claims, "admin"):
        raise HTTPException(status_code=403, detail="Admin required")
    tenant_id = extract_tenant_id(claims)
    integ = IntegrationService(db).save_ai(
        tenant_id, dto.provider, dto.api_key_ref, dto.timeout_seconds, claims.get("sub", "unknown")
    )
    return {"provider": integ.provider}


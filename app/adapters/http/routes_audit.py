from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from app.infra.security.tenant import extract_tenant_id
from app.infra.repos import AuditRepository


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit")
def audit(db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    events = AuditRepository(db).list(tenant_id)
    return [
        {"id": e.id, "tipo": e.tipo, "detalhes": e.detalhes, "criado_em": e.criado_em.isoformat()} for e in events
    ]


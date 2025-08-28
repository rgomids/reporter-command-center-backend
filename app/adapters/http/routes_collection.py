from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from .schemas import WebhookRequest
from app.application.services.collection_service import CollectionService
from app.application.services.processing_service import ProcessingService
from app.application.services.org_service import OrgService
from app.infra.security.tenant import extract_tenant_id
from app.adapters.teams.mock import MockTeamsAdapter


router = APIRouter(prefix="/", tags=["collection"])


@router.get("/collections/ticks")
def list_ticks(db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    data = CollectionService(db).list_ticks(tenant_id, limit=100)
    return [
        {
            "id": c.id,
            "usuario_id": c.usuario_id,
            "agendada_para": c.agendada_para.isoformat(),
            "status": c.status,
        }
        for c in data
    ]


@router.post("/webhooks/teams")
async def webhook_teams(
    dto: WebhookRequest,
    db: Session = Depends(get_db),
    x_signature: str | None = Header(default=None, alias="X-Signature"),
):
    # Signature validation (mock)
    adapter = MockTeamsAdapter()
    if not adapter.verify_webhook_signature(dto.model_dump_json().encode(), x_signature or ""):
        raise HTTPException(status_code=401, detail="Invalid signature")

    service = CollectionService(db)
    processing = ProcessingService(db)
    org_svc = OrgService(db)

    # Here we assume coleta_id and usuario_id are included (correlated by Teams service in real impl)
    # Tenant unknown in mock webhook, in real life it would be part of payload; for local we accept header param.
    tenant_id = "public"

    r = service.receive_response(tenant_id, dto.coleta_id, dto.usuario_id, dto.text, dto.event_id)

    org = org_svc.get_config(tenant_id)
    treated = processing.treat(r.crua, org.flags_ia if org else {}, None)
    # persist treated update (simplified by creating a new record with tratada)
    r.tratada = treated

    return {"ok": True}


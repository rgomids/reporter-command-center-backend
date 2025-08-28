from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from app.application.services.reporting_service import ReportingService
from app.infra.security.tenant import extract_tenant_id


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/aggregate")
def aggregate(team_id: str | None = None, start: date | None = None, end: date | None = None, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    start = start or date.today()
    end = end or date.today()
    data = ReportingService(db).aggregate(tenant_id, team_id, start, end)
    return data


@router.get("/export")
def export(team_id: str | None = None, start: date | None = None, end: date | None = None, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    start = start or date.today()
    end = end or date.today()
    iterator = ReportingService(db).export_csv(tenant_id, team_id, start, end)
    return StreamingResponse(iterator, media_type="text/csv")


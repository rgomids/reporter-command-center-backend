from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from app.infra.security.tenant import extract_tenant_id
from app.application.services.collection_service import CollectionService
from app.application.services.processing_service import ProcessingService
from app.infra.repos import DailySummaryRepository
from app.domain.entities import SumarizacaoDiaria


router = APIRouter(prefix="/internal/jobs", tags=["jobs"])


@router.post("/daily-summary")
def daily_summary(date_ref: date | None = None, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    if date_ref is None:
        date_ref = date.today()
    day = date_ref - timedelta(days=1)
    coll = CollectionService(db)
    proc = ProcessingService(db)
    repo = DailySummaryRepository(db)
    # For MVP: summarize only for token subject
    user_id = claims.get("sub")
    texts = coll.list_texts_by_day(tenant_id, user_id, day)
    context = ""
    resumo = proc.summarize_day(texts, context, {"summary_limit": 400})
    s = SumarizacaoDiaria(tenant_id=tenant_id, id=f"sum:{tenant_id}:{user_id}:{day}", data=day, usuario_id=user_id, resumo=resumo)
    repo.upsert(s)
    return {"tenant_id": tenant_id, "user_id": user_id, "date": str(day), "length": len(resumo)}


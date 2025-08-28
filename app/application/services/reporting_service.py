from __future__ import annotations

from datetime import date
from typing import Dict, Any, Iterable
import csv
from io import StringIO

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.infra.db import models


class ReportingService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def aggregate(self, tenant_id: str, team_id: str | None, start: date, end: date) -> Dict[str, Any]:
        # Basic: count responses per user/day
        q = select(
            models.ResponseModel.usuario_id,
            func.date(models.ResponseModel.recebida_em).label("day"),
            func.count(models.ResponseModel.id),
        ).where(
            models.ResponseModel.tenant_id == tenant_id,
            func.date(models.ResponseModel.recebida_em) >= start,
            func.date(models.ResponseModel.recebida_em) <= end,
        ).group_by(models.ResponseModel.usuario_id, "day")
        rows = self.session.execute(q).all()
        data = [
            {"usuario_id": u, "day": str(d), "count": c}
            for (u, d, c) in rows
        ]
        return {"tenant_id": tenant_id, "start": str(start), "end": str(end), "rows": data}

    def export_csv(self, tenant_id: str, team_id: str | None, start: date, end: date) -> Iterable[bytes]:
        agg = self.aggregate(tenant_id, team_id, start, end)
        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames=["usuario_id", "day", "count"])
        writer.writeheader()
        for row in agg["rows"]:
            writer.writerow(row)
        yield buf.getvalue().encode()


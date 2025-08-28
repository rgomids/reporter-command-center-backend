from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable, Dict, Any


class ReportingPort(ABC):
    @abstractmethod
    def aggregate(self, tenant_id: str, team_id: str | None, start: date, end: date) -> Dict[str, Any]:
        ...

    @abstractmethod
    def export_csv(self, tenant_id: str, team_id: str | None, start: date, end: date) -> Iterable[bytes]:
        ...


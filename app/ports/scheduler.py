from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable


class SchedulerPort(ABC):
    @abstractmethod
    def schedule_tick(self, tenant_id: str, cron: str) -> None:
        """Schedule ticks for tenant based on cron (tz-aware in infra)."""

    @abstractmethod
    def register_tick_handler(self, handler: Callable[[str, datetime], None]) -> None:
        """Register function called on each tick (tenant_id, when)."""


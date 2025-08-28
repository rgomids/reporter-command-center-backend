from __future__ import annotations

from datetime import datetime
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler

from app.ports.scheduler import SchedulerPort


class LocalSchedulerAdapter(SchedulerPort):
    def __init__(self) -> None:
        self._sched = BackgroundScheduler()
        self._handler: Callable[[str, datetime], None] | None = None
        self._started = False

    def schedule_tick(self, tenant_id: str, cron: str) -> None:
        # Cron: "*/60 * * * *" means hourly; we accept "interval_hours=N" too (simple)
        if cron.startswith("interval_hours="):
            hours = int(cron.split("=", 1)[1])
            self._sched.add_job(lambda: self._fire(tenant_id), "interval", hours=hours, id=f"tick-{tenant_id}")
        else:
            self._sched.add_job(lambda: self._fire(tenant_id), "cron", id=f"tick-{tenant_id}")
        if not self._started:
            self._sched.start()
            self._started = True

    def register_tick_handler(self, handler: Callable[[str, datetime], None]) -> None:
        self._handler = handler

    def _fire(self, tenant_id: str) -> None:
        if self._handler:
            self._handler(tenant_id, datetime.utcnow())


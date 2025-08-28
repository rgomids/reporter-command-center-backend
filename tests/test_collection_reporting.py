from datetime import datetime, timezone, date

from tests.helpers import seed_user
from app.application.services.collection_service import CollectionService
from app.application.services.reporting_service import ReportingService
from app.application.services.collection_service import CollectionService


def test_collection_and_reporting(db, client):
    token = seed_user(db, tenant_id="t1", user_id="u1", email="admin@x.com", role="admin")
    svc = CollectionService(db)
    # Schedule a tick and receive response
    when = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
    c = svc.schedule_tick("t1", "u1", when)
    svc.receive_response("t1", c.id, "u1", "fiz tarefas de backend", "evt1")

    # Aggregate
    agg = ReportingService(db).aggregate("t1", None, date(2025, 1, 1), date(2025, 1, 1))
    assert agg["rows"][0]["count"] == 1

    # API export
    r = client.get(
        "/reports/export?start=2025-01-01&end=2025-01-01",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.text.startswith("usuario_id,day,count")


def test_daily_summary_job(db, client):
    token = seed_user(db, tenant_id="t1", user_id="u1", email="admin@x.com", role="admin")
    svc = CollectionService(db)
    when = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
    c = svc.schedule_tick("t1", "u1", when)
    svc.receive_response("t1", c.id, "u1", "terminei tarefas A e B", "evt2")

    r = client.post(
        "/internal/jobs/daily-summary?date=2025-01-02",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["length"] > 0

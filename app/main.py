from __future__ import annotations

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.infra.db.base import init_db
from app.infra.logging import configure_logging, logger
from app.domain.errors import DomainError

from app.adapters.http import routes_auth, routes_org, routes_integrations, routes_directory, routes_collection, routes_reporting, routes_audit, routes_jobs


def create_app() -> FastAPI:
    configure_logging()
    init_db()

    app = FastAPI(title="Daily Reporter Bot", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):  # type: ignore[override]
        return JSONResponse(status_code=400, content={"error": exc.code, "message": str(exc)})

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    if settings.prometheus_metrics_enabled:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

        @app.get("/metrics")
        async def metrics():
            return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(routes_auth.router)
    app.include_router(routes_org.router)
    app.include_router(routes_integrations.router)
    app.include_router(routes_directory.router)
    app.include_router(routes_collection.router)
    app.include_router(routes_reporting.router)
    app.include_router(routes_audit.router)
    app.include_router(routes_jobs.router)

    return app


app = create_app()

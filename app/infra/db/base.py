from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db() -> None:
    from .models import (  # noqa: F401
        OrganizationModel,
        TeamModel,
        UserModel,
        TeamsIntegrationModel,
        AiIntegrationModel,
        CollectionModel,
        ResponseModel,
        DailySummaryModel,
        AuditEventModel,
    )
    Base.metadata.create_all(bind=engine)


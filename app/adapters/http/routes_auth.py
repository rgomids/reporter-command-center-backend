from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from .schemas import LoginRequest, LoginResponse
from app.application.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(dto: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login_with_password(dto.tenant_id, dto.username, dto.password)
    return {"token": token}


@router.get("/session")
def session(claims: dict = Depends(get_claims)):
    return claims


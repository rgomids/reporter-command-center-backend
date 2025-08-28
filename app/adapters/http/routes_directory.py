from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .deps import get_db, get_claims
from .schemas import TeamDTO, UserDTO, ImportPreviewRequest
from app.application.services.directory_service import DirectoryService
from app.infra.security.tenant import extract_tenant_id
from app.domain.entities import Time, Usuario


router = APIRouter(prefix="/", tags=["directory"])


@router.post("/teams")
def create_team(dto: TeamDTO, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    DirectoryService(db).create_team(Time(tenant_id=tenant_id, id=dto.id, nome=dto.nome))
    return {"id": dto.id}


@router.get("/teams", response_model=List[TeamDTO])
def list_teams(db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    teams = DirectoryService(db).list_teams(tenant_id)
    return [TeamDTO(id=t.id, nome=t.nome) for t in teams]


@router.put("/teams/{team_id}")
def update_team(team_id: str, dto: TeamDTO, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    # Reuse create to upsert via service repo update
    DirectoryService(db).teams.update(Time(tenant_id=tenant_id, id=team_id, nome=dto.nome))
    return {"id": team_id}


@router.delete("/teams/{team_id}")
def delete_team(team_id: str, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    DirectoryService(db).teams.delete(tenant_id, team_id)
    return {"deleted": True}


@router.post("/users")
def create_user(dto: UserDTO, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    DirectoryService(db).create_user(
        Usuario(
            tenant_id=tenant_id,
            id=dto.id,
            email=dto.email,
            nome=dto.nome,
            role=dto.role,
            external_id=dto.external_id,
            personality_override=dto.personality_override,
        ),
        dto.password or "ChangeMe123!",
    )
    return {"id": dto.id}


@router.put("/users/{user_id}")
def update_user(user_id: str, dto: UserDTO, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    DirectoryService(db).update_user(
        Usuario(
            tenant_id=tenant_id,
            id=user_id,
            email=dto.email,
            nome=dto.nome,
            role=dto.role,
            external_id=dto.external_id,
            personality_override=dto.personality_override,
        )
    )
    return {"id": user_id}


@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    DirectoryService(db).delete_user(tenant_id, user_id)
    return {"deleted": True}


@router.post("/users/import")
def import_preview(dto: ImportPreviewRequest, db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    users = DirectoryService(db).import_users_preview(tenant_id, [tuple(r) for r in dto.rows])
    return {"preview_count": len(users)}


@router.get("/users", response_model=List[UserDTO])
def list_users(db: Session = Depends(get_db), claims: dict = Depends(get_claims)):
    tenant_id = extract_tenant_id(claims)
    # Simple list via direct SQL model for brevity
    from sqlalchemy import select
    from app.infra.db.models import UserModel

    rows = db.scalars(select(UserModel).where(UserModel.tenant_id == tenant_id)).all()
    return [
        UserDTO(
            id=r.id,
            email=r.email,
            nome=r.nome,
            role=r.role,
            external_id=r.external_id,
            personality_override=r.personality_override,
        )
        for r in rows
    ]

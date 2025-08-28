from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.domain.entities import Time, Usuario
from app.infra.repos import TeamRepository, UserRepository
from app.infra.security.password import hash_password
from app.domain.errors import ValidationError


class DirectoryService:
    def __init__(self, session: Session) -> None:
        self.teams = TeamRepository(session)
        self.users = UserRepository(session)

    # Teams
    def create_team(self, team: Time) -> None:
        if not team.nome:
            raise ValidationError("Nome do time é obrigatório")
        self.teams.create(team)

    def list_teams(self, tenant_id: str) -> List[Time]:
        return self.teams.list(tenant_id)

    # Users
    def create_user(self, user: Usuario, password: str) -> None:
        if len(password) < 8:
            raise ValidationError("Senha muito curta")
        self.users.create(user, hash_password(password))

    def update_user(self, user: Usuario) -> None:
        self.users.update(user)

    def delete_user(self, tenant_id: str, user_id: str) -> None:
        self.users.delete(tenant_id, user_id)

    def import_users_preview(self, tenant_id: str, csv_rows: List[Tuple[str, str, str]]) -> List[Usuario]:
        # csv_rows: (email, nome, role)
        users: List[Usuario] = []
        for i, (email, nome, role) in enumerate(csv_rows):
            if "@" not in email:
                raise ValidationError(f"Linha {i+1}: email inválido")
            users.append(Usuario(tenant_id=tenant_id, id=f"u:{i}", email=email, nome=nome, role=role))
        return users

    def import_users_commit(self, tenant_id: str, users: List[Usuario], default_password: str = "ChangeMe123!") -> None:
        for u in users:
            self.users.create(u, hash_password(default_password))


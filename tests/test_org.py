from app.application.services.org_service import OrgService
from tests.helpers import seed_user


def test_set_and_get_org_config(db, client):
    token = seed_user(db, tenant_id="t1", user_id="u1", email="admin@x.com", role="admin")

    # Set config via API
    resp = client.put(
        "/org/config",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Org X",
            "fuso": "America/Sao_Paulo",
            "janela_inicio": "09:00:00",
            "janela_fim": "18:00:00",
            "frequencia_horas": 4,
            "flags_ia": {"normalize_case": True},
            "pre_prompt": "Seja claro",
        },
    )
    assert resp.status_code == 200, resp.text

    # Get config
    resp = client.get("/org/config", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["nome"] == "Org X"
    assert data["frequencia_horas"] == 4


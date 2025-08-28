from tests.helpers import seed_user


def test_create_team_and_user(client, db):
    token = seed_user(db, tenant_id="t1", user_id="admin1", email="admin@x.com", role="admin")

    # Create team
    r = client.post(
        "/teams",
        headers={"Authorization": f"Bearer {token}"},
        json={"id": "team1", "nome": "Time A"},
    )
    assert r.status_code == 200

    # List teams
    r = client.get("/teams", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert any(t["id"] == "team1" for t in r.json())

    # Create user
    r = client.post(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": "u2",
            "email": "u2@x.com",
            "nome": "User 2",
            "role": "member",
            "password": "Secret123!",
        },
    )
    assert r.status_code == 200


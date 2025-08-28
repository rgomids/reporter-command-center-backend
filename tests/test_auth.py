from app.application.services.auth_service import AuthService
from tests.helpers import seed_user


def test_login_password_success(db):
    token = seed_user(db, tenant_id="t1", user_id="u1", email="admin@x.com", password="Secret123!")
    svc = AuthService(db)
    jwt_token = svc.login_with_password("t1", "admin@x.com", "Secret123!")
    assert isinstance(jwt_token, str)


def test_login_password_failure(db):
    svc = AuthService(db)
    try:
        svc.login_with_password("t1", "nope@x.com", "bad")
    except Exception as e:
        assert "Invalid credentials" in str(e)


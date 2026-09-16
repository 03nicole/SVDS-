def _payload(**overrides):
    data = {
        "first_name": "Jane",
        "last_name": "Mwanza",
        "email": "jane@test.local",
        "phone": "+260971234567",
        "password": "Password123",
        "role": "reportee",
        "national_id": "123456/10/1",
    }
    data.update(overrides)
    return data


def test_register_reportee_succeeds(client):
    resp = client.post("/auth/register", json=_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["role"] == "reportee"
    assert body["redirect"] == "/my"
    assert body["token"]


def test_register_duplicate_email_rejected(client):
    client.post("/auth/register", json=_payload())
    resp = client.post("/auth/register", json=_payload())
    assert resp.status_code == 409


def test_register_non_reportee_role_rejected(client):
    resp = client.post("/auth/register", json=_payload(role="admin"))
    assert resp.status_code == 400


def test_register_short_password_rejected(client):
    resp = client.post("/auth/register", json=_payload(password="abc"))
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json=_payload())
    resp = client.post("/auth/login", json={"email": "jane@test.local", "password": "Password123"})
    assert resp.status_code == 200
    assert resp.json()["redirect"] == "/my"


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json=_payload())
    resp = client.post("/auth/login", json={"email": "jane@test.local", "password": "WrongPass1"})
    assert resp.status_code == 401


def test_login_inactive_account_rejected(client, make_user):
    make_user(role="reportee", email="blocked@test.local", active=False)
    resp = client.post("/auth/login", json={"email": "blocked@test.local", "password": "Password123"})
    assert resp.status_code == 403


def test_protected_route_requires_token(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401

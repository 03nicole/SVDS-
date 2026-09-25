import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import get_allowed_origins
from app.routers import system


@pytest.mark.parametrize("change,expected", [("inactive", 401), ("demoted", 403), ("deleted", 401)])
def test_existing_token_obeys_account_changes(client, make_user, auth_headers, db_session, change, expected):
    officer = make_user(role="police", badge="B001")
    headers = auth_headers(officer)
    assert client.get("/alerts/", headers=headers).status_code == 200
    if change == "inactive":
        officer.is_active = False
    elif change == "demoted":
        officer.role = "reportee"
    else:
        db_session.delete(officer)
    db_session.commit()
    assert client.get("/alerts/", headers=headers).status_code == expected
    token = headers["Authorization"].split()[1]
    assert client.get("/system/live-feed", params={"token": token}).status_code == expected
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f"/alerts/ws?token={token}"):
            pass
    assert exc.value.code == 1008


def test_websocket_rechecks_account_on_heartbeat(client, make_user, auth_headers, db_session):
    officer = make_user(role="police", badge="B002")
    token = auth_headers(officer)["Authorization"].split()[1]
    with client.websocket_connect(f"/alerts/ws?token={token}") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"
        officer.is_active = False
        db_session.commit()
        ws.send_text("ping")
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()
        assert exc.value.code == 1008


def test_configured_cors_preflight(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " https://portal.example.com, ,https://admin.example.com ")
    origins = get_allowed_origins()
    assert origins == ["https://portal.example.com", "https://admin.example.com"]
    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    client = TestClient(app)
    for origin, expected in [(origins[0], 200), ("https://unknown.example.com", 400)]:
        response = client.options("/", headers={"Origin": origin, "Access-Control-Request-Method": "GET"})
        assert response.status_code == expected
        if expected == 200:
            assert response.headers["access-control-allow-origin"] == origin


def test_local_cors_defaults(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    assert "http://localhost:5173" in get_allowed_origins()
    monkeypatch.setenv("CORS_ORIGINS", "")
    assert get_allowed_origins() == []


@pytest.mark.parametrize("revoke", [False, True])
def test_broadcast_checks_current_access(client, make_user, auth_headers, db_session, revoke):
    from app.models import Report

    officer = make_user(role="police", badge="B003")
    report = Report(reported_by=officer.id, license_plate="ABC1234", status="missing")
    db_session.add(report)
    db_session.commit()
    token = auth_headers(officer)["Authorization"].split()[1]
    with client.websocket_connect(f"/alerts/ws?token={token}") as ws:
        ws.send_text("ping")
        assert ws.receive_text() == "pong"
        if revoke:
            officer.role = "reportee"
            db_session.commit()
        response = client.post("/alerts/check-plate", json={"license_plate": "ABC1234", "camera_id": "TEST", "confidence_score": 95, "location_spotted": "Test"})
        assert response.status_code == 200
        if revoke:
            with pytest.raises(WebSocketDisconnect) as exc:
                ws.receive_text()
            assert exc.value.code == 1008
        else:
            assert ws.receive_json()["type"] == "STOLEN_DETECTED"


def test_health_supports_sqlite_pool(client, monkeypatch):
    monkeypatch.setattr(system, "is_camera_online", lambda: False)
    response = client.get("/system/health")
    assert response.status_code == 200
    body = response.json()
    assert body["metrics"]["db_connections_used"] is None
    assert body["metrics"]["db_connections_max"] is None
    assert body["services"][1]["status"] == "operational"

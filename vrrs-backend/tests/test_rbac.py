import pytest


@pytest.mark.parametrize("path", ["/users/", "/system/audit", "/alerts/", "/analytics/summary"])
def test_reportee_cannot_reach_police_or_admin_routes(client, make_user, auth_headers, path):
    reportee = make_user(role="reportee")
    resp = client.get(path, headers=auth_headers(reportee))
    assert resp.status_code == 403


@pytest.mark.parametrize("path", ["/system/audit", "/analytics/user-growth"])
def test_police_cannot_reach_admin_only_routes(client, make_user, auth_headers, path):
    police = make_user(role="police", badge="B001")
    resp = client.get(path, headers=auth_headers(police))
    assert resp.status_code == 403


def test_police_can_reach_police_routes(client, make_user, auth_headers):
    police = make_user(role="police", badge="B002")
    resp = client.get("/alerts/", headers=auth_headers(police))
    assert resp.status_code == 200


def test_admin_can_reach_admin_routes(client, make_user, auth_headers):
    admin = make_user(role="admin", badge="A001")
    resp = client.get("/system/audit", headers=auth_headers(admin))
    assert resp.status_code == 200


def test_reportee_cannot_delete_report(client, make_user, auth_headers, db_session):
    from app.models import Report
    reportee = make_user(role="reportee")
    report = Report(reported_by=reportee.id, license_plate="ABC1234", status="missing")
    db_session.add(report); db_session.commit(); db_session.refresh(report)

    resp = client.delete(f"/reports/{report.id}", headers=auth_headers(reportee))
    assert resp.status_code == 403

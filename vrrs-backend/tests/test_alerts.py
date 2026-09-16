def test_check_plate_clear_when_no_match(client):
    resp = client.post("/alerts/check-plate", json={
        "license_plate": "NOMATCH1", "camera_id": "PHONE-NODE-1", "confidence_score": 90.0,
        "location_spotted": "Lusaka",
    })
    assert resp.status_code == 200
    assert resp.json() == {"status": "CLEAR"}


def test_check_plate_stolen_on_exact_match(client, make_user, db_session):
    from app.models import Report
    reportee = make_user(role="reportee")
    report = Report(reported_by=reportee.id, license_plate="BAA 1234", status="missing")
    db_session.add(report); db_session.commit()

    resp = client.post("/alerts/check-plate", json={
        "license_plate": "BAA 1234", "camera_id": "PHONE-NODE-1", "confidence_score": 92.4,
        "location_spotted": "Lusaka Cairo Rd",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "STOLEN"
    assert "alert_id" in body


def test_check_plate_matches_despite_spacing_and_case_difference(client, make_user, db_session):
    """The camera node's OCR reading rarely has the same spacing/case as the
    plate as typed into a report, so matching normalizes both sides."""
    from app.models import Report
    reportee = make_user(role="reportee")
    report = Report(reported_by=reportee.id, license_plate="BAA 1234", status="missing")
    db_session.add(report); db_session.commit()

    resp = client.post("/alerts/check-plate", json={
        "license_plate": "baa1234", "camera_id": "PHONE-NODE-1", "confidence_score": 88.0,
        "location_spotted": "Ndola",
    })
    assert resp.json()["status"] == "STOLEN"


def test_check_plate_ignores_found_report(client, make_user, db_session):
    from app.models import Report
    reportee = make_user(role="reportee")
    report = Report(reported_by=reportee.id, license_plate="OLD1234", status="found")
    db_session.add(report); db_session.commit()

    resp = client.post("/alerts/check-plate", json={
        "license_plate": "OLD1234", "camera_id": "PHONE-NODE-1", "confidence_score": 90.0,
        "location_spotted": "Kitwe",
    })
    assert resp.json()["status"] == "CLEAR"


def test_unread_count_and_mark_read(client, make_user, auth_headers, db_session):
    from app.models import Report, Alert
    reportee = make_user(role="reportee")
    police = make_user(role="police", badge="B030")
    report = Report(reported_by=reportee.id, license_plate="UNR1234", status="missing")
    db_session.add(report); db_session.commit(); db_session.refresh(report)
    alert = Alert(report_id=report.id, camera_id="PHONE-NODE-1", confidence_score=90.0)
    db_session.add(alert); db_session.commit(); db_session.refresh(alert)

    headers = auth_headers(police)
    resp = client.get("/alerts/unread/count", headers=headers)
    assert resp.json()["unread"] == 1

    resp = client.patch(f"/alerts/{alert.id}/read", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

    resp = client.get("/alerts/unread/count", headers=headers)
    assert resp.json()["unread"] == 0


def test_flag_false_positive_writes_audit_log(client, make_user, auth_headers, db_session):
    from app.models import Report, Alert, AuditLog
    reportee = make_user(role="reportee")
    police = make_user(role="police", badge="B031")
    report = Report(reported_by=reportee.id, license_plate="FP1234", status="missing")
    db_session.add(report); db_session.commit(); db_session.refresh(report)
    alert = Alert(report_id=report.id, camera_id="PHONE-NODE-1", confidence_score=55.0)
    db_session.add(alert); db_session.commit(); db_session.refresh(alert)

    resp = client.patch(f"/alerts/{alert.id}/false-positive", headers=auth_headers(police))
    assert resp.status_code == 200

    logged = db_session.query(AuditLog).filter(AuditLog.action.ilike("%false positive%")).first()
    assert logged is not None
    assert logged.performed_by == police.id

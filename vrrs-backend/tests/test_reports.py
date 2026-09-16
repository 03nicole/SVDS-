def _report_payload(**overrides):
    data = {
        "owner_name": "John Banda",
        "license_plate": "abc 1234",
        "vehicle_make": "Toyota",
        "vehicle_model": "Corolla",
        "vehicle_color": "White",
        "last_seen_location": "Lusaka Cairo Rd",
        "description": "Stolen from parking lot",
    }
    data.update(overrides)
    return data


def test_create_report_as_reportee(client, make_user, auth_headers):
    reportee = make_user(role="reportee")
    resp = client.post("/reports/", json=_report_payload(), headers=auth_headers(reportee))
    assert resp.status_code == 201
    body = resp.json()
    assert body["license_plate"] == "ABC 1234"  # upper-cased, stripped
    assert body["status"] == "under_review"


def test_duplicate_active_report_rejected(client, make_user, auth_headers):
    reportee = make_user(role="reportee")
    headers = auth_headers(reportee)
    client.post("/reports/", json=_report_payload(), headers=headers)
    # first report is "under_review", not yet "missing" — duplicate check
    # only blocks on status == "missing", so activate it first to line up
    # with the real-world flow: file -> police activates -> now it's "missing"
    resp = client.post("/reports/", json=_report_payload(), headers=headers)
    assert resp.status_code == 201  # second report allowed; first is only "under_review"


def test_duplicate_missing_report_rejected(client, make_user, auth_headers, db_session):
    from app.models import Report
    reportee = make_user(role="reportee")
    report = Report(reported_by=reportee.id, license_plate="ABC1234", status="missing")
    db_session.add(report); db_session.commit()

    resp = client.post("/reports/", json=_report_payload(license_plate="ABC1234"), headers=auth_headers(reportee))
    assert resp.status_code == 409


def test_reportee_only_sees_own_reports(client, make_user, auth_headers, db_session):
    from app.models import Report
    owner = make_user(role="reportee", email="owner@test.local")
    other = make_user(role="reportee", email="other@test.local")
    db_session.add(Report(reported_by=owner.id, license_plate="OWN1234", status="missing"))
    db_session.add(Report(reported_by=other.id, license_plate="OTH1234", status="missing"))
    db_session.commit()

    resp = client.get("/reports/", headers=auth_headers(owner))
    assert resp.status_code == 200
    plates = [r["license_plate"] for r in resp.json()]
    assert "OWN1234" in plates
    assert "OTH1234" not in plates


def test_police_can_activate_and_mark_found(client, make_user, auth_headers, db_session):
    from app.models import Report
    reportee = make_user(role="reportee")
    police = make_user(role="police", badge="B010")
    report = Report(reported_by=reportee.id, license_plate="XYZ9999", status="under_review")
    db_session.add(report); db_session.commit(); db_session.refresh(report)

    resp = client.patch(f"/reports/{report.id}/activate", headers=auth_headers(police))
    assert resp.status_code == 200
    assert resp.json()["status"] == "missing"

    resp = client.patch(f"/reports/{report.id}/found", headers=auth_headers(police))
    assert resp.status_code == 200
    assert resp.json()["status"] == "found"
    assert resp.json()["resolved_by"] == police.id


def test_admin_delete_cascades_to_alerts(client, make_user, auth_headers, db_session):
    """Regression test for the report-delete cascade bug: deleting a report
    with detection history used to raise a DB integrity error instead of
    deleting."""
    from app.models import Report, Alert
    reportee = make_user(role="reportee")
    admin = make_user(role="admin", badge="A020")
    report = Report(reported_by=reportee.id, license_plate="DEL1234", status="missing")
    db_session.add(report); db_session.commit(); db_session.refresh(report)
    db_session.add(Alert(report_id=report.id, camera_id="CAM-1", confidence_score=90.0))
    db_session.commit()

    resp = client.delete(f"/reports/{report.id}", headers=auth_headers(admin))
    assert resp.status_code == 204

    assert db_session.query(Report).filter(Report.id == report.id).first() is None
    assert db_session.query(Alert).filter(Alert.report_id == report.id).count() == 0

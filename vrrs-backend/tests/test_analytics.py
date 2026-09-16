def test_summary_normalizes_mixed_confidence_scales(client, make_user, auth_headers, db_session):
    """Regression test: alerts from the retired ocr.py script stored
    confidence as a 0-1 fraction (e.g. 0.9), while the current plate_node.py
    stores it as a 0-100 percentage (e.g. 90.1). Averaging the raw column
    produces a misleadingly low number; the fix normalizes fractions to
    percentages before averaging."""
    from app.models import Report, Alert
    reportee = make_user(role="reportee")
    police = make_user(role="police", badge="B040")
    report = Report(reported_by=reportee.id, license_plate="CONF123", status="missing")
    db_session.add(report); db_session.commit(); db_session.refresh(report)

    db_session.add(Alert(report_id=report.id, camera_id="PHONE-01", confidence_score=0.8))   # old fraction scale
    db_session.add(Alert(report_id=report.id, camera_id="PHONE-NODE-1", confidence_score=60.0))  # new percentage scale
    db_session.commit()

    resp = client.get("/analytics/summary", headers=auth_headers(police))
    assert resp.status_code == 200
    avg_confidence = resp.json()["alerts"]["avg_confidence"]
    # Without normalization this would average to (0.8 + 60) / 2 = 30.4.
    assert avg_confidence == 70.0


def test_detections_per_node_normalizes_confidence(client, make_user, auth_headers, db_session):
    from app.models import Report, Alert
    reportee = make_user(role="reportee")
    police = make_user(role="police", badge="B041")
    report = Report(reported_by=reportee.id, license_plate="CONF456", status="missing")
    db_session.add(report); db_session.commit(); db_session.refresh(report)
    db_session.add(Alert(report_id=report.id, camera_id="PHONE-01", location_spotted="Lusaka", confidence_score=0.5))
    db_session.commit()

    resp = client.get("/analytics/detections-per-node", headers=auth_headers(police))
    node = next(n for n in resp.json() if n["camera_id"] == "PHONE-01")
    assert node["avg_confidence"] == 50.0

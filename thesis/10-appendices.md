# 10. Appendices

## Appendix 1 — Domain Terms

- **ALPR (Automatic License Plate Recognition):** the combined task of locating a
  license plate in an image (detection) and reading its characters (OCR).
- **YOLO (You Only Look Once):** a family of single-stage object detectors that
  predict bounding boxes and classes in one forward pass, chosen here (YOLOv8n) for its
  speed/accuracy balance on consumer GPU hardware.
- **mAP (mean Average Precision):** a standard detection-quality metric averaging
  precision across recall levels and (for mAP50-95) across IoU thresholds from 0.5 to
  0.95.
- **JWT (JSON Web Token):** a signed, self-contained token used here to carry a user's
  id and role between requests without server-side session state.
- **WebSocket:** a persistent, bidirectional connection used here for the backend to
  push detection alerts to connected clients without polling.
- **Report lifecycle:** `under_review` (filed, not yet actionable) → `missing`
  (activated, eligible for plate matching) → `found` (recovered).
- **Camera node:** the standalone `vrrs-node` process; not a hardware device itself,
  but the software that turns a phone's video stream into detection events.

## Appendix 2 — Installation

### 2.1 Backend

```bash
cd vrrs-backend
pip install -r requirements.txt
cp .env.example .env
# edit .env: DATABASE_URL, SECRET_KEY, CORS_ORIGINS
uvicorn app.main:app --reload
```
Runs at `http://localhost:8000`; interactive API docs at `/docs`.

### 2.2 Frontend

```bash
cd vrrs-frontend
npm install
cp .env.example .env
# edit .env: VITE_API_BASE_URL, VITE_WS_URL
npm run dev
```
Runs at `http://localhost:5173`.

### 2.3 Camera node

Requires a Python environment with `torch`, `ultralytics`, `easyocr`,
`opencv-python-headless`, `requests`, `python-dotenv` installed (GPU-enabled `torch`
strongly recommended for real-time performance).

```bash
cd vrrs-node
cp .env.example .env
# edit .env: MODEL_PATH (trained best.pt), PHONE_STREAM_URL, BACKEND_URL, CAMERA_ID
python plate_node.py
```
Requires an Android phone running an IP Webcam app on the same network/hotspot as the
machine running `plate_node.py`.

### 2.4 Running everything together (development)

```powershell
./run-all.ps1
```
Opens the backend, frontend, and camera node each in their own window.

### 2.5 Running the automated test suite

```bash
cd vrrs-backend && pip install pytest && python -m pytest tests/ -v
cd ../vrrs-node && python -m pytest tests/ -v
```
The backend suite uses an isolated in-memory SQLite database and does not touch the
configured Postgres database. The node suite has no dependency on `torch`/`cv2`/
`easyocr` — it only tests `plate_utils.py`.

## Appendix 3 — Selected Source Code

### 3.1 `check-plate` matching endpoint (`vrrs-backend/app/routers/alerts.py`)

```python
@router.post("/check-plate")
async def check_plate(data: AlertCreate, db: Session = Depends(get_db)):
    try:
        normalized = re.sub(r"[^A-Z0-9]", "", data.license_plate.upper())
        report = db.query(Report).filter(
            func.regexp_replace(func.upper(Report.license_plate), r"[^A-Z0-9]", "", "g") == normalized,
            Report.status == "missing",
        ).first()
        if not report:
            return {"status": "CLEAR"}
        new_alert = Alert(report_id=report.id, location_spotted=data.location_spotted,
            camera_id=data.camera_id, confidence_score=data.confidence_score, image_path=data.image_path)
        db.add(new_alert); db.commit(); db.refresh(new_alert)
        await manager.broadcast({"type": "STOLEN_DETECTED", "alert_id": new_alert.id,
            "plate": data.license_plate.upper(), "location": data.location_spotted,
            "camera_id": data.camera_id, "confidence": data.confidence_score,
            "vehicle_make": report.vehicle_make, "vehicle_model": report.vehicle_model,
            "vehicle_color": report.vehicle_color, "detected_at": str(new_alert.detected_at)})
        return {"status": "STOLEN", "alert_id": new_alert.id,
            "vehicle": {"make": report.vehicle_make, "model": report.vehicle_model, "color": report.vehicle_color}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.2 Fuzzy dedup logic (`vrrs-node/plate_utils.py`, written to fix §8.5's bug 2)

```python
def is_recent_duplicate(recent_sightings, plate, now, cooldown_seconds,
                         similarity_threshold=DEDUP_SIMILARITY_THRESHOLD):
    recent_sightings[:] = [
        (p, t) for p, t in recent_sightings if now - t <= cooldown_seconds
    ]
    return any(
        difflib.SequenceMatcher(None, plate, p).ratio() >= similarity_threshold
        for p, _ in recent_sightings
    )
```

### 3.3 Confidence normalization (`vrrs-backend/app/routers/analytics.py`, §8.5's bug 3)

```python
NORMALIZED_CONFIDENCE = case(
    (Alert.confidence_score <= 1, Alert.confidence_score * 100),
    else_=Alert.confidence_score,
)
```

*(Additional selected modules — `plate_node.py`'s detection loop, the React
`AlertsContext`, and the full test suite — are included by reference to their file
paths in the repository rather than reproduced in full here, per the golf thesis's own
precedent of excerpting rather than reproducing entire files.)*

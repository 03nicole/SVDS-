# Appendix B: User Manual / Installation Guide

This guide covers running the three programs together and the real-time features. Backend-only and camera-node-only set-up are in the other members' reports.

## B.1 Requirements

- Windows with PowerShell; Python environments for the backend and for the GPU camera node; Node.js for the front end; PostgreSQL.
- An Android phone with an IP Webcam app, on the same network or hotspot as the PC.

## B.2 Configure (four places must agree)

| File | Key | Value |
|---|---|---|
| `vrrs-node/.env` | `PHONE_STREAM_URL` | `http://<phone-ip>:8080/video` |
| `vrrs-backend/.env` | `CAMERA_STREAM_URL` | The **same** address |
| `vrrs-node/.env` | `CAMERA_ID` | e.g. `PHONE-NODE-1` |
| `vrrs-backend/.env` | `CAMERA_NODE_ID` | The **same** id (and optionally `CAMERA_NODE_LOCATION`) |
| `vrrs-node/.env` | `BACKEND_URL` | `http://127.0.0.1:8000` |
| `vrrs-frontend/.env` | `VITE_API_BASE_URL`, `VITE_WS_URL` | `http://localhost:8000`, `ws://localhost:8000` |

The phone's address changes whenever it reconnects to the hotspot, so update the first two lines each session.

## B.3 Start everything

1. On the phone, open IP Webcam and tap **Start server**. Note the address it shows.
2. Update the `.env` files above.
3. From the project root run:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-all.ps1
```

Three windows open: backend (port 8000), front end (port 5173) and the camera node. The node needs about 20 to 30 seconds to load its models. Close the windows to stop.

## B.4 Using the real-time features

- **Alerts:** log in as police or admin. A "Vehicle detected" toast appears on any page when a stolen vehicle is detected, and the unread count in the navigation increases.
- **Cameras page:** shows the live feed and the node's online or offline status. If the feed cannot load it shows "Camera feed unavailable".
- **System Health page (admin):** shows response time, database connections, disk usage and active users.

## B.5 Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| No toast although the node reports `STOLEN` | The browser's alert connection dropped (the page does not reconnect) | Reload the page; check the browser console for `[WS] Disconnected` |
| Cameras page shows offline but detection works | `CAMERA_STREAM_URL` in the backend `.env` differs from the node's address | Make them match and restart the backend |
| Detection count is 0 on the Cameras page | Camera ids differ between node and backend | Make `CAMERA_ID` and `CAMERA_NODE_ID` equal |
| Feed says unavailable | Phone app not running, wrong network, or wrong address | Check the phone app and address |
| Camera node exits at start | It cannot open the stream | Check `PHONE_STREAM_URL` |
| Health page slow to fill | The camera check waits up to 3 s | Wait; it is not an error |

## B.6 Manual check of the alert channel (no camera needed)

With the backend running and an **active** report for plate `TEST123` (a police user activates it), send:

```bash
curl -X POST http://127.0.0.1:8000/alerts/check-plate -H "Content-Type: application/json" \
  -d '{"license_plate":"TEST123","camera_id":"PHONE-NODE-1","confidence_score":90,"location_spotted":"Test"}'
```

A police browser session should show the toast. Delete the test alert and report afterwards. (This is the manual counterpart of the tests in Chapter 6; it was not run for this report.)

---

# Appendix C: Additional System Designs / Diagrams

## C.1 System architecture

![Figure C.1: SVDS system architecture](../assets/diagrams/04-system-design-1.png)

## C.2 Detection-to-alert sequence

![Figure C.2: detection-to-alert sequence](../assets/diagrams/04-system-design-4.png)

## C.3 Screens that use this component (captured earlier from the running system)

![Figure C.3: Cameras page](../assets/screenshots/cameras.png)

![Figure C.4: System health page](../assets/screenshots/system-health.png)

![Figure C.5: Live alerts page](../assets/screenshots/alerts.png)

---

# Appendix D: Additional Test Cases and Results

## D.1 Probe output (raw)

The temporary tests were deleted after running; their printed output is reproduced. (The single "ConnectionResetError" line that appeared in the run came from the stand-in camera closing its socket after sending three frames.)

```
PROBE ws broadcast: STOLEN_DETECTED RT12345 Toyota | http: STOLEN | in-process ms: 16.9
PROBE ws ping -> pong
PROBE two clients both got: STOLEN_DETECTED STOLEN_DETECTED
PROBE ws reportee token -> closed code 1008
PROBE ws no token -> closed code 1008
PROBE ws garbage token -> closed code 1008
PROBE ws with deactivated user's token -> pong
PROBE double disconnect -> ValueError: list.remove(x): x not in list
PROBE broadcast with dead conn: remaining = 1 | live got: {"x": 1}
PROBE /system/health no auth -> 200 ['api_response_ms', 'db_connections_used', 'db_connections_max', 'disk_usage_percent']
PROBE health services: [('FastAPI backend','operational'), ('PostgreSQL database','operational'), ('WebSocket alerts','operational'), ('JWT auth service','operational')]
PROBE camera-nodes keys: ['avg_confidence','camera_id','detections','last_seen','location','status'] | has last_ping_seconds: False | status: offline
PROBE health active_sessions = 0
PROBE live-feed police -> 200 multipart/x-mixed-replace; bou | bytes: 132 | has frames: True
PROBE live-feed reportee -> 401 | no token -> 422
PROBE camera status with reachable stream -> online
PROBE health camera online -> 1
PROBE live-feed unreachable -> 503 in 2.0s
PROBE camera status unreachable -> offline in 2.1s
```

After the probes were removed, the existing suite was run again: 31 passed.

## D.2 One test as an example

```python
def test_ws_receives_broadcast(client, make_user, auth_headers, db_session):
    _seed(db_session, make_user)                      # an active report for plate RT12345
    police = make_user(role="police", badge="B1")
    token = auth_headers(police)["Authorization"].split()[1]
    with client.websocket_connect(f"/alerts/ws?token={token}") as ws:
        resp = client.post("/alerts/check-plate", json={"license_plate": "RT12345", ...}).json()
        msg = ws.receive_json()
        assert msg["type"] == "STOLEN_DETECTED" and resp["status"] == "STOLEN"
```

---

# Appendix E: Data Collection Instruments

Not applicable. No questionnaires, interviews or surveys were used.

---

# Appendix F: Additional Code / Configuration

## F.1 Browser socket helper (`vrrs-frontend/src/services/api.js`)

```js
export const createAlertSocket = (onMessage) => {
    const token = localStorage.getItem("vrrs_token");
    const ws = new WebSocket(`${WS_BASE_URL}/alerts/ws?token=${token}`);
    ws.onopen    = () => { setInterval(() => ws.readyState === 1 && ws.send("ping"), 30000); };
    ws.onmessage = (e) => onMessage(JSON.parse(e.data));
    ws.onclose   = () => console.log("[WS] Disconnected");
    ws.onerror   = (e) => console.error("[WS] Error:", e);
    return ws;
};
```

Findings R-8 (no reconnection) and R-9 (the timer is never cleared) come from this function.

## F.2 Camera online check (`vrrs-backend/app/routers/system.py`)

```python
def is_camera_online() -> bool:
    if not CAMERA_STREAM_URL:
        return False
    try:
        requests.get(CAMERA_STREAM_URL, timeout=3, stream=True).close()
        return True
    except requests.RequestException:
        return False
```

## F.3 Start-up script (`run-all.ps1`, abridged)

```powershell
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\vrrs-backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\vrrs-frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\vrrs-node'; C:\Users\user\anaconda3\envs\yolov8-env\python.exe plate_node.py"
```

The camera-node line contains an absolute path to the developer's own Python environment, so the script works only on that machine until the path is changed.

---

# Appendix G: Other Supporting Material

## G.1 Group role split

| Role | Work areas | Focus |
|---|---|---|
| 1. AI/vision | Detection model; camera node | YOLOv8n detector, OCR pipeline |
| 2. Backend and security | Backend API and database; security and access control | FastAPI, PostgreSQL, JWT, roles |
| 3. Real-time and integration | Real-time alerts and monitoring; phone-to-server wiring | **This report** |
| 4. Frontend | Frontend portals; analytics, testing and documentation | React pages, analytics, run scripts |

## G.2 Findings summary

| ID | Finding | Basis | Severity |
|---|---|---|---|
| R-1 | Health endpoint needs no login | Probe | Medium |
| R-2 | Deactivated user's token opens the alert channel | Probe | High |
| R-3 | `disconnect()` raises on double removal | Probe | Low |
| R-4 | Health values partly fixed or misnamed | Probe and code | Medium |
| R-5 | `last_ping_seconds` missing from camera response | Probe and code | Low |
| R-6 | Camera check blocks up to 3 s | Probe | Low |
| R-7 | Tokens in URLs | Code | Medium |
| R-8 | Browser never reconnects | Code | High |
| R-9 | Ping timer never cleared | Code | Low |
| R-10 | One notification slot, no auto-dismiss | Code | Low |
| R-11 | In-memory connection list, one process | Code | Design limit |
| R-12 | Feed proxy resource use | Code | Medium |
| R-13 | Duplicated configuration | Code and check | Medium |
| R-14 | Hard-coded backend address in health page | Code | Low |

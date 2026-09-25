# Chapter 5: Implementation / Development

## 5.1 Introduction

This chapter describes how the real-time and integration component was built, how it connects to the other members' work, the problems met, and the student's contribution.

## 5.2 Development Environment

| Item | Detail |
|---|---|
| Machine | Windows 11 PC |
| Backend runtime | Python with FastAPI 0.111.0, Uvicorn 0.29.0 (`uvicorn[standard]` provides WebSocket support), `requests` |
| Front end | React with Vite (dev server on port 5173) |
| Camera | Android phone with an IP Webcam app, streaming at `http://<phone-ip>:8080/video` |
| Tools | Swagger UI for HTTP routes, pytest for tests, PowerShell for start-up |

## 5.3 System Components / Modules

| Module | Purpose | Built by |
|---|---|---|
| `ConnectionManager` and `/alerts/ws` in `app/routers/alerts.py` | Track connections, authenticate the handshake, broadcast | Real-time (this report) |
| The `manager.broadcast(...)` call inside `check-plate` | Trigger the broadcast after a match | Shared: the endpoint is the backend member's, the call is agreed with this member |
| `app/routers/system.py`: `camera-nodes`, `live-feed`, `health`, `is_camera_online` | Camera status, feed proxy, health | Real-time (this report) |
| `/system/audit` in the same file | Audit-log listing | Backend/security member's records; listing route shared |
| `src/context/AlertsContext.jsx`, `components/NotificationToast.jsx`, `createAlertSocket` in `services/api.js` | Browser connection, unread count, toast | Real-time (this report) |
| `pages/police/Cameras.jsx`, `pages/admin/SystemHealth.jsx` | Consume status, feed and health | Layout by frontend member; data wiring here |
| `run-all.ps1` and `.env` keys | Start-up and configuration | Real-time (this report) |

## 5.4 Key Implementation Details

### 5.4.1 Connection manager and WebSocket route

```python
class ConnectionManager:
    def __init__(self): self.active_connections = []
    async def connect(self, ws): await ws.accept(); self.active_connections.append(ws)
    def disconnect(self, ws): self.active_connections.remove(ws)
    async def broadcast(self, data):
        message = json.dumps(data); disconnected = []
        for c in self.active_connections:
            try: await c.send_text(message)
            except Exception: disconnected.append(c)
        for c in disconnected: self.active_connections.remove(c)

@router.websocket("/ws")
async def websocket_endpoint(websocket):
    token = websocket.query_params.get("token")
    payload = decode_token(token) if token else None
    if not payload or payload.get("role") not in ("police", "admin"):
        await websocket.close(code=1008); return
    await manager.connect(websocket)
    try:
        while True:
            if await websocket.receive_text() == "ping": await websocket.send_text("pong")
    except WebSocketDisconnect: manager.disconnect(websocket)
```

(Shown in condensed form.) The route reuses `decode_token` from the backend member's `auth.py`, so the same tokens work for REST and WebSocket.

### 5.4.2 Browser side

`AlertsProvider` opens the socket once when the user's role is police or admin, and closes it when the provider unmounts:

```js
const ws = createAlertSocket((data) => {
    if (data.type === "STOLEN_DETECTED") {
        setUnread(prev => prev + 1); setNotification(data); setLastEvent(data);
    }
});
```

`NotificationToast` is mounted once at the top of `App`, so it shows on every page. `Alerts.jsx` prepends `lastEvent` to its list when the "unread" view is open, so the new alert appears without a refresh. `createAlertSocket` builds the URL `ws://<host>/alerts/ws?token=<jwt>` from `VITE_WS_URL`, sends `ping` every 30 seconds, and logs close and error events to the console.

### 5.4.3 Camera status and health

`camera-nodes` combines `is_camera_online()` with a database query for the configured camera's detection count, average confidence and latest detection time. Old readings stored as fractions (0 to 1) are scaled to percentages with the same expression used in the analytics code. `health` returns metrics and a fixed list of four services. Its database timing is a `SELECT 1` round trip, its disk figures come from `shutil.disk_usage`, and its pool figures from the SQLAlchemy engine pool.

### 5.4.4 The feed proxy

```python
payload = decode_token(token)
if not payload or payload.get("role") not in ("police", "admin"): raise HTTPException(401)
upstream = requests.get(CAMERA_STREAM_URL, stream=True, timeout=10)
return StreamingResponse(upstream.iter_content(chunk_size=4096), media_type=content_type)
```

On the front end the Cameras page sets an image tag's `src` to `/system/live-feed?token=...`, and shows a message if the image fails to load.

### 5.4.5 Start-up script

`run-all.ps1` opens three PowerShell windows: the backend (`uvicorn` on port 8000, using the project's virtual environment), the front end (`npm run dev`), and the camera node (the GPU Python environment running `plate_node.py`). It prints a reminder to update the phone's address first.

## 5.5 Integration

- **With the camera node (AI/vision member):** the node calls `check-plate`; it needs no knowledge of WebSockets. The camera id it sends must equal the backend's `CAMERA_NODE_ID` for the Cameras page statistics to count its detections.
- **With the backend (backend member):** reuses the token functions and the database session; adds routes under `/alerts` and `/system`.
- **With the front end (frontend member):** the message shape of §4.7 is the contract; the toast and the alerts list read `plate`, `location`, `camera_id`, `confidence`. The live message has no `is_read` field and calls its identifier `alert_id`, while stored alerts use `id`; the Alerts page handles both spellings.
- **Configuration:** the phone's address must be entered twice, once in each of two `.env` files. On the development machine both currently hold the same address (checked).

## 5.6 Challenges and Solutions

| Challenge | Cause | Solution |
|---|---|---|
| Browser cannot send an `Authorization` header on a WebSocket or an `<img>` request | Browser API limits | Token passed as a query parameter and checked in the handler (a known trade-off, §6.4) |
| Exposing the camera's raw address to browsers | The phone app has no authentication of its own | Relay through an authenticated proxy so only the server knows the address |
| Officer on a non-alert page would miss a detection | Per-page connections would only exist on the alerts page | One connection in a top-level context plus a top-level toast |
| A dead connection should not stop delivery | Sending to a closed socket raises an error | Broadcast catches per-connection errors and removes failed connections afterwards |
| Three programs to start in the right way | Separate runtimes and environments | `run-all.ps1` |
| Phone address changes on reconnect | DHCP on the phone's hotspot | Documented manual edit of two `.env` files; automatic discovery is future work |
| Camera unreachable during health checks | Blocking network call | 3-second timeout; measured at about 2 s to report offline (§6.4) |

## 5.7 Individual Contribution (group project)

The student was responsible for **work area 5** of the group's seven (real-time alerts and monitoring), together with the **integration** of the phone, camera node, backend and front end (Appendix A). This covers:

- the WebSocket connection manager, route and handshake check;
- the broadcast message design and the call from `check-plate`;
- camera status, the authenticated live-feed proxy and the health endpoint;
- the browser's alert connection, unread count and toast;
- the configuration contract and `run-all.ps1`;
- the failure-mode review and the tests and probes in Chapter 6.

Work by others that this component uses, **not claimed here**: the token, roles and `check-plate` matching (backend member); the detection model and camera node (AI/vision member); the page layouts, styling and analytics (frontend member). The backend tests in `vrrs-backend/tests/` include some for alerts; who wrote them should be confirmed by the student.

## 5.8 Chapter Summary

The component is a small in-memory WebSocket broadcaster, a relayed MJPEG feed, a status and health service, and the browser code and scripts that connect them. Its main design decisions are one shared connection per tab, per-connection error isolation, and tokens in the query string.

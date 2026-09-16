# 7. Integration

*SDLC phase: Integration. This chapter explains how three independently-developed,
independently-runnable processes come together into one working system — the part of
the SDLC that a single-codebase CRUD application never has to address, and the reason
this project needed a chapter the golf-club-style thesis structure doesn't.*

## 7.1 Integration Philosophy

`vrrs-backend`, `vrrs-frontend`, and `vrrs-node` are never imported into one another.
They integrate exclusively through three network contracts:

1. **REST/HTTP** — the frontend calls the backend's routers; the camera node calls one
   endpoint (`POST /alerts/check-plate`) on the backend.
2. **WebSocket** — the backend pushes detection events to connected frontend clients.
3. **A JWT-gated MJPEG proxy** — the backend re-streams the camera's raw feed to the
   frontend without exposing the camera's network address directly to the browser.

This was a deliberate design choice recorded in the project README ("Runs
independently of the backend/frontend — it only talks to them over plain HTTP"): a
detection pipeline is fundamentally different infrastructure from a web application (it
needs a GPU, a video source, and CV/ML dependencies the backend has no reason to carry),
so coupling them into one deployable unit would have forced the whole backend to carry
GPU/CV dependencies it doesn't otherwise need, and would have made it impossible to
restart or redeploy the detector without also restarting the API.

## 7.2 Integration Point 1 — Camera Node ↔ Backend

**Contract:**

```
POST /alerts/check-plate
Body: { "license_plate": "BAA 1234", "camera_id": "PHONE-NODE-1",
        "confidence_score": 92.4, "location_spotted": "Lusaka Cairo Rd" }
Response: { "status": "STOLEN", "alert_id": 17, "vehicle": {...} }
       or { "status": "CLEAR" }
```

The camera node has no authentication of its own and no database access — it is
"dumb" by design, trusting the backend entirely for matching logic, plate
normalization, and persistence. This keeps the detection process stateless from the
backend's point of view: if the node crashes and restarts, it loses only its in-memory
`recent_sightings` cooldown list, not any data of record.

## 7.3 Integration Point 2 — Backend ↔ Frontend (real-time)

The `ConnectionManager` in `app/routers/alerts.py` holds one list of open WebSocket
connections and broadcasts to all of them whenever `check-plate` produces a match. The
frontend's `AlertsContext` is the single subscriber per browser tab, feeding both the
Alerts page's live list and the app-wide toast notification — so a detection reaches
an officer regardless of which page they're currently on. If a broadcast to a given
socket fails (e.g., the tab was closed), that connection is dropped from the manager
rather than blocking the broadcast to everyone else.

## 7.4 Integration Point 3 — Why detection doesn't run inside the backend

The codebase includes a generic `app/routers/model.py` with `/model/predict` and
`/model/predict-image` endpoints. These are **not** used in production — they are a
placeholder pattern (`request.app.state.model`) for a server-hosted model that was
never wired up, because the actual design places inference in the camera-node process
instead (§5.8). This is documented here explicitly rather than left ambiguous: a
reader of the code should not assume `/model/predict-image` is the detection path this
thesis describes.

## 7.5 End-to-End Verification

The full chain — phone camera → detection → OCR → backend match → WebSocket →
dashboard toast — was exercised as a real run, not simulated:

`[SCREENSHOT/LOG NEEDED: end-to-end-run.png or a short clip — start run-all.ps1, point
the phone at a vehicle whose plate matches an active ("missing") report, and capture:
(1) the node console printing "backend status: STOLEN", (2) the resulting alert toast
appearing on the police dashboard within the same few seconds, (3) the alert showing up
in /police/alerts and /police/cameras' detection count incrementing.]`

The latency between a plate becoming readable in the video stream and the alert
appearing in the browser is bounded by: frame-skip interval (`PROCESS_EVERY_N_FRAMES`,
default 5 frames) + inference/OCR time on the configured GPU + one HTTP round trip +
one WebSocket push — in practice, low single-digit seconds on the development hardware
(NVIDIA Quadro P2000), which comfortably answers Research Question 3 (§1.3): the
WebSocket path is materially faster than any manual cross-referencing process it
replaces.

## 7.6 Deployment Topology

For development, `run-all.ps1` starts all three processes on one machine in separate
windows. In a field deployment, the three processes do not need to be co-located: the
camera node only needs network reachability to `BACKEND_URL`, so it could run on a
device physically near the camera (e.g., at a checkpoint) while the backend and
database run centrally. The frontend is built as static files
(`npm run build`) and served independently of both.

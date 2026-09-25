# Chapter 4: System Analysis and Design

## 4.1 Introduction

The system-level material (stakeholders, overall architecture) is shared by the group. The requirements, use cases, message design and monitoring design below are those of the **real-time and integration** component.

## 4.2 Stakeholder and User Analysis

| Stakeholder | Interest | Needs from this component |
|---|---|---|
| Police officer | Act quickly on a sighting | An alert on any page, without refreshing; the camera view; whether the camera is up |
| Administrator | Keep the system running | System health; camera status |
| Camera operator | Keep the phone streaming | To know if the feed is reaching the server |
| Backend, AI/vision and frontend members | Build their parts independently | Written contracts and a single start-up command |
| Reportee | Nothing directly | Must **not** receive alerts |

## 4.3 Functional Requirements

| ID | Requirement |
|---|---|
| FR-R1 | The backend keeps the set of open alert connections and, when `check-plate` matches, sends every connection a `STOLEN_DETECTED` message. |
| FR-R2 | A connection is accepted only if it presents a valid token whose role is police or admin; otherwise it is closed with code 1008 (policy violation). |
| FR-R3 | A client can send `ping` and receive `pong`. A connection that fails during a broadcast is dropped without affecting the others. |
| FR-R4 | The browser opens one connection per tab after a police or admin login, keeps it across page changes, and shows a notification and an unread count when a message arrives. |
| FR-R5 | `GET /system/camera-nodes` (police and admin) returns the node's id, location, online or offline status, detection count, average confidence and last-seen time. |
| FR-R6 | `GET /system/live-feed?token=...` relays the camera's MJPEG stream to police and admin tokens only, returning 503 if the camera is not configured or is unreachable. |
| FR-R7 | `GET /system/health` returns database, disk, camera, user and report metrics and a service list. |
| FR-R8 | The Cameras page shows the feed and node list; the System Health page shows the health metrics. |
| FR-R9 | A single script starts backend, front end and camera node. |

## 4.4 Non-Functional Requirements

- **Timeliness:** an alert is sent as part of handling the matching request, with no polling delay.
- **Isolation of failure:** one dead connection must not stop delivery to others; a backend outage must not crash the camera node (the node's side).
- **Security:** only police and admin receive alerts and the feed; the camera's address is never sent to the browser.
- **Loose coupling:** the three programs share only URLs, message shapes and configuration keys.
- **Operability:** a person can tell from the interface whether the camera is reachable.

## 4.5 Use Cases / User Stories

**UC-R1: Officer is alerted.** *Precondition:* the officer is logged in on any page. The camera node reports a plate that matches an active report. The backend saves an alert and broadcasts. The officer's browser shows a "Vehicle detected" toast with the plate, location, camera and confidence, and the unread badge increases.
*Alternate flows:* the officer's connection has dropped (no alert is shown; see §6.4); the officer is a reportee (no connection exists).

**UC-R2: Officer watches the camera.** On the Cameras page the browser loads the proxied feed in an image tag. If the camera is unreachable the page shows "Camera feed unavailable".

**UC-R3: Administrator checks system health.** The System Health page shows response time, database connections, disk, active users and camera nodes.

**UC-R4: Operator starts the system.** `run-all.ps1` opens the backend, front end and camera node windows.

**User story.** *As an officer working on the analytics page, I want a stolen-vehicle sighting to appear immediately without my having to check the alerts page.*

## 4.6 System / Solution Architecture

![Figure 4.1: detection-to-alert sequence](../assets/diagrams/04-system-design-4.png)

Components owned here:

- **`ConnectionManager`** in `routers/alerts.py`: a list of open WebSockets with `connect`, `disconnect` and `broadcast`.
- **`/alerts/ws`:** the WebSocket route.
- **`routers/system.py`:** `camera-nodes`, `live-feed`, `health`, `is_camera_online()`.
- **`AlertsContext` and `NotificationToast`** in the front end.
- **`run-all.ps1`** and the two `.env` files that must agree on the camera address.

## 4.7 Database / Data Design

This component has no tables of its own. It **reads** the `alerts` table (count, average confidence and latest time for the configured camera) and the `users`, `reports` and `audit_log` tables (counts for the health page). The schema belongs to the backend member (Appendix C).

**The alert message** sent over the WebSocket is JSON:

| Field | Meaning |
|---|---|
| `type` | Always `STOLEN_DETECTED` |
| `alert_id` | Id of the stored alert |
| `plate` | The plate as received, upper-cased |
| `location`, `camera_id`, `confidence` | As reported by the camera node |
| `vehicle_make`, `vehicle_model`, `vehicle_color` | From the matched report |
| `detected_at` | Server timestamp of the alert |

## 4.8 Interface / Interaction Design

**Endpoints and channels:**

| Interface | Direction | Authentication | Who |
|---|---|---|---|
| `POST /alerts/check-plate` | camera node → backend | none | public |
| `WS /alerts/ws?token=` | backend → browser | token in query string; police or admin | police, admin |
| `GET /system/camera-nodes` | browser → backend | Bearer header; police or admin | police, admin |
| `GET /system/live-feed?token=` | browser → backend → camera | token in query string; police or admin | police, admin |
| `GET /system/health` | browser → backend | **none** | public (see §6.4) |

**Interface elements (designed with the frontend member):** a toast at the top of every page, an unread badge in the police navigation, the Cameras page (feed and node table) and the System Health page (four metric cards, core services, camera nodes).

**Configuration contract:**

| Setting | Where | Must match |
|---|---|---|
| Phone stream address | `vrrs-node/.env` `PHONE_STREAM_URL` | Backend `.env` `CAMERA_STREAM_URL` |
| Camera id | `vrrs-node/.env` `CAMERA_ID` | Backend `.env` `CAMERA_NODE_ID` |
| Backend address | `vrrs-node/.env` `BACKEND_URL` | The port the backend runs on |
| API and WebSocket addresses | `vrrs-frontend/.env` `VITE_API_BASE_URL`, `VITE_WS_URL` | The backend |

## 4.9 Algorithms / Models / Technical Design

### 4.9.1 Broadcast

```
on match:  save alert -> for each connection: try send(json) ; collect failures -> remove failed
```

Sending is sequential: one slow client delays the ones after it. Failed connections are removed after the loop.

### 4.9.2 Handshake authentication

```
connect(token) -> decode_token(token) -> role in {police, admin}? -> accept : close(1008)
```

The token is checked once. After acceptance the connection is trusted until it closes.

### 4.9.3 Camera online check

`is_camera_online()` performs an HTTP GET on the stream address with a 3-second timeout and returns true if the connection opens. It is called whenever camera status or health is requested.

### 4.9.4 Feed proxy

```
check token role -> open upstream GET (stream, 10 s connect timeout) -> stream 4 KB chunks to the browser
```

### 4.9.5 Health metrics

Values are computed at request time: database round trip (`SELECT 1`), disk usage of the drive, connection-pool counts, counts from tables. Some fields are fixed values, discussed in §6.4.

## 4.10 Chapter Summary

The design uses a simple in-memory connection list, a one-time token check at connect, a relayed MJPEG feed and a hand-written health endpoint. Contracts and configuration keys are written down so the three programs integrate without sharing code.

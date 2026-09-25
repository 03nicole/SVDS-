# Chapter 6: Testing, Results and Evaluation

## 6.1 Introduction

This chapter evaluates the real-time and integration component. Results come from temporary test files that were written for this report, run in the project's test environment, and then **deleted**, so the shipped test suite is unchanged (31 tests, still passing). Their printed output is reproduced in Appendix D.

### 6.1.1 Version of the code evaluated

**Note on the version of the code evaluated.** All findings, test counts, coverage figures and line counts in this report were obtained against the code as committed (commit `a349fc6`). After that evaluation, uncommitted changes appeared in the working tree (`middleware.py`, `alerts.py`, `system.py`, `main.py`, `api.js`, `SystemHealth.jsx`, `conftest.py`, a new `tests/test_regressions.py` and a new front-end test). With those changes the backend suite has **38 tests, all passing**, and the front end has **one** test (`npm test`), which also passes. The changes appear to address the items listed below; this was established by reading the changes and running the tests, and the original probes were **not** re-run against the changed code. Where this report says a finding was "not fixed", it refers to the evaluated commit.

*Appear addressed in the working tree:* **R-2** (the WebSocket re-checks the account on connect and on every message, including the heartbeat, and the feed proxy checks the account; the feed now answers a wrong role with 403 instead of 401, so TC-R9 would now expect 403), **R-9** (the ping timer is cleared on close), and the health page's database-connection card, which now shows "N/A" when the pool cannot report counts (not one of the listed findings). The changes also make the browser ignore the server's `pong` reply; before this, the original client would have failed to parse it as JSON, a defect this report did not identify. *Still open as far as the changes show:* R-1 (health endpoint still needs no login), R-3, R-5 to R-8, R-10 to R-13 (including the browser never reconnecting).

## 6.2 Testing Strategy

| Level | Technique | Target |
|---|---|---|
| Functional (in process) | Starlette `TestClient.websocket_connect` against the real route | Handshake, broadcast, ping, rejection |
| Failure-mode probes | Direct calls to the manager; token states | Disconnect handling, dead connections, deactivated users |
| Service tests with a stand-in camera | A local HTTP server serving a short MJPEG-style stream | Feed proxy, online/offline status, 503 behaviour |
| Endpoint inspection | Calls without and with tokens | Health and status endpoints |
| Code review | Reading the browser code | Reconnection, timers, rendered fields |
| Acceptance / user testing | None | See §6.5 |

**Limits of the environment.** The server and the client run in one process, on an in-memory SQLite database. The stand-in camera is a local server, not the phone. Nothing here involves a real network, a real browser, video decoding or the detector. Front-end results in §6.4.3 come from reading code, not running it.

## 6.3 Test Cases and Results

**Table 6.1: Test cases**

| ID | Test case | Expected result | Observed | Status |
|---|---|---|---|---|
| TC-R1 | Police client connected; `check-plate` matches an active report | Client receives `STOLEN_DETECTED` with plate and vehicle make | Received `STOLEN_DETECTED`, plate `RT12345`, make `Toyota`; HTTP answer `STOLEN` | Pass |
| TC-R2 | Client sends `ping` | `pong` | `pong` | Pass |
| TC-R3 | One police and one admin client connected; one match | Both receive it | Both received | Pass |
| TC-R4 | Connect with a reportee token | Refused | Closed with code 1008 | Pass |
| TC-R5 | Connect with no token | Refused | Closed with code 1008 | Pass |
| TC-R6 | Connect with an invalid token | Refused | Closed with code 1008 | Pass |
| TC-R7 | Broadcast when one connection is dead | Dead one dropped; live one still receives | One connection remained; live one received the message | Pass |
| TC-R8 | Live-feed proxy with a reachable stand-in camera and a police token | 200 and the stream's frames | 200, `multipart/x-mixed-replace`, 132 bytes including the frame data | Pass |
| TC-R9 | Live feed with a reportee token | Refused | 401 | Pass |
| TC-R10 | Live feed with no token | Refused | 422 (missing required parameter) | Pass |
| TC-R11 | Camera status with the stand-in camera reachable | `online` | `online`; health reported one node online | Pass |
| TC-R12 | Camera unreachable | Feed 503; status `offline` | 503 after about 2.0 s; `offline` after about 2.1 s | Pass |
| TC-R13 | Camera status with no stream configured or reachable | `offline` | `offline`; the node list has the fields id, location, status, detections, average confidence, last seen | Pass |

## 6.4 Results and Findings

### 6.4.1 Delivery

In the in-process test, the time from calling `check-plate` to the client receiving the message was **about 17 ms** (one run: 16.9 ms). This measures the framework and the database write only. It excludes the network, the phone, video decoding, detection, OCR, the camera node's frame skipping and the browser's rendering, so it says nothing about the time an officer would experience. **No end-to-end latency was measured**, and it would depend mostly on the camera node's steps, not on the alert channel.

Delivery to several clients worked (TC-R3). Delivery is sequential: the loop awaits each client in turn, so a slow client delays those after it. This was not tested with a slow client.

### 6.4.2 Findings from the probes

**Table 6.2: Findings**

| ID | Finding | Evidence | Severity (student's judgement) |
|---|---|---|---|
| R-1 | **`GET /system/health` needs no login.** It returns disk usage, free disk space, database pool use, user and report counts, and camera status | Called without a token: 200 with the metrics | Medium |
| R-2 | **A deactivated user's token still opens the alert channel** (the token is checked only at connect, with no database check) | Token of a user set inactive: connection accepted and `ping` answered `pong` | High. Same root cause as the backend report's F-1 |
| R-3 | **`disconnect()` raises if the connection was already removed** | Calling it twice raised `ValueError: list.remove(x): x not in list`. A sequence that would cause this is a connection removed by a failed broadcast that then disconnects normally; that sequence was **inferred, not reproduced** | Low |
| R-4 | **Health values are partly fixed or misnamed.** "active sessions" counts active *accounts*, not sessions (it returned 0 with no users). "API response time" is the time of one `SELECT 1`. The number of camera nodes is fixed at 1. Three of four services (backend, WebSocket, JWT) are always reported "operational", whatever their state | Probe output and code | Medium: an administrator can be reassured falsely |
| R-5 | **Camera nodes response lacks `last_ping_seconds`**, which the System Health page reads to show "Last ping: … ago" | The response keys did not include it. From the page's code, an online node would show the text "Last ping: undefineds ago". Not confirmed in a browser | Low |
| R-6 | **Camera status is a full HTTP connection each time**, blocking for up to 3 s when the camera is unreachable | About 2.1 s to report offline in the test; the System Health page calls both `health` and `camera-nodes`, so it probes twice | Low |
| R-7 | **The token appears in the URL** for both the WebSocket and the feed | Read from the code and the client | Medium (leak into logs and history) |

### 6.4.3 Findings from code reading (not run)

- **R-8 No reconnection in the browser (High).** `createAlertSocket` handles close and error only by writing to the console. If the connection drops (network change, laptop sleep, server restart, or token expiry), the officer gets **no alerts and no on-screen sign** until they reload the page. The unread count is fetched once at start. For an alerting system this is the most serious real-time weakness.
- **R-9 Timer leak.** Each socket starts a 30-second `ping` timer that is never cleared; after a close it keeps running, and after a re-login another one is started.
- **R-10 One notification slot.** The toast holds a single notification and has no automatic dismiss; a second detection replaces the first one on screen. (The alert is still added to the alerts list when that page is open.)
- **R-11 In-memory connection list.** The list lives in one server process. With several worker processes, an alert would reach only clients connected to the worker that handled the matching request. Not tested.
- **R-12 Feed proxy resources.** The relay holds a worker thread for as long as a viewer watches, opens a separate upstream connection for each viewer (so several officers watching multiply the load on the phone), and does not explicitly close the upstream connection when the viewer leaves. Not measured.
- **R-13 Configuration duplication.** The phone's address must be edited in two files and the camera id must match in two places. They currently agree. A mismatch would make the Cameras page show the node offline or with zero detections while detection itself still works.
- **R-14 Hard-coded backend address in the health page.** The "FastAPI backend" service row shows the literal text `http://127.0.0.1:8000`.

### 6.4.4 What was not tested

A real phone, real network, real browser, video decoding, the full path from a real vehicle to a real screen, several officers at once, a slow client, several server processes, long-running connections, reconnection after a server restart, and the start-up script's behaviour on another machine.

## 6.5 User Evaluation

None carried out. No officer used the alert channel, and no survey or interview data exist.

## 6.6 Analysis of Results

- **The push channel works as designed.** A matching detection reaches every connected police and admin client, unauthorised connections are refused with the standard policy-violation code, and one dead connection does not block the rest.
- **The weaknesses are mostly about the connection's lifetime.** R-2 (token not rechecked), R-8 (no reconnection) and R-3 (disconnect handling) all concern what happens *after* the connection exists. The design assumes a connection is opened once and stays valid. Real networks and real accounts do not behave that way.
- **The monitoring pages are more reassuring than accurate.** R-4 shows that parts of "system health" are constants. A health page that says "operational" without measuring is worse than none for an operator.
- **The proxy solves the address-hiding problem but not the scaling one** (R-12).
- **The 17 ms figure is not a result about the system.** It only shows that the alert channel itself adds negligible delay compared with the seconds a camera pipeline needs.

## 6.7 Objective-by-Objective Evaluation

| Objective | Evidence | Verdict |
|---|---|---|
| R1 Push detections to connected clients | TC-R1 to TC-R3, TC-R7 | **Achieved** (in process) |
| R2 Restrict to police and admin | TC-R4 to TC-R6 | **Achieved at connect**; a deactivated user still connects (R-2) |
| R3 Camera status and statistics | TC-R11 to TC-R13 | **Achieved**; `last_ping_seconds` missing (R-5) |
| R4 Feed proxy hiding the camera address | TC-R8 to TC-R10 | **Achieved** for the tested case; token in URL (R-7); scaling untested |
| R5 System health endpoint | Endpoint returns metrics | **Partly achieved**: open to the public (R-1) and partly fixed values (R-4) |
| R6 Integration through contracts and start-up script | Contracts in §4.8; script exists and was read; camera ids and addresses agree | **Achieved on the development machine**; the script was not run on another machine and configuration is duplicated (R-13) |
| R7 Verify and record weaknesses | 13 tests, 7 findings from probes, 7 from code reading | **Achieved** for this scope |

## 6.8 Individual Results

All results here concern the real-time and integration component. The backend test suite, the camera node results and the front-end pages are in the other members' reports and are not claimed.

## 6.9 Chapter Summary

The alert channel, feed proxy and status logic pass all 13 in-process tests. Probes and code reading found fourteen weaknesses; the most serious are that the browser never reconnects, that a deactivated user's token still opens the alert channel, and that the health endpoint is public and partly fixed values. None has been fixed in this project.

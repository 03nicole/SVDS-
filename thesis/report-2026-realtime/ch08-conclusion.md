# Chapter 8: Conclusion and Recommendations

## 8.1 Introduction

This chapter summarises the project, states the conclusions the evidence supports, reviews the objectives, and gives recommendations and future work.

## 8.2 Summary of the Project

The group built SVDS so that a stolen-vehicle report filed by the public can be matched against plates seen by a camera. This report covered the real-time and integration component: a WebSocket channel that pushes a detection to every connected police and admin client, an authenticated proxy for the camera's live feed, camera status and system-health endpoints, the browser's alert connection and toast, and the configuration and start-up script that make the three programs work together. It was verified with in-process WebSocket tests, a stand-in camera and failure-mode probes.

## 8.3 Conclusions

1. A plain WebSocket channel using the same token as the REST API delivers detections to all connected officers without polling, and refuses reportees and invalid tokens.
2. A relayed MJPEG feed can hide the camera's address and be limited to police and admin.
3. The three programs integrate through network contracts only.
4. The design has confirmed and likely weaknesses: the browser never reconnects, a deactivated user's token still opens the alert channel, the health endpoint is public and partly made of constants, and several resource and scaling limits are untested.
5. No end-to-end latency and no live `STOLEN` alert were recorded, so the claim that the system alerts officers "in real time" rests on design and in-process tests, not on a measured real-world run.

## 8.4 Achievement of Objectives

| Objective | Status |
|---|---|
| R1 Push detections | Achieved (in process) |
| R2 Restrict to police and admin | Achieved at connect; deactivated users still connect |
| R3 Camera status | Achieved; one field missing |
| R4 Feed proxy | Achieved for the tested case |
| R5 Health endpoint | Partly achieved |
| R6 Integration and start-up | Achieved on the development machine |
| R7 Verification and honest record | Achieved for this scope |

Research questions 1 and 2: yes. Research question 3: fourteen weaknesses recorded.

## 8.5 Recommendations

In priority order:

1. **Reconnect automatically in the browser** with a growing delay, show a visible "alerts disconnected" indicator, re-fetch the unread count and recent alerts on reconnect, and clear the ping timer on close (R-8, R-9).
2. **Recheck the user** when a WebSocket connects and periodically after, and close connections when the token expires or the user is deactivated (R-2).
3. **Require a login (admin) for `/system/health`**, and make each reported value measured: real service checks, real session counts or a renamed label, the actual number of camera nodes (R-1, R-4).
4. **Fix the status field mismatch** by adding a last-seen value to the camera response or changing the page (R-5), and remove the hard-coded address (R-14).
5. **Make `disconnect` safe** if the connection is already gone (R-3).
6. **Move the tokens out of URLs**: send the WebSocket token as the first message, and use a short-lived, single-purpose feed token or a cookie (R-7).
7. **Cache the camera status** for a few seconds instead of connecting on every request (R-6).
8. **Use one configuration source** for the phone address and camera id, or have the node register itself with the backend (R-13).
9. **If more than one server process or many viewers are expected,** use a message broker for alerts and one shared upstream connection for the feed (R-11, R-12).
10. Show more than one notification, with automatic dismissal (R-10).

## 8.6 Future Work

- Record a full live run from a real vehicle to a real dashboard, with timestamps at each step, and report the latency.
- Confirm the browser findings by running the pages, and add browser-level tests.
- Add push notifications outside the browser (for example SMS or a mobile app) for officers away from a screen.
- Support several camera nodes with per-node status.
- Add historical monitoring of the camera and the server.

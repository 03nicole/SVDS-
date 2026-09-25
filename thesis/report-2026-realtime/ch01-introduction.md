# Chapter 1: Introduction

## 1.1 Background and Context

Vehicle theft is a persistent problem for law enforcement in Zambia. Recovering a stolen vehicle depends heavily on chance: an officer happens to recognise a plate number from a paper report or a radio bulletin. Reports are kept on paper or in disconnected spreadsheets, so a report filed at one station is invisible to an officer elsewhere.

This report describes **SVDS**, the Stolen Vehicle Detection System, built by a group of four students on top of the **VRRS** registry. The public files stolen-vehicle reports through a web application. A camera node reads plates from a phone's video stream and asks the backend whether each plate belongs to an active report. When it does, connected police officers must find out *immediately*, whichever page they are looking at.

Getting that information from the moment of detection to an officer's screen, and letting the operators see whether the camera and the system are healthy, is the job of the **real-time and integration** component. It also covers the wiring that lets three separately run programs (backend, front end, camera node) behave as one system. This is the individual report of the student responsible for it.

## 1.2 Problem Statement

A detection is only useful if someone acts on it. If an alert reaches the police dashboard late, or not at all, the vehicle is gone. Three problems follow:

1. **Delivery.** How does a detection made by a camera process reach every logged-in officer within moments, without the officer refreshing a page, and without unauthorised users receiving it?
2. **Visibility.** How do officers and administrators know the camera is working, see what it sees, and know whether the platform itself is healthy?
3. **Integration.** How are a camera process, a web server and a browser application, developed separately, configured and started so that they work together reliably?

## 1.3 Project Aim

**Group aim.** To design, implement and evaluate SVDS: a vehicle registry and reporting web application integrated with a real-time, camera-based licence plate detection pipeline, for the Zambia Police Service and the public it serves.

**Individual aim (Real-time and integration).** To build and evaluate the WebSocket alert channel, the camera status and live-feed services, the system-health endpoint, and the integration between the camera node, backend and front end.

## 1.4 Project Objectives

### Group objectives

1. Role-based accounts (Reportee, Police, Admin) with scoped access.
2. Public filing and tracking of stolen-vehicle reports.
3. A live view of alerts, the registry and analytics for police.
4. Administrator control of accounts, system health and the audit trail.
5. Detection and reading of plates from a live camera feed, matched against active reports.
6. Real-time alerts to connected police clients.

### Individual objectives (Real-time and integration)

| No. | Objective | Measure of success |
|---|---|---|
| R1 | Push a detection to all connected police and admin clients as it happens | A connected client receives a message after `check-plate` matches, without polling |
| R2 | Restrict the alert channel to police and admin | Connections without a valid police or admin token are refused |
| R3 | Report the camera's status and detection statistics | An endpoint returns online or offline and counts for the configured node |
| R4 | Let officers watch the camera feed in the browser without exposing the camera's address | An authenticated proxy streams the feed; unauthorised requests are refused |
| R5 | Provide a system-health endpoint for administrators | Metrics for database, disk, camera and users are returned |
| R6 | Integrate the three processes through documented contracts and a start-up script | One command starts all three; contracts are written down |
| R7 | Verify the real-time path and record its weaknesses honestly | Tests or probes for each objective; findings documented |

## 1.5 Research Questions

1. Can a plain WebSocket channel, authenticated with the same token as the rest of the API, deliver detections to all connected officers with no polling?
2. Can the three processes be integrated using only network contracts, so that none needs the others' code?
3. What breaks, or could break, in this real-time design, and which of those weaknesses can be demonstrated?

(Whether the alert is *faster than the manual process it replaces* is not answered: no manual-process timing was collected, and no latency across a real network and browser was measured.)

## 1.6 Scope of the Project

### 1.6.1 In Scope

- **This report:** the WebSocket manager and endpoint, the `check-plate` broadcast call, camera status, the authenticated live-feed proxy, the system-health endpoint, the front end's alert connection and toast notification, the camera-status and system-health pages' use of these services, `run-all.ps1`, and the configuration that ties the phone's address into the camera node and backend.
- **Group:** the whole system.

### 1.6.2 Out of Scope

- The detection model and camera node (AI/vision member).
- Accounts, roles, reports, matching logic and the database (backend member).
- The visual design of the pages and the analytics charts (frontend member).
- Production hosting, TLS, and running more than one server process.

## 1.7 Significance of the Project

The real-time channel is what turns a passive registry into an alerting system. For the Zambia Police Service it means an officer on any page is told about a sighting as it is recorded. For the group it is the seam where three programs meet, and getting that seam right is what lets each member work independently. The report also documents where the current design would fail an officer, which matters more here than in a normal web page because a silent failure means a missed vehicle.

## 1.8 Limitations

- **No real network or browser measurement.** The real-time tests ran in one process using the framework's test client. The 17 ms figure reported in Chapter 6 excludes the network, the phone, video decoding, detection, OCR and the browser, and must not be read as end-to-end latency.
- **No recorded live `STOLEN` alert.** The recorded live run of the camera node (eight readings) returned `CLEAR` every time, so a real detection travelling all the way to a real dashboard has not been captured.
- **Front-end behaviour is from code reading.** The browser code (reconnection, timers, rendered text) was read, not run in a browser for this report.
- **One camera, one server process.** Nothing was tested with several cameras, several officers at scale, or several server workers.
- **Tests run on SQLite.** As in the backend report.

## 1.9 Organisation of the Report

Chapter 2 reviews WebSockets, streaming and monitoring concepts. Chapter 3 describes the method, tools and ethics. Chapter 4 gives the analysis and design. Chapter 5 describes the implementation and the student's contribution. Chapter 6 presents the tests, probes and objective-by-objective evaluation. Chapter 7 discusses the findings. Chapter 8 concludes. The appendices hold the contribution statement, installation guide, extra diagrams, test output and code.

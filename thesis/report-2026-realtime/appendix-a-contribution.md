# Appendix A: Individual Contribution Statement (Group Projects)

## Purpose of this Statement

This statement identifies the work for which the student was primarily responsible. It is consistent with the main report. Work by other group members is acknowledged and is not claimed.

## A.1 Project and Group Information

| Item | Details |
|---|---|
| Project Title | SVDS: A Camera-Based Stolen Vehicle Detection System for the Zambia Police Service (built on the VRRS registry) |
| Student Name | [STUDENT NAME] |
| Computer Number | [COMPUTER NUMBER] |
| Supervisor | [SUPERVISOR NAME] |
| Group Size | 4 |
| Group Members | 1. Moomba Nicholas Katapazi, [COMPUTER NUMBER] (AI/vision)<br/>2. [NAME], [COMPUTER NUMBER] (Backend and security)<br/>3. [STUDENT NAME], [COMPUTER NUMBER] (Real-time and integration)<br/>4. [NAME], [COMPUTER NUMBER] (Frontend, analytics, testing and documentation) |

## A.2 Overall Group Project

The group built **SVDS/VRRS**, a system with which the public files stolen-vehicle reports and police officers are alerted automatically when a camera sees a reported vehicle. It has three independently running processes: a FastAPI and PostgreSQL backend, a React frontend with three role-based portals (Reportee, Police, Admin), and a camera node that reads number plates from a phone's video stream using a custom-trained YOLOv8 detector and OCR. The common problem is that stolen-vehicle recovery depends on officers chancing to recognise a plate. The core flow is: the camera node reads a plate, the backend matches it against active reports, and connected police dashboards receive an alert over WebSocket.

## A.3 Individual Role and Responsibilities

The group's work was divided into four roles. The student's role was **Role 3: Real-time and integration**.

| No. | Area of Responsibility | Description |
|---|---|---|
| 5 | Real-time alerts and monitoring | WebSocket alerts pushed to police and admin screens; camera status and live-feed proxy; system-health endpoint; the browser's alert connection and toast |
| - | Phone-to-server integration | Contracts and configuration tying phone, camera node, backend and front end together; start-up script; running the live demonstration |

Other roles, for reference: **Role 1** AI/vision; **Role 2** Backend and security; **Role 4** Frontend, analytics, testing and documentation.

## A.4 Detailed Individual Contribution

- **Real-time channel:** wrote the WebSocket connection manager, route and handshake check, and the alert message.
- **Monitoring:** wrote the camera-status, live-feed proxy and system-health endpoints.
- **Browser side:** wired the alert connection, unread count and toast notification into the front end.
- **Integration:** wrote the configuration contract (phone address, camera id, backend address) and `run-all.ps1`.
- **Testing and review:** wrote and ran the in-process WebSocket tests, the stand-in camera tests and the failure-mode probes, and reviewed the browser code, recording fourteen findings.
- **Documentation:** this report.

## A.5 Individual Deliverables

| No. | Deliverable | Student's Contribution |
|---|---|---|
| 1 | WebSocket alert channel (`ConnectionManager`, `/alerts/ws`) | Designed and implemented |
| 2 | Camera status, live-feed proxy and health endpoints (`routers/system.py`) | Designed and implemented |
| 3 | Browser alert connection and toast (`AlertsContext.jsx`, `NotificationToast.jsx`, `createAlertSocket`) | Designed and implemented |
| 4 | Start-up script and configuration contract (`run-all.ps1`, `.env` keys) | Designed and implemented |
| 5 | Failure-mode review and findings R-1 to R-14 | Carried out and documented |

## A.6 Contribution to the Main System or Research Output

The student produced the part that carries a detection from the backend to the officer's screen and lets operators see the camera and system state. The matching logic and the `check-plate` endpoint were built by the backend member, who calls the broadcast written here. The camera node was built by the AI/vision member; the page layouts and analytics by the frontend member. The `/system/audit` listing route sits in the same file as the monitoring routes; the records it lists were designed by the backend member.

## A.7 Individual Implementation and Technical Work

Modules implemented by the student: the `ConnectionManager` and `/alerts/ws` route in `routers/alerts.py`; the `camera-nodes`, `live-feed` and `health` routes and `is_camera_online` in `routers/system.py`; `AlertsContext.jsx`, `NotificationToast.jsx` and `createAlertSocket` in the front end; `run-all.ps1`.

## A.8 Individual Testing and Evaluation Contribution

The student wrote and ran the temporary tests and probes described in Chapter 6 and interpreted their results. The 31-test backend suite includes alert tests, and **who wrote each of those test files should be confirmed by the student**; the report does not claim them.

## A.9 Collaboration with Other Group Members

- The **AI/vision member's** camera node sends readings to `check-plate`; the camera id it sends must equal the backend's `CAMERA_NODE_ID`, and both share the phone stream address.
- The **backend member's** token functions and `check-plate` endpoint are reused and called.
- The **frontend member's** pages display the alerts, camera and health data, and use the message shape defined here.

## A.10 Contribution Summary

1. **Work primarily completed by the student:** the WebSocket channel, camera status, feed proxy, health endpoint, browser alert connection and toast, start-up script and configuration contract.
2. **Work completed jointly with other members:** the alert message shape (with the frontend member); the camera-node contract (with the AI/vision and backend members).
3. **Work primarily completed by other members and used here:** token handling and `check-plate` matching; the detection model and camera node; page layouts and analytics.

## A.11 Estimated Contribution

*The percentages below are the student's own estimate and must be completed by the student. They were not derived from any record.*

| Project Activity | Individual Contribution | Collaborative Contribution |
|---|---|---|
| Problem Analysis | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Literature Review | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Requirements Analysis | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| System/Research Design | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Implementation / Development | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Testing and Evaluation | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Documentation | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Other | <span class="todo">[%]</span> | <span class="todo">[%]</span> |

## A.12 Statement of Authorship and Contribution

I confirm that the contribution described in this statement accurately represents the work that I personally undertook as part of the group project. I have identified collaborative work and have not knowingly claimed the work of another group member as my own.

**Student Name:** ______________________
**Computer Number:** ______________________
**Signature:** ______________________
**Date:** ______________________

## A.13 Supervisor Verification

I confirm that, to the best of my knowledge, the contribution described above is consistent with the student's participation in the group project.

**Supervisor Name:** ______________________
**Signature:** ______________________
**Date:** ______________________

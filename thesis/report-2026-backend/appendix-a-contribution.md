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
| Group Members | 1. Moomba Nicholas Katapazi, [COMPUTER NUMBER] (AI/vision)<br/>2. [STUDENT NAME], [COMPUTER NUMBER] (Backend and security)<br/>3. [NAME], [COMPUTER NUMBER] (Real-time and integration)<br/>4. [NAME], [COMPUTER NUMBER] (Frontend, analytics, testing and documentation) |

## A.2 Overall Group Project

The group built **SVDS/VRRS**, a system with which the public files stolen-vehicle reports and police officers are alerted automatically when a camera sees a reported vehicle. It has three independently running processes: a FastAPI and PostgreSQL backend, a React frontend with three role-based portals (Reportee, Police, Admin), and a camera node that reads number plates from a phone's video stream using a custom-trained YOLOv8 detector and OCR. The common problem is that stolen-vehicle recovery depends on officers chancing to recognise a plate. The system's core flow is: camera node reads a plate, the backend matches it against active reports, and connected police dashboards receive an alert over WebSocket.

## A.3 Individual Role and Responsibilities

The group's work was divided into four roles. The student's role was **Role 2: Backend and security**, which covers work areas 3 (backend API and database) and 4 (security and access control).

| No. | Area of Responsibility | Description |
|---|---|---|
| 3 | Backend API and database | FastAPI service and PostgreSQL schema; report CRUD and lifecycle; the `/alerts/check-plate` matching endpoint |
| 4 | Security and access control | JWT login, bcrypt password hashing, Reportee/Police/Admin roles and middleware, user management, audit records |

Other roles, for reference: **Role 1** the plate-detection model and camera node; **Role 3** WebSocket alerts, camera status and live-feed proxy, system health, and the phone-to-server wiring; **Role 4** the React portals, analytics, integration tests, run scripts and documentation.

## A.4 Detailed Individual Contribution

- **Data design:** designed the four-table schema (users, reports, alerts, audit log), keys, unique email and the cascade from reports to alerts.
- **Software development:** wrote the FastAPI application structure, database session handling, ORM models and Pydantic schemas with telephone and national ID formats.
- **Security:** implemented bcrypt password storage, JWT issue and checking, and the `require_role` dependencies; implemented ownership rules on reports and the admin safeguards on user management.
- **Business logic:** implemented the report lifecycle (`under_review` to `missing` to `found`), the duplicate-active-report rule, and the plate-match endpoint with case and spacing normalisation.
- **Auditing:** added audit records to state-changing actions.
- **Defect fixing:** fixed the report-delete cascade defect.
- **Testing and security review:** ran the 31-test suite, wrote and ran the security probes, and recorded ten findings with recommendations.
- **Documentation:** this report, including the API and role tables.

## A.5 Individual Deliverables

| No. | Deliverable | Student's Contribution |
|---|---|---|
| 1 | Database schema and ORM models (`models.py`, `database.py`) | Designed and implemented |
| 2 | Authentication and access control (`auth.py`, `middleware.py`, `routers/auth.py`, `routers/users.py`) | Designed and implemented |
| 3 | Report lifecycle and plate-match endpoint (`routers/reports.py`, `check-plate` in `routers/alerts.py`) | Designed and implemented |
| 4 | Request and response schemas (`schemas.py`) | Designed and implemented |
| 5 | Security review: probe results and findings F-1 to F-10 | Carried out and documented |

## A.6 Contribution to the Main System or Research Output

The student produced the server that stores and protects the system's data and answers the camera's question "is this plate stolen?". The camera node itself was built by the AI/vision member; the WebSocket delivery, camera status and live-feed proxy by the real-time and integration member; the web pages and analytics by the frontend member. The `check-plate` request and response format was agreed with the AI/vision member. The WebSocket manager lives in the same file as `check-plate` (`routers/alerts.py`) and was written by the real-time member.

## A.7 Individual Implementation and Technical Work

Modules implemented by the student: `main.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`, `middleware.py`, `routers/auth.py`, `routers/users.py`, `routers/reports.py`, and the `check-plate` and alert-listing routes in `routers/alerts.py`. Databases and integrations: PostgreSQL schema, the camera-node contract, and the hook that calls the real-time broadcast.

## A.8 Individual Testing and Evaluation Contribution

The student ran the 31-test backend suite, wrote and ran the security probe tests, interpreted the results, and wrote Chapters 6 and 7. **Authorship of each file in `vrrs-backend/tests/` should be confirmed by the student**: the group's role split placed "tests" with the frontend member, so this report does not claim the suite as the student's own work. The camera-node tests and the manual browser checks belong to other members.

## A.9 Collaboration with Other Group Members

- The **AI/vision member's** camera node calls `POST /alerts/check-plate`; its request and response format was agreed jointly.
- The **real-time and integration member's** WebSocket manager is called by `check-plate` and reuses `decode_token`; the WebSocket admits only police and admin tokens.
- The **frontend member's** pages call every route in Chapter 4 and depend on the role and redirect returned at login.

## A.10 Contribution Summary

1. **Work primarily completed by the student:** the data model, authentication and access control, the report lifecycle, the plate-match endpoint, audit records and the security review.
2. **Work completed jointly with other members:** the camera-node contract; the alert broadcast hook; start-up through `run-all.ps1`.
3. **Work primarily completed by other members and used here:** the detection model and camera node; the WebSocket delivery, camera status and health endpoints; the web portals and analytics.

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

**Student Name:** [STUDENT NAME]
**Computer Number:** ______________________
**Signature:** ______________________
**Date:** ______________________

## A.13 Supervisor Verification

I confirm that, to the best of my knowledge, the contribution described above is consistent with the student's participation in the group project.

**Supervisor Name:** ______________________
**Signature:** ______________________
**Date:** ______________________

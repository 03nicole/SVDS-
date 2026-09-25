# Chapter 1: Introduction

## 1.1 Background and Context

Vehicle theft is a persistent problem for law enforcement in Zambia. Recovering a stolen vehicle depends heavily on chance: an officer at a checkpoint or on patrol happens to recognise a plate number from a paper report or a radio bulletin. Vehicle records, incident reports and eyewitness descriptions are typically kept on paper or in disconnected station-level spreadsheets, so a report filed at one police station is invisible to an officer elsewhere.

This report describes **SVDS**, the Stolen Vehicle Detection System, built by a group of four students on top of the **VRRS** (Vehicle Registry and Reporting System). Members of the public file stolen-vehicle reports through a web application. A camera node reads number plates from a phone's video stream and asks the server whether each plate belongs to an active report. Police officers are alerted when it does.

Every part of that flow depends on one server-side component: the **backend**. It stores the reports and accounts, decides who may see and change what, and answers the camera's question "is this plate stolen?". This report is the individual report of the student responsible for that component and for **security and access control**.

## 1.2 Problem Statement

Stolen-vehicle information in Zambia is fragmented and slow to reach the people who could act on it. A system that lets the public report a theft and lets cameras check plates against those reports needs a central service that:

1. keeps one authoritative record of reports, users and detections;
2. is trustworthy about *who* is asking, so that public users, officers and administrators each see only what their role permits; and
3. keeps a record of who did what, so that decisions about a report can be traced.

Without these, a reporting system either leaks sensitive vehicle and personal data, or lets the wrong person activate, alter or delete a report. The specific problem addressed here is **designing and building a database-backed API that stores reports securely, enforces role-based access on the server, and answers plate-match queries from the camera node**.

## 1.3 Project Aim

**Group aim.** To design, implement and evaluate SVDS: a vehicle registry and reporting web application integrated with a real-time, camera-based licence plate detection pipeline, for the Zambia Police Service and the public it serves.

**Individual aim (Backend and security).** To build and evaluate the backend API, its PostgreSQL data model, and its authentication and access-control layer.

## 1.4 Project Objectives

### Group objectives

1. Role-based accounts (Reportee, Police, Admin) with scoped access.
2. Public filing and tracking of stolen-vehicle reports (`under_review` → `missing` → `found`).
3. A live view of alerts, the registry and analytics for police.
4. Administrator control of accounts, system health and the audit trail.
5. Detection and reading of plates from a live camera feed, matched against active reports.
6. Real-time alerts to connected police clients.

### Individual objectives (Backend and security)

| No. | Objective | Measure of success |
|---|---|---|
| B1 | Design and implement the relational data model (users, reports, alerts, audit log) | Four tables with keys and constraints created from the ORM models |
| B2 | Implement registration, login and password storage without plaintext passwords | Passwords stored as bcrypt hashes; login issues a signed, expiring JWT |
| B3 | Enforce three-role access control on the server for every route | A test matrix shows each role reaching only its permitted routes |
| B4 | Implement the report lifecycle with validation and ownership rules | Reportees see only their own reports; only police can activate or resolve; only admins can delete |
| B5 | Implement the plate-match endpoint used by the camera node | Tolerates case and spacing differences; matches only active reports; records an alert |
| B6 | Write an audit record for state-changing actions | Each such action produces a row naming the actor and target |
| B7 | Verify the above with automated tests and a security review | All backend tests pass; weaknesses found are recorded honestly |

## 1.5 Research Questions

1. Can role-based access control be enforced consistently on the server, using a signed token that carries the user's role, so that no route depends on the front end to hide it?
2. What security weaknesses remain in such a design once it works, and which of them can be demonstrated rather than merely suspected?

## 1.6 Scope of the Project

### 1.6.1 In Scope

- **This report:** the FastAPI application structure, the SQLAlchemy models and PostgreSQL schema, the schemas that validate input and output, registration and login, password hashing, JWT creation and checking, the role-checking dependencies, user management, the report lifecycle endpoints, the `check-plate` endpoint, audit logging, and the tests of these.
- **Group:** the whole system, including the components in Chapter 5's table that belong to other members.

### 1.6.2 Out of Scope

- The detection model and camera node (AI/vision member).
- The WebSocket broadcast, camera status and live-feed proxy, and system health (real-time and integration member). The `check-plate` endpoint *calls* the broadcast but does not implement it.
- The React portals and analytics charts (frontend member).
- Production hosting, TLS termination, backups and database migrations.

## 1.7 Significance of the Project

The backend is what makes SVDS safe to use. The Zambia Police Service gains a single record of reports that officers in any station can search, with each action traceable to an account. The public gain a way to file a report and follow its status without being able to see anyone else's. The project also documents, honestly, where a small role-based API of this kind is weak, which is useful to anyone extending it.

## 1.8 Limitations

- Security testing was limited to automated tests and targeted probes run against an in-memory test database. No penetration test, load test or external review was carried out.
- The tests run on SQLite, not on the PostgreSQL database used in practice. One PostgreSQL-specific function is emulated in the test set-up (§6.2).
- No formal stakeholder interviews are recorded, so requirements are the group's own analysis.
- Several weaknesses found (§6.4) were **documented, not fixed**, within the project's time.

## 1.9 Organisation of the Report

Chapter 2 reviews the concepts (REST, JWT, bcrypt, RBAC) and related practice. Chapter 3 describes the method, tools, ethics and evaluation. Chapter 4 gives the analysis and design of the backend. Chapter 5 describes the implementation and the student's contribution. Chapter 6 presents the tests, the security probes and an objective-by-objective evaluation. Chapter 7 discusses the findings. Chapter 8 concludes. The appendices contain the Individual Contribution Statement, installation guide, extra diagrams, test output and code.

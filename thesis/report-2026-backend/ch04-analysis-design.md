# Chapter 4: System Analysis and Design

## 4.1 Introduction

This chapter presents the analysis and design of the backend. Stakeholders and the architecture are shared by the group; the requirements, data design, API design and security design are those of the **backend and security component**, the subject of this report.

## 4.2 Stakeholder and User Analysis

| Stakeholder | Interest | Needs from the backend |
|---|---|---|
| Reportee (public) | Report a theft, follow its status | Register and log in; file and view **only their own** reports; edit own profile |
| Police officer | Investigate, activate and resolve reports, act on alerts | See all reports; activate and mark found; view and flag alerts; view analytics |
| Administrator | Manage accounts and oversee the system | Create police accounts, change roles, deactivate or delete users, delete reports, read the audit log |
| Camera node | Ask whether a plate is stolen | One public endpoint that answers `CLEAR` or `STOLEN` |
| Front-end and real-time developers | Build on the API | A stable, documented API; a broadcast hook for alerts |

## 4.3 Functional Requirements

| ID | Requirement |
|---|---|
| FR-B1 | Public registration creates reportee accounts only; police and admin accounts are created by an administrator. |
| FR-B2 | Login with email and password returns a signed token, the role and a redirect path; deactivated accounts cannot log in. |
| FR-B3 | Passwords are stored only as bcrypt hashes; a password must be at least 6 characters. |
| FR-B4 | Every protected route requires a valid token; role rules are checked on the server. |
| FR-B5 | A reportee can file a report; a new report starts as `under_review`. An active (`missing`) report for the same plate blocks a new one. |
| FR-B6 | A reportee can list and read only their own reports; police and admin can list and read all, with search and status filters and paging. |
| FR-B7 | Police can activate a report (`under_review` → `missing`) and mark it found (recording who and when). Police can edit report details. |
| FR-B8 | Only an administrator can delete a report, and deleting it also deletes its alerts. |
| FR-B9 | An administrator can create police accounts, change a user's role, deactivate or reactivate a user, and delete a user. An administrator cannot change, deactivate or delete their own account. |
| FR-B10 | `POST /alerts/check-plate` normalises the plate, matches only `missing` reports, records an alert and triggers the real-time broadcast on a match. |
| FR-B11 | Police can list alerts, mark them read, and flag false positives. |
| FR-B12 | State-changing actions write an audit record naming the actor, action and target. |
| FR-B13 | Users can view and edit their own profile and change their password (the current password must be supplied). |

## 4.4 Non-Functional Requirements

- **Security:** no plaintext passwords; signed, expiring tokens; server-side role checks; responses limited to the fields a client needs (`UserOut` excludes the password hash, national ID and badge number).
- **Validation:** telephone numbers must match `+260 XX XXXXXXX`, national IDs `NNNNNN/NN/N`, enforced by Pydantic patterns at registration.
- **Consistency:** database constraints back the business rules (unique email, foreign keys, cascade delete of alerts).
- **Maintainability:** access rules are expressed once, as reusable dependencies (`is_reportee`, `is_police`, `is_admin`), not repeated in each route.
- **Testability:** the database session is injected so tests can swap in an in-memory database.
- **Performance:** list endpoints are paged (default 20 reports, 30 users and alerts; maximum 100).

## 4.5 Use Cases / User Stories

**UC-B1: Register and log in.** A member of the public registers with name, email, telephone, national ID and password, and receives a token and a redirect to `/my`. On later visits they log in with email and password.
*Alternate flows:* duplicate email (409); role other than reportee requested (400); password too short (400); wrong credentials (401); deactivated account (403).

**UC-B2: File a report.** A logged-in reportee submits plate and vehicle details. The server upper-cases the plate, refuses it if an active report for that plate exists (409), stores it as `under_review`, and writes an audit record.

**UC-B3: Police activate and resolve a report.** An officer activates an `under_review` report so it becomes matchable, and later marks it found.

**UC-B4: Camera checks a plate.** The node sends a plate; the server returns `CLEAR`, or creates an alert and returns `STOLEN` with the vehicle's make, model and colour.

**UC-B5: Administrator manages accounts.** The administrator invites an officer, changes a role (a badge number is required for police or admin), or deactivates an account.

**User story.** *As a member of the public, I want to see only my own reports, so that other people's theft reports and personal details stay private.*

## 4.6 System / Solution Architecture

![Figure 4.1: detection-to-alert sequence, which the backend's check-plate endpoint serves](../assets/diagrams/04-system-design-4.png)

The backend is a single FastAPI application. `main.py` registers six routers (`auth`, `reports`, `alerts`, `users`, `analytics`, `system`) and the CORS middleware. Shared modules provide the database session (`database.py`), the ORM models (`models.py`), the validation schemas (`schemas.py`), password and token functions (`auth.py`), and the access-control dependencies (`middleware.py`).

```
vrrs-backend/app/
  main.py        app, CORS, router registration, create_all()
  database.py    engine, session, get_db
  models.py      User, Report, Alert, AuditLog
  schemas.py     Pydantic request/response models
  auth.py        bcrypt + JWT
  middleware.py  get_current_user, require_role, is_reportee/is_police/is_admin
  routers/       auth, reports, alerts, users, analytics, system
```

## 4.7 Database / Data Design

Four tables, defined once in `models.py`.

![Figure 4.2: entity-relationship diagram](../assets/diagrams/04-system-design-2.png)

| Table | Purpose | Key constraints |
|---|---|---|
| `users` | Accounts | Primary key `id`; unique, indexed `email`; `role` string (`reportee`, `police`, `admin`); `is_active` flag; `password_hash` |
| `reports` | Stolen-vehicle reports | Foreign key `reported_by` → `users`; `resolved_by` → `users`; indexed `license_plate`; `status` string |
| `alerts` | Detections | Foreign key `report_id` → `reports` with `ON DELETE CASCADE` |
| `audit_log` | Action trail | Foreign key `performed_by` → `users` (nullable) |

Design decisions:
- **`alerts.license_plate` is not stored.** It is a computed property reading through the linked report, avoiding duplicated data.
- **Cascade delete.** Deleting a report also deletes its alerts (the ORM relationship uses `cascade="all, delete-orphan"`, and the database constraint uses `ON DELETE CASCADE`).
- **Roles and statuses are plain strings**, not database enumerations or check constraints. This is simple, but the database itself does not stop an invalid value (§6.4).
- **No migration tool.** `Base.metadata.create_all()` runs at start-up. It creates missing tables but never changes existing ones, so a constraint change on an existing table needs a manual `ALTER TABLE`.

## 4.8 Interface / Interaction Design

The backend's interface is its HTTP API, documented automatically at `/docs`. Access is by role (`✔` allowed):

| Route group | Endpoint(s) | Reportee | Police | Admin |
|---|---|---|---|---|
| Auth | `POST /auth/register`, `/auth/login`, `/auth/logout` | public | public | public |
| Reports | `POST /reports/`, `GET /reports/`, `GET /reports/{id}` | ✔ (own only for reads) | ✔ all | ✔ all |
| Reports | `PATCH /reports/{id}`, `/activate`, `/found` | | ✔ | ✔ |
| Reports | `DELETE /reports/{id}` | | | ✔ |
| Alerts | `POST /alerts/check-plate` | public | public | public |
| Alerts | `GET /alerts/`, `/{id}`, `/unread/count`, `PATCH .../read`, `/read-all`, `/false-positive` | | ✔ | ✔ |
| Users | `GET/PATCH /users/me`, `PATCH /users/me/password` | ✔ | ✔ | ✔ |
| Users | `GET /users/`, `GET /users/{id}` | | ✔ | ✔ |
| Users | `POST /users/invite`, `PATCH /users/{id}/role`, `/toggle-active`, `DELETE /users/{id}` | | | ✔ |
| Analytics | `GET /analytics/...` | | ✔ | ✔ (`user-growth` admin only) |
| System | `GET /system/audit` | | | ✔ |

The web pages that use these routes were designed by the frontend member.

## 4.9 Algorithms / Models / Technical Design

### 4.9.1 Authentication and token design

![Figure 4.3: authentication sequence](../assets/diagrams/04-system-design-3.png)

On login the server looks up the user by lower-cased email, verifies the password against the stored bcrypt hash, rejects deactivated accounts, writes an audit record, and returns a JWT whose claims are `sub` (user id), `role` and `exp` (default 24 hours, configurable). The token is signed with HS256 using `SECRET_KEY` from the environment. On each request, `get_current_user` decodes the token and returns the user id and role **taken from the token**.

### 4.9.2 Role enforcement

`require_role(*roles)` builds a dependency that returns `403` if the token's role is not in the list. Three shortcuts wrap it: `is_reportee` (all three roles), `is_police` (police and admin), `is_admin` (admin only). Routes attach them with `Depends(...)`. Row-level rules are added inside the route: a reportee's list is filtered by `reported_by`, and reading another reportee's report returns 403.

![Figure 4.4: role-based route access](../assets/diagrams/04-system-design-5.png)

### 4.9.3 Plate matching

`check-plate` removes every character except letters and digits from the received plate, upper-cases it, and compares it with the same normalisation applied to the stored plate in SQL (`regexp_replace(upper(license_plate), '[^A-Z0-9]', '', 'g')`). It matches only reports whose status is `missing`. This makes `abc 1234`, `ABC-1234` and `ABC1234` equal. On a match it inserts an alert, calls the WebSocket broadcast (the real-time member's component) and returns `STOLEN` with make, model and colour.

### 4.9.4 Report lifecycle

```
under_review --(police: activate)--> missing --(police: mark found)--> found
```

Only `missing` reports are matched. `activate` accepts only `under_review`; `found` refuses a report that is already found. The general `PATCH /reports/{id}` route is separate and is discussed in §6.4.

## 4.10 Chapter Summary

The backend is a FastAPI service over four PostgreSQL tables. Access control is expressed as three reusable role dependencies plus per-row ownership rules. Authentication uses bcrypt and a signed JWT that carries the role. The plate-match endpoint normalises both sides so formatting differences do not prevent a match.

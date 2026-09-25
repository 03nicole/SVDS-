# Chapter 5: Implementation / Development

## 5.1 Introduction

This chapter describes how the backend was built: its modules, the key implementation decisions, how it connects to the other components, the problems met, and the student's own contribution.

## 5.2 Development Environment

| Item | Detail |
|---|---|
| Machine | Windows 11 PC |
| Language and runtime | Python (the test virtual environment used Python 3.12.10) |
| Database | PostgreSQL (`vrrs_db`), connection string from `DATABASE_URL` |
| Frameworks | FastAPI 0.111.0, SQLAlchemy 2.0.30, Pydantic 2.7.1 |
| Security libraries | passlib 1.7.4 + bcrypt 4.1.3, python-jose 3.3.0 |
| Tools | Swagger UI at `/docs` for manual trials, pytest for automated tests, Git |
| Configuration | `.env` (not committed); `.env.example` lists `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `TOKEN_EXPIRY_HOURS`, `CORS_ORIGINS` |

## 5.3 System Components / Modules

| Module | Lines | Purpose | Built by |
|---|---|---|---|
| `app/main.py` | 55 | App creation, CORS, router registration, schema creation | Backend (this report) |
| `app/database.py` | 20 | Engine, session factory, `get_db` dependency | Backend (this report) |
| `app/models.py` | 65 | `User`, `Report`, `Alert`, `AuditLog` ORM models | Backend (this report) |
| `app/schemas.py` | 132 | Pydantic request and response models with validation patterns | Backend (this report) |
| `app/auth.py` | 33 | bcrypt hashing; JWT create and decode | Backend (this report) |
| `app/middleware.py` | 34 | `get_current_user`, `require_role`, role shortcuts | Backend (this report) |
| `app/routers/auth.py` | 48 | Register, login, logout | Backend (this report) |
| `app/routers/users.py` | 125 | Profile, password change, admin user management | Backend (this report) |
| `app/routers/reports.py` | 94 | Report create, list, read, update, activate, found, delete | Backend (this report) |
| `app/routers/alerts.py` | 123 | `check-plate` and alert listing (this report); WebSocket manager and endpoint (real-time member) | Shared |
| `app/routers/analytics.py`, `system.py` | 87, 146 | Statistics; audit-log listing, camera status, feed proxy, health | Frontend and real-time members |
| `tests/` | 5 test files and `conftest.py` | Automated tests | See §5.7 |

Line counts are from the files as they stand.

## 5.4 Key Implementation Details

### 5.4.1 Password hashing and tokens (`auth.py`)

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)

def create_access_token(user_id, role):
    payload = {"sub": str(user_id), "role": role,
               "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

`decode_token` returns `None` on any signature or expiry error. The signing key is read from the environment. The code falls back to the string `"changeme"` if `SECRET_KEY` is unset; on the development machine the key is set and is not the default (checked, §6.4).

### 5.4.2 Access control (`middleware.py`)

```python
def require_role(*roles):
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail=f"Access denied. Required roles: {list(roles)}")
        return user
    return checker

is_reportee = require_role("reportee", "police", "admin")
is_police   = require_role("police", "admin")
is_admin    = require_role("admin")
```

(In the source these are small wrapper functions; they are shown here in condensed form.) A route needs one line to require a role, for example `user=Depends(is_admin)`.

### 5.4.3 Ownership and lifecycle rules (`reports.py`)

- `create_report` upper-cases and trims the plate, returns 409 if a `missing` report with that plate exists, saves the report as `under_review`, and writes an audit row.
- `get_reports` filters by `reported_by` when the caller is a reportee, and supports `status`, `search` (plate or owner name, case-insensitive), `skip` and `limit`.
- `get_report` returns 403 if a reportee asks for someone else's report.
- `activate_report` accepts only `under_review`; `mark_found` records `resolved_by` and `resolved_date`.
- `delete_report` is admin-only and relies on the cascade to remove alerts.

### 5.4.4 Plate matching (`alerts.py`)

```python
normalized = re.sub(r"[^A-Z0-9]", "", data.license_plate.upper())
report = db.query(Report).filter(
    func.regexp_replace(func.upper(Report.license_plate), r"[^A-Z0-9]", "", "g") == normalized,
    Report.status == "missing",
).first()
if not report:
    return {"status": "CLEAR"}
new_alert = Alert(report_id=report.id, ...)
db.add(new_alert); db.commit()
await manager.broadcast({... "type": "STOLEN_DETECTED" ...})
return {"status": "STOLEN", "alert_id": new_alert.id, "vehicle": {...}}
```

### 5.4.5 Admin safeguards (`users.py`)

An administrator cannot change, deactivate or delete their own account (prevents locking out the last admin by accident). Assigning `police` or `admin` requires the target user to have a badge number. Password change requires the current password and rejects an unchanged or too-short new password. `UserUpdate`, the model used for profile edits, has no `role` or `is_active` field, so a user cannot promote themselves through their profile.

### 5.4.6 Audit records

Registration, login, report filing, updates, activation, found, deletion, account creation, role change, activation or deactivation of an account, password change, profile update and false-positive flags each add an `AuditLog` row with the actor's id, a text description, the target table and the target id.

## 5.5 Integration

- **Camera node (AI/vision member):** the only contract is `POST /alerts/check-plate` with `license_plate`, `camera_id`, `confidence_score`, `location_spotted` and optional `image_path`. The backend normalises the plate itself, so the node does not need to reproduce the matching rules.
- **Real-time member:** `check-plate` calls the `ConnectionManager.broadcast` method they wrote; the WebSocket handshake reuses `decode_token` and admits only police and admin tokens.
- **Frontend member:** the front end calls the routes in §4.8 with the token in an `Authorization: Bearer` header and reads the role from the login response. CORS is limited to the local development origins `localhost:5173` and `5174` (and `127.0.0.1` equivalents).

Note: `main.py` builds the CORS list from four hard-coded origins. `CORS_ORIGINS` appears in `.env.example` but is not read by the application code, so changing it has no effect (checked by searching the source).

## 5.6 Challenges and Solutions

| Challenge | Cause | Solution |
|---|---|---|
| Deleting a report that had detections failed with a database error | The `alerts.report_id` foreign key was created with no delete action | Added `ondelete="CASCADE"` to the foreign key and `cascade="all, delete-orphan"` to the relationship. Because `create_all()` does not alter existing tables, the live constraint was also altered by hand and the change verified in PostgreSQL's constraint catalogue. Covered by a regression test |
| A PostgreSQL-only function in `check-plate` could not run under the test database | SQLite has no four-argument `regexp_replace` | The test set-up registers a Python implementation on each SQLite connection, so the production query runs unchanged in tests |
| Cascade delete did not fire in tests | SQLite ignores foreign keys unless enabled | The test set-up runs `PRAGMA foreign_keys=ON` per connection |
| Tests must not touch the real database | `database.py` connects to PostgreSQL at import | The tests override the `get_db` dependency with an in-memory SQLite session using a static pool |
| Camera cannot log in | It has no user identity | `check-plate` is left public and limited in what it can do (it cannot create or alter reports); see §6.4 for the consequence |
| Roles enforced only in the UI would be bypassable | Clients can send any request | Every route declares its role dependency; a parametrised test hits police and admin routes as a reportee |

## 5.7 Individual Contribution (group project)

The student was responsible for **work areas 3 and 4** of the group's seven (Appendix A): the backend API and database, and security and access control. This covers:

- the four-table data model and its relationships, keys and cascade;
- the FastAPI application structure and configuration;
- registration, login, password hashing and token issue and checking;
- the role dependencies and the ownership rules on reports;
- user management, including the admin safeguards;
- the report lifecycle endpoints and the plate-match endpoint;
- writing of audit records;
- the security review in Chapter 6.

Work by other members that this component uses, **not claimed here**: the WebSocket manager and endpoint, camera status, live-feed proxy and system health (real-time and integration member); analytics endpoints and the React pages (frontend member); the detection model and camera node (AI/vision member).

*Tests.* The group's role split placed "tests" with the frontend member. The 31 backend tests exercise this component, and the student ran them and interpreted their results for this report. **Who wrote each test file should be confirmed by the student before submission**; §6.3 describes them without claiming authorship.

## 5.8 Chapter Summary

The backend is about 730 lines of Python across ten modules (`main.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`, `middleware.py` and four routers; the generic `model.py` placeholder is not counted). It hashes passwords with bcrypt, issues signed role-carrying tokens, enforces roles with reusable dependencies, and answers plate-match queries. Its notable implementation problems were the missing cascade and the gap between PostgreSQL and the SQLite test database.

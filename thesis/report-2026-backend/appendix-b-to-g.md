# Appendix B: User Manual / Installation Guide

This guide covers the backend. The camera node and front end are documented in the other members' reports and the project `README.md`.

## B.1 Requirements

- Python 3.12 or later, and PostgreSQL with an empty database (for example `vrrs_db`).
- The packages in `vrrs-backend/requirements.txt`.

## B.2 Install and configure

```bash
cd vrrs-backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

| Key | Meaning | Note |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | e.g. `postgresql://postgres:<password>@localhost:5432/vrrs_db` |
| `SECRET_KEY` | Token signing key | **Must be a long random value.** The code falls back to `changeme` if it is missing (finding F-8) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `TOKEN_EXPIRY_HOURS` | Token lifetime | 24 by default |
| `CORS_ORIGINS` | Listed in the template but **not read by the code**; allowed origins are hard-coded in `main.py` (finding F-9) | |

## B.3 Run

```bash
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive documentation is at `/docs`. Tables are created automatically at start-up if they do not exist.

Public registration creates reportees only, so the first administrator is created with the helper script `create_admin.py`:

```bash
set ADMIN_EMAIL=admin@example.local
set ADMIN_PASSWORD=<choose a strong password>
python create_admin.py
```

**Always set `ADMIN_PASSWORD` yourself.** If it is unset the script uses a default password that is written in its source (finding F-10). The script also defaults to a local SQLite file when `DATABASE_URL` is not set, so set that too. Later role changes are made by an administrator, and a promoted account must have a badge number.

## B.4 Roles at a glance

| Role | Can do |
|---|---|
| Reportee | Register, log in, file reports, see own reports, edit own profile |
| Police | Everything a reportee can, plus see all reports and users, activate and mark reports found, edit reports, view and flag alerts, view analytics |
| Admin | Everything police can, plus create police accounts, change roles, deactivate or delete users, delete reports, read the audit log |

## B.5 Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `401 Invalid or expired token` | Missing, expired or wrongly signed token | Log in again; check `SECRET_KEY` has not changed since the token was issued |
| `403 Access denied` | Role too low for the route | Use an account with the required role |
| `409` when filing a report | A `missing` report for that plate exists | Check the existing report |
| Start-up prints "error creating DB schema" | Cannot reach PostgreSQL | Check `DATABASE_URL` and that PostgreSQL is running |
| Frontend blocked by CORS | Its origin is not in the hard-coded list | Add the origin in `main.py` |
| Deleting a report fails on an older database | The cascade constraint was created before the fix | Alter the `alerts.report_id` foreign key to `ON DELETE CASCADE` by hand |

## B.6 Run the tests

```bash
cd vrrs-backend
python -m pytest tests/ -v
```

The tests use an in-memory SQLite database and do not touch PostgreSQL.

---

# Appendix C: Additional System Designs / Diagrams

## C.1 Authentication sequence

![Figure C.1: authentication sequence](../assets/diagrams/04-system-design-3.png)

## C.2 Role-based route access

![Figure C.2: role-based route access](../assets/diagrams/04-system-design-5.png)

## C.3 Database schema

![Figure C.3: entity-relationship diagram](../assets/diagrams/04-system-design-2.png)

## C.4 Detection-to-alert sequence

![Figure C.4: detection-to-alert sequence](../assets/diagrams/04-system-design-4.png)

---

# Appendix D: Additional Test Cases and Results

## D.1 Raw test output

The full captured output of the 31 passing tests is in `thesis/assets/test-results/backend-pytest-output.txt`. The suite was re-run while preparing this report and again passed (31 passed).

## D.2 Probe results (raw)

The probe tests were temporary and were deleted after running; their printed output is reproduced below.

```
PROBE deactivated-user token /users/me            -> 200
PROBE demoted-admin old token /system/audit       -> 200
PROBE PATCH status=banana                         -> 200 banana
PROBE check-plate no-auth x3                      -> ['STOLEN','STOLEN','STOLEN']  alerts rows: 3
PROBE 20 wrong logins status set                  -> {401}
PROBE register password 'abcdef'                  -> 422   (invalid probe: payload incomplete)
PROBE default-key forged token accepted           -> False
PROBE SECRET_KEY equals 'changeme'                -> False | length 47
PROBE token after /auth/logout                    -> 200
```

## D.3 One probe as an example

```python
def test_probe_deactivated_token_still_works(client, make_user, auth_headers, db_session):
    u = make_user(role="reportee"); h = auth_headers(u)
    u.is_active = False; db_session.commit()
    print(client.get("/users/me", headers=h).status_code)          # observed: 200
    assert client.post("/auth/login",
        json={"email": u.email, "password": "Password123"}).status_code == 403
```

---

# Appendix E: Data Collection Instruments

Not applicable. No questionnaires, interviews or surveys were used.

---

# Appendix F: Additional Code / Configuration

## F.1 Role dependencies (`app/middleware.py`)

```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.",
                            headers={"WWW-Authenticate": "Bearer"})
    return {"id": int(payload["sub"]), "role": payload["role"]}

def require_role(*roles):
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403,
                detail=f"Access denied. Required roles: {list(roles)}")
        return user
    return checker
```

## F.2 Where finding F-1 and F-2 come from

`get_current_user` returns the role from the token and never reads the database, so a changed role or a deactivated account is not seen until the token expires. A fix would look up `User` by id here and reject inactive users.

## F.3 Environment template (`.env.example`)

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/vrrs_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
TOKEN_EXPIRY_HOURS=24
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

# Appendix G: Other Supporting Material

## G.1 Group role split

| Role | Work areas | Focus |
|---|---|---|
| 1. AI/vision | Detection model; camera node | YOLOv8n detector, OCR pipeline |
| 2. Backend and security | Backend API and database; security and access control | **This report** |
| 3. Real-time and integration | Real-time alerts and monitoring; phone-to-server wiring | WebSocket, camera status, feed proxy, health |
| 4. Frontend | Frontend portals; analytics, testing and documentation | React pages, analytics, run scripts |

## G.2 Findings summary

| ID | Finding | Severity |
|---|---|---|
| F-1 | Token valid after deactivation | High |
| F-2 | Token keeps old role after demotion | High |
| F-3 | Report status accepts any value | Medium |
| F-4 | Public `check-plate` creates repeat alerts | Medium |
| F-5 | Duplicate check ignores `under_review` | Low |
| F-6 | No limit on failed logins | Medium |
| F-7 | Logout does not invalidate token | Medium |
| F-8 | Default signing key fallback (latent) | Latent |
| F-9 | `CORS_ORIGINS` setting unused | Low |
| F-10 | `create_admin.py` default password in source | Medium |

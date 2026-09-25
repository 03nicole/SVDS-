# Chapter 3: Methodology

## 3.1 Introduction

This chapter explains how the backend was developed and evaluated: the approach, how requirements were obtained, the architecture, tools, ethical and legal considerations, and the evaluation method.

## 3.2 Research / Development Approach

The project was built **iteratively**. The web application (backend and frontend) and the camera-node pipeline were two work-streams that met at one point, `POST /alerts/check-plate`. For the backend, work proceeded in slices: data model first, then authentication, then role checks, then the report lifecycle, then the plate-match endpoint and the alert and analytics routes. Each slice was tried through FastAPI's interactive `/docs` page and later covered by automated tests.

A **design-and-verify** approach was used for security: after the features worked, the code was read for weaknesses, each suspected weakness was turned into a short probe test, and findings were distinguished as observed test behaviour, configuration checks or source-code observations (§6.4).

```
Requirements → Design → Implementation → Integration → Testing / Security review → (issues found? back)
```

## 3.3 Requirements / Data Collection

Requirements came from (a) the gap in Chapter 1, (b) the natural three-way split of people who touch a stolen-vehicle report (the person who filed it, the officer investigating it, the administrator), and (c) the needs of the other components: the camera node needs one endpoint, the front end needs role-scoped listings, and the real-time member needs a hook to broadcast alerts. No stakeholder interviews or surveys are recorded, so the requirements are the group's own analysis.

The data handled by the backend is personal and sensitive: names, telephone numbers, national ID numbers, police badge numbers, vehicle details and locations. Test data used in this report is synthetic (for example `jane@test.local`); no real personal data appears in the tests.

## 3.4 System Architecture / Research Workflow

SVDS has three independently runnable processes that communicate only over the network: `vrrs-backend` (this report), `vrrs-frontend` and `vrrs-node`.

![Figure 3.1: SVDS system architecture](../assets/diagrams/04-system-design-1.png)

## 3.5 Tools and Technologies

| Area | Technology |
|---|---|
| Language | Python |
| Web framework | FastAPI 0.111.0 with Uvicorn 0.29.0 |
| Database | PostgreSQL, accessed through `psycopg2-binary` 2.9.9 |
| ORM | SQLAlchemy 2.0.30 (Alembic 1.13.1 is listed in `requirements.txt` but not wired up) |
| Validation | Pydantic 2.7.1 |
| Password hashing | `passlib[bcrypt]` 1.7.4 with `bcrypt` 4.1.3 |
| Tokens | `python-jose[cryptography]` 3.3.0, algorithm HS256 |
| Configuration | `python-dotenv` (`.env`) |
| Testing | pytest with FastAPI `TestClient` and in-memory SQLite |
| OS | Windows 11 |

Versions are those pinned in `vrrs-backend/requirements.txt`.

## 3.6 Ethical and Legal Considerations

- **Personal data.** The system stores personal and police data. Access is limited by role, passwords are hashed, and many account and report changes are audited, with gaps and non-atomic writes described in section 6.4. The Data Protection Act, 2021 is relevant background legislation [16]; this project has not established deployment compliance or a complete retention policy.
- **Data exposure.** Reportees can read only their own reports. Police can read all reports and all users. The response models limit which user fields are returned (§4.4); the password hash is not among them.
- **Accountability.** The audit log gives a trace of who activated, resolved or deleted a report and who changed a role, but it has gaps (§6.4).
- **False matches.** A wrong plate match could point officers at an innocent driver. The backend matches reports whose stored status is `missing`; the generic update route can also set that status without using activation (F-3), and officers can flag alerts as false positives.
- **Unauthenticated endpoint.** `check-plate` is public because the camera has no user identity. This is a deliberate trade-off with a demonstrated consequence (§6.4).
- **Secrets.** The signing key and database password live in a `.env` file that is not committed; `.env.example` documents the keys with placeholder values.
- **Responsible testing.** Security probes were run only against the project's own code using an in-memory test database, never against a live deployment or anyone else's system.

## 3.7 Evaluation Method

1. **Automated tests** (pytest [11]; 31 tests at the evaluated commit, 40 after the fix) covering authentication, role access, reports, the plate-match endpoint and analytics.
2. **Targeted security probes**: short, temporary tests written to confirm or refute suspected weaknesses. They were run, their output recorded, and then removed so that the test suite stays a suite of intended behaviour.
3. **Code review** against the OWASP categories listed in §2.3.
4. **Objective-by-objective review** against B1 to B7 in §1.4.

No load or performance testing and no user evaluation were carried out.

## 3.8 Chapter Summary

The backend was built iteratively in slices and verified by automated tests plus probe tests that check suspected weaknesses. Data handled is sensitive; test data is synthetic.

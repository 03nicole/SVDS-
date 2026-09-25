# Chapter 6: Testing, Results and Evaluation

## 6.1 Introduction

This chapter evaluates the backend. It reports the automated test results, then the security findings from targeted probes, then judges each individual objective. The retained automated tests can be re-run. Historical probe results are transcribed in Appendix D, but the deleted probe source prevents exact independent reproduction of that earlier run.

### 6.1.1 Version of the code evaluated

**Note on the version of the code evaluated.** The findings F-1 to F-10 were first obtained against the code as committed at commit `a349fc6` (31 tests; line counts and coverage figures in this report are from that commit). The code was then changed and committed as `b326b21` (`middleware.py`, `alerts.py`, `system.py`, `main.py`, `conftest.py`, a new `tests/test_regressions.py`, and two front-end files with a new front-end test). Against that commit the backend suite has **40 tests, all passing** (`thesis/assets/test-results/backend-pytest-output.txt`), and the front-end suite has one test, which also passes. The original probes were then **re-run** against the fixed code (Table 6.4 in §6.4.1).

*Fixed and re-verified:* **F-1** and **F-2** (every protected request now re-reads the user from the database, so a deactivated, demoted or deleted user's old token is rejected with 401 or 403, and the role comes from the database, not the token) and **F-9** (`CORS_ORIGINS` is now read). The same check now also protects the WebSocket and the live-feed proxy. *Still open, re-confirmed by re-running the probes:* F-3, F-4, F-6 and F-7. *Still open, not re-probed:* F-5 (TC-19 still passes), F-8 (the fallback is unchanged) and F-10 (the script is unchanged).

## 6.2 Testing Strategy

| Level | Technique | Target |
|---|---|---|
| Integration (API) | pytest with FastAPI `TestClient`, real routes, real ORM | Auth, RBAC, reports, plate matching, analytics |
| Security probing | Short temporary tests confirming suspected weaknesses | Token lifetime, status validation, public endpoint, login attempts, signing key, logout |
| Code review | Reading the source against OWASP categories | All backend modules |
| Acceptance / user testing | None | See §6.5 |

**Test environment.** The tests use an in-memory SQLite database, not PostgreSQL, and the real `get_db` dependency is replaced by an override. Two SQLite gaps are closed in `conftest.py`: foreign keys are switched on, and a Python version of PostgreSQL's four-argument `regexp_replace` is registered so the production matching query runs unchanged. This means results say nothing about behaviour that differs between SQLite and PostgreSQL (for example locking, data types or the constraint catalogue).

## 6.3 Test Cases and Results

The suite has **40 tests, all passing** (re-run against commit `b326b21` while preparing this report; the captured output is in `thesis/assets/test-results/backend-pytest-output.txt`). Thirty-one of them are the tests that existed at the evaluated commit `a349fc6` and are described below. The other nine were added with the fix and are summarised in the last row of the table.

**Table 6.2: Automated test cases**

| ID | Area | Test case | Expected result | Status |
|---|---|---|---|---|
| TC-01 | Auth | Register a reportee | 201; role `reportee`; redirect `/my` | Pass |
| TC-02 | Auth | Register with an existing email | Rejected | Pass |
| TC-03 | Auth | Register asking for a non-reportee role | Rejected | Pass |
| TC-04 | Auth | Register with a short password | Rejected | Pass |
| TC-05 | Auth | Login with correct credentials | Token returned | Pass |
| TC-06 | Auth | Login with a wrong password | 401 | Pass |
| TC-07 | Auth | Login to a deactivated account | Rejected | Pass |
| TC-08 | Auth | Protected route without a token | 401 | Pass |
| TC-09 to TC-12 | RBAC | Reportee requests `/users/`, `/system/audit`, `/alerts/`, `/analytics/summary` | 403 each | Pass (4 cases) |
| TC-13, TC-14 | RBAC | Police request `/system/audit`, `/analytics/user-growth` | 403 each | Pass (2 cases) |
| TC-15 | RBAC | Police request `/alerts/` | 200 | Pass |
| TC-16 | RBAC | Admin request `/system/audit` | 200 | Pass |
| TC-17 | RBAC | Reportee tries to delete a report | 403 | Pass |
| TC-18 | Reports | Reportee files a report | 201; plate upper-cased; `under_review` | Pass |
| TC-19 | Reports | A second report while the first is only `under_review` | 201 (allowed; see §6.4 finding F-5) | Pass |
| TC-20 | Reports | Filing against a plate with a `missing` report | 409 | Pass |
| TC-21 | Reports | Reportee lists reports | Sees only their own | Pass |
| TC-22 | Reports | Police activate then mark found | `missing` then `found`; `resolved_by` set | Pass |
| TC-23 | Reports | Admin deletes a report that has an alert | 204; report and alert both gone | Pass |
| TC-24 | Plate match | Unknown plate | `CLEAR` | Pass |
| TC-25 | Plate match | Exact plate on a `missing` report | `STOLEN` | Pass |
| TC-26 | Plate match | Different case and spacing | `STOLEN` | Pass |
| TC-27 | Plate match | Plate on a `found` report | `CLEAR` | Pass |
| TC-28 | Alerts | Unread count and marking read | Counts update | Pass |
| TC-29 | Alerts | Flag false positive | Audit row written | Pass |
| TC-30, TC-31 | Analytics | Confidence averages across mixed scales | Normalised | Pass (owned by the analytics work; listed for completeness) |
| TC-32 to TC-40 | Regression (`tests/test_regressions.py`) | A deactivated, demoted or deleted user's token is refused on a normal route, on the live-feed proxy and on the WebSocket; the WebSocket re-checks on each heartbeat and before each broadcast; configured and default CORS origins; health metrics on SQLite | 401/403 or WebSocket close code 1008 as appropriate; CORS as configured; `200` with `null` pool figures | Pass |

A consistency run on 25 September 2026 at checkout `bea7410` again produced **40 passed, 87 warnings in 23.19 seconds**, using Python 3.12.10, pytest 9.1.1, FastAPI 0.111.0, Pydantic 2.7.1, SQLAlchemy 2.0.30 and HTTPX 0.28.1. The warnings concern deprecated APIs; they are not test failures. The frontend heartbeat suite also passed its one test. The backend application/tests and frontend files have no diff between `b326b21` and this checkout. A verification summary is retained in `thesis/assets/test-results/report-consistency-check-2026-09-25.txt`.

Counting the parametrised cases, TC-01 to TC-31 are 31 tests and TC-32 to TC-40 are nine more. TC-19 is worth reading closely: it is a test that *documents* current behaviour, and that behaviour is itself a weakness (F-5).

## 6.4 Security Findings from Probes

The retained historical output records probes for F-1 to F-4, F-6 and F-7, a signing-key check relevant to F-8, and an invalid registration probe. The temporary probe source is not retained, so its original test-file count and exact execution cannot be independently reconstructed from the current repository. F-5 is supported by retained test TC-19. The initial observations below must be read together with the post-fix status in Table 6.4.

**Table 6.3: Findings**

| ID | Suspected weakness | What was observed | Severity (student's judgement) |
|---|---|---|---|
| F-1 | A token stays valid after the user is deactivated | After setting `is_active = False`, the user's existing token still got `200` from `GET /users/me`, while a fresh login was refused with 403 | High |
| F-2 | A token keeps the role it was issued with | After an admin was demoted to reportee, their old token still got `200` from `GET /system/audit` (an admin-only route) | High |
| F-3 | `PATCH /reports/{id}` accepts any status | A police user set `status` to `"banana"`; the server returned `200` and stored it. The same route can also set `missing` without going through `activate` | Medium |
| F-4 | `check-plate` is unauthenticated and not rate-limited | Three identical unauthenticated calls for one active plate returned `STOLEN` three times and created **three** alert rows | Medium |
| F-5 | The duplicate-report check ignores `under_review` reports | A second report for the same plate was accepted while the first was `under_review` (TC-19) | Low |
| F-6 | No limit on failed logins | Twenty wrong-password attempts against one account all returned `401`; none was locked out or slowed | Medium |
| F-7 | Logout does not invalidate the token | After `POST /auth/logout`, the same token still got `200` from `GET /users/me` | Medium |

Three further observations came from reading and from checking configuration:

- **F-8 Signing key.** The code falls back to `"changeme"` if `SECRET_KEY` is unset. A check showed the development configuration uses a 47-character key that is not the default, and a token forged with `"changeme"` was rejected. The weakness is therefore *latent* (a deployment that forgets to set the variable would be forgeable), not active.
- **F-10 Admin seed script.** `vrrs-backend/create_admin.py`, the script that creates the first administrator, falls back to a hard-coded default password if `ADMIN_PASSWORD` is not set, prints the credentials to the console, and is committed to the repository. Anyone who runs it without setting the variable creates an administrator with a password that is public in the source. It also defaults `DATABASE_URL` to a local SQLite file if none is set. This was found by reading the script; it was not run.
- **F-9 CORS configuration (initial version; fixed).** At `a349fc6`, the configured value was ignored in favour of hard-coded localhost origins. Since `b326b21`, `get_allowed_origins` reads a comma-separated value, trims whitespace and removes empty entries. An explicitly empty value allows no browser origin; only an absent variable enables the four local-development defaults. The retained CORS tests cover these cases.

**A probe that was invalid.** A probe intended to test whether a six-character password such as `abcdef` is accepted at registration used an incomplete payload (missing the required national ID) and returned `422` for that reason. It shows nothing about the password rule, so **no finding is claimed**. The password minimum (six characters, enforced in the route) is covered by TC-04. The six-character minimum is a code observation. NIST SP 800-63B-4 recommends at least 15 characters for single-factor passwords, blocking common or compromised passwords, and limiting failed attempts; it does not recommend mandatory character-type composition rules [15]. The absence of a composition rule is therefore not itself a defect.

Additional points from reading the code (not probed):

- Roles and statuses are free-text columns without database check constraints. `ReportUpdate.status` accepts an arbitrary string (F-3). In contrast, public registration restricts the role to `reportee`, and the admin role-change route checks an explicit allow-list. A plain-string schema alone does not mean the role-changing API accepts arbitrary roles.
- `email` is a plain string, not validated as an email address.
- `UserUpdate` has no format pattern for phone or national ID, unlike registration, so profile edits can store malformed values.
- Failed logins are not written to the audit log; successful ones are.
- Many list and detail routes are `async` functions that call blocking database code; under load this could stall the event loop. This was not measured.
- In `delete_report`, the audit row is written *after* the delete is committed, so a failure between the two would leave a deletion with no record.

### 6.4.1 Re-run of the probes after the fix

The probes were re-written as temporary tests and run against commit `b326b21` on the in-memory database (same method as above; the temporary file was deleted afterwards). This checks the fix against the exact scenarios that exposed the weaknesses, not just against the new regression tests.

**Table 6.4: Finding status at commit `b326b21`**

| ID | Result before (`a349fc6`) | Result after (`b326b21`) | Status |
|---|---|---|---|
| F-1 | Deactivated user's token: `200` on `/users/me` | `401` | **Fixed** |
| F-2 | Demoted admin's old token: `200` on `/system/audit` | `403` | **Fixed** |
| F-3 | `PATCH` status `banana`: `200`; `missing` via `PATCH`: `200` | Same: `200` and `200` | Open |
| F-4 | Three unauthenticated `check-plate` calls: three `STOLEN`, three alert rows | Same: alert ids 1, 2, 3 | Open |
| F-5 | Second report accepted while first `under_review` (TC-19) | TC-19 still passes | Open |
| F-6 | Twenty wrong passwords: all `401` | Same: `{401}` for all twenty | Open |
| F-7 | Token after `POST /auth/logout`: `200` | Same: `200` | Open |
| F-8 | Default key `changeme` is a latent fallback | Code unchanged | Open (latent) |
| F-9 | `CORS_ORIGINS` ignored | Read from the environment; TC-32 to TC-40 cover it | **Fixed** |
| F-10 | `create_admin.py` default password | Script unchanged (by reading) | Open |

Three of the ten findings are fixed, including the two rated High. One consequence of the fix is worth stating: because F-1 and F-2 were fixed by re-checking the database, a logged-out token (F-7) is still accepted, since logout changes nothing in the database. F-7 therefore needs a revocation mechanism such as a token deny-list or server-side session version. Shorter token lifetimes only reduce the exposure window; they do not provide immediate logout invalidation.

One behaviour change from the fix should be noted: `/system/live-feed` now answers `403` (not `401`) for a valid token whose user is not police or admin, and an empty `CORS_ORIGINS` value now allows no origin at all.

### 6.4.2 Coverage and remaining gaps

The nine added backend cases cover account deactivation, demotion and deletion on HTTP routes, the live-feed authorisation gate and WebSocket connection; heartbeat and broadcast rechecks; configured/default CORS; and SQLite-compatible health metrics. One frontend test checks heartbeat handling, alert delivery and timer cleanup. These are limited automated checks, not full browser or camera-stream tests.

No load test, penetration test, deployed PostgreSQL integration suite, TLS/deployment audit or end-to-end browser/camera test was carried out in this consistency review. A dated database catalogue inspection appears in section 4.7.1; it is not equivalent to testing PostgreSQL runtime behaviour.

## 6.5 User Evaluation

None carried out. No officers, administrators or members of the public used the backend directly, and no survey or interview data exist.

## 6.6 Analysis of Results

- **The intended behaviour is well covered.** The role matrix, ownership rule, lifecycle, cascade delete and plate normalisation all have passing tests, so the core promises of Chapter 4 hold under test.
- **The weaknesses cluster around the token design.** F-1, F-2 and F-7 shared one cause: the server trusted the token's contents (`role`, and the fact that it was issued) and did not re-check the database on each request. That is the stateless trade-off named in §2.2.4. At the evaluated commit it meant a deactivated or demoted police officer kept their old access until the token expired (24 hours by default), which for a police system was the most important finding. The fix removes it for F-1 and F-2 at the price of one database read per request, and leaves F-7 (logout) open, as Table 6.4 shows.
- **F-3 and F-5 are validation gaps.** F-3 concerns status changes by police/admin users. F-5 concerns report creation, which is also available to reportees; it is not limited to police. Both can put the data into states the intended workflow does not expect.
- **F-4 is a consequence of a design choice** (a public endpoint for a camera with no identity). The endpoint cannot alter reports, but anyone who can reach it can flood the alert table and the police dashboard with false alerts for any active plate they know.
- **F-6** matters more if passwords are short, as here.
- **The tests cannot see PostgreSQL-specific problems**, so passing tests are evidence about logic, not about the deployed database.

## 6.7 Objective-by-Objective Evaluation

| Objective | Evidence | Verdict |
|---|---|---|
| B1 Data model | Four tables with keys, unique email, cascade; tests create the schema and the cascade test passes. `create_all()` only, no migrations | **Achieved**, with the migration limitation |
| B2 Registration, login, hashing, JWT | bcrypt hashes; token with `sub`, `role`, `exp`; TC-01 to TC-08 pass; deactivation now takes effect at once (Table 6.4) | **Achieved**; logout revocation and lockout not provided (F-6, F-7) |
| B3 Server-side role enforcement | Role dependencies on every route; role matrix TC-09 to TC-17 pass; the role is now read from the database each request (TC-32 to TC-40) | **Achieved**; the stale-role weakness (F-1, F-2) is fixed and re-verified |
| B4 Report lifecycle and ownership | TC-18 to TC-23 pass | **Largely achieved**; status validation missing (F-3) and duplicate check incomplete (F-5) |
| B5 Plate-match endpoint | TC-24 to TC-27 pass | **Achieved**; public and unthrottled (F-4) |
| B6 Audit records | Rows written for selected actions; TC-29 checks one | **Largely achieved**; incomplete and non-atomic audit coverage; one audit action directly tested |
| B7 Verification and security review | 40 passing tests; ten findings recorded; probes re-run after the fix | **Achieved** for this scope; no penetration test |

## 6.8 Individual Results

All results in this chapter concern the backend and security component, except TC-30 and TC-31 (analytics), which are shown for completeness and are not claimed. The camera node, full WebSocket implementation and frontend belong to other work areas. The shared authentication boundary is nevertheless exercised by the backend regression tests; the frontend heartbeat test is reported separately as supporting integration evidence.

## 6.9 Chapter Summary

All 31 tests at the evaluated commit passed, and all 40 pass after the fix. Six weaknesses were confirmed by probes and one (F-5) by an existing test, the most serious being that tokens outlived deactivation and demotion. Ten findings in total, including three from configuration and code reading, were recorded. F-1 and F-2 were re-checked by the historical probes and retained regression tests; F-9 is verified by configuration/preflight tests; the other seven remain open and are listed as recommendations in Chapter 8.

# Chapter 6: Testing, Results and Evaluation

## 6.1 Introduction

This chapter evaluates the backend. It reports the automated test results, then the security findings from targeted probes, then judges each individual objective. Every result below comes from output that was produced during the preparation of this report and can be re-run.

### 6.1.1 Version of the code evaluated

**Note on the version of the code evaluated.** All findings, test counts, coverage figures and line counts in this report were obtained against the code as committed (commit `a349fc6`). After that evaluation, uncommitted changes appeared in the working tree (`middleware.py`, `alerts.py`, `system.py`, `main.py`, `api.js`, `SystemHealth.jsx`, `conftest.py`, a new `tests/test_regressions.py` and a new front-end test). With those changes the backend suite has **38 tests, all passing**, and the front end has **one** test (`npm test`), which also passes. The changes appear to address the items listed below; this was established by reading the changes and running the tests, and the original probes were **not** re-run against the changed code. Where this report says a finding was "not fixed", it refers to the evaluated commit.

*Appear addressed in the working tree:* **F-1** and **F-2** (every request now re-reads the user from the database, so a deactivated or demoted user's old token is rejected, and the role comes from the database, not the token) and **F-9** (`CORS_ORIGINS` is now read). *Still open as far as the changes show:* F-3, F-4, F-5, F-6, F-7 (logout does not end a session by itself), F-8 and F-10.

## 6.2 Testing Strategy

| Level | Technique | Target |
|---|---|---|
| Integration (API) | pytest with FastAPI `TestClient`, real routes, real ORM | Auth, RBAC, reports, plate matching, analytics |
| Security probing | Short temporary tests confirming suspected weaknesses | Token lifetime, status validation, public endpoint, login attempts, signing key, logout |
| Code review | Reading the source against OWASP categories | All backend modules |
| Acceptance / user testing | None | See §6.5 |

**Test environment.** The tests use an in-memory SQLite database, not PostgreSQL, and the real `get_db` dependency is replaced by an override. Two SQLite gaps are closed in `conftest.py`: foreign keys are switched on, and a Python version of PostgreSQL's four-argument `regexp_replace` is registered so the production matching query runs unchanged. This means results say nothing about behaviour that differs between SQLite and PostgreSQL (for example locking, data types or the constraint catalogue).

## 6.3 Test Cases and Results

The suite has **31 tests, all passing** (re-run while preparing this report; the original captured output is in `thesis/assets/test-results/backend-pytest-output.txt`).

**Table 6.1: Automated test cases**

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

Counting the parametrised cases, this is 31 tests. TC-19 is worth reading closely: it is a test that *documents* current behaviour, and that behaviour is itself a weakness (F-5).

## 6.4 Security Findings from Probes

Seven probe tests were written as temporary tests, run against the in-memory database, and then deleted, so the shipped suite stays a specification of intended behaviour. They produced findings F-1 to F-4, F-6 and F-7 and the key check in F-8; one probe was invalid (see below) and is not reported. F-5 comes from an existing test (TC-19), not a probe.

**Table 6.2: Findings**

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
- **F-9 CORS configuration.** `CORS_ORIGINS` in `.env.example` is not used; origins are hard-coded to localhost. This is safe for development but means the setting does nothing, and a real deployment would need a code change.

**A probe that was invalid.** A probe intended to test whether a six-character password such as `abcdef` is accepted at registration used an incomplete payload (missing the required national ID) and returned `422` for that reason. It shows nothing about the password rule, so **no finding is claimed**. The password minimum (six characters, enforced in the route) is covered by TC-04. Six characters is short by current guidance and there is no complexity check, which is a design observation, not a probe result.

Additional points from reading the code (not probed):

- Roles and statuses are free-text columns with no database check constraint, and the role and status are not validated by an enumeration in the schemas (`ReportUpdate.status` is `Optional[str]`), which is the root of F-3.
- `email` is a plain string, not validated as an email address.
- `UserUpdate` has no format pattern for phone or national ID, unlike registration, so profile edits can store malformed values.
- Failed logins are not written to the audit log; successful ones are.
- Many list and detail routes are `async` functions that call blocking database code; under load this could stall the event loop. This was not measured.
- In `delete_report`, the audit row is written *after* the delete is committed, so a failure between the two would leave a deletion with no record.

### 6.4.1 What was not tested

No load or performance test; no PostgreSQL-specific test; no penetration test; no test of the WebSocket or live-feed proxy (other member); no test of TLS or deployment configuration; no automated test of the front end.

## 6.5 User Evaluation

None carried out. No officers, administrators or members of the public used the backend directly, and no survey or interview data exist.

## 6.6 Analysis of Results

- **The intended behaviour is well covered.** The role matrix, ownership rule, lifecycle, cascade delete and plate normalisation all have passing tests, so the core promises of Chapter 4 hold under test.
- **The weaknesses cluster around the token design.** F-1, F-2 and F-7 have one cause: the server trusts the token's contents (`role`, and the fact that it was issued) and does not re-check the database on each request. That is the stateless trade-off named in §2.2.4. In practice it means a deactivated or demoted police officer keeps their old access until the token expires (24 hours by default). For a police system that is the most important finding.
- **F-3 and F-5 are validation gaps**, not access-control failures: the people who can do these things are already trusted (police), but the data can end up in states the rest of the system does not expect.
- **F-4 is a consequence of a design choice** (a public endpoint for a camera with no identity). The endpoint cannot alter reports, but anyone who can reach it can flood the alert table and the police dashboard with false alerts for any active plate they know.
- **F-6** matters more if passwords are short, as here.
- **The tests cannot see PostgreSQL-specific problems**, so passing tests are evidence about logic, not about the deployed database.

## 6.7 Objective-by-Objective Evaluation

| Objective | Evidence | Verdict |
|---|---|---|
| B1 Data model | Four tables with keys, unique email, cascade; tests create the schema and the cascade test passes. `create_all()` only, no migrations | **Achieved**, with the migration limitation |
| B2 Registration, login, hashing, JWT | bcrypt hashes; token with `sub`, `role`, `exp`; TC-01 to TC-08 pass | **Achieved**; token revocation and lockout not provided (F-1, F-6, F-7) |
| B3 Server-side role enforcement | Role dependencies on every route; role matrix TC-09 to TC-17 pass | **Achieved** for the token as issued; **weakened** by F-1 and F-2, which let a stale role persist |
| B4 Report lifecycle and ownership | TC-18 to TC-23 pass | **Largely achieved**; status validation missing (F-3) and duplicate check incomplete (F-5) |
| B5 Plate-match endpoint | TC-24 to TC-27 pass | **Achieved**; public and unthrottled (F-4) |
| B6 Audit records | Rows written for the listed actions; TC-29 checks one | **Largely achieved**; failed logins not recorded; only one action is directly tested |
| B7 Verification and security review | 31 passing tests; ten findings recorded | **Achieved** for this scope; no penetration test |

## 6.8 Individual Results

All results in this chapter concern the backend and security component, except TC-30 and TC-31 (analytics), which are shown for completeness and are not claimed. The camera-node tests, the WebSocket and the front end are in the other members' reports.

## 6.9 Chapter Summary

All 31 tests pass. Six weaknesses were confirmed by probes and one (F-5) by an existing test, the most serious being that tokens outlive deactivation and demotion. Ten findings in total, including three from configuration and code reading, were recorded and none has been fixed in this project; they are listed as recommendations in Chapter 8.

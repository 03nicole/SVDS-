# Chapter 6: Testing, Results and Evaluation

## 6.1 Introduction

This chapter reports what was measured and observed for the front end, analytics, tests and documentation. Every result comes from a command or script run while preparing this report. Temporary probe tests were deleted after running, so the shipped suites are unchanged.

### 6.1.1 Version of the code evaluated

**Note on the version of the code evaluated.** All findings, test counts, coverage figures and line counts in this report were obtained against the code as committed (commit `a349fc6`). After that evaluation, uncommitted changes appeared in the working tree (`middleware.py`, `alerts.py`, `system.py`, `main.py`, `api.js`, `SystemHealth.jsx`, `conftest.py`, a new `tests/test_regressions.py` and a new front-end test). With those changes the backend suite has **38 tests, all passing**, and the front end has **one** test (`npm test`), which also passes. The changes appear to address the items listed below; this was established by reading the changes and running the tests, and the original probes were **not** re-run against the changed code. Where this report says a finding was "not fixed", it refers to the evaluated commit.

*Appear addressed in the working tree:* **D-1** (the backend now reads `CORS_ORIGINS`, so the README instruction takes effect), **U-11** in part (one front-end test now exists, for the alert socket helper), and the health page's connection card. *Still open as far as the changes show:* U-1 and U-2 (the 401 handler is unchanged, so the failed-login problem remains), U-3 to U-10, D-2 to D-4, and the low coverage of user management and system routes (coverage was not re-measured).

## 6.2 Testing Strategy

| Level | Technique | Target |
|---|---|---|
| Build | `vite build` | The front end compiles |
| Automated tests | pytest (31 backend, 8 node) | API behaviour and pure logic |
| Coverage | Standard-library line tracing across all threads | The backend package |
| Browser check | Headless Chrome over the DevTools Protocol against the running app | Failed login behaviour, label association |
| Analytics probes | Temporary tests with edge-case data | The analytics endpoints |
| Code review | Reading pages and the README | Error handling, keys, search, documentation |
| User evaluation | None | See §6.5 |

## 6.3 Test Cases and Results

**Table 6.1: Test cases for this component**

| ID | Test case | Expected | Observed | Status |
|---|---|---|---|---|
| TC-U1 | Production build | Compiles | 107 modules transformed; `index.html` 0.43 kB, CSS 13.50 kB (3.53 kB gzipped), JS 263.64 kB (82.49 kB gzipped); built in 2.31 s | Pass |
| TC-U2 | Backend suite | All pass | 31 passed | Pass |
| TC-U3 | Node suite | All pass | 8 passed | Pass |
| TC-U4 | Summary averages mixed confidence scales (0.8 and 60.0) | 70.0 | 70.0 (existing test) | Pass |
| TC-U5 | Detections per node normalises a fraction (0.5) | 50.0 | 50.0 (existing test) | Pass |
| TC-U6 | Reports per month with reports in months 1, 2 and 4 ago | Each month present | Months 1, 2 and 4 present; the empty third month is **omitted** | Pass with finding U-6 |
| TC-U7 | Recovery time for one found report resolved 6 days after filing | 6 days | `avg_days` 6.0, fastest 6, slowest 6, recovered 1 | Pass |
| TC-U8 | Analytics query bounds (`months=0`, `days=3`) | Rejected | 422 for both | Pass |
| TC-U9 | Wrong-password login in a real browser | Error message shown | **Not shown**: page reloaded (§6.4, U-1) | **Fail** |
| TC-U10 | Labels on the login form associated with inputs | Associated | 0 of 2 labels had a `for` attribute | **Fail** (U-3) |
| TC-U11 | Automated front-end tests | Exist | None exist | **Not present** |

## 6.4 Results and Findings

### 6.4.1 Coverage of the backend by the automated tests

Measured with a small all-threads line tracer (it counts executable lines run at least once; a run line is not proof its result was checked). The usual tool, coverage.py, could not be installed offline, so these figures are approximate.

| File | Lines run / executable | % |
|---|---|---|
| `models.py` | 61 / 61 | 100.0 |
| `schemas.py` | 114 / 114 | 100.0 |
| `routers/auth.py` | 42 / 43 | 97.7 |
| `auth.py` | 24 / 26 | 92.3 |
| `middleware.py` | 23 / 27 | 85.2 |
| `main.py` | 31 / 39 | 79.5 |
| `database.py` | 12 / 16 | 75.0 |
| `routers/reports.py` | 65 / 87 | 74.7 |
| `routers/analytics.py` | 50 / 72 | 69.4 |
| `routers/alerts.py` | 75 / 110 | 68.2 |
| `routers/system.py` | 37 / 117 | 31.6 |
| `routers/users.py` | 31 / 115 | 27.0 |
| `model.py`, `routers/model.py` (unused placeholder) | 0 / 61 | 0.0 |
| **Total** | **565 / 888** | **63.6** |

Excluding the two unused placeholder files, coverage is 565 / 827, about 68%. The weakest areas are **user management** (27%: invite, role change, deactivate, delete and profile edits are largely untested) and **system** routes (32%; the real-time member's probes cover part of these but are not part of the suite). There is no coverage figure for the front end because it has no tests.

### 6.4.2 Interface findings

| ID | Finding | Evidence | Severity |
|---|---|---|---|
| U-1 | **A failed login never shows its error.** With a wrong password the server returns 401, the response handler clears storage and reassigns the location to `/login`, and the page reloads before the login page's error message can be read | Browser check: the login response statuses were `[200, 401]` (the page load and the failed login), the page's own marker variable was gone after the click (page reloaded), the page text showed only the empty form with no error, and two frame navigations occurred | High (usability) |
| U-2 | Root cause of U-1: **every 401 is treated as an expired session**, including a failed login | Read from `api.js` | (same) |
| U-3 | **Login form labels are not associated with their inputs** | Browser check: 0 of 2 labels have a `for` attribute. The Register page does associate its labels (read from code) | Medium (accessibility) |
| U-4 | **Several data loads have no error handling**: Alerts, Cameras, Police home, and System Health call the API without a failure branch, so a failed request leaves "Loading" or an empty page with no message. (Analytics does handle failure with a Retry button) | Read from code, not run | Medium |
| U-5 | **The registry search sends a request on every keystroke** with no delay, and nothing guards against replies arriving out of order | Read from code | Low |
| U-11 | **No automated front-end tests** | No test files exist | Medium |

### 6.4.3 Analytics findings

| ID | Finding | Evidence | Severity |
|---|---|---|---|
| U-6 | **Months and days with no data are omitted**, so the "Reports per month" bars skip empty months (June was missing in the probe), which misrepresents the time axis. The bars are also **not proportional**: height is `max(20, min(count×10, 170))` px, so counts of 1 and 2 look the same and counts of 17 or more look the same | Probe; arithmetic from the code | Medium |
| U-7 | **The detections table splits one camera into several rows** when its location text varies ("Cairo Rd" and "Cairo Road" gave two rows), and the page uses the camera id as the React key, which would then repeat | Probe; key read from code. A duplicate-key warning was not observed in a browser | Low |
| U-8 | **A stored confidence of exactly 1.0 is treated as a fraction and displayed as 100%**, though it could mean 1% | Probe: stored 1.0 displayed as 100.0 | Low. The rule is a heuristic |
| U-9 | **"False positives" is counted by searching audit text** for the phrase, so any audit row containing it is counted | Probe: an unrelated audit row containing the phrase raised the count to 1 | Low |
| U-10 | **Definitions worth stating on screen:** the recovery rate divides found reports by *all* reports including those not yet worked (the probe gave 20% for 1 found of 5), and average confidence includes alerts later flagged as false | Probe and code | Low |

### 6.4.4 Documentation findings

Checked by searching `README.md` and reading it against the code:

| ID | Finding | Severity |
|---|---|---|
| D-1 | The README tells the reader to set `CORS_ORIGINS` and, for deployment, to set it to the deployed front end's address. **The backend does not read this setting**, so following the README would leave a deployed front end blocked (backend report, F-9) | High for deployment |
| D-2 | The README never mentions `run-all.ps1`, `create_admin.py` (the only way to create the first administrator), the tests, or the phone camera app | Medium |
| D-3 | The README's camera example shows a `NODE-001` camera id and a `STOLEN`/`CLEAR` response but not `alert_id` or the `vehicle` details the server actually returns | Low |
| D-4 | `run-all.ps1` contains an absolute path to the developer's own Python environment | Medium (portability) |

### 6.4.5 What was not tested

Other browsers, mobile screens, keyboard or screen-reader use, page load time, a live alert on a real screen, behaviour with large data sets, and any user task. The other pages were not driven through the browser in this session; the screenshots in Chapter 4 were captured earlier from the running application.

## 6.5 User Evaluation

None carried out. No officer, reportee or administrator used the interface for this report, and no survey or interview data exist.

## 6.6 Analysis of Results

- **The build and test suites are healthy**: the front end compiles into a small bundle (82 kB gzipped JavaScript), and all 39 Python tests pass.
- **The tests cover the core well and the edges poorly.** Authentication, models and schemas are near fully exercised, while user management and the system routes are mostly not. A change to role changes or account deletion would not be caught.
- **The most damaging interface defect is small and invisible to code review of a single file**: the reload comes from the response handler in one file undoing the error message in another. It was found only by running the application. It means a user who mistypes a password gets no feedback at all.
- **The analytics are correct on the cases tested but easy to misread.** Recovery time, status counts and confidence normalisation match expectation. The weaknesses are about presentation (skipped empty periods, non-proportional bars), heuristics (the fraction rule) and definitions that are not stated on screen.
- **Documentation trails the code.** The README describes a configuration option that no longer does anything and omits the steps a newcomer needs first.

## 6.7 Objective-by-Objective Evaluation

| Objective | Evidence | Verdict |
|---|---|---|
| U1 Role-based portals with guards | Fourteen guarded routes; build passes; guards read from code | **Achieved**; guards not exercised in the browser in this session |
| U2 Reportee flows | Pages exist; screenshots; API tests cover registration, login and reports | **Largely achieved**; failed-login feedback broken (U-1) |
| U3 Police flows | Pages exist; API tests cover activate and found | **Largely achieved**; loading errors unhandled (U-4) |
| U4 Admin flows | Pages exist; user-management routes only 27% covered | **Achieved in implementation**; weakly tested |
| U5 Correct analytics | Fixed confidence scale; probes on counts and times | **Largely achieved**; presentation and definition issues (U-6 to U-10) |
| U6 Automated tests and coverage | 39 tests pass; backend coverage 63.6% | **Achieved** for the backend; **not achieved** for the front end |
| U7 Documentation and run script | README and script exist | **Partly achieved**: errors and omissions (D-1 to D-4) |
| U8 Honest evaluation | One browser check, probes, coverage, findings | **Achieved** for this scope |

## 6.8 Individual Results

All results here concern the front end, analytics, test evidence and documentation. Results about token handling (backend member), the alert channel and status pages (real-time member), and the detector and camera node (AI/vision member) are in their own reports.

## 6.9 Chapter Summary

The application builds and all 39 Python tests pass, with 63.6% approximate line coverage of the backend. A real browser check found that a wrong password gives no error message, and other checks found unhandled load failures, non-proportional and gappy charts, and README instructions that no longer match the code. None has been fixed in this project.

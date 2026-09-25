# Chapter 5: Implementation / Development

## 5.1 Introduction

This chapter describes how the front end, analytics, tests and documentation were built, how they connect to the other members' work, the problems met, and the student's contribution.

## 5.2 Development Environment

| Item | Detail |
|---|---|
| Machine | Windows 11 PC |
| Front end | Node.js with npm; Vite 5.4 (the production build in §6.4 ran with Vite 5.4.21) |
| Backend for tests | Python 3.12 virtual environment with pytest |
| Browser | Google Chrome (development, and headless for the scripted check) |
| Version control | Git |

## 5.3 System Components / Modules

| Module | Size | Purpose | Built by |
|---|---|---|---|
| `vrrs-frontend/src` (24 JS/JSX files) | 1,786 lines | The React application | Frontend (this report) |
| `src/styles.css` | 1,084 lines | All styling | Frontend (this report) |
| `services/api.js` | | Axios instance, token header, 401 handler, grouped API calls | Frontend (this report) |
| `context/AuthContext.jsx`, `components/ProtectedRoute.jsx`, `App.jsx` | | Session and guards | Frontend (this report) |
| `context/AlertsContext.jsx`, `components/NotificationToast.jsx`, `createAlertSocket` | | Alert connection and toast | Real-time member |
| `app/routers/analytics.py` | 87 lines | Seven analytics endpoints | Frontend/analytics (this report) |
| `vrrs-backend/tests/`, `vrrs-node/tests/` | 31 + 8 tests | Automated tests | See §5.7 |
| `README.md`, `run-all.ps1` | 91 lines | Documentation and start-up | Frontend/documentation (this report), with `run-all.ps1` also described in the real-time report |

## 5.4 Key Implementation Details

### 5.4.1 Routing and guards

```jsx
const Guard = ({ roles, children }) => <ProtectedRoute allowedRoles={roles}>{children}</ProtectedRoute>;
<Route path="/police/alerts" element={<Guard roles={["police","admin"]}><Alerts /></Guard>} />
<Route path="/admin/users"   element={<Guard roles={["admin"]}><UserManagement /></Guard>} />
```

`ProtectedRoute` shows "Loading..." while the session loads, redirects to `/login` if nobody is signed in, and redirects to the user's own home if the role is not allowed. Reportee routes allow all three roles, so officers and admins can also file reports.

### 5.4.2 Analytics and the confidence fix

All averages use one expression:

```python
NORMALIZED_CONFIDENCE = case(
    (Alert.confidence_score <= 1, Alert.confidence_score * 100),
    else_=Alert.confidence_score,
)
```

**The defect.** Detections from a retired standalone script stored confidence as a fraction (0.9), while the camera node stores a percentage (90.1). On the live database, rows for the old camera ids averaged about 0.9 and rows for the current node about 87, so averaging the raw column reported roughly 30 instead of about 87. **The fix** scales any value at or below 1 up to a percentage before averaging, and was chosen over rewriting the old rows so historical data stays untouched. Two regression tests cover it: a mixed 0.8 and 60.0 pair must average 70.0, and a lone 0.5 must display as 50.0. The same expression is used in the camera status code (real-time member).

The other analytics endpoints are direct SQL aggregates (counts by status, by month, by day, by camera; mean recovery time in Python over found reports).

### 5.4.3 The API module

`api.js` builds one Axios instance whose base address comes from `VITE_API_BASE_URL`, adds `Authorization: Bearer <token>` from `localStorage`, and groups calls into `authAPI`, `reportsAPI`, `alertsAPI`, `usersAPI`, `analyticsAPI` and `systemAPI`. A response interceptor treats any 401 as an expired session: it clears `localStorage` and sets `window.location.href = "/login"`. (This behaviour is the cause of finding U-1, §6.4.)

### 5.4.4 Pages

- **Registry (`PoliceHome`):** loads reports and the summary, sends a new request on each search or status change, and calls activate and mark-found then reloads the list.
- **Alerts:** loads unread or all alerts with a page size, prepends live events, and updates the unread count when items are cleared.
- **Analytics:** loads five endpoints together, shows an error box with a Retry button if any fails, and draws the bars and donut.
- **Report vehicle:** upper-cases and trims the plate, sends `null` for an empty incident date, and shows the server's error message on failure.
- **Register:** validates fields (including matching passwords) in the browser before sending.
- **User management:** search and role filter; invite, role change, activate/deactivate, delete with a confirmation dialog.

### 5.4.5 Tests and documentation

The backend tests use FastAPI's `TestClient` with an in-memory SQLite database, an overridden database dependency, and fixtures that create users and tokens for each role (Chapter 6 of the backend report describes the set-up). The node tests cover the pure plate functions. `README.md` gives quick-start steps, the role table, the API list and the camera-node contract; `run-all.ps1` starts all three programs.

## 5.5 Integration

- **With the backend:** every API group in `api.js` maps to a backend router; the login response supplies the token, role and redirect path.
- **With the real-time member:** the alerts context and toast are mounted by `App.jsx`; the Cameras and System Health pages call the status endpoints.
- **With the AI/vision member:** the node's confidence scale (percentage) is what the analytics normalisation assumes.
- **Configuration:** `VITE_API_BASE_URL` and `VITE_WS_URL` in the front-end `.env`.

## 5.6 Challenges and Solutions

| Challenge | Cause | Solution |
|---|---|---|
| Analytics average confidence was wrong (about 30 instead of 87) | Two storage scales in one column | Normalise in SQL before averaging; two regression tests |
| Charts and numbers had to come from real data | Early versions used fixed sample values | Every figure is computed by an endpoint; empty states ("No detections yet") handled |
| Each role needs its own navigation and layout | Three audiences on one app | Shared `PortalLayout`, `ReporteeLayout`, and a `policeNav` config |
| Browser cannot send a header on a WebSocket or `<img>` | Browser limits | Query-string token (discussed in the real-time report) |
| Tests must not touch PostgreSQL | `database.py` connects at import | Dependency override with in-memory SQLite (backend report) |
| Getting three programs to run together | Separate environments | `run-all.ps1` and README steps (with the gaps listed in §6.4) |

## 5.7 Individual Contribution (group project)

The student was responsible for **work areas 6 and 7** of the group's seven (Appendix A):

- the React front end: routing and guards, the API module, the three portals and their fourteen pages, shared layouts and the stylesheet;
- the analytics endpoints, the analytics page, and the confidence-scale fix with its regression tests;
- the automated test suites as a body of evidence (running, extending and reporting them), and the coverage measurement in this report;
- the README and the run script;
- the evaluation in Chapter 6.

Work by others that this component uses, **not claimed here**: the token, roles, data model and report rules (backend member); the alert channel, camera status, feed proxy and health endpoint (real-time member); the detection model and camera node (AI/vision member).

*Test authorship.* The role split assigned "tests" to this role, but the suites also test other members' code. **The student should state which test files they wrote themselves**; this report claims the analytics tests, the running and measuring of the suites, and the coverage analysis.

## 5.8 Chapter Summary

The front end is a small hand-written React application with fourteen guarded pages. The analytics are SQL aggregates with one shared confidence normalisation, fixed after a real defect. Tests and documentation were assembled around them.

# Chapter 4: System Analysis and Design

## 4.1 Introduction

Stakeholders and the architecture are shared by the group. The requirements, interface design and analytics design below are those of the **frontend, analytics, testing and documentation** component.

## 4.2 Stakeholder and User Analysis

| Stakeholder | Goal | What the interface must give |
|---|---|---|
| Reportee (public) | Report a theft and follow it | Simple registration and login; a report form; a list of their own reports with status; profile editing |
| Police officer | Recover vehicles | Registry search and filter; activate and mark found; live alerts to review or dismiss; camera view; analytics |
| Administrator | Run the system | User list with role and account controls; audit log; system health |
| Maintainer | Keep the system working | Tests, documentation, one-command start |

## 4.3 Functional Requirements

| ID | Requirement |
|---|---|
| FR-U1 | Login and registration pages; after login, redirect to the portal for the user's role. |
| FR-U2 | Route guards: reportee pages require any signed-in user; police pages require police or admin; admin pages require admin; otherwise redirect to the user's home. |
| FR-U3 | Reportee portal: home, report-vehicle form, my reports (with status), profile (edit details, change password). |
| FR-U4 | Police portal: vehicle registry with search and status filter and activate / mark-found actions; live alerts with mark-read, mark-all-read and false-positive; cameras; analytics. |
| FR-U5 | Admin portal: overview, user management (invite police, change role, deactivate, delete), system health, audit log. |
| FR-U6 | Attach the token to every API request; on an authentication failure clear the session and go to the login page. |
| FR-U7 | Analytics endpoints for summary counts, reports per month, status breakdown, detections per camera, alerts over time, recovery time and user growth. |
| FR-U8 | Every figure shown by analytics is computed from stored records. Confidence scores stored on different scales are normalised before averaging. |
| FR-U9 | The repository has instructions for installing and running each part, and a script that starts all three. |

## 4.4 Non-Functional Requirements

- **Consistency with the server:** the interface's role rules mirror the server's, which remains the authority.
- **Simplicity and low dependency count:** four runtime packages.
- **Clarity:** errors from the server are shown to the user in plain text where the code handles them.
- **Correctness of statistics:** unambiguous definitions; mixed units handled.
- **Repeatability:** tests can be run with one command and do not touch the real database.
- **Maintainability:** shared layouts (`PortalLayout`, `ReporteeLayout`), one API module, two contexts.

## 4.5 Use Cases / User Stories

**UC-U1: A member of the public reports a theft.** They register, log in, fill in the report form (plate, vehicle details, incident date, last seen, description), submit, and later see the report in "My reports" with its status.

**UC-U2: An officer works a report.** They search the registry by plate or owner, filter by status, activate an under-review report so cameras can match it, and mark it found when the vehicle is recovered.

**UC-U3: An officer reviews alerts.** They open Live alerts, see unread items, and mark them read, mark all read, or flag a false positive.

**UC-U4: An officer reviews performance.** On Analytics they see totals, average recovery time, average detection confidence, false positives, reports per month, the status breakdown and detections by location.

**UC-U5: An administrator manages users.** They invite a police officer, change a role, deactivate an account or delete one, and read the audit log.

**User story.** *As a police commander, I want the recovery rate and average confidence on the analytics page to be computed from real records, so that I can trust them when reporting to my superiors.*

## 4.6 System / Solution Architecture

```
src/
  main.jsx, App.jsx           entry point, providers, routes with role guards
  context/AuthContext.jsx     signed-in user, login/logout, session restore
  context/AlertsContext.jsx   alert connection and unread count (real-time member)
  services/api.js             Axios instance, token header, 401 handler, API groups
  components/                 ProtectedRoute, PortalLayout, ReporteeLayout, NotificationToast
  config/policeNav.js         police navigation with unread badge
  pages/                      Login, Register, reportee/, police/, admin/  (14 pages)
```

`App.jsx` wraps everything in `AuthProvider` and `AlertsProvider`, mounts the toast once, and declares fourteen routes, each inside a `Guard` with the roles allowed.

![Figure 4.1: role-based route access](../assets/diagrams/04-system-design-5.png)

## 4.7 Database / Data Design

The front end has no database. The analytics read the backend's four tables (users, reports, alerts, audit log), whose design is in the backend member's report (Appendix C). The analytics **derived values** are defined here:

| Figure | Definition in the code |
|---|---|
| Recovery rate | `found / total reports × 100`, where total includes `under_review` and `missing` reports |
| Average recovery time | Mean of `(resolved_date − report_date)` in whole days over reports that are found and have a resolved date |
| Average detection confidence | Mean of normalised confidence over **all** alerts, including ones later flagged as false positives |
| False positives | Number of audit-log rows whose text contains "false positive" |
| Reports per month | Count of reports by calendar month for the last *n × 30* days; months with no reports are omitted |
| Alerts over time | Count of alerts per day for the last *n* days; days with none are omitted |
| Detections per node | Alert counts grouped by camera id **and** location text |

**Confidence normalisation.** Older detections stored confidence as a fraction (0 to 1) and the current camera node stores a percentage (0 to 100). Every average first converts any value at or below 1 to a percentage (`value × 100`).

## 4.8 Interface / Interaction Design

The pages were captured from the running application. They are reproduced here as evidence of the interface.

![Figure 4.2: Login](../assets/screenshots/login.png)

![Figure 4.3: Register](../assets/screenshots/register.png)

![Figure 4.4: Reportee home](../assets/screenshots/reportee-home.png)

![Figure 4.5: Report vehicle](../assets/screenshots/report-vehicle.png)

![Figure 4.6: My reports](../assets/screenshots/my-reports.png)

![Figure 4.7: Police home (vehicle registry)](../assets/screenshots/police-home.png)

![Figure 4.8: Live alerts](../assets/screenshots/alerts.png)

![Figure 4.9: Analytics](../assets/screenshots/analytics.png)

![Figure 4.10: Admin overview](../assets/screenshots/admin-home.png)

![Figure 4.11: User management](../assets/screenshots/user-management.png)

![Figure 4.12: Audit log](../assets/screenshots/audit-log.png)

Further screens (profile, cameras, system health, interactive API documentation) are in Appendix C.

**Interaction design choices:** each role has its own navigation (police navigation shows an unread badge); a toast notification appears on any page; forms show server error text; the register page validates fields in the browser before sending; destructive user deletion asks for confirmation.

## 4.9 Algorithms / Models / Technical Design

- **Route guard:** `ProtectedRoute` waits for the session to load, redirects to login if no user, and redirects to the user's own home if their role is not allowed.
- **Session restore:** on load, the saved user and token are read from `localStorage`, the user is set at once, and `GET /users/me` refreshes it; failure logs the user out.
- **Request pipeline:** an Axios request interceptor adds the token; a response interceptor treats any HTTP 401 as an expired session (clear storage, go to `/login`).
- **Search:** the registry sends a request on each keystroke with the current search and status.
- **Charts:** bar height = `max(20, min(count × 10, 170))` pixels; the donut is a CSS conic gradient from rounded percentages of found and missing (the remainder is drawn as "under review").
- **Analytics queries:** SQL aggregates with `func.count`, `func.avg`, `func.date` and `extract`; the confidence normalisation is one shared expression.

## 4.10 Chapter Summary

The front end is fourteen guarded pages over one API module and two contexts. Analytics figures have explicit definitions in the code, and a shared expression normalises confidence scales. The evaluation in Chapter 6 tests those definitions against edge cases.

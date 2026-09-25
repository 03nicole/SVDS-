# Chapter 3: Methodology

## 3.1 Introduction

This chapter explains how the front end, analytics, tests and documentation were developed and evaluated: the approach, requirements, architecture, tools, ethics and evaluation method.

## 3.2 Research / Development Approach

The project was built **iteratively**. The front end was developed against the running API: each page was built, tried in the browser against the real backend, and adjusted. Analytics endpoints were written alongside the page that shows them, so each chart had real data behind it from the start; the project's working rule was that a statistic on screen must be computed from stored records, not typed in.

Testing followed a **find, fix, lock-in** pattern for defects: a suspected defect was checked against the running system, fixed, and covered by a regression test (for example the confidence-scale fix, §5.4.2). For this report a further **verify-what-was-claimed** step was added: the production build was run, coverage was measured, suspected interface and analytics defects were checked in a real browser or with probe tests, and only observed behaviour was recorded.

```
Requirements → Design → Implementation → Integration → Testing / Evaluation → (issues found? back)
```

## 3.3 Requirements / Data Collection

Requirements came from (a) the gap in Chapter 1, (b) the three groups of users and what each needs to do, and (c) what the server offers. No interviews, surveys or usability sessions are recorded, so the requirements are the group's own analysis.

The analytics use the system's own records: reports, alerts, users and the audit log. Test data is synthetic. Screenshots of the running system (Chapter 4) were captured earlier from the live application with demonstration accounts.

## 3.4 System Architecture / Research Workflow

![Figure 3.1: SVDS system architecture](../assets/diagrams/04-system-design-1.png)

The front end is one of three independent processes; it talks to the backend by HTTPS/JSON with a Bearer token and by WebSocket for alerts.

## 3.5 Tools and Technologies

| Area | Technology |
|---|---|
| Front end | React 18.2, React Router 6.22, Axios 1.6 (the only runtime dependencies) |
| Build and dev server | Vite 5 with `@vitejs/plugin-react`; dev server on port 5173 |
| Styling | One hand-written stylesheet (`styles.css`, 1,084 lines) plus inline styles on the login and register pages |
| Charts | Hand-made with CSS (bars, conic-gradient donut); no charting library |
| Analytics queries | SQLAlchemy aggregate queries in FastAPI routes |
| Testing | pytest with FastAPI `TestClient`; Python's standard-library tracing for approximate line coverage |
| Browser check | Headless Chrome driven over the DevTools Protocol from a short Python script |
| Documentation and start-up | `README.md`, `run-all.ps1` |
| OS | Windows 11 |

## 3.6 Ethical and Legal Considerations

- **Personal data on screen.** Pages show names, telephone numbers, plates and locations. Server-side role checks decide who receives them; the interface's guards only avoid showing controls that would fail.
- **Token storage.** The token is kept in the browser's `localStorage` (readable by any script running on the page). React escapes displayed text and the code does not use `dangerouslySetInnerHTML`, which lowers, but does not remove, the risk.
- **Analytics honesty.** Statistics can mislead officers and the public if they are wrongly defined or drawn. §6.4 records where they can.
- **Accessibility.** Fields without associated labels are hard for screen-reader users; this was checked on the login page (§6.4).
- **Responsible testing.** The browser check used a made-up email address and password, which the server rejected; nothing was written to the database. Probes ran on an in-memory database. Servers started for the check were stopped afterwards.
- **Test data.** Tests use synthetic names and plates.

## 3.7 Evaluation Method

1. **Build check:** run the production build and record its output.
2. **Automated tests:** run the 31-test backend suite and 8-test node suite; measure line coverage of the backend package.
3. **Browser check:** start the backend and dev server, drive headless Chrome through a failed login, and record what appears and what network calls are made.
4. **Analytics probes:** temporary tests with edge-case data to see what each analytics endpoint returns.
5. **Code review** of the pages for error handling, keys, labels and search behaviour.
6. **Objective-by-objective review** against U1 to U8 in §1.4.

Not done: cross-browser, mobile, load, screen-reader or user evaluation.

## 3.8 Chapter Summary

The interface and analytics were built against the live API and checked by running the build, the tests, a scripted browser session and edge-case probes. What was and was not observed is stated in Chapter 6.

# Chapter 1: Introduction

## 1.1 Background and Context

Vehicle theft is a persistent problem for law enforcement in Zambia. Recovering a stolen vehicle depends heavily on chance: an officer happens to recognise a plate number from a paper report or a radio bulletin. Reports are kept on paper or in disconnected spreadsheets, so a report filed at one station is invisible to an officer elsewhere.

This report describes **SVDS**, the Stolen Vehicle Detection System, built by a group of four students on top of the **VRRS** registry. The public files stolen-vehicle reports, a camera node reads plates from a phone's video stream and checks them against active reports, and police officers are alerted.

None of this is usable unless people can reach it. Members of the public need a simple way to file and follow a report; officers need to search reports, activate them, mark vehicles recovered and act on alerts; administrators need to manage accounts and the system. Someone also has to show whether the system is *working and effective*, with statistics that are true, and to check that the parts of the system do what they claim. That is the work of the **frontend, analytics, testing and documentation** component, and this is the individual report of the student responsible for it.

## 1.2 Problem Statement

A registry that only its developers can operate does not solve the problem. The specific problems are:

1. **Access.** Three different groups of people (public, police, administrators) need three different, role-appropriate ways into the same data, on an ordinary browser.
2. **Insight.** Police and administrators need statistics (reports by status, recovery rate, recovery time, detections, alert confidence) that are computed from real records and are not misleading.
3. **Assurance.** The group needs evidence that the system behaves as intended, and a way to repeat that check as the code changes.
4. **Usability of the project itself.** Others must be able to install, run and understand the system.

## 1.3 Project Aim

**Group aim.** To design, implement and evaluate SVDS: a vehicle registry and reporting web application integrated with a real-time, camera-based licence plate detection pipeline, for the Zambia Police Service and the public it serves.

**Individual aim (Frontend, analytics, testing and documentation).** To build the three role-based web portals and the analytics that feed them, to verify the system with automated tests, and to document how to run it, and to evaluate these honestly.

## 1.4 Project Objectives

### Group objectives

1. Role-based accounts (Reportee, Police, Admin) with scoped access.
2. Public filing and tracking of stolen-vehicle reports.
3. A live view of alerts, the registry and analytics for police.
4. Administrator control of accounts, system health and the audit trail.
5. Detection and reading of plates from a live camera feed, matched against active reports.
6. Real-time alerts to connected police clients.

### Individual objectives (Frontend, analytics, testing and documentation)

| No. | Objective | Measure of success |
|---|---|---|
| U1 | Build a single-page web application with separate Reportee, Police and Admin portals and route guards that mirror the server's roles | Fourteen pages; each role sees only its own navigation |
| U2 | Let the public register, log in, file a report, view their reports and edit their profile | The flows work against the real API |
| U3 | Let police search and filter the registry, activate reports, mark vehicles found, and review and clear alerts | The flows work against the real API |
| U4 | Let administrators manage users and view the audit log and system health | The flows work against the real API |
| U5 | Provide analytics endpoints and a page whose numbers are computed from real records, including correct handling of mixed confidence scales | Values match the data in tests |
| U6 | Verify the system with an automated test suite and measure how much of the backend it exercises | Suite passes; coverage measured |
| U7 | Document how to install and run the system, and provide a run script | Written guide and one-command start |
| U8 | Evaluate the interface and analytics honestly and record defects | Build verified; a browser check; findings listed |

## 1.5 Research Questions

1. Can a single-page application with client-side route guards give each role only the interface it needs, while leaving the real enforcement to the server?
2. Are the analytics figures shown to users correct and unambiguous, and where are they not?

## 1.6 Scope of the Project

### 1.6.1 In Scope

- **This report:** the React front end (14 pages, shared layouts, contexts, API client), the analytics endpoints and the page that shows them, the confidence-scale normalisation fix, the backend and node automated tests as a body of evidence, and the run script and documentation.
- **Group:** the whole system.

### 1.6.2 Out of Scope

- The detection model and camera node (AI/vision member).
- Authentication, roles, the data model and report rules on the server (backend member).
- The WebSocket alert channel, camera status, feed proxy and health endpoint (real-time member). The pages consume them, but their design is covered in that member's report.
- A native mobile app, accessibility certification and internationalisation.

## 1.7 Significance of the Project

The interface is how the Zambia Police Service and the public meet the system. A clear reporting flow makes reports more complete, and an honest analytics page tells officers whether the system is actually recovering vehicles. A test suite and written instructions let the system be maintained after the students leave.

## 1.8 Limitations

- **No automated front-end tests.** The interface was checked by building it, reading the code and one scripted browser session; there is no unit, component or browser test suite.
- **Limited browser evidence.** One scripted headless-browser check (the login failure in §6.4) was run for this report. Fifteen screenshots of the running application were captured earlier. No cross-browser, mobile or screen-reader testing was done.
- **Coverage is approximate.** Line coverage was measured with a small tracer built on Python's standard library because the usual coverage tool could not be installed offline; figures may differ slightly from the standard tool.
- **No user evaluation.** No member of the public or officer used the interface for this report.
- **Test authorship.** The tests exercise other members' code; who wrote each file should be confirmed by the student (Appendix A).

## 1.9 Organisation of the Report

Chapter 2 reviews single-page applications, client-side access control, analytics and testing concepts. Chapter 3 describes the method and tools. Chapter 4 gives the analysis and design. Chapter 5 describes the implementation. Chapter 6 presents testing, browser findings and analytics checks. Chapter 7 discusses them, Chapter 8 concludes, and the appendices contain the contribution statement, user manual, extra designs, test evidence and code.

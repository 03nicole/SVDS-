# Appendix A: Individual Contribution Statement (Group Projects)

## Purpose of this Statement

This statement identifies the work for which the student was primarily responsible. It is consistent with the main report. Work by other group members is acknowledged and is not claimed.

## A.1 Project and Group Information

| Item | Details |
|---|---|
| Project Title | SVDS: A Camera-Based Stolen Vehicle Detection System for the Zambia Police Service (built on the VRRS registry) |
| Student Name | [STUDENT NAME] |
| Computer Number | [COMPUTER NUMBER] |
| Supervisor | [SUPERVISOR NAME] |
| Group Size | 4 |
| Group Members | 1. Moomba Nicholas Katapazi, [COMPUTER NUMBER] (AI/vision)<br/>2. [NAME], [COMPUTER NUMBER] (Backend and security)<br/>3. [NAME], [COMPUTER NUMBER] (Real-time and integration)<br/>4. [STUDENT NAME], [COMPUTER NUMBER] (Frontend, analytics, testing and documentation) |

## A.2 Overall Group Project

The group built **SVDS/VRRS**, a system with which the public files stolen-vehicle reports and police officers are alerted automatically when a camera sees a reported vehicle. It has three independently running processes: a FastAPI and PostgreSQL backend, a React frontend with three role-based portals (Reportee, Police, Admin), and a camera node that reads number plates from a phone's video stream using a custom-trained YOLOv8 detector and OCR. The common problem is that stolen-vehicle recovery depends on officers chancing to recognise a plate. The core flow is: the camera node reads a plate, the backend matches it against active reports, and connected police dashboards receive an alert over WebSocket.

## A.3 Individual Role and Responsibilities

The group's work was divided into four roles. The student's role was **Role 4: Frontend, analytics, testing and documentation**.

| No. | Area of Responsibility | Description |
|---|---|---|
| 6 | Frontend (three portals) | The React web application with role-based routing: Reportee, Police and Admin portals |
| 7 | Analytics, testing and documentation | Real computed statistics and charts; the automated tests as evidence; bug fixes; README and run script |

Other roles, for reference: **Role 1** AI/vision; **Role 2** Backend and security; **Role 3** Real-time and integration.

## A.4 Detailed Individual Contribution

- **Front end:** built the routing and guards, the API module, the shared layouts, the stylesheet and the fourteen pages.
- **Analytics:** wrote the seven analytics endpoints and the analytics page, and fixed the mixed confidence-scale defect with two regression tests.
- **Testing:** ran and interpreted the 39-test suites, measured backend line coverage, ran a scripted browser check, and ran analytics probes.
- **Documentation:** the README and the start-up script; audited the README against the code.
- **Evaluation:** recorded the findings U-1 to U-11 and D-1 to D-4 with evidence.
- **Report:** this report.

## A.5 Individual Deliverables

| No. | Deliverable | Student's Contribution |
|---|---|---|
| 1 | React front end (`vrrs-frontend/src`, 24 files, 1,786 lines, plus `styles.css`) | Designed and implemented |
| 2 | Analytics endpoints and page (`routers/analytics.py`, `Analytics.jsx`) | Designed and implemented |
| 3 | Confidence-scale fix and its two regression tests | Diagnosed, fixed, tested |
| 4 | README and `run-all.ps1` | Written (start-up script also described in the real-time member's report) |
| 5 | Coverage measurement and interface/analytics/documentation evaluation | Carried out and documented |

## A.6 Contribution to the Main System or Research Output

The student produced the part of the system that people use directly, and the statistics and tests that show whether it works. The server rules, tokens and data model were built by the backend member; the alert channel, camera status and health endpoint by the real-time member; the detection model and camera node by the AI/vision member. The alert connection and toast live in the front end's files but were written by the real-time member.

## A.7 Individual Implementation and Technical Work

Modules implemented by the student: `App.jsx`, `main.jsx`, `AuthContext.jsx`, `ProtectedRoute.jsx`, `PortalLayout.jsx`, `ReporteeLayout.jsx`, `policeNav.js`, `services/api.js` (except `createAlertSocket`), the reportee, police and admin pages, `styles.css`, and `routers/analytics.py`.

## A.8 Individual Testing and Evaluation Contribution

The student ran the 31-test backend suite and the 8-test node suite, measured coverage, ran the browser check and the analytics probes, and wrote Chapter 6. The two analytics regression tests belong to this component. **The student should state which of the remaining test files they wrote themselves**, because the role split assigned tests to this role but the suites also test other members' code.

## A.9 Collaboration with Other Group Members

- The **backend member's** API and token are what every page calls; the login response drives the redirect.
- The **real-time member's** alert connection, toast and status pages are mounted and shown by this front end.
- The **AI/vision member's** node stores confidence as a percentage, which the analytics normalisation assumes.

## A.10 Contribution Summary

1. **Work primarily completed by the student:** the front end, the analytics endpoints and page, the confidence fix and its tests, the README, and the evaluation.
2. **Work completed jointly with other members:** the run script (with the real-time member); the analytics numbers' consistency with the camera node's confidence scale (with the AI/vision member).
3. **Work primarily completed by other members and used here:** the server rules and tokens; the alert channel and camera status; the detection model and camera node.

## A.11 Estimated Contribution

*The percentages below are the student's own estimate and must be completed by the student. They were not derived from any record.*

| Project Activity | Individual Contribution | Collaborative Contribution |
|---|---|---|
| Problem Analysis | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Literature Review | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Requirements Analysis | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| System/Research Design | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Implementation / Development | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Testing and Evaluation | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Documentation | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Other | <span class="todo">[%]</span> | <span class="todo">[%]</span> |

## A.12 Statement of Authorship and Contribution

I confirm that the contribution described in this statement accurately represents the work that I personally undertook as part of the group project. I have identified collaborative work and have not knowingly claimed the work of another group member as my own.

**Student Name:** ______________________
**Computer Number:** ______________________
**Signature:** ______________________
**Date:** ______________________

## A.13 Supervisor Verification

I confirm that, to the best of my knowledge, the contribution described above is consistent with the student's participation in the group project.

**Supervisor Name:** ______________________
**Signature:** ______________________
**Date:** ______________________

<div class="plain-title">ABSTRACT</div>

Stolen-vehicle recovery in Zambia depends largely on police officers chancing to recognise a plate number from a paper report or radio bulletin. This project, carried out by a group of four students, built SVDS, a Stolen Vehicle Detection System on top of the VRRS vehicle registry. The public files stolen-vehicle reports through a web application, and a camera node reads plates from a phone's video stream and checks them against active reports, so connected police officers are alerted in real time.

This individual report covers the backend and security component: the FastAPI service, its PostgreSQL data model, and its authentication and access control. The backend has four tables (users, reports, alerts, audit log), stores passwords as bcrypt hashes, issues signed JSON Web Tokens that carry the user's role, and enforces three roles (reportee, police, admin) on the server with reusable dependencies plus per-report ownership rules. It implements the report lifecycle (under review, missing, found), an audit trail, and the endpoint the camera node calls to ask whether a plate is stolen, which matches plates regardless of case and spacing.

The backend was verified with 31 automated tests, all of which pass, run against an in-memory SQLite database. Targeted probe tests then confirmed weaknesses that the tests did not cover: tokens remain valid after a user is deactivated, demoted or logged out; report status accepts arbitrary values; the public plate-check endpoint can be called repeatedly to create false alerts; and failed logins are not limited. These findings are documented with recommended fixes and have not been fixed in this project. The report concludes that the backend meets its access-control goals for tokens as issued but should not be used with real police data until the recommendations are applied.

**Keywords:** role-based access control; JSON Web Token; FastAPI; PostgreSQL; API security

**Note on the version of the code evaluated.** All findings, test counts, coverage figures and line counts in this report were obtained against the code as committed (commit `a349fc6`). After that evaluation, uncommitted changes appeared in the working tree (`middleware.py`, `alerts.py`, `system.py`, `main.py`, `api.js`, `SystemHealth.jsx`, `conftest.py`, a new `tests/test_regressions.py` and a new front-end test). With those changes the backend suite has **38 tests, all passing**, and the front end has **one** test (`npm test`), which also passes. The changes appear to address the items listed below; this was established by reading the changes and running the tests, and the original probes were **not** re-run against the changed code. Where this report says a finding was "not fixed", it refers to the evaluated commit.

*Appear addressed in the working tree:* **F-1** and **F-2** (every request now re-reads the user from the database, so a deactivated or demoted user's old token is rejected, and the role comes from the database, not the token) and **F-9** (`CORS_ORIGINS` is now read). *Still open as far as the changes show:* F-3, F-4, F-5, F-6, F-7 (logout does not end a session by itself), F-8 and F-10.

<div class="plain-title">ACKNOWLEDGEMENTS</div>

<span class="todo">[Write acknowledgements here: supervisor, group members (AI/vision, real-time and integration, frontend), family, and anyone who helped collect plate images. The author must write this; it is personal.]</span>

<div class="plain-title">CONTENTS</div>

**Preliminary pages:** Declaration · Approval · Abstract · Acknowledgements · List of Abbreviations and Acronyms · Note on Group Projects

**1 Introduction** — 1.1 Background and Context · 1.2 Problem Statement · 1.3 Project Aim · 1.4 Project Objectives · 1.5 Research Questions · 1.6 Scope of the Project (In Scope, Out of Scope) · 1.7 Significance · 1.8 Limitations · 1.9 Organisation of the Report

**2 Literature Review** — 2.1 Introduction · 2.2 Key Concepts and Theories · 2.3 Existing Systems / Related Work · 2.4 Comparative Analysis · 2.5 Research / Knowledge Gap · 2.6 Conceptual Framework · 2.7 Chapter Summary

**3 Methodology** — 3.1 Introduction · 3.2 Research / Development Approach · 3.3 Requirements / Data Collection · 3.4 System Architecture / Research Workflow · 3.5 Tools and Technologies · 3.6 Ethical and Legal Considerations · 3.7 Evaluation Method · 3.8 Chapter Summary

**4 System Analysis and Design** — 4.1 Introduction · 4.2 Stakeholder and User Analysis · 4.3 Functional Requirements · 4.4 Non-Functional Requirements · 4.5 Use Cases / User Stories · 4.6 System / Solution Architecture · 4.7 Database / Data Design · 4.8 Interface / Interaction Design · 4.9 Algorithms / Models / Technical Design · 4.10 Chapter Summary

**5 Implementation / Development** — 5.1 Introduction · 5.2 Development Environment · 5.3 System Components / Modules · 5.4 Key Implementation Details · 5.5 Integration · 5.6 Challenges and Solutions · 5.7 Individual Contribution · 5.8 Chapter Summary

**6 Testing, Results and Evaluation** — 6.1 Introduction · 6.2 Testing Strategy · 6.3 Test Cases and Results · 6.4 Experimental / Performance Results · 6.5 User Evaluation · 6.6 Analysis of Results · 6.7 Objective-by-Objective Evaluation · 6.8 Individual Results · 6.9 Chapter Summary

**7 Discussion** — 7.1 Introduction · 7.2 Interpretation of Findings · 7.3 Comparison with Existing Work · 7.4 Contributions of the Project · 7.5 Limitations and Implications · 7.6 Chapter Summary

**8 Conclusion and Recommendations** — 8.1 Introduction · 8.2 Summary of the Project · 8.3 Conclusions · 8.4 Achievement of Objectives · 8.5 Recommendations · 8.6 Future Work

**References**

**Appendices** — A Individual Contribution Statement · B User Manual / Installation Guide · C Additional System Designs / Diagrams · D Additional Test Cases and Results · E Data Collection Instruments · F Additional Code / Configuration · G Other Supporting Material

<span class="todo">[Page numbers are not shown here. In Word, apply heading styles and use References → Table of Contents to generate a numbered contents page, and a List of Figures and List of Tables the same way.]</span>

<div class="plain-title">LIST OF ABBREVIATIONS AND ACRONYMS</div>

| Abbreviation | Meaning |
|---|---|
| ALPR | Automatic Licence Plate Recognition |
| API | Application Programming Interface |
| CUDA | Compute Unified Device Architecture (NVIDIA GPU computing platform) |
| CORS | Cross-Origin Resource Sharing |
| ORM | Object-Relational Mapper |
| OWASP | Open Worldwide Application Security Project |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| DBMS | Database Management System |
| GPU | Graphics Processing Unit |
| HTTP | Hypertext Transfer Protocol |
| IoU | Intersection over Union |
| JWT | JSON Web Token |
| mAP | mean Average Precision |
| MJPEG | Motion JPEG (video stream format) |
| ML | Machine Learning |
| OCR | Optical Character Recognition |
| SVDS | Stolen Vehicle Detection System |
| UI | User Interface |
| VRRS | Vehicle Registry and Reporting System |
| YOLO | You Only Look Once (object detector family) |

<div class="plain-title">NOTE ON GROUP PROJECTS</div>

Students who worked on a project as a group are strongly encouraged to prepare their own individual final reports rather than submitting identical reports. The project, system, dataset, or overall research problem may be shared, but each student's report should clearly demonstrate that student's own understanding, responsibilities, work, results, and contribution to the project.

In particular, group-project students should:

- state the overall group project and explain how the individual work fits within it;
- clearly identify their own responsibilities and deliverables;
- focus detailed analysis, design, implementation, experiments, testing, and/or evaluation on their own contribution;
- acknowledge the work completed by other group members where it is discussed;
- include an *Individual Contribution Statement* in the appendices; and
- not claim another group member's work, results, code, data collection, or design decisions as their own.

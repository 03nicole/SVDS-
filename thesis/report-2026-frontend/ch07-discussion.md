# Chapter 7: Discussion

## 7.1 Introduction

This chapter interprets the results of Chapter 6, compares them with related practice, states the contributions, and discusses limitations.

## 7.2 Interpretation of Findings

**Research question 1** (can a single-page application with client-side guards give each role only the interface it needs, while the server stays the authority?). Yes for the structure: fourteen routes, each with an explicit role list that mirrors the server's, and navigation that differs by role. The guards are convenience, not security, and the code does not pretend otherwise; the backend report shows where server-side enforcement itself has gaps.

**Research question 2** (are the analytics correct and unambiguous?). Correct on the cases tested, not unambiguous. Counts, recovery time and the normalised confidence average behaved as expected. But several figures depend on choices a reader cannot see: what the recovery rate divides by, whether false alerts are in the confidence average, whether a stored 1.0 is 1% or 100%, and whether an empty month is shown. Two of these (U-6 and U-8) can produce a picture that looks right and is not.

**Bugs live between files.** The login failure (U-1) is not a mistake in the login page or in the API module taken alone. Each does something reasonable: the page shows the server's message, and the API module logs out on a 401. Together they erase the message. It was found by running the application, not by reading the code. This is the main argument for the missing front-end and browser tests: the interface's faults are interactions, and only interaction tests find them.

**Coverage tells where to look, not how good the tests are.** A 63.6% approximate line coverage with 100% on models and schemas sounds reassuring, but those files mostly run just by loading the application. The informative numbers are the low ones: user management at 27% and system routes at 32%. Those are also routes where the other members' reports found real weaknesses (stale tokens, an open health endpoint), which is consistent with untested code hiding defects.

**Documentation is a second interface.** The README's instruction to set `CORS_ORIGINS` is worse than no instruction, because it sends a deployer to a setting that does nothing and gives no sign of failure until the front end is blocked in the browser.

## 7.3 Comparison with Existing Work

No numeric comparison was made. Against the component-library route in Chapter 2, this project has fewer dependencies and a small bundle, and pays for it in hand-written charts that lack the guarantees a charting library gives (proportional bars, empty periods, axes), and in no accessibility support beyond what was hand-coded. Against typical practice for web applications, a front end with no automated tests is common in student work and is the largest gap here.

## 7.4 Contributions of the Project

- **Practical:** three role-based portals in fourteen pages; analytics computed from real records; a single-command start and a written quick-start; a body of 39 passing tests.
- **Technical:** a shared confidence-normalisation expression that fixed a real defect and is regression-tested; a small, dependency-light front end (four runtime packages, 82 kB gzipped JavaScript).
- **Analytical:** a list of front-end, analytics and documentation defects with evidence, including one confirmed in a real browser, and a measured coverage profile of the backend that shows where testing is thin.

## 7.5 Limitations and Implications

| Limitation | Implication |
|---|---|
| One scripted browser check only | Other pages may have defects not found; U-4 and U-5 are from reading, not running |
| Approximate coverage from a home-made tracer | Figures may differ slightly from coverage.py; treat as indicative |
| No front-end tests | Every front-end claim rests on inspection or one session |
| No user evaluation | Usability judgements are the student's own |
| Severity ratings are the student's own | Not a formal scale |
| Findings not fixed | The delivered system still has them |
| Screenshots are from an earlier session | They show the interface as it was then |

## 7.6 Chapter Summary

The front end and analytics work and are lightweight, and their weaknesses lie in interactions, presentation and documentation, not in the core computations. A running application found what reading did not, which argues for interaction tests and for keeping documentation under test.

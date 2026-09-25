# Chapter 8: Conclusion and Recommendations

## 8.1 Introduction

This chapter summarises the project, states the conclusions the evidence supports, reviews the objectives, and gives recommendations and future work.

## 8.2 Summary of the Project

The group built SVDS so that stolen-vehicle reports filed by the public can be matched against plates seen by a camera. This report covered the front end, analytics, testing and documentation: a React single-page application with three role-based portals (fourteen pages), seven analytics endpoints and the page that displays them, a fix for mixed confidence scales, an automated test base of 39 tests, and a README and run script. It was evaluated by a production build, the test suites, an approximate coverage measurement, a scripted browser check and analytics probes.

## 8.3 Conclusions

1. A small hand-written React application can give each role its own portal, with guards that mirror the server's roles, using four runtime packages and about 82 kB of gzipped JavaScript.
2. The analytics compute real figures from stored records and are correct on the cases tested, after the confidence-scale defect was fixed and regression-tested.
3. The backend test suite passes and exercises about 64% of the backend's lines, unevenly: authentication and models well, user management and system routes poorly.
4. The interface has real defects: a wrong password gives no error message (confirmed in a browser), several page loads fail silently, some charts mislead, and the login form's labels are not associated with its fields.
5. The documentation contains instructions that no longer match the code, including one that would break a deployment.
6. The system is not yet at the standard where it can be handed to users without a fix pass, and it has no automated interface tests to protect such a pass.

## 8.4 Achievement of Objectives

| Objective | Status |
|---|---|
| U1 Role-based portals with guards | Achieved; guards not browser-tested |
| U2 Reportee flows | Largely achieved; failed-login feedback broken |
| U3 Police flows | Largely achieved; load errors unhandled |
| U4 Admin flows | Achieved in implementation; weakly tested |
| U5 Correct analytics | Largely achieved; presentation and definition issues |
| U6 Tests and coverage | Achieved for the backend; not for the front end |
| U7 Documentation and run script | Partly achieved |
| U8 Honest evaluation | Achieved for this scope |

Research question 1: yes. Research question 2: correct on the cases tested, not unambiguous.

## 8.5 Recommendations

In priority order:

1. **Fix the login feedback:** apply the 401 redirect only when the request was not the login call (or when a token existed), so a wrong password shows its message (U-1, U-2).
2. **Correct the README:** remove or fix the `CORS_ORIGINS` instruction (and make the backend read it), add first-administrator creation, the run script, the tests and the phone camera setup, and correct the camera example (D-1 to D-3).
3. **Handle failures on every data load** with an error message and a Retry, as the Analytics page already does (U-4).
4. **Fill empty periods and make bars proportional** (start at zero, scale to the maximum), or use a charting library (U-6). Label the definitions of recovery rate and average confidence on screen (U-8, U-10).
5. **Record false-positive flags in a column** on the alert, and count that instead of searching audit text (U-9). Store confidence on one scale and migrate the old rows so the normalisation heuristic can be removed (U-8).
6. **Group detections by camera id** (with the latest location), not by camera and location text (U-7).
7. **Associate every form label with its input** and add labels to the login page (U-3).
8. **Add tests where coverage is lowest:** user management and system routes on the backend, then component tests for the guards and forms and one browser test of the login failure (U-11).
9. **Debounce the registry search** and ignore stale responses (U-5).
10. **Remove the absolute path from `run-all.ps1`** (D-4).

## 8.6 Future Work

- Add continuous testing (run the suites and the build on each change).
- Add browser tests for each role's main task using a tool such as Playwright.
- Add a proper charting library, with accessible chart descriptions.
- Measure real usability with officers and members of the public.
- Add pagination totals and export of analytics for reporting.
- Support English and local languages.

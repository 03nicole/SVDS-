# Chapter 8: Conclusion and Recommendations

## 8.1 Introduction

This chapter summarises the project, states the conclusions the evidence supports, reviews the objectives, and gives recommendations and future work.

## 8.2 Summary of the Project

The group built SVDS so that stolen-vehicle reports filed by the public can be matched automatically against plates seen by a camera. This report covered the backend and security component: a FastAPI service over a four-table PostgreSQL model, with bcrypt password hashing, signed role-carrying tokens, server-side role checks, a report lifecycle, a plate-match endpoint for the camera node, and an audit trail. It was verified by 31 automated tests (40 after a later fix) and by targeted security probes that were re-run after the fix.

## 8.3 Conclusions

1. Server-side role-based access control with a signed token is achievable with a small amount of code and behaves correctly under test.
2. Passwords are stored as bcrypt hashes and the reportee, police and admin roles are separated as designed.
3. The plate-match endpoint works across case and spacing differences and matches only active reports.
4. The evaluated design had confirmed weaknesses. Tokens outliving deactivation and demotion was fixed and re-verified. Seven of the ten recorded findings remain open: F-3 (status validation), F-4 (public repeated alerts), F-5 (duplicate pending reports), F-6 (login throttling), F-7 (logout), F-8 (default signing-key fallback) and F-10 (administrator seed defaults). Four of these, F-3, F-4, F-6 and F-7, were re-demonstrated in the recorded post-fix probes.
5. The system is a good prototype and is **not** ready for production use with real police data until the recommendations below are addressed.

## 8.4 Achievement of Objectives

| Objective | Status |
|---|---|
| B1 Data model | Achieved (no migrations) |
| B2 Authentication and password storage | Achieved; logout revocation and lockout missing |
| B3 Server-side role enforcement | Achieved; stale-role weakness fixed and re-verified |
| B4 Report lifecycle and ownership | Largely achieved; status validation and duplicate check incomplete |
| B5 Plate-match endpoint | Achieved; public and unthrottled |
| B6 Audit records | Largely achieved; failed logins not recorded |
| B7 Verification and security review | Achieved for this scope |

Research question 1: yes. Research question 2: ten weaknesses were found and recorded; three (F-1, F-2, F-9) have been fixed and re-verified, seven are open.

## 8.5 Recommendations

In priority order:

1. **Done for deactivation and demotion (F-1, F-2):** protected requests now re-check the user. **Still to do for logout (F-7):** implement token revocation (for example a deny-list or session version). Short token lifetimes and refresh-token rotation reduce exposure but do not by themselves invalidate an issued access token immediately.
2. **Validate report status** with an enumeration in the schema and a database check constraint, and route status changes through the lifecycle endpoints only (F-3). Add a database constraint for `role` as defence in depth; registration and admin role changes already restrict values in route code.
3. **Protect `check-plate`** with an API key or a private network, and add rate limiting and de-duplication of repeated alerts (F-4).
4. **Throttle failed logins**, log them in the audit trail, and adopt an appropriate minimum length and a common/compromised-password block-list; avoid mandatory character-type composition rules (F-6) [15].
5. **Fail at start-up if `SECRET_KEY` is unset** instead of using a default (F-8), (allowed origins are now read from configuration, F-9).
6. Remove the default password from `create_admin.py`, require `ADMIN_PASSWORD`, and stop printing it (F-10).
7. Extend the duplicate check to `under_review` reports (F-5).
8. Adopt Alembic migrations and run the test suite against PostgreSQL.
9. Validate email addresses, and apply the registration formats to profile edits.
10. Write the audit row in the same transaction as the action it records.

## 8.6 Future Work

- Fix the open findings above and turn each remaining probe into a permanent regression test, as was done for F-1 and F-2.
- Add multi-factor authentication for police and admin accounts.
- Add a structured penetration test and a load test.
- Add pagination totals and stronger search to the report lists.
- Move blocking database calls out of `async` routes, or use an async database driver.
- Define data retention and access-request rules that meet Zambian data protection requirements.

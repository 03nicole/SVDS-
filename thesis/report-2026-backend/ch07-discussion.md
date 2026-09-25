# Chapter 7: Discussion

## 7.1 Introduction

This chapter interprets the results of Chapter 6, compares them with related practice, states the contributions, and discusses limitations.

## 7.2 Interpretation of Findings

**The access-control design works as specified.** Every protected route rejects a missing token, and the role matrix behaves as designed. Reportees cannot read each other's reports, only administrators can delete, and administrators cannot lock themselves out. This answers research question 1 in the affirmative: role-based access can be enforced consistently on the server, using a signed token to identify the account and the current database row to authorise access, without relying on the front end. Public endpoints remain exceptions, including `/system/health`, which exposes operational metrics without a role dependency.

**Current account checks fix stale access, but not logout.** In the initial evaluation at `a349fc6`, a token retained the role and account access it had when issued. Since `b326b21`, `resolve_token_user` validates the token and re-reads the database user; inactive or deleted accounts are refused, and authorisation uses the current database role. HTTP routes check this on each protected request, while WebSockets check at connection, on received messages and before broadcasts. Logout still only returns a message and invalidates neither the token nor a server-side session. F-1 and F-2 are fixed; F-7 remains open. Database revalidation adds a lookup, while token-specific logout requires a separate revocation mechanism.

**Validation is thinner than authorisation.** The role checks are consistent, but free-text `status` and `role` columns, a plain-string email field and an unvalidated status update let bad values in from people who are already trusted. This is typical of a first version: access control was designed carefully because it is the headline requirement, and data validation was left to the front end.

**The public camera endpoint is the sharpest design trade-off.** Making `check-plate` public keeps the camera node simple, and it cannot create or edit reports. But it lets anyone who can reach the server, and who knows or guesses an active plate, generate real-looking alerts on police screens. The risk is bounded by network placement, which the code does not enforce.

## 7.3 Comparison with Existing Work

No comparison of measured results with other systems was made, because none of the systems reviewed in Chapter 2 publish comparable security test results for a stolen-vehicle registry. On design, this backend implements a small version of what hosted identity providers and mature frameworks provide (hashing, signed tokens, roles) and lacks what they add (revocation, refresh tokens, multi-factor authentication, rate limiting). That is the expected difference between a student prototype and a hardened service. The historical review uses the OWASP Top 10:2021 and API Security Top 10:2023 as organising references [8], [14]. The findings broadly concern access control, authentication, configuration and input validation; this is a qualitative mapping, not an OWASP certification or a complete assessment.

## 7.4 Contributions of the Project

- **Practical:** a working, documented API with role-scoped access, a report lifecycle, an audit trail and a plate-match endpoint that tolerates formatting differences.
- **Technical:** an access-control layer expressed once as reusable dependencies; a test set-up that runs the production PostgreSQL query on SQLite and checks the cascade.
- **Analytical:** ten recorded findings, supported by the historical probe output, retained regression tests and code inspection. Not every finding came from a probe, and the temporary probe files are not retained.

## 7.5 Limitations and Implications

| Limitation | Implication |
|---|---|
| Tests run on SQLite | Passing tests do not show PostgreSQL behaviour; the cascade fix and the dated schema catalogue inspection provide limited PostgreSQL evidence, not a PostgreSQL integration suite |
| Probes were written by the author of the code | They test the weaknesses the author thought of. Other weaknesses may exist |
| No penetration test or external review | The findings are a lower bound |
| No load testing | Behaviour under many simultaneous requests, including the `async`-with-blocking-code concern, is unknown |
| Severity ratings are the student's own judgement | They are not a formal scoring such as CVSS |
| Seven findings not fixed | The delivered system still contains F-3 to F-8 and F-10 (§8.5) |
| No stakeholder input | Requirements may miss needs of real officers |

## 7.6 Chapter Summary

The backend meets its access-control goals, and the tests show it; the stale-token weakness found in the first evaluation was fixed and re-verified. Its remaining weaknesses are concentrated in logout, input validation, login throttling and the public endpoint, and each was demonstrated or read from the code. They are documented here so they can be fixed, not hidden.

# Chapter 7: Discussion

## 7.1 Introduction

This chapter interprets the results of Chapter 6, compares them with related practice, states the contributions, and discusses limitations.

## 7.2 Interpretation of Findings

**The access-control design works as specified, for the token as issued.** Every protected route rejects a missing token, and the role matrix behaves as designed. Reportees cannot read each other's reports, only administrators can delete, and administrators cannot lock themselves out. This answers research question 1 in the affirmative: role-based access can be enforced consistently on the server, using a signed token that carries the role, without relying on the front end.

**The same design is what limits it.** Research question 2 asked what weaknesses remain. The main one is that the token is trusted for its whole lifetime. A deactivated officer or a demoted administrator keeps working until the token expires, and logging out does not end a session. These are not coding mistakes in the role checks; they follow directly from choosing stateless tokens without a revocation check. The fix is small (look up the user in the database on each request, or keep a token deny-list), but it costs one query per request, which is the trade the design originally avoided.

**Validation is thinner than authorisation.** The role checks are consistent, but free-text `status` and `role` columns, a plain-string email field and an unvalidated status update let bad values in from people who are already trusted. This is typical of a first version: access control was designed carefully because it is the headline requirement, and data validation was left to the front end.

**The public camera endpoint is the sharpest design trade-off.** Making `check-plate` public keeps the camera node simple, and it cannot create or edit reports. But it lets anyone who can reach the server, and who knows or guesses an active plate, generate real-looking alerts on police screens. The risk is bounded by network placement, which the code does not enforce.

## 7.3 Comparison with Existing Work

No comparison of measured results with other systems was made, because none of the systems reviewed in Chapter 2 publish comparable security test results for a stolen-vehicle registry. On design, this backend implements a small version of what hosted identity providers and mature frameworks provide (hashing, signed tokens, roles) and lacks what they add (revocation, refresh tokens, multi-factor authentication, rate limiting). That is the expected difference between a student prototype and a hardened service. The OWASP categories used as a checklist line up with the findings: broken access control (F-1, F-2), identification and authentication failures (F-6, F-7), security misconfiguration (F-8, F-9) and insufficient input validation (F-3).

## 7.4 Contributions of the Project

- **Practical:** a working, documented API with role-scoped access, a report lifecycle, an audit trail and a plate-match endpoint that tolerates formatting differences.
- **Technical:** an access-control layer expressed once as reusable dependencies; a test set-up that runs the production PostgreSQL query on SQLite and checks the cascade.
- **Analytical:** a verified list of what this style of design does *not* protect against, with a reproducible probe for each.

## 7.5 Limitations and Implications

| Limitation | Implication |
|---|---|
| Tests run on SQLite | Passing tests do not show PostgreSQL behaviour; the constraint and data-type behaviour of the real database was checked only for the cascade fix |
| Probes were written by the author of the code | They test the weaknesses the author thought of. Other weaknesses may exist |
| No penetration test or external review | The findings are a lower bound |
| No load testing | Behaviour under many simultaneous requests, including the `async`-with-blocking-code concern, is unknown |
| Severity ratings are the student's own judgement | They are not a formal scoring such as CVSS |
| Findings not fixed | The delivered system still contains them (§8.5) |
| No stakeholder input | Requirements may miss needs of real officers |

## 7.6 Chapter Summary

The backend meets its access-control goals for tokens as issued, and the tests show it. Its weaknesses are concentrated in token lifetime, input validation and the public endpoint, and each was demonstrated or read from the code. They are documented here so they can be fixed, not hidden.

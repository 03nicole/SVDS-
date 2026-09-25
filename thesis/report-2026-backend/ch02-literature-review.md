# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews the concepts behind the backend: resource-oriented APIs, relational data, password hashing, signed tokens, role-based access control and audit logging. It compares selected documented capabilities with the implemented prototype. Numbered references identify the sources; implementation claims are checked against the local repository.

## 2.2 Key Concepts and Theories

### 2.2.1 REST APIs and FastAPI

REST is an architectural style defined by constraints, not simply the use of HTTP verbs [10]. SVDS uses resource-oriented routes for reports, users and alerts, but this report does not establish full REST conformance. FastAPI supports typed request handling, dependency injection and generated interactive API documentation [1]. Pydantic models validate the declared input structure [4]. Validation is only as restrictive as those declarations and the route logic: declaring `status` as a string does not enforce a lifecycle.

### 2.2.2 Relational databases and ORMs

PostgreSQL provides relational tables and constraints [3]. SQLAlchemy maps application classes to database structures and supports ORM queries [2]. In this project, `create_all()` creates missing tables but is not a migration mechanism for altering an existing schema. This distinction matters to the dated model/database discrepancy reported in section 4.7.1. The SQLite test database exercises much of the application logic, but cannot establish every PostgreSQL-specific behaviour.

### 2.2.3 Password hashing

Password storage should use a purpose-built, salted password hash. The original bcrypt work describes an adaptable computation cost intended to make offline guessing more expensive as hardware improves [6]. Passlib provides the `CryptContext` interface used by this backend [7]. Hashing does not compensate for weak passwords or unrestricted online guesses. The six-character minimum and missing login throttling are assessed separately against NIST guidance in Chapter 6 [15].

### 2.2.4 JSON Web Tokens

RFC 7519 defines JWT claims, including the subject (`sub`) and expiry (`exp`) [5]. JWTs can be signed or encrypted; SVDS specifically uses signed HS256 tokens. A valid signature establishes that token contents have not been altered without the signing key; it does not establish that the account is still active or that its role is unchanged.

The initial backend trusted the role claim until expiry. The corrected backend also looks up the current account on protected requests and authorises using its database role. Its authorisation decisions therefore depend on current server-side state even though the credential is a JWT. Logout remains a separate issue: returning a success message does not revoke an already-issued token.

### 2.2.5 Role-based access control

RBAC assigns permissions through roles rather than defining each user's permissions independently [9]. SVDS has reportee, police and admin roles, with broader privileges for police and admin. These are implemented as explicit allowed-role sets, not a database role hierarchy. Row-level ownership checks additionally restrict reportee access to reports. Public endpoints remain outside these protected-route checks.

### 2.2.6 Audit logging

The project's audit table records selected account and report actions with actor and target identifiers. Such records support investigation, but the implemented trail is incomplete: failed logins are not logged, alert creation is not itself an audit-log entry, and several business changes and audit inserts use separate commits. An audit table alone therefore does not establish complete or atomic traceability.

## 2.3 Existing Systems / Related Work

- **Django REST framework** documents pluggable authentication approaches and related permission mechanisms [12]. Its authentication framework is a useful comparison; it is not evidence that a default installation meets this project's requirements.
- **Keycloak** documents central identity administration, session management, refresh tokens and configurable multi-factor authentication [13]. Those capabilities are broader than the project's login/JWT implementation. SVDS is not an OAuth 2.0 or OpenID Connect identity-provider equivalent merely because it issues JWTs.
- **OWASP Top 10:2021 and API Security Top 10:2023** provide the named risk taxonomies used to organise the review [8], [14]. They guide questions about access, authentication, configuration and resource use. Mapping findings to them does not constitute certification or an exhaustive assessment.
- **Police-system comparison:** no independently evaluated police registry was included. The report therefore makes no comparative security or recovery-performance claim about existing police systems.

## 2.4 Comparative Analysis

| Criterion | This project | Django REST framework | Keycloak |
|---|---|---|---|
| Authentication basis | Local passwords and signed JWTs | Pluggable authentication [12] | Configurable identity service [13] |
| Current-account checks | Added after initial findings | Depends on chosen authentication implementation | Session and account management available |
| Refresh / revocation | Not implemented | Depends on scheme or integration | Documented session/token capabilities |
| Multi-factor authentication | Not implemented | Requires chosen integration | Configurable |
| Production suitability | Not established; open findings | Depends on application and deployment | Depends on secure configuration and integration |

The table compares documented capabilities with code-observed features. No comparative performance measurements or setup-effort experiment was conducted. A library or identity provider does not, by itself, make a deployment secure.

## 2.5 Research / Knowledge Gap

The project's practical contribution is a working backend and a documented examination of its access-control behaviour in a stolen-vehicle reporting workflow. This is a project-specific engineering contribution, not a claim that the broader literature lacks JWT security analysis. The initial and corrected versions show why current-account checks, lifecycle validation and logout invalidation must be considered separately.

## 2.6 Conceptual Framework

The following is a conceptual view of a protected request, not a claim about the exact order of FastAPI's internal validation and dependency execution:

```
Request + token -> validate token -> read active database user
                -> apply current role and ownership rules
Validated input -> apply business rules -> database work -> response
Selected state changes -> audit insert (currently a separate commit)
```

CORS affects browser cross-origin access; it is not an authentication gate for all clients. Public endpoints do not follow the protected-request path. Authentication identifies the account, authorisation determines permitted actions, and input validation constrains data values.

## 2.7 Chapter Summary

The documented building blocks support the prototype, but their presence alone does not establish security. The review distinguishes a signed credential from current authorisation, input shape from business validation, and an audit table from complete traceability. The following chapters evaluate those distinctions using the project's code and test evidence.

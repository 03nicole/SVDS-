# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews the concepts and technologies behind the SVDS backend: REST APIs, token-based authentication, password hashing, role-based access control, relational data modelling and audit logging. It then looks at existing systems and identifies the gap. Section numbers follow the template.

## 2.2 Key Concepts and Theories

### 2.2.1 REST APIs and FastAPI

A REST API exposes resources (here: reports, users, alerts) at URLs and uses HTTP methods (`GET`, `POST`, `PATCH`, `DELETE`) to act on them. **FastAPI** is a Python framework that builds such APIs from type-annotated functions. It validates request bodies with **Pydantic** models and generates interactive documentation (Swagger UI at `/docs`). Its **dependency injection** mechanism lets a route declare what it needs (a database session, the current user), which is how access control is attached to routes in this project.

### 2.2.2 Relational databases and ORMs

A relational database stores data in tables linked by keys, and constraints (uniqueness, foreign keys, `ON DELETE CASCADE`) keep the data consistent. **PostgreSQL** is an open-source relational database. **SQLAlchemy** is an object-relational mapper (ORM): tables are described as Python classes and queries are written in Python. A weakness of `create_all()` schema creation, relevant here, is that it creates missing tables but never alters existing ones.

### 2.2.3 Password hashing

Passwords must never be stored in plaintext. A password *hash function* turns a password into a fixed string that cannot practically be reversed. General-purpose hashes are too fast; password hashing needs a deliberately slow, salted algorithm. **bcrypt** is such an algorithm: each hash includes a random salt and a cost factor, so identical passwords give different hashes and brute-force guessing is slow. The `passlib` library provides a `CryptContext` wrapper.

### 2.2.4 JSON Web Tokens

A **JSON Web Token (JWT, RFC 7519)** is a signed string carrying *claims*, such as the user id (`sub`), the role, and an expiry (`exp`). The server signs it with a secret key (here HMAC-SHA256, `HS256`) and can later verify that it was issued by the server and has not been altered, without a database lookup. This makes the server *stateless* about sessions. The trade-off is that a token stays valid until it expires, even if the user is later deactivated or demoted, unless the server adds extra checks.

### 2.2.5 Role-based access control

In **role-based access control (RBAC)**, permissions attach to roles and users are given roles. SVDS uses three, in a hierarchy: **reportee** (public) ⊂ **police** ⊂ **admin**. The principle of *least privilege* says each role should have only what it needs. Checks must run on the server: hiding a button in the user interface is not access control, because a client can send any request.

### 2.2.6 Audit logging

An **audit log** records who performed which significant action on what, and when. It supports accountability and later investigation, which matters in a police system where a report can be activated, altered or deleted.

## 2.3 Existing Systems / Related Work

- **Django REST Framework / Flask** are common Python alternatives. They offer built-in or add-on authentication and permission classes. FastAPI was chosen here for its automatic validation and documentation and for explicit dependency-based access checks.
- **OAuth 2.0 / OpenID Connect providers** (for example Keycloak or Auth0) provide hardened login, refresh tokens, revocation and multi-factor authentication. They are the mature answer for production but add a service to run and configure; this project implements a small self-contained equivalent.
- **The OWASP guidance** (the OWASP Top 10 and the API Security Top 10) lists the risks a system like this should be checked against: broken access control, cryptographic failures, identification and authentication failures, security misconfiguration, and excessive data exposure. The security review in Chapter 6 uses these categories as a checklist.
- **Police records systems** in the public domain are mostly closed. Published descriptions concentrate on data content, not on how access is enforced, so no detailed comparison is possible.

*Note on sources.* This chapter relies on the projects' public documentation and standards, listed in the References. No performance or security figures from other systems are quoted.

## 2.4 Comparative Analysis

| Criterion | This project (FastAPI + own JWT) | Django REST Framework | Hosted identity provider |
|---|---|---|---|
| Setup effort | Low | Medium | Medium to high |
| Token revocation / refresh | Not implemented | Available via add-ons | Built in |
| Multi-factor authentication | No | Add-on | Built in |
| Understandable end to end by a student team | Yes | Yes | Less (external service) |
| Suitable for production as is | No (see Chapter 6) | With configuration | Yes |

The table compares design properties, not measured performance.

## 2.5 Research / Knowledge Gap

Tutorials show how to add JWT login to FastAPI, but rarely show a *verified* account of what such a design does and does not protect against. The gap this report addresses is a working, tested role-based backend for a stolen-vehicle registry, together with **demonstrated** (not assumed) limitations of the token design.

## 2.6 Conceptual Framework

The backend follows a layered flow in which each request passes the same gates:

```
HTTP request → CORS check → JWT decoded (get_current_user)
             → role check (require_role) → input validation (Pydantic)
             → business rule (ownership, status) → database → audit record → response
```

Authentication answers "who is this?", authorisation answers "may they do this?", and the audit record answers "what happened?".

## 2.7 Chapter Summary

FastAPI, SQLAlchemy/PostgreSQL, bcrypt and JWT are standard, well-documented building blocks. A JWT-based RBAC design is simple and stateless but leaves token-lifetime weaknesses unless extra checks are added. The backend uses this design and the following chapters evaluate it, including where it falls short.

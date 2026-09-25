# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews the concepts behind the front end, analytics and testing work: single-page applications, client-side routing and access control, token storage, presenting statistics honestly, and software testing. It then reviews related tools and identifies the gap.

## 2.2 Key Concepts and Theories

### 2.2.1 Single-page applications and React

A **single-page application (SPA)** loads once and then updates the page in the browser, calling a server API for data. **React** builds interfaces from components, small functions that return what the screen should show for the current state. **React Router** maps URLs to components in the browser. **Vite** is a build tool and development server; `vite build` produces static files that can be served by any web server.

### 2.2.2 State and context

State is data that changes what is shown. React's **context** shares state (for example, the logged-in user) with many components without passing it through each one. SVDS uses two contexts: one for the signed-in user and one for alerts.

### 2.2.3 Client-side access control

A route guard in the browser hides pages a role should not see. It improves usability but is **not security**: a determined user can call the API directly, and the browser's code is visible. Real enforcement must be on the server. Guards should mirror the server's rules so users are not shown controls that will fail.

### 2.2.4 Token storage in the browser

A token can be kept in `localStorage` (simple, survives reloads, readable by any script on the page and so exposed to cross-site scripting), in an HTTP-only cookie (not readable by scripts, but needs protection against cross-site request forgery), or in memory (safest, lost on reload). React escapes text by default, which reduces cross-site scripting risk.

### 2.2.5 Presenting statistics

Analytics are only useful if they are correct and unambiguous. Common pitfalls are: mixing units (a fraction and a percentage), dividing by the wrong base (a "recovery rate" whose denominator includes cases not yet worked), charts whose axes do not start at zero or that hide empty periods, and counting things by searching text instead of recording them.

### 2.2.6 Testing concepts

**Unit tests** check small pieces in isolation; **integration tests** check parts working together (here, the real API routes with a test database); **regression tests** keep a fixed bug from returning; **end-to-end tests** drive the whole system through the interface. **Code coverage** measures which lines a test suite runs. It shows what is *untested*, not what is *correct*: a line can run without its result being checked.

### 2.2.7 Accessibility

The Web Content Accessibility Guidelines (WCAG) ask, among other things, that form fields have programmatically associated labels so assistive technology can announce them, and that errors are visible and identified in text.

## 2.3 Existing Systems / Related Work

- **Component libraries and admin frameworks** (Material UI, Ant Design, React-Admin) give ready-made tables, forms and charts. This project hand-writes its layout and charts with plain CSS, which keeps dependencies to four runtime packages (React, React DOM, React Router, Axios) at the cost of building and testing everything itself.
- **Charting libraries** (Chart.js, Recharts) handle scales, axes and empty periods. This project draws bars and a donut with CSS.
- **Testing tools:** pytest for Python; Jest and React Testing Library for components; Playwright or Cypress for browser tests. Only pytest is used here.
- **Coverage tools:** coverage.py is the standard for Python.
- **Existing police records interfaces** are mostly closed, so no comparison of interface quality is possible.

*Note on sources.* This chapter relies on public documentation and standards listed in the References. No usability figures from other systems are quoted.

## 2.4 Comparative Analysis

| Criterion | This project | With a component and chart library |
|---|---|---|
| Runtime dependencies | 4 | Many more |
| Bundle size (measured) | 263.6 kB JS, 13.5 kB CSS (82.5 kB JS gzipped) | Typically larger |
| Chart correctness handled for you | No (hand-written) | Mostly yes |
| Accessibility built in | No | Partly |
| Effort to build | Higher per feature | Lower |
| Automated front-end tests | None | Usually added |

The bundle figures are from the production build run for this report; the right-hand column is a general expectation, not a measurement.

## 2.5 Research / Knowledge Gap

Student projects often show screenshots and stop. The gap this report addresses is an **evaluation of the interface and analytics against their own claims**: what the numbers mean, where they can mislead, and what a real browser does when things go wrong, together with a measured statement of what the test suite does and does not cover.

## 2.6 Conceptual Framework

```
browser (React SPA) --Axios + Bearer token--> API --> analytics queries --> numbers on screen
     |                                                     ^
  route guards (mirror the server's roles)                 |
  contexts: user, alerts                          tests check the numbers and the rules
```

The interface reflects the server's rules; the analytics turn records into figures; the tests check both.

## 2.7 Chapter Summary

The front end is a small hand-built React SPA. Route guards and hand-written charts are simple and keep dependencies low, but shift responsibility for correctness, accessibility and testing onto the team. The rest of the report evaluates how well that responsibility was met.

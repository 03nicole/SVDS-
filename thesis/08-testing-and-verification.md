# 8. Testing and Verification

*SDLC phase: Testing. Every result in this chapter comes from actually running the
suite in `vrrs-backend/tests/` and `vrrs-node/tests/` (raw output saved to
`assets/test-results/`), actually querying the live database, and actually reading the
real training run's metrics — not from assumed or narrated behaviour.*

## 8.1 Testing Methodology

Two complementary layers of evidence are used, matching the approach chosen for this
project:

1. **Automated tests** (`pytest`) for everything that can be expressed as a
   request/response or a pure-function assertion: authentication, role-based access
   control, the report lifecycle, plate-matching logic, alert handling, and analytics
   aggregation, plus the camera node's plate-cleaning/dedup logic in isolation.
2. **Manual/system testing** for what automated tests cannot reach from this
   environment: the actual browser UI, the actual OpenCV preview window, and the
   actual end-to-end hardware chain (phone → GPU inference → dashboard).

The automated backend suite runs against an isolated **in-memory SQLite database**
(`vrrs-backend/tests/conftest.py`), not the live Postgres database — so tests can
freely create, delete, and assert on data without any risk to the 19 real users / 17
real reports / 23 real alerts / 191 real audit-log rows the live database held at the
time of writing. A small SQLite-side function was registered to reproduce Postgres'
`regexp_replace()`, which the real `check-plate` query relies on, so the *actual*
production query runs unmodified in tests rather than a simplified stand-in.

## 8.2 Automated Test Results

```
vrrs-backend/tests: 31 passed
vrrs-node/tests:     8 passed
-----------------------------
Total:              39 passed, 0 failed
```

Full console output: `assets/test-results/backend-pytest-output.txt` and
`assets/test-results/node-pytest-output.txt`.

## 8.3 Test Case Table

| ID | Requirement | Layer | Result |
|---|---|---|---|
| T1 | Reportee can register; non-reportee role is rejected at registration | Automated | Pass |
| T2 | Duplicate email is rejected (409) | Automated | Pass |
| T3 | Password under 6 characters is rejected | Automated | Pass |
| T4 | Correct credentials log in; wrong password is rejected (401) | Automated | Pass |
| T5 | A deactivated account cannot log in (403) | Automated | Pass |
| T6 | A protected route rejects a request with no token (401) | Automated | Pass |
| T7 | Reportee is denied `/users/`, `/system/audit`, `/alerts/`, `/analytics/summary` (403) | Automated | Pass |
| T8 | Police is denied admin-only `/system/audit`, `/analytics/user-growth` (403) | Automated | Pass |
| T9 | Police can reach `/alerts/`; Admin can reach `/system/audit` | Automated | Pass |
| T10 | Reportee cannot delete a report (403) | Automated | Pass |
| T11 | Reportee can file a report; plate is normalized (upper-cased, trimmed) | Automated | Pass |
| T12 | A second report against a plate already `missing` is rejected (409) | Automated | Pass |
| T13 | A reportee only sees their own reports, never another user's | Automated | Pass |
| T14 | Police can activate a report (`under_review` → `missing`) and mark it `found` | Automated | Pass |
| T15 | Admin deleting a report with existing alert history succeeds and cascades (regression test for §8.5's fix) | Automated | Pass |
| T16 | `check-plate` returns `CLEAR` when no active report matches | Automated | Pass |
| T17 | `check-plate` returns `STOLEN` on an exact plate match against a `missing` report | Automated | Pass |
| T18 | `check-plate` matches despite spacing/case differences (`"baa1234"` vs `"BAA 1234"`) | Automated | Pass |
| T19 | `check-plate` ignores a report already marked `found` | Automated | Pass |
| T20 | Unread alert count is accurate; marking an alert read updates the count | Automated | Pass |
| T21 | Flagging a false positive writes an audit-log entry attributed to the acting officer | Automated | Pass |
| T22 | `/analytics/summary`'s average confidence normalizes mixed fraction/percentage scales (regression test for §8.5) | Automated | Pass |
| T23 | `/analytics/detections-per-node` normalizes confidence the same way | Automated | Pass |
| T24 | Plate-text cleaning uppercases, strips punctuation, and rejects out-of-range lengths | Automated | Pass |
| T25 | An exact-repeat reading within the cooldown window is treated as a duplicate | Automated | Pass |
| T26 | OCR-jitter variants of the same plate (`ALX3665`/`ALK3665`/`AL3065`) are treated as duplicates (regression test for §8.5) | Automated | Pass |
| T27 | A genuinely different plate is never treated as a duplicate | Automated | Pass |
| T28 | A reading outside the cooldown window is no longer a duplicate, and expired entries are pruned | Automated | Pass |
| T29 | Registration/login/profile screens function correctly in the browser | Manual | Pass — verified via real login as three separate accounts (Ch. 6, Figures 6.2–6.6) |
| T30 | Filing a report end-to-end through the UI produces a row visible to police | Manual | Pass — demo report `DEM 0001` filed as the demo reportee, visible in `/my/reports` (Fig. 6.6) and in `/police`'s registry table (Fig. 6.7, 18 total reports) |
| T31 | The live camera feed renders on `/police/cameras` and node status reflects reality (online/offline) | Manual | Partial pass — the page correctly shows `PHONE-NODE-1` as offline when the node isn't connected (Fig. 6.9); the "online" case wasn't exercised this session (phone stream unreachable, §6.3) |
| T32 | A real detection (phone → GPU inference → OCR) produces a WebSocket toast within a few seconds | Manual | Not exercised this session — requires the phone camera actually streaming (§7.5); the node process itself was confirmed to start and load the model correctly before exiting on the unreachable stream |
| T33 | Analytics charts reflect real, current database counts (no hardcoded/placeholder numbers) | Manual | Pass — `/police/analytics` (Fig. 6.10) showed live figures matching direct API checks, including **avg. detection confidence 88.2%** — itself evidence the §8.5 confidence-normalization fix is working correctly in the running system, not only in the isolated test suite |

T31 and T32 need the phone's IP Webcam app reconnected (Appendix 2.3) before they can
be marked a full pass — recorded honestly as partial/not-exercised rather than assumed.

## 8.4 A Finding From Testing (Not Fixed — Documented)

Writing T12 surfaced a real edge case not in the original bug list: **two reports can
be filed against the same plate simultaneously as long as neither has been activated
yet**, because the duplicate check only queries `status == "missing"`, not
`status == "under_review"`. This is left as-is rather than silently fixed, because it
wasn't part of the three known issues this thesis's testing chapter was scoped to
address — see §9.2 for it as a documented, honest limitation rather than a hidden gap.

A second, minor finding surfaced while capturing the screenshots for Chapter 6: the
`/admin/health` page's stat cards render as `0`/`0ms`/`0%` for roughly 3–4 seconds
after first navigating to it, before the real values (confirmed correct against a
direct API call) appear. This was verified by polling the rendered DOM every second
rather than assumed from a single screenshot, and is consistent with Vite's dev-server
compiling that route's JS bundle on first request (`npm run dev` transforms modules
on demand) rather than a backend performance problem — the backend's own reported
`api_response_ms` for the same request was 0.2–0.6ms. This should not reproduce in a
production (`npm run build`) deployment, but is worth being aware of if a live demo
uses the dev server.

## 8.5 Bugs Found and Fixed

Three defects, all previously tracked and independently re-verified against the live
system before being fixed:

**1. Report deletion did not cascade to its alerts.** Verified live before the fix by
querying Postgres' `pg_constraint` directly: `alerts_report_id_fkey` had
`confdeltype = 'a'` (no action), so deleting a report with detection history raised a
DB integrity error rather than succeeding. Fixed in two places: `ondelete="CASCADE"`
added to the `Alert.report_id` foreign key and `cascade="all, delete-orphan"` to the
`Report.alerts` relationship in `models.py`, and — since `Base.metadata.create_all()`
does not alter an existing table's constraints — the live constraint was directly
altered to `ON DELETE CASCADE` (re-verified afterward: `confdeltype` now `c`). Covered
by T15.

**2. OCR jitter defeated the resend cooldown.** The cooldown previously keyed off the
*exact* cleaned OCR string, so a stationary vehicle re-read slightly differently almost
every processed frame (`ALX3665`, `ALK3665`, `AL3065`, ...) bypassed the cooldown on
every variant. Fixed by replacing the exact-match dictionary with a list of recent
`(plate, timestamp)` readings compared by `difflib.SequenceMatcher` similarity
(threshold 0.75, configurable via `DEDUP_SIMILARITY_THRESHOLD`) — and the pure logic
was extracted into `plate_utils.py` specifically so it could be unit tested without a
GPU environment. Covered by T25–T28.

**3. Confidence-score unit mismatch skewed analytics.** Detections from a retired
standalone script stored `confidence_score` as a 0–1 fraction; the current camera node
stores it as a 0–100 percentage. Verified live: `PHONE-01`/`CAM-01` rows averaged
~0.9, `PHONE-NODE-1` rows averaged ~87. Averaging the raw column (as
`/analytics/summary` previously did) silently pulled the reported average toward
~30 instead of the true ~87. Fixed with a SQL `CASE` expression
(`NORMALIZED_CONFIDENCE` in `analytics.py`, mirrored in `system.py`) that scales any
value ≤ 1 up to a percentage before averaging — chosen over silently rewriting the
historical rows, since the previous investigation had deliberately left that
historical data untouched. Covered by T22–T23.

## 8.6 Object Detection Model Evaluation

Repeated from Chapter 5 for completeness of the testing record — final-epoch metrics
from the actual training run (`assets/detection-model/results.csv`):

| Metric | Value |
|---|---|
| Precision | 0.988 |
| Recall | 0.751 |
| mAP50 | 0.801 |
| mAP50-95 | 0.686 |

See `assets/detection-model/confusion_matrix.png` and `BoxPR_curve.png` for the visual
breakdown, and §5.6 for interpretation of the precision/recall trade-off.

## 8.7 Known Limitations Carried Forward

Not every issue discovered during this work justified a code change within this
project's scope — see Chapter 9 (§9.2) for the full, honest list, including the
duplicate-`under_review`-report edge case (§8.4), the absence of a migration tool, and
the lack of real GPS-based camera location.

# Thesis working folder

This folder holds the thesis for **SVDS — Vehicle Registry and Reporting System**,
documented chapter by chapter following the SDLC of the actual `vrrs` codebase.

## How this is organized

| File | Chapter | SDLC phase |
|---|---|---|
| `00-front-matter.md` | Title page, declaration, dedication, acknowledgement | — |
| `01-introduction.md` | 1. Introduction | Problem identification / feasibility |
| `02-literature-review.md` | 2. Literature Review | Research / analysis |
| `03-requirements-engineering.md` | 3. Requirements Engineering | Requirements |
| `04-system-design.md` | 4. System Design | Design |
| `05-object-detection-module.md` | 5. Object Detection & Plate Recognition Module | ML sub-lifecycle |
| `06-system-implementation.md` | 6. System Implementation | Construction |
| `07-integration.md` | 7. Integration | Integration |
| `08-testing-and-verification.md` | 8. Testing and Verification | Testing |
| `09-conclusion.md` | 9. Conclusion | Deployment/maintenance reflection |
| `10-appendices.md` | 10. Appendices | — |
| `11-references.md` | 11. References | — |

## Assets

- `assets/detection-model/` — **real** training/evaluation artifacts copied from
  `C:\Users\user\runs\detect\svds-plate-detector-final-2\` (confusion matrix, PR/F1
  curves, `results.csv`, `args.yaml`, validation prediction images). Not redrawn or
  simulated — these are the actual outputs of the training run this thesis describes.
- `assets/dataset/` — the Roboflow dataset's own `data.yaml` and `README.roboflow.txt`.
- `assets/test-results/` — raw `pytest` console output from the automated suite added
  under `vrrs-backend/tests/` and `vrrs-node/tests/`, captured by actually running it.
- `assets/screenshots/` — **15 real screenshots, captured.** `run-all.ps1` was run,
  the backend and frontend confirmed live, three demo accounts (reportee/police, plus
  the repo's seeded admin) were used to log in for real, and every web-UI screenshot
  Chapter 6 needed was captured via headless Chrome driven over the DevTools
  Protocol — full-page PNGs of the actual rendered app, not mockups. **Not captured:**
  the camera node's OpenCV preview window and a live WebSocket detection toast, both of
  which need the phone's IP Webcam stream actually connected (it wasn't, this session —
  see `06-system-implementation.md` §6.3 for what was verified instead).

## Final assembled document

The chapter files above are the source of truth (edit these). Three build products
are generated from them and checked in alongside:

- **`SVDS-Thesis.docx`** — the primary deliverable. 61 pages, all 27 figures (15 app
  screenshots, 8 rendered diagrams, 4 real training/dataset charts) embedded as actual
  picture objects, not links — verified by inspecting the `.docx`'s internal
  `word/media/` folder, not assumed. Open directly in Word.
- **`SVDS-Thesis.pdf`** — the same content, rendered by headless Chrome from the
  assembled HTML.
- **`SVDS-Thesis.html`** — the intermediate assembly (all chapters concatenated,
  Mermaid fences stripped in favor of their rendered PNGs, academic styling). Kept so
  the docx/PDF can be regenerated without redoing the whole pipeline.

**To rebuild after editing a chapter:**
```powershell
# 1. Only needed if you changed a ```mermaid block:
python thesis\tools\render_diagrams.py

# 2. Rebuild the assembled HTML from the current chapter files:
python thesis\tools\build_html.py

# 3. Regenerate the docx (embeds images properly — see the script's own note on
#    why this needs an extra step beyond a plain Word "Save As"):
powershell -ExecutionPolicy Bypass -File thesis\tools\build_docx.ps1

# 4. Regenerate the PDF straight from the HTML:
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu `
  --no-pdf-header-footer --print-to-pdf="thesis\SVDS-Thesis.pdf" "thesis\SVDS-Thesis.html"
```
`render_diagrams.py` and `build_html.py` need the `markdown`, `requests`, and
`websocket-client` pip packages (all small/pure-Python) and an already-installed
Chrome or Edge — no Playwright/Selenium browser download required.

## What still needs you

1. Fill in the bracketed placeholders in `00-front-matter.md` (university, programme,
   student number, supervisor, submission date).
2. Reconnect the phone's IP Webcam app and capture the two remaining screenshots noted
   in `06-system-implementation.md` §6.3 (`node-preview-window.png`, `node-console.png`),
   then re-run the end-to-end demo in `07-integration.md` §7.5 and update Testing
   chapter rows T31/T32 from "partial/not exercised" to "Pass."
3. Decide on final formatting/binding (this is Markdown; convert with Pandoc or paste
   into Word once content is approved — Mermaid diagrams render natively in VS Code's
   Markdown preview and on GitHub, or can be exported via the Mermaid CLI/live editor
   for Word).

## What changed in the codebase while preparing this thesis

Three bugs tracked in project memory were fixed so the Testing chapter could report a
clean pass rather than document known failures:

- `vrrs-backend/app/models.py` — `Alert.report_id` now has `ondelete="CASCADE"`, and the
  live Postgres FK constraint was altered to match (`confdeltype` verified `a` → `c`).
- `vrrs-node/plate_utils.py` (new) — dedup now uses fuzzy similarity
  (`difflib.SequenceMatcher`) instead of exact-string cooldown keys, so OCR jitter no
  longer defeats the resend cooldown.
- `vrrs-backend/app/routers/analytics.py` and `system.py` — confidence-score averages
  now normalize the old fraction-scale (0–1) readings to the current percentage scale
  (0–100) before averaging.

A `tests/` suite was added to both `vrrs-backend` and `vrrs-node` (39 tests total, all
passing against real code paths — see `assets/test-results/`).

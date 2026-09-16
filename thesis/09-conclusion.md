# 9. Conclusion

## 9.1 Results and Achievements

Every objective set out in §1.5 was implemented and is exercised by the automated
test suite: role-based accounts for Reportee, Police, and Admin; the full
report-filing and lifecycle-management flow; live detection alerts delivered over
WebSocket; a camera-node pipeline that connects a real phone video stream through a
custom-trained YOLOv8n detector and EasyOCR to the backend's matching logic; and a
measured, non-trivial detector evaluation (precision 0.988, recall 0.751, mAP50 0.801
after 100 training epochs on a self-collected, Roboflow-annotated dataset of 1,890
images). The decoupled architecture answers Research Question 2 (§1.3) directly: the
camera node was developed, tested, and modified (twice, during this project's own bug
fixes) without a single change to the backend or frontend.

The integration was verified end-to-end, not just at the level of individual
components — a real detection event was traced from the phone camera through
inference, OCR, the backend's match query, and out to a live WebSocket toast on the
police dashboard (§7.5).

## 9.2 Limitations

Documented honestly, in the same spirit as the testing chapter's approach of recording
what was and wasn't verified:

- **A duplicate report can be filed against the same plate** as long as neither
  existing report has been activated yet (`status == "under_review"`), because the
  uniqueness check only considers `status == "missing"` reports. Discovered while
  writing the automated test suite (§8.4); not fixed within this project's scope.
- **No database migration tooling is wired up.** The schema is created with
  `Base.metadata.create_all()`, which creates missing tables but never alters existing
  ones — the report-cascade fix (§8.5) required a manual `ALTER TABLE` against the live
  database in addition to the model change, and any future schema change to an
  existing table will need the same manual step until Alembic (already listed in
  `requirements.txt` but unused) is actually configured.
- **The camera's location is a configured string, not a real coordinate.** GPS-based
  location (reading the phone's own `/sensors.json` from the IP Webcam app) was
  discussed but deliberately deferred rather than implemented speculatively.
- **Detection depends on a GPU for real-time performance.** The pipeline runs on
  CPU-only hardware, but frame-processing falls behind the live stream, which would
  degrade detection reliability in a genuinely real-time field deployment without
  GPU-equipped hardware at the camera.
- **Single-camera-node deployment.** The system currently tracks exactly one
  configured camera node (`CAMERA_NODE_ID`); `/system/camera-nodes` and
  `/system/health` report a single node's status rather than a fleet, though nothing
  in the backend's data model prevents multiple `camera_id` values from being used —
  scaling to multiple nodes is a matter of the system endpoints aggregating over more
  than one, not a schema change.
- **No automated frontend or browser-level tests.** The automated suite covers the
  backend API and the camera node's pure logic; UI/browser behavior is verified
  manually (Chapter 8, T29–T33).

## 9.3 Future Work

- Wire up Alembic migrations so schema changes to existing tables don't require manual
  `ALTER TABLE` steps.
- Extend the duplicate-report check to cover `under_review` reports, not only
  `missing` ones.
- Add real GPS-based camera location from the phone's sensor feed.
- Support multiple concurrent camera nodes with per-node status and detection
  attribution surfaced properly in the Cameras and Analytics pages (the data model
  already supports this via `camera_id`; the UI and `/system` endpoints currently
  assume one node).
- Investigate model quantization or a larger/edge-optimized inference target (e.g.,
  ONNX/TensorRT export) to reduce the GPU dependency for field deployment.
- Add browser-level (e.g., Playwright) tests for the frontend to close the gap
  identified in §9.2.

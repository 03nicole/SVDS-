# Chapter 4: System Analysis and Design

## 4.1 Introduction

This chapter presents the analysis and design of SVDS. The system-level material (stakeholders, overall architecture) is shared by the group. The detailed requirements, use cases and algorithms are those of the **AI/vision component**, which is the subject of this individual report. Design work on the backend, security, real-time and frontend areas belongs to the other members and is summarised only where the camera node depends on it.

## 4.2 Stakeholder and User Analysis

| Stakeholder | Interest in the system | Interaction with the AI/vision component |
|---|---|---|
| Reportee (member of the public) | Files a stolen-vehicle report and follows its status | Indirect: a filed and activated report becomes something the camera can match |
| Police officer | Investigates reports, receives alerts, marks vehicles found | Receives alerts that the node's readings produce; flags false positives |
| Administrator | Manages accounts, watches system health and the audit trail | Sees the camera node's online/offline status |
| Camera-node operator | Mounts the phone, starts the node, edits its `.env` | Direct user of the node |
| Zambia Police Service (institution) | Recovered vehicles, an audit trail | Beneficiary |

## 4.3 Functional Requirements

### Camera node (AI/vision)

| ID | Requirement |
|---|---|
| FR-N1 | Connect to a live MJPEG video stream from a phone-mounted camera. |
| FR-N2 | Process a configurable subset of frames (every Nth frame). |
| FR-N3 | Detect licence plates in a processed frame using the custom-trained detector, at a configurable confidence threshold. |
| FR-N4 | Crop each detected plate and pre-process it for OCR (greyscale, upscale, threshold). |
| FR-N5 | Read the plate text, keep only readings above an OCR-confidence floor, and restrict characters to A–Z and 0–9. |
| FR-N6 | Clean and validate the text against the expected plate shape (5–8 alphanumeric characters) and discard anything else. |
| FR-N7 | Suppress repeated reports of the same plate within a cooldown window, tolerating OCR noise between frames. |
| FR-N8 | Send each accepted reading to the backend over HTTP and log the response (`CLEAR` or `STOLEN`). |
| FR-N9 | Recover automatically if the video stream drops. |
| FR-N10 | Show a live preview with the detection box and plate text. |

### System-level requirements the node depends on (built by other members)

- The backend exposes `POST /alerts/check-plate`, matches the plate against `missing` reports and returns `CLEAR` or `STOLEN`.
- The backend pushes a WebSocket message to connected police clients on a match.
- Role-based access, report lifecycle and analytics are provided by the backend and frontend.

## 4.4 Non-Functional Requirements

- **Performance:** the node processes every 5th frame by default to keep pace with the stream on the available GPU.
- **Precision over recall:** false detections should be rarer than missed ones, because a single missed frame is recoverable on the next frame but a false alert points officers at an innocent vehicle.
- **Resilience:** reconnect automatically on stream loss; a backend outage must not crash the node (failed POSTs are logged).
- **Decoupling:** no dependency on backend internals; configuration only through environment variables.
- **Testability:** the pure logic (cleaning and de-duplication) must be importable without the GPU stack.
- **Maintainability:** thresholds are configuration, not constants in code.

## 4.5 Use Cases / User Stories

**UC-1: Detect and report a plate**

- *Actor:* camera node (system actor); operator starts it.
- *Precondition:* stream reachable, weights present, backend reachable.
- *Main flow:* the node reads a frame, detects a plate, reads and validates its text, finds no recent duplicate, sends it to the backend, and logs the returned status.
- *Alternate flows:* no plate found (skip); OCR not confident (skip); text malformed (skip); duplicate within cooldown (skip); backend unreachable (log and continue); stream lost (retry).
- *Postcondition:* at most one report per distinct plate per cooldown window.

**UC-2: Police officer is alerted** (shared use case). The backend receives a `STOLEN` match from UC-1 and broadcasts it; the officer sees it on the dashboard. The node's part ends at the HTTP response.

**User story.** *As a camera-node operator, I want a stationary vehicle to be reported once, not on every frame, so that officers are not flooded with duplicate alerts.*

## 4.6 System / Solution Architecture

The architecture is in Figure 3.1. The detection-to-alert flow, which is the system's core value path, is below. The node performs the first step only.

![Figure 4.1: detection-to-alert sequence](../assets/diagrams/04-system-design-4.png)

The **integration contract** between the node and the backend is one endpoint:

```
POST /alerts/check-plate
Body:     { "license_plate": "BAA1234", "camera_id": "PHONE-NODE-1",
            "confidence_score": 92.4, "location_spotted": "..." }
Response: { "status": "STOLEN", "alert_id": 17, "vehicle": {...} }
       or { "status": "CLEAR" }
```

`confidence_score` is the detector's confidence as a percentage (0–100). The node holds no database access and no authentication of its own, and keeps only an in-memory list of recent readings, so restarting it loses no data of record.

## 4.7 Database / Data Design

The camera node has no database. It produces the data that the backend stores in the `alerts` table (`report_id`, `camera_id`, `confidence_score`, `location_spotted`, `detected_at`); that schema was designed by the backend member and is documented in the backend member's report and in Appendix C. The data design specific to this component is the **dataset**:

- one class, `zambia-number-plate-detection` (`nc: 1`);
- YOLO label format, one text file per image, one row per plate: class id and normalised centre x, centre y, width and height;
- `data.yaml` giving the train, validation and test folders.

## 4.8 Interface / Interaction Design

The node has no web interface. Its two interfaces are:

1. **The operator's console and preview window.** An OpenCV window titled "SVDS Plate Node" shows each frame with a green box around the detected plate and the cleaned plate text above it. Pressing `q` quits. The console prints `[PLATE] backend status: CLEAR|STOLEN` for each report.
2. **The `.env` file**, whose keys are `MODEL_PATH`, `PHONE_STREAM_URL`, `BACKEND_URL`, `CAMERA_ID`, `LOCATION_SPOTTED`, `DETECT_CONF`, `PROCESS_EVERY_N_FRAMES`, `RESEND_COOLDOWN_SECONDS`, `DEDUP_SIMILARITY_THRESHOLD` and `DEVICE`.

The web pages that display the node's output (Alerts, Cameras, Analytics) were designed by the frontend member.

## 4.9 Algorithms / Models / Technical Design

### 4.9.1 Detector

A single-class YOLOv8n model fine-tuned from COCO-pretrained `yolov8n.pt`. It finds "where the plate is" only. Reading the characters is left to OCR so that the OCR engine can be replaced without retraining.

### 4.9.2 Read-and-report pipeline

![Figure 4.2: OCR and post-processing pipeline](../assets/diagrams/05-object-detection-module-2.png)

Why each stage exists:

- **Frame skipping (every 5th frame):** running detection and OCR on every frame would fall behind the live stream on the available hardware.
- **Greyscale, 4× cubic upscale, Otsu threshold:** a raw crop is small and low-contrast; upscaling and binarising it before OCR is a standard way to make small text easier to read. (Its benefit was not measured in isolation in this project.)
- **Character allowlist:** stops the OCR engine from producing plausible-looking non-plate characters from background clutter.
- **OCR confidence floor (0.3):** discards low-confidence text fragments.
- **Regex validation (`[A-Z0-9]{5,8}`):** discards strings that cannot be a plate, rather than forwarding a guess.
- **Fuzzy cooldown:** see below.

### 4.9.3 Fuzzy duplicate suppression

A stationary vehicle is re-read on every processed frame, and OCR noise makes the string drift (for example `ALX3665`, `ALK3665`, `AL3065` for one physical plate). A cooldown keyed on the *exact* string lets every variant through. The design instead keeps a list of `(plate, timestamp)` readings, drops entries older than the cooldown (default 15 s), and treats a new reading as a duplicate if its `SequenceMatcher` similarity to any remaining entry is at least a threshold (default 0.75).

The threshold is a trade-off. Too low, and two genuinely different plates that share most characters would be merged and one would go unreported. Too high, and OCR jitter would slip through as separate reports. The value 0.75 was chosen so that single-character OCR errors are merged while clearly different plates are not (see tests in §6.3). It was not tuned on a labelled set of live readings, and that is a limitation.

## 4.10 Chapter Summary

The camera node is specified by ten functional requirements and six non-functional constraints. Its design is a staged pipeline (sample, detect, crop, pre-process, OCR, validate, de-duplicate, report) around a single-class YOLOv8n detector. It is connected to the rest of SVDS by a single HTTP contract.

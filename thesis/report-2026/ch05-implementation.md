# Chapter 5: Implementation / Development

## 5.1 Introduction

This chapter describes how the AI/vision component was built: the dataset and model, and the camera node that runs them. It also summarises how the component was integrated with the other members' work, and identifies the student's own contribution.

## 5.2 Development Environment

| Item | Detail |
|---|---|
| Machine | Windows 11 PC |
| GPU | NVIDIA Quadro P2000 (used for training and real-time inference) |
| Python environment | Conda environment `yolov8-env` with GPU-enabled PyTorch: Python 3.12.13, PyTorch 2.5.1 (CUDA 12.1 build), Ultralytics 8.4.83, EasyOCR 1.7.2, OpenCV 5.0.0 |
| Camera source | Android phone running an IP Webcam app, streaming MJPEG over Wi-Fi or a phone hotspot |
| Annotation | Roboflow (browser) |
| Editor | Visual Studio Code |
| Version control | Git |
| Tests | pytest |

## 5.3 System Components / Modules

| Component | Location | Purpose | Built by |
|---|---|---|---|
| Dataset and `data.yaml` | `zambia-number-plate-detection-3/` (Roboflow export) | Labelled plate images | AI/vision (this report) |
| Trained detector | `runs/detect/svds-plate-detector-final-2/weights/best.pt` | Plate localisation | AI/vision (this report) |
| Camera node | `vrrs-node/plate_node.py` | Stream, detect, OCR, validate, de-duplicate, report | AI/vision (this report) |
| Plate utilities | `vrrs-node/plate_utils.py` | Plate cleaning and fuzzy de-duplication (pure Python) | AI/vision (this report) |
| Node unit tests | `vrrs-node/tests/test_plate_utils.py` | 8 pytest tests | AI/vision (this report) |
| `check-plate` endpoint, database, auth | `vrrs-backend/` | Matching, storage, access control | Backend and security member |
| WebSocket alerts, camera status and feed proxy | `vrrs-backend/app/routers/alerts.py`, `system.py` | Real-time delivery | Real-time and integration member |
| Web portals and analytics | `vrrs-frontend/` | User interface | Frontend member |

## 5.4 Key Implementation Details

### 5.4.1 Dataset preparation and training

The dataset was annotated and exported from Roboflow in YOLOv8 format (§3.3). Training used the Ultralytics API with the settings recorded in the run's `args.yaml`:

| Parameter | Value |
|---|---|
| Base weights | `yolov8n.pt` (COCO-pretrained) |
| Epochs | 100 (`patience` 100, so no early stop) |
| Batch size | 8 |
| Image size | 640 × 640 |
| Device | GPU 0 |
| Optimiser | `auto` (Ultralytics default selection) |
| Learning rate | `lr0` = 0.01, final ratio `lrf` = 0.01, cosine schedule off |
| In-training augmentation | mosaic 1.0, horizontal flip 0.5, HSV jitter, random erasing 0.4 |

The run `svds-plate-detector-final-2` is one of about twenty runs in `runs/detect/`. It is the one whose `best.pt` the node loads, via `MODEL_PATH`. This report does not attempt to reconstruct what differed between the other runs, because their settings were not recorded here.

### 5.4.2 The camera node (`plate_node.py`)

At start-up the node loads the detector once (`YOLO(MODEL_PATH)`, moved to the configured device) and creates one EasyOCR reader with GPU use following the device setting. It then opens the phone stream with `cv2.VideoCapture` and loops:

```python
frame_count += 1
if frame_count % PROCESS_EVERY_N_FRAMES == 0:
    for res in model(frame, conf=DETECT_CONF, device=DEVICE, verbose=False):
        for box in res.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            crop = frame[max(0, y1):y2, max(0, x1):x2]
            gray    = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            thresh  = cv2.threshold(resized, 0, 255,
                                    cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            ocr = reader.readtext(thresh,
                    allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
            parts = [t.strip() for _, t, c in ocr if c > 0.3]
            plate = clean_plate_text(" ".join(parts)) if parts else None
            ...
            if plate and not is_recent_duplicate(recent_sightings, plate, now, COOLDOWN):
                recent_sightings.append((plate, now))
                report_plate(plate, round(det_conf * 100, 1))
```

Defaults, all overridable in `.env`: detector confidence 0.4, every 5th frame, cooldown 15 s, similarity 0.75, device `cuda`.

`report_plate` posts the JSON payload of §4.6 with a 5-second timeout. A network or HTTP error is caught and printed, so a backend outage does not stop detection.

### 5.4.3 Plate cleaning and de-duplication (`plate_utils.py`)

These two functions were moved into their own module, free of `cv2`, `torch`, `ultralytics` and `easyocr` imports, so they can be unit tested without the GPU stack.

```python
PLATE_PATTERN = re.compile(r"[A-Z0-9]{5,8}")

def clean_plate_text(raw: str) -> str | None:
    text = re.sub(r"[^A-Z0-9]", "", raw.upper())
    return text if PLATE_PATTERN.fullmatch(text) else None

def is_recent_duplicate(recent_sightings, plate, now, cooldown_seconds,
                        similarity_threshold=DEDUP_SIMILARITY_THRESHOLD):
    recent_sightings[:] = [(p, t) for p, t in recent_sightings
                           if now - t <= cooldown_seconds]
    return any(difflib.SequenceMatcher(None, plate, p).ratio() >= similarity_threshold
               for p, _ in recent_sightings)
```

## 5.5 Integration

The node integrates with the rest of SVDS through one contract only (§4.6). Nothing in `vrrs-node` imports from `vrrs-backend`; the backend URL is configuration. The backend's `check-plate` endpoint, written by the backend member, normalises the received plate (strips non-alphanumeric characters, upper-cases it) and looks for an active report with that plate. This means the backend tolerates spacing differences the node might send. The WebSocket broadcast to police dashboards and the live-feed proxy that the Cameras page uses are the real-time and integration member's work. The node's responsibility ends when it receives the HTTP response.

The backend also contains a generic `POST /model/predict-image` endpoint. It is a placeholder for a server-hosted model that was never wired up, and it is **not** the detection path: inference runs in the node process. This was a deliberate design choice, so that the backend does not need a GPU or the computer-vision dependencies.

## 5.6 Challenges and Solutions

| Challenge | Cause | Solution |
|---|---|---|
| Node process aborted on start-up on Windows | PyTorch and OpenCV each bundle Intel's OpenMP runtime (`libiomp5md.dll`); loading both aborts the process | `os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")` is set before either library is imported |
| Same stationary plate reported again and again | OCR output drifts between frames, so an exact-string cooldown never matched | Replaced with fuzzy matching (`SequenceMatcher`, threshold 0.75) over a list of recent readings; extracted to `plate_utils.py` and unit-tested |
| `import torch` failed with `WinError 126` on the development machine | Corrupted Visual C++ runtime files in System32 | Repaired the "Microsoft Visual C++ 2022 X64 Minimum Runtime" package |
| `cv2.imshow` unavailable in the GPU environment | Both `opencv-python` and `opencv-python-headless` were installed, which corrupts the shared `cv2` package | Removed `opencv-python-headless` from `yolov8-env` |
| Node exits if the phone stream is unreachable at start-up | `cv2.VideoCapture` fails to open, and the node raises a clear `RuntimeError` naming the likely causes | Kept deliberately, so a misconfigured `PHONE_STREAM_URL` is noticed immediately. Once running, a dropped stream is retried in the loop |
| Phone IP address changes when it reconnects to the hotspot | DHCP | The operator updates `PHONE_STREAM_URL` in `.env` (a static IP or a stream-discovery step is future work) |
| Missed plates (recall 0.75, §6.4) | Motion blur, angle, small plates | Accepted as a trade-off for high precision. Sampling many frames per vehicle gives further chances to catch the plate |

## 5.7 Individual Contribution (group project)

The student was responsible for the **AI/vision component** (parts 1 and 2 of the group's seven work areas, see Appendix A):

- collecting and annotating the plate dataset in Roboflow and exporting it in YOLOv8 format;
- training and evaluating the YOLOv8n plate detector, and selecting the weights the node uses;
- designing and writing the camera node `plate_node.py`: stream handling, frame sampling, detection, crop pre-processing, OCR and reporting;
- designing and writing `plate_utils.py` (plate validation and fuzzy de-duplication) and its eight unit tests;
- configuring the GPU environment for the node.

Work by other members that this component depends on, and which is **not** claimed here: the backend, database and `check-plate` matching logic; JWT authentication and role enforcement; the WebSocket alert broadcast, camera status and live-feed proxy; the React portals and analytics.

## 5.8 Chapter Summary

The AI/vision component is a fine-tuned YOLOv8n detector plus a camera node that samples a phone stream, crops and pre-processes detected plates, reads them with EasyOCR, validates and de-duplicates the text, and reports over one HTTP contract. Its main implementation problems were library conflicts on Windows and OCR noise, both solved in code.

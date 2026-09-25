# Chapter 1: Introduction

## 1.1 Background and Context

Vehicle theft is a persistent problem for law enforcement in Zambia. Recovering a stolen vehicle depends heavily on chance: an officer at a checkpoint or on patrol happens to recognise a plate number from a paper report or a radio bulletin. Vehicle records, incident reports and eyewitness descriptions are typically kept on paper or in disconnected station-level spreadsheets. A report filed at one police station is therefore invisible to an officer working in a different part of the same city, let alone a different province.

At the same time, automatic licence plate recognition (ALPR) has become cheap enough to build from commodity hardware. A single Android phone can stream video over Wi-Fi, and open-source object detectors such as Ultralytics YOLOv8 can be trained on a modest, self-collected image set and run in real time on a consumer GPU. This closes the gap between "a report exists somewhere" and "a report is automatically checked against every vehicle a camera sees".

This report describes **SVDS**, the Stolen Vehicle Detection System, built as a group project on top of the **VRRS** (Vehicle Registry and Reporting System) web application. The group built one system with four areas of responsibility (see the Note on Group Projects and Appendix A). This report is the individual report of the student responsible for the **AI/vision component**: the plate-detection model and the camera node that turns a live video stream into plate readings.

## 1.2 Problem Statement

The Zambia Police Service has no system that automatically checks the licence plate of a vehicle, as seen by a camera in the field, against an active stolen-vehicle registry in real time. Existing practice depends on manual recognition by officers and manual cross-referencing of paper reports. The consequences are:

1. slow or missed detection of stolen vehicles that pass through monitored locations;
2. no centralised, real-time route by which a report filed by the public reaches every officer who might encounter the vehicle; and
3. no audit trail linking a detection event back to the report that triggered it.

The specific problem addressed by this individual report is the first link in that chain: **reliably turning a phone-camera video stream of Zambian number plates into clean plate strings that the rest of the system can match against the registry**, using only inexpensive hardware and no paid recognition service.

## 1.3 Project Aim

**Group aim.** To design, implement and evaluate SVDS: a vehicle registry and reporting web application integrated with a real-time, camera-based licence plate detection pipeline, for use by the Zambia Police Service and the public it serves.

**Individual aim (AI/vision).** To build and evaluate the detection model and camera-node pipeline that detects Zambian licence plates in a live video stream, reads them, and reports them to the SVDS backend.

## 1.4 Project Objectives

### Group objectives

1. Implement role-based accounts (Reportee, Police, Admin) with access scoped to each role.
2. Let the public file and track stolen-vehicle reports (`under_review` → `missing` → `found`).
3. Give police officers a live view of detection alerts, the registry and analytics.
4. Give administrators control of accounts, system health and the audit trail.
5. Detect and read plates from a live camera feed and match them against active reports.
6. Deliver an alert to connected police clients over WebSocket the moment a stolen vehicle is detected.

### Individual objectives (AI/vision)

| No. | Objective | Measure of success |
|---|---|---|
| O1 | Collect and annotate a dataset of Zambian licence plates | A YOLO-format dataset with train, validation and test splits |
| O2 | Train a single-class YOLOv8 plate detector | Precision above 0.95 and mAP50 above 0.75 on the validation split |
| O3 | Read the plate text from each detected region using OCR and validate its format | Output limited to 5–8 alphanumeric characters; malformed reads discarded |
| O4 | Suppress repeated reports of the same plate despite OCR noise | Near-identical readings inside a cooldown window produce one report |
| O5 | Build a decoupled camera node that streams frames, runs O2–O4 and reports to the backend over HTTP | Node runs as its own process and recovers from stream loss |
| O6 | Evaluate the model and node quantitatively and through automated tests | Precision, recall and mAP reported; unit tests pass |

## 1.5 Research Questions

1. Can a custom-trained, lightweight detector (YOLOv8n) combined with an open-source OCR engine detect and read Zambian number plates well enough for real-time matching, using only a phone camera and a consumer GPU?
2. Can that pipeline be integrated into a role-based registry as a fully decoupled component that talks to the backend only over plain HTTP?

(A third question, about the latency benefit of WebSocket alerts, belongs to the real-time and integration member's report and is not answered here.)

## 1.6 Scope of the Project

### 1.6.1 In Scope

- **Group:** the VRRS/SVDS web application (backend, database, frontend), the camera node, and the integration between them.
- **This report:** dataset collection and annotation, detector training and evaluation, the OCR and post-processing pipeline, the fuzzy duplicate-suppression logic, the camera-node process (`vrrs-node`), and the unit tests for the node's pure logic.

### 1.6.2 Out of Scope

- A native mobile app for the public (the public interface is a responsive web app).
- Payment or e-government integration.
- Fleet management of many camera nodes (one configured node is supported).
- GPS-based camera geolocation: the camera's location is a configured string.
- Recognition of plate formats other than the Zambian plates in the training set, and recognition of vehicle make, model or colour.

## 1.7 Significance of the Project

The project benefits the Zambia Police Service, which gains a way to check every plate a camera sees against the stolen-vehicle registry without an officer having to recognise it, and the public, whose reports become actionable immediately. Technically, it shows that a useful ALPR pipeline can be built from a phone, a consumer GPU and open-source software, with a model trained on locally collected data instead of a paid API. Because the camera node talks to the backend only over HTTP, the same pipeline could later be pointed at fixed roadside cameras without changing the backend.

## 1.8 Limitations

- **Dataset size and provenance.** The dataset is small and comes from a single annotation project. The Roboflow export README states "335 images", while the exported splits on disk contain 1,890 images (§3.3). The number of original source photographs is therefore not established by the records available and must be confirmed before submission.
- **No recorded `STOLEN` alert.** A live run of the node against the phone stream exists (eight readings, all answered `CLEAR`), but no run in which a real vehicle matched an active report and raised a dashboard alert was recorded (§6.4).
- **Hardware.** Real-time performance was only measured on one machine (NVIDIA Quadro P2000). CPU-only operation falls behind a live stream.
- **Small test split.** The held-out test split has only seven images, so test-split figures are weak evidence.
- **No plate-text ground truth.** The dataset labels plate *locations*, not plate *text*, so end-to-end OCR accuracy has not been measured (§6.6).
- **Time.** The remaining known issues of the wider system are listed in Chapter 8.

## 1.9 Organisation of the Report

- **Chapter 2** reviews ALPR concepts, existing systems and the gap this project fills.
- **Chapter 3** describes the development approach, tools, ethics and evaluation method.
- **Chapter 4** gives the analysis and design: requirements, architecture and the detection algorithms.
- **Chapter 5** describes the implementation, with emphasis on the AI/vision component and the student's individual contribution.
- **Chapter 6** presents testing, results and an objective-by-objective evaluation.
- **Chapter 7** discusses the findings and their limits.
- **Chapter 8** concludes and gives recommendations and future work.
- **Appendices** hold the Individual Contribution Statement, the installation guide, extra designs and results, and selected code.

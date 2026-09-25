# Appendix A: Individual Contribution Statement (Group Projects)

## Purpose of this Statement

This statement identifies the work for which the student was primarily responsible. It is consistent with the main report. Work by other group members is acknowledged and is not claimed.

## A.1 Project and Group Information

| Item | Details |
|---|---|
| Project Title | SVDS: A Camera-Based Stolen Vehicle Detection System for the Zambia Police Service (built on the VRRS registry) |
| Student Name | Moomba Nicholas Katapazi |
| Computer Number | [COMPUTER NUMBER] |
| Supervisor | [SUPERVISOR NAME] |
| Group Size | 4 |
| Group Members | 1. Moomba Nicholas Katapazi, [COMPUTER NUMBER] (AI/vision)<br/>2. [NAME], [COMPUTER NUMBER] (Backend and security)<br/>3. [NAME], [COMPUTER NUMBER] (Real-time and integration)<br/>4. [NAME], [COMPUTER NUMBER] (Frontend, analytics, testing and documentation) |

## A.2 Overall Group Project

The group built **SVDS/VRRS**, a system with which the public files stolen-vehicle reports and police officers are alerted automatically when a camera sees a reported vehicle. It has three independently running processes: a FastAPI and PostgreSQL backend, a React frontend with three role-based portals (Reportee, Police, Admin), and a camera node that reads number plates from a phone's video stream using a custom-trained YOLOv8 detector and OCR. The common problem is that stolen-vehicle recovery depends on officers chancing to recognise a plate. The system's core flow is: camera node reads a plate, the backend matches it against active reports, and connected police dashboards receive an alert over WebSocket.

## A.3 Individual Role and Responsibilities

The group's work was divided into four roles. The student's role was **Role 1: AI/vision**, which covers work areas 1 (detection model) and 2 (camera node).

| No. | Area of Responsibility | Description |
|---|---|---|
| 1 | Detection model (AI) | Collect and label Zambian plate images, train YOLOv8n to find the plate, evaluate it |
| 2 | Camera node (edge) | Read the phone video stream, run detection and OCR, clean and validate the text, drop duplicate reads, send results to the backend |

Other roles, for reference: **Role 2** backend API, database, `check-plate` logic, JWT, bcrypt, role enforcement, user management and audit log; **Role 3** WebSocket alerts, camera status and live-feed proxy, system health, and the phone-to-server wiring; **Role 4** the React portals, analytics, integration tests, run scripts and documentation.

## A.4 Detailed Individual Contribution

- **Data collection and annotation:** collected Zambian plate images with a phone camera; annotated them in Roboflow with one class; exported in YOLOv8 format with the recorded pre-processing and augmentation.
- **Model development:** trained YOLOv8n from COCO-pretrained weights on GPU; compared runs; selected the weights used by the node (`svds-plate-detector-final-2/weights/best.pt`).
- **Algorithm development:** designed the read-and-report pipeline (frame sampling, crop, greyscale, 4× upscale, Otsu threshold, EasyOCR with allowlist, confidence floor, regex validation) and the fuzzy duplicate-suppression algorithm.
- **Software development:** wrote `vrrs-node/plate_node.py` and `vrrs-node/plate_utils.py`.
- **Testing:** wrote the eight unit tests for the node's pure logic and evaluated the detector.
- **Deployment and configuration:** set up the GPU Python environment and resolved the OpenMP, Visual C++ runtime and OpenCV package conflicts.
- **Documentation:** this report's AI/vision material, including the detection chapter content and the node's `.env` documentation.

## A.5 Individual Deliverables

| No. | Deliverable | Student's Contribution |
|---|---|---|
| 1 | Annotated dataset (`zambia-number-plate-detection`, v3) | Collected, annotated, exported |
| 2 | Trained detector `best.pt` and its training record (`args.yaml`, `results.csv`, curves) | Trained, evaluated, selected |
| 3 | Camera node `plate_node.py` | Designed and implemented |
| 4 | `plate_utils.py` with 8 unit tests | Designed, implemented, tested |
| 5 | Node configuration (`.env` keys) and set-up instructions | Defined and documented |

## A.6 Contribution to the Main System or Research Output

The student produced the component that turns camera video into plate strings. It is the input to the backend's `POST /alerts/check-plate` endpoint. The endpoint itself, the matching against reports and the storage of alerts were built by the backend member. The alert broadcast and camera status display were built by the real-time and integration member. The pages that show the results were built by the frontend member. The `check-plate` contract (§4.6) was agreed jointly between the node and the backend.

## A.7 Individual Implementation and Technical Work

Modules and components implemented by the student: the plate dataset and `data.yaml`; the trained YOLOv8n detector; `plate_node.py` (stream capture and reconnection, frame sampling, detector inference, crop pre-processing, OCR call, reporting to the backend, preview window); `plate_utils.py` (`clean_plate_text`, `is_recent_duplicate`); `tests/test_plate_utils.py`. Datasets and experiments handled: the Roboflow export (1,890 images), the 100-epoch training run, and the validation and test-split evaluations in Chapter 6.

## A.8 Individual Testing and Evaluation Contribution

The student designed and ran the node unit tests (8 of 8 passing) and the detector evaluations reported in Chapter 6, and wrote the analysis in Chapters 6 and 7. The backend `pytest` suite and the manual browser checks of the web application were carried out by other members and are not claimed here.

## A.9 Collaboration with Other Group Members

- The node depends on the **backend member's** `check-plate` endpoint: its request format and its `CLEAR`/`STOLEN` response were agreed jointly. The backend's plate normalisation means the node does not have to reproduce the backend's matching rules.
- The **real-time and integration member's** alert broadcast and camera status/feed proxy depend on the node's `CAMERA_ID` and on the phone stream address, which both share.
- The **frontend member's** pages display the node's detections and status.

## A.10 Contribution Summary

1. **Work primarily completed by the student:** the dataset, the trained detector, the camera node, the plate utilities and their tests.
2. **Work completed jointly with other members:** the node-to-backend contract; shared configuration of the phone stream address; end-to-end start-up through `run-all.ps1`.
3. **Work primarily completed by other members and used here:** the backend, database and `check-plate` matching; authentication and access control; the WebSocket alert delivery; the web portals.

## A.11 Estimated Contribution

*The percentages below are the student's own estimate and must be completed by the student. They were not derived from any record.*

| Project Activity | Individual Contribution | Collaborative Contribution |
|---|---|---|
| Problem Analysis | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Literature Review | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Requirements Analysis | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| System/Research Design | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Implementation / Development | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Testing and Evaluation | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Documentation | <span class="todo">[%]</span> | <span class="todo">[%]</span> |
| Other | <span class="todo">[%]</span> | <span class="todo">[%]</span> |

## A.12 Statement of Authorship and Contribution

I confirm that the contribution described in this statement accurately represents the work that I personally undertook as part of the group project. I have identified collaborative work and have not knowingly claimed the work of another group member as my own.

**Student Name:** Moomba Nicholas Katapazi
**Computer Number:** ______________________
**Signature:** ______________________
**Date:** ______________________

## A.13 Supervisor Verification

I confirm that, to the best of my knowledge, the contribution described above is consistent with the student's participation in the group project.

**Supervisor Name:** ______________________
**Signature:** ______________________
**Date:** ______________________

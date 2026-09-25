# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews the concepts behind automatic licence plate recognition (ALPR), the existing systems relevant to SVDS, and the gap the project fills. It is organised as: key concepts (§2.2), existing systems (§2.3), a comparison (§2.4), the gap (§2.5), and the framework that guides the design (§2.6).

## 2.2 Key Concepts and Theories

### 2.2.1 Two-stage ALPR

Most ALPR pipelines split the problem into two stages: (1) **localisation**, which finds the plate in the image, and (2) **recognition**, which reads the characters inside the located region. Keeping the stages separate makes each one simpler, independently testable and replaceable.

### 2.2.2 Object detection and YOLO

Object detection predicts a bounding box and a confidence score for each object of interest in an image. The YOLO ("You Only Look Once") family are single-stage detectors: one network pass produces all boxes, which makes them fast enough for video. YOLOv8, from Ultralytics, is an anchor-free member of the family with several sizes; the smallest, **YOLOv8n**, is used here because it runs in real time on a modest GPU. Models are normally fine-tuned from weights pretrained on a large dataset (COCO) rather than trained from scratch, which reduces the amount of new data needed.

### 2.2.3 Optical character recognition

OCR converts an image of text into a string. **EasyOCR** is an open-source, PyTorch-based engine that supports a character *allowlist*, which restricts the output alphabet and reduces spurious characters. OCR accuracy on a small plate crop depends strongly on pre-processing such as greyscale conversion, upscaling and binarisation (thresholding). **Otsu's method** chooses the binarisation threshold automatically from the image histogram.

### 2.2.4 Detection metrics

- **Precision** = TP / (TP + FP): of the boxes the model draws, the fraction that are correct.
- **Recall** = TP / (TP + FN): of the real plates, the fraction the model finds.
- **IoU** (intersection over union) measures how well a predicted box overlaps a true box.
- **mAP50** is the mean average precision when a prediction counts as correct at IoU ≥ 0.5; **mAP50-95** averages over IoU thresholds from 0.5 to 0.95 and is stricter.

### 2.2.5 Fuzzy string matching

OCR on a moving or stationary vehicle rarely returns exactly the same string in consecutive frames. Comparing readings by *similarity* instead of equality tolerates this. Python's `difflib.SequenceMatcher` returns a similarity ratio between 0 and 1 for two strings; it is used here to decide whether a new reading is the same plate as a recent one.

## 2.3 Existing Systems / Related Work

- **OpenALPR** is an open-source ALPR library with pre-trained models for several countries' plate formats. It is a strong general reference, but it does not ship a model trained on Zambian plates.
- **Plate Recognizer** is a commercial ALPR service. It uses the same split as this project, a lightweight capture client plus a separate recognition service. It is a paid API, which is a barrier for a budget-limited public-sector deployment.
- **Ultralytics YOLOv8** is chosen here over older YOLO versions and over two-stage detectors such as Faster R-CNN for its balance of speed and accuracy on one consumer GPU, and for its support for training on a small custom single-class dataset.
- **EasyOCR** is used for recognition (§2.2.3).
- **Vehicle registry and reporting systems.** Registry and reporting systems store reports, ownership records and status but do not themselves watch for the reported vehicle. Where ALPR is used in policing, it is typically fixed roadside infrastructure rather than something integrated with a public reporting system.

*Note on sources.* The descriptions above are based on the projects' public documentation, listed in the References. No comparative accuracy figures from other systems are quoted, because none were measured on Zambian plates in this project.

## 2.4 Comparative Analysis

| Criterion | OpenALPR | Plate Recognizer | This project (SVDS) |
|---|---|---|---|
| Cost model | Open source | Paid service | Open source, self-hosted |
| Trained on Zambian plates | No (generic regional models) | Not specifically | Yes (custom dataset) |
| Runs on own hardware | Yes | Cloud API | Yes (phone + local GPU) |
| Linked to a public reporting workflow | No | No | Yes (matches against active reports) |
| Alerts to officers in real time | Not included | Not included | Yes (WebSocket, built by the integration member) |

The table compares design properties, not accuracy. No accuracy comparison was carried out.

## 2.5 Research / Knowledge Gap

No system reviewed combines (a) public self-service reporting, (b) role-based police and admin oversight, (c) a detector trained for the specific plate format, and (d) real-time delivery of detection alerts. SVDS fills that gap. For the AI/vision component the specific gap is a **detector trained on locally collected Zambian plate images and a robust, noise-tolerant read-and-report pipeline around it**.

## 2.6 Conceptual Framework

The design follows a staged pipeline in which each stage discards input it cannot trust, so only clean, validated readings reach the backend:

```
frame → sample every Nth frame → detect plate (YOLOv8n) → crop
      → greyscale / 4x upscale / Otsu threshold → OCR (allowlist)
      → clean and validate text → fuzzy duplicate check → report to backend
```

Localisation is separated from recognition (§2.2.1), and the camera node is separated from the backend so the two can be deployed and changed independently.

## 2.7 Chapter Summary

ALPR and vehicle-registry systems are both mature on their own, but no reviewed system joins them for a Zambian plate format with a public, police and admin role split. The AI/vision component therefore adopts a two-stage pipeline: a custom-trained YOLOv8n localiser, EasyOCR recognition with pre-processing and validation, and fuzzy duplicate suppression, run in a decoupled camera-node process.

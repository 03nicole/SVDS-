# Chapter 8: Conclusion and Recommendations

## 8.1 Introduction

This chapter summarises the project, states the conclusions the evidence supports, reviews the individual objectives, and gives recommendations and future work.

## 8.2 Summary of the Project

Stolen-vehicle recovery in Zambia relies on officers chancing to recognise a plate. The group built SVDS on top of the VRRS registry so that a plate seen by a camera is checked automatically against active reports. This report covered the AI/vision component. A single-class YOLOv8n detector was fine-tuned on 1,890 labelled images of Zambian plates, and a camera node was built around it. The node samples a phone video stream, crops and pre-processes detected plates, reads them with EasyOCR, validates the text, suppresses noisy duplicate reads by fuzzy matching, and reports each reading to the backend over one HTTP endpoint.

## 8.3 Conclusions

1. A small, locally collected dataset is enough to train a plate detector with high precision (0.990) and moderate recall (0.752) on the validation split, at about 11 ms per image on a Quadro P2000.
2. OCR noise, not detection, was the main practical problem on live footage. A fuzzy similarity check handles it, and unit tests confirm the behaviour.
3. A decoupled node that talks to the backend over one HTTP contract works: live readings from a phone stream reached the backend and were answered.
4. The evidence does not yet show end-to-end read accuracy, alert latency, or a recorded `STOLEN` alert from a live run. The test split (7 images) is too small to support strong claims.

## 8.4 Achievement of Objectives

| Objective | Status |
|---|---|
| O1 Dataset | Achieved (original photograph count to be confirmed) |
| O2 Detector above 0.95 precision and 0.75 mAP50 | Achieved (0.990 / 0.797) |
| O3 OCR and validation | Achieved in implementation; read accuracy unmeasured |
| O4 Duplicate suppression | Achieved at unit level; not measured on live footage |
| O5 Decoupled node | Largely achieved; live reporting shown, alert path and reconnection not shown |
| O6 Evaluation | Achieved for the model and pure logic, not the whole pipeline |

Research question 1 is answered for detection and left open for reading accuracy. Research question 2 is answered yes.

## 8.5 Recommendations

- Before any field use, build a labelled set of plate crops with typed text and measure OCR accuracy.
- Enlarge the test split and include night, glare, motion blur and angled shots.
- Put `/alerts/check-plate` behind a private network or an API key.
- Keep a human officer in the loop: treat every alert as a lead, never as proof.
- Confirm the licences of YOLOv8 (AGPL-3.0), EasyOCR and the dataset before any deployment beyond a prototype.

## 8.6 Future Work

- Record a full live run that produces a `STOLEN` alert, and measure latency.
- Tune the fuzzy threshold on labelled live readings.
- Evaluate the pre-processing stage and alternative OCR engines.
- Read GPS location from the phone instead of a configured string.
- Export the model to ONNX or TensorRT to reduce GPU dependence, and support several camera nodes.
- Discover the phone stream address automatically instead of editing `.env`.

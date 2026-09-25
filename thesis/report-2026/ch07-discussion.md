# Chapter 7: Discussion

## 7.1 Introduction

This chapter interprets the results of Chapter 6 in relation to the problem and the objectives, compares them with related work, states the contributions, and discusses limitations.

## 7.2 Interpretation of Findings

**The detector suits the use case.** Precision of about 0.99 means almost every box the model draws is a real plate. Recall of about 0.75 means roughly one plate in four is missed in a still image. For a system whose alerts go to police, this is the right side of the trade-off. A missed plate in one sampled frame is likely to be caught in a later frame of the same passing vehicle, whereas a false box would trigger OCR and possibly a wrong match. This reasoning is an argument from design, not a measurement: the per-vehicle detection rate across a video was not measured.

**mAP50 versus mAP50-95.** The gap between mAP50 (about 0.80) and mAP50-95 (about 0.69) shows that boxes are usually in the right place but not always tight. That matters little for this pipeline, because the crop is upscaled and binarised before OCR and a slightly loose box still contains the plate. A box that clips characters would hurt OCR more than one that is too large, and this was not analysed.

**Software-level noise handling matters as much as the model.** The largest practical problem on real footage was not detection but OCR jitter on a stationary vehicle. Fuzzy de-duplication fixed it in a few lines of code, and unit tests now pin the behaviour down.

**Answer to research question 1** (can YOLOv8n plus an open-source OCR engine read Zambian plates well enough for real-time matching on a phone camera and consumer GPU?). The detection half is supported by measured metrics. The reading half is **not yet supported by measurement**: no labelled plate-text set exists, so end-to-end read accuracy is unknown, and no live run producing a `STOLEN` alert was recorded. The honest answer is "detection: yes, on this evidence; reading and real-time matching: plausible and implemented, but unproven".

**Answer to research question 2** (can the pipeline be a decoupled component talking only over HTTP?). Yes. The node is a separate process with a single-endpoint contract, and it has been run and tested without importing anything from the backend.

## 7.3 Comparison with Existing Work

No accuracy figures from OpenALPR, Plate Recognizer or published ALPR studies were reproduced on the Zambian test set, so no numerical comparison is made. The comparison in §2.4 is on design properties: the project is self-hosted and open source, is trained on locally collected plates, and is linked to a reporting workflow. Reported mAP values from other datasets are not comparable with these results, because the datasets, the number of classes and the difficulty differ.

## 7.4 Contributions of the Project

- **Practical:** a working prototype in which a phone camera and a consumer GPU feed plate readings into a police-facing stolen-vehicle registry.
- **Technical:** a single-class YOLOv8n plate detector fine-tuned on locally collected Zambian plate images, released as reproducible artifacts (training arguments, per-epoch metrics, curves); a noise-tolerant read-validate-de-duplicate pipeline; a GPU-free unit-testable core.
- **Architectural:** a decoupled camera-node design that could be moved to fixed roadside cameras without backend changes.

## 7.5 Limitations and Implications

| Limitation | Implication for interpreting the results |
|---|---|
| Small dataset with uncertain source-image count | The metrics may not generalise to other cameras, regions, plate styles or lighting |
| Splits checked for leakage by filename only | No source-image name appears in more than one split (verified, §3.3), so augmented copies of one photograph did not leak between training and validation. This rests on filenames being faithful to the original photographs |
| Test split has 7 images | Test-split metrics have wide uncertainty and cannot support strong claims |
| No plate-text ground truth | OCR accuracy, and therefore the true rate of correct end-to-end matches, is unknown |
| No recorded `STOLEN` alert from a live run | Latency and the full alert path are not established |
| Single machine and camera | Performance on other hardware is unknown; CPU-only operation falls behind the stream |
| Fuzzy threshold not tuned on live data | The value 0.75 could merge different plates that differ by one or two characters |
| Plate crops are pre-processed the same way in all lighting | Night-time and glare performance is unknown |

## 7.6 Chapter Summary

The measured results support the detector's suitability for a precision-first police use case. Reading accuracy and live performance remain unmeasured, and the report states this instead of extrapolating. The main contribution is a decoupled, tested pipeline with a locally trained model.

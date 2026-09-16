# 2. Literature Review

*SDLC phase: Research / analysis (precedes formal requirements gathering)*

## 2.1 Introduction

This chapter surveys existing automatic license plate recognition (ALPR) approaches and
law-enforcement/vehicle-registry systems relevant to SVDS, to establish what already
exists, what is transferable, and what gap this project fills — specifically, the
absence of any ALPR-integrated stolen-vehicle registry built for the Zambian context.

## 2.2 Review of Similar Systems

### 2.2.1 Commercial and open ALPR platforms

- **OpenALPR** — an open-source ALPR library offering pre-trained models for several
  countries' plate formats. It is a strong general-purpose reference but ships no model
  trained on Zambian plates, and its default pipeline (classical image processing plus
  a small CNN) predates the anchor-free, single-stage detectors (e.g., YOLOv8) used in
  this project.
- **Plate Recognizer** (a commercial ALPR SaaS) — demonstrates the split this project
  also uses: a lightweight edge client that captures frames and a separate service that
  performs recognition. Its accuracy is strong across many plate formats but the service
  is a paid API, which is a barrier for public-sector deployment on a limited budget —
  reinforcing the case for a self-hosted, custom-trained alternative.
- **Ultralytics YOLOv8** (the detector family used in this project) — chosen over older
  YOLO versions and over two-stage detectors (e.g., Faster R-CNN) for its balance of
  inference speed and accuracy on a single consumer GPU, and its first-class support for
  training on a small, custom, single-class dataset via the Ultralytics CLI/Python API.
- **EasyOCR** — an open-source, PyTorch-based OCR engine supporting a character
  allowlist, which is used here to constrain readings to the alphanumeric character set
  a Zambian plate can contain, reducing spurious reads from background text.

### 2.2.2 Vehicle registry and reporting systems

Existing vehicle registry and reporting workflows in the literature and in observed
practice are predominantly record-keeping systems: they store reports, ownership
records, and status, but do not themselves watch for the reported vehicle. Where ALPR
is used in policing literature, it is typically deployed as fixed, purpose-built
roadside camera infrastructure (e.g., number-plate recognition cameras on major routes)
rather than integrated with a public-facing reporting system that a citizen can use
directly. SVDS's contribution is closing that loop: a report filed by the public
immediately becomes something a camera node can match against, without a separate
data-entry step for police to "load" the report into a detection system.

### 2.2.3 Gap this project addresses

No system reviewed combines all of: (a) public self-service reporting, (b)
role-based access for police/admin oversight, (c) a custom-trained detector for the
specific plate format in question, and (d) real-time WebSocket delivery of detection
alerts to connected officers. SVDS's architecture — a fully decoupled camera node
talking to a conventional registry backend over HTTP — is deliberately chosen so the
detection pipeline could later be pointed at fixed roadside cameras without changing
the backend at all.

## 2.3 Research Methodology

Requirements and design decisions for SVDS were informed by:

- **Background reading** on ALPR architectures (YOLO family detectors, OCR engines) and
  on typical vehicle-registry data models (report lifecycle, audit logging).
- **Direct inspection of the problem domain** — the manual, paper-based nature of
  current stolen-vehicle reporting, and the fact that police, reportees, and
  administrators need materially different views of the same underlying data (which
  directly shaped the three-role design).
- **Iterative build-and-test cycles**, where the camera-node pipeline (frame capture →
  detection → OCR → cleaning → dedup → HTTP report) was refined against real footage
  from a phone camera rather than only against the training/validation image set.

## 2.4 Summary

ALPR technology and vehicle-registry web applications are both mature, well-documented
domains individually. The literature and available products show little precedent for
combining the two into a single system aimed at a specific national plate format and a
public/police/admin role split — which is the space this project occupies.

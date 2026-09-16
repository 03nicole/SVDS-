[Your University]
[School / Faculty]
[Department of Computer Science]

# SVDS — VEHICLE REGISTRY AND STOLEN VEHICLE DETECTION SYSTEM

### A camera-based license plate detection and vehicle registry system for the Zambia Police Service

BY

**[Your Full Name]**

[Course Code] FINAL YEAR COURSE PROJECT

A THESIS SUBMITTED IN PARTIAL FULFILMENT OF THE
REQUIREMENT FOR THE AWARD OF A BACHELOR'S DEGREE OF
COMPUTER SCIENCE

SUPERVISOR: [Supervisor Name]

---

## DECLARATION

I, the undersigned, hereby declare that the Vehicle Registry and Reporting System /
Stolen Vehicle Detection System (VRRS/SVDS) is my own work. That it has not been
submitted for any degree or examination in any other university to my knowledge, and
that all sources I have used or quoted have been indicated and acknowledged by complete
references.

Author: **[Your Full Name]**
Student Number: **[Student Number]**
Signature: ___________________________
Date: [Submission Date]

Supervisor: **[Supervisor Name]**
Signature: ___________________________

---

## DEDICATION

[Write your own — the golf thesis dedicated the work to family/faith; keep this
section personal to you rather than templated.]

---

## ACKNOWLEDGEMENT

I want to express my gratitude to [Supervisor Name], my supervisor, for guidance and
feedback throughout this project. [Add anyone else who supported the work — family,
the Zambia Police Service contacts who informed the requirements interviews, etc.]

---

## ABSTRACT

Vehicle theft investigation in Zambia currently relies on manual, paper-based reporting
and word-of-mouth alerting between police stations — a stolen vehicle report filed at
one station has no mechanism to automatically flag the vehicle if it is later sighted
elsewhere. This project, SVDS (Stolen Vehicle Detection System), addresses that gap by
combining a conventional vehicle-registry web application with a real-time,
camera-based automatic license plate recognition (ALPR) pipeline.

The system has three cooperating parts. A FastAPI backend exposes a REST and WebSocket
API over a PostgreSQL database, enforcing role-based access for three user types:
Reportee (the public, filing and tracking stolen-vehicle reports), Police (viewing live
detection alerts, managing the vehicle registry, and analytics), and Admin (user and
system management). A React single-page application provides the interface for all
three roles. A separate, decoupled camera-node process streams video from a
phone-mounted camera, detects license plates with a custom-trained YOLOv8n object
detector, reads the plate text with EasyOCR, and reports matches to the backend over
plain HTTP — requiring no coupling to the backend's internals or technology choices.

The detection model was trained on a self-collected, Roboflow-annotated dataset of
Zambian number plates (335 source images, augmented to 1,890) and evaluated at
precision 0.988 and recall 0.751 (mAP50 0.801) after 100 training epochs. The full
system was tested end-to-end — from a real phone camera feed, through detection and
OCR, to a live WebSocket alert appearing on the police dashboard — and validated with
an automated test suite (39 tests) covering authentication, role-based access control,
the report lifecycle, plate-matching logic, and the analytics layer.

This work demonstrates that a real-time ALPR pipeline can be integrated into a
practical, role-based law-enforcement registry system using consumer hardware (an
Android phone as the camera) and open-source computer vision tooling, without recourse
to commercial ALPR licensing.

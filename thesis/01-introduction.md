# 1. Introduction

*SDLC phase: Problem identification / feasibility study*

## 1.1 Background

Vehicle theft is a persistent problem for law enforcement in Zambia, and the process
of recovering a stolen vehicle depends heavily on chance: an officer at a checkpoint or
on patrol happening to recognize a plate number from a paper report or a radio
bulletin. Vehicle registry records, incident reports, and eyewitness descriptions are
typically kept on paper or in disconnected station-level spreadsheets, which means a
report filed at one police station is invisible to an officer working in a different
part of the same city, let alone a different province.

At the same time, automatic license plate recognition (ALPR) has become inexpensive
enough to build from commodity hardware. A single Android phone can stream video over
Wi-Fi, and open-source object detection models (this project uses Ultralytics YOLOv8)
can be trained on a modest, self-collected image set and run in real time on a
consumer GPU. This closes the gap between "a report exists somewhere" and "a report is
automatically checked against every vehicle a camera sees."

## 1.2 Problem Statement

There is no system available to the Zambia Police Service that automatically checks a
vehicle's license plate — as seen by a camera in the field — against an active
stolen-vehicle registry in real time. Existing practice depends on manual recognition
by officers and manual cross-referencing of paper reports. This results in: (a) slow or
missed detections of stolen vehicles that pass through monitored locations, (b) no
centralized, real-time way for a report filed by the public to reach every officer who
might encounter the vehicle, and (c) no audit trail connecting a detection event back to
the report that triggered it.

## 1.3 Research Questions

1. Can a custom-trained, lightweight object detector (YOLOv8n) combined with an
   open-source OCR engine achieve detection and recognition accuracy sufficient for
   real-time plate matching on Zambian number plates, using only a phone camera and a
   consumer GPU?
2. Can such a detection pipeline be integrated into a role-based registry system as a
   fully decoupled component — communicating only over plain HTTP/WebSocket — without
   requiring the detection logic to be embedded in the backend itself?
3. Does a real-time alert delivered over WebSocket meaningfully reduce the latency
   between "a stolen vehicle is sighted" and "a police officer is notified," compared
   to the manual process it replaces?

## 1.4 Aim

The aim of this project is to design, implement, and evaluate SVDS: a vehicle registry
and reporting web application integrated with a real-time, camera-based license plate
detection pipeline, for use by the Zambia Police Service and the public it serves.

## 1.5 Objectives

- Implement role-based accounts for three user types — Reportee, Police, and Admin —
  each with access scoped to what that role needs (`vrrs-backend/app/middleware.py`).
- Allow the public to file, track, and view the status of stolen-vehicle reports
  (`under_review` → `missing` → `found`).
- Give police officers a live view of detection alerts, the vehicle registry, and
  system analytics, with the ability to activate reports, mark vehicles recovered, and
  flag false positives.
- Give administrators control over user accounts, roles, and visibility into system
  health and the audit trail.
- Collect and annotate a dataset of Zambian license plates, and train a YOLOv8-based
  object detector to localize plates in a camera frame.
- Integrate an OCR stage (EasyOCR) to read the localized plate text, and validate/clean
  that text against the expected format.
- Build a decoupled camera-node process that connects a real video stream (an Android
  phone's IP Webcam feed) to the detection pipeline and reports matches to the backend
  over HTTP, independent of the backend's and frontend's technology stack.
- Deliver real-time alerts to connected police/admin clients over WebSocket the moment
  a stolen vehicle is detected.
- Evaluate the detector quantitatively (precision, recall, mAP) and the system as a
  whole through automated and manual/system testing.

## 1.6 Scope

This project covers the vehicle-registry web application (backend + frontend), the
camera-node detection pipeline, and the integration between them. It does **not**
cover: a native mobile app for the public (the public-facing interface is a responsive
web app), payment/e-government integration, multi-camera fleet management beyond a
single configured node, or GPS-based camera geolocation (the camera's location is
currently a configured string, not read from the phone's sensors — see §9.2).

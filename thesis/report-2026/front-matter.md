<div class="plain-title">ABSTRACT</div>

Stolen-vehicle recovery in Zambia depends largely on police officers chancing to recognise a plate number from a paper report or radio bulletin. This project, carried out by a group of four students, built SVDS, a Stolen Vehicle Detection System on top of the VRRS vehicle registry. The public files stolen-vehicle reports through a web application, and a camera node reads plates from a phone's video stream and checks them against active reports, so connected police officers are alerted in real time.

This individual report covers the AI/vision component: the plate-detection model and the camera node. A single-class YOLOv8n detector was fine-tuned on a Roboflow-annotated dataset of 1,890 labelled images (1,476 training, 407 validation, 7 test) of Zambian number plates. Detected plates are cropped, converted to greyscale, upscaled and thresholded, and read with EasyOCR restricted to letters and digits. The text is validated as 5–8 alphanumeric characters and then de-duplicated by fuzzy string similarity, because OCR noise defeats exact-match cooldowns. Each accepted reading is sent to the backend over a single HTTP endpoint, so the node runs as a decoupled process.

After 100 training epochs the model reached a precision of 0.988, a recall of 0.751, an mAP50 of 0.801 and an mAP50-95 of 0.686 on the validation split. The eight unit tests for the node's plate-cleaning and de-duplication logic all pass. A live run of the node read plates from a phone stream and reached the backend, but reading accuracy (OCR), alert latency and a recorded stolen-vehicle alert were not measured, and the report states these limitations plainly. The main contributions are a locally trained plate detector, a noise-tolerant read-and-report pipeline, and a decoupled camera-node design that could be moved to fixed roadside cameras without changing the backend.

**Keywords:** licence plate recognition; YOLOv8; object detection; optical character recognition; stolen vehicle detection

<div class="plain-title">ACKNOWLEDGEMENTS</div>

<span class="todo">[Write acknowledgements here: supervisor, group members (backend and security, real-time and integration, frontend), family, and anyone who helped collect plate images. The author must write this; it is personal.]</span>

<div class="plain-title">CONTENTS</div>

**Preliminary pages:** Declaration · Approval · Abstract · Acknowledgements · List of Abbreviations and Acronyms · Note on Group Projects

**1 Introduction** — 1.1 Background and Context · 1.2 Problem Statement · 1.3 Project Aim · 1.4 Project Objectives · 1.5 Research Questions · 1.6 Scope of the Project (In Scope, Out of Scope) · 1.7 Significance · 1.8 Limitations · 1.9 Organisation of the Report

**2 Literature Review** — 2.1 Introduction · 2.2 Key Concepts and Theories · 2.3 Existing Systems / Related Work · 2.4 Comparative Analysis · 2.5 Research / Knowledge Gap · 2.6 Conceptual Framework · 2.7 Chapter Summary

**3 Methodology** — 3.1 Introduction · 3.2 Research / Development Approach · 3.3 Requirements / Data Collection · 3.4 System Architecture / Research Workflow · 3.5 Tools and Technologies · 3.6 Ethical and Legal Considerations · 3.7 Evaluation Method · 3.8 Chapter Summary

**4 System Analysis and Design** — 4.1 Introduction · 4.2 Stakeholder and User Analysis · 4.3 Functional Requirements · 4.4 Non-Functional Requirements · 4.5 Use Cases / User Stories · 4.6 System / Solution Architecture · 4.7 Database / Data Design · 4.8 Interface / Interaction Design · 4.9 Algorithms / Models / Technical Design · 4.10 Chapter Summary

**5 Implementation / Development** — 5.1 Introduction · 5.2 Development Environment · 5.3 System Components / Modules · 5.4 Key Implementation Details · 5.5 Integration · 5.6 Challenges and Solutions · 5.7 Individual Contribution · 5.8 Chapter Summary

**6 Testing, Results and Evaluation** — 6.1 Introduction · 6.2 Testing Strategy · 6.3 Test Cases and Results · 6.4 Experimental / Performance Results · 6.5 User Evaluation · 6.6 Analysis of Results · 6.7 Objective-by-Objective Evaluation · 6.8 Individual Results · 6.9 Chapter Summary

**7 Discussion** — 7.1 Introduction · 7.2 Interpretation of Findings · 7.3 Comparison with Existing Work · 7.4 Contributions of the Project · 7.5 Limitations and Implications · 7.6 Chapter Summary

**8 Conclusion and Recommendations** — 8.1 Introduction · 8.2 Summary of the Project · 8.3 Conclusions · 8.4 Achievement of Objectives · 8.5 Recommendations · 8.6 Future Work

**References**

**Appendices** — A Individual Contribution Statement · B User Manual / Installation Guide · C Additional System Designs / Diagrams · D Additional Test Cases and Results · E Data Collection Instruments · F Additional Code / Configuration · G Other Supporting Material

<span class="todo">[Page numbers are not shown here. In Word, apply heading styles and use References → Table of Contents to generate a numbered contents page, and a List of Figures and List of Tables the same way.]</span>

<div class="plain-title">LIST OF ABBREVIATIONS AND ACRONYMS</div>

| Abbreviation | Meaning |
|---|---|
| ALPR | Automatic Licence Plate Recognition |
| API | Application Programming Interface |
| CUDA | Compute Unified Device Architecture (NVIDIA GPU computing platform) |
| DBMS | Database Management System |
| GPU | Graphics Processing Unit |
| HTTP | Hypertext Transfer Protocol |
| IoU | Intersection over Union |
| JWT | JSON Web Token |
| mAP | mean Average Precision |
| MJPEG | Motion JPEG (video stream format) |
| ML | Machine Learning |
| OCR | Optical Character Recognition |
| SVDS | Stolen Vehicle Detection System |
| UI | User Interface |
| VRRS | Vehicle Registry and Reporting System |
| YOLO | You Only Look Once (object detector family) |

<div class="plain-title">NOTE ON GROUP PROJECTS</div>

Students who worked on a project as a group are strongly encouraged to prepare their own individual final reports rather than submitting identical reports. The project, system, dataset, or overall research problem may be shared, but each student's report should clearly demonstrate that student's own understanding, responsibilities, work, results, and contribution to the project.

In particular, group-project students should:

- state the overall group project and explain how the individual work fits within it;
- clearly identify their own responsibilities and deliverables;
- focus detailed analysis, design, implementation, experiments, testing, and/or evaluation on their own contribution;
- acknowledge the work completed by other group members where it is discussed;
- include an *Individual Contribution Statement* in the appendices; and
- not claim another group member's work, results, code, data collection, or design decisions as their own.

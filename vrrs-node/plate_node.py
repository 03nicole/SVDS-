"""SVDS camera node: watches a phone-streamed video feed, detects license
plates with YOLO, reads them with EasyOCR, and reports matches to the VRRS
backend's /alerts/check-plate endpoint.

Runs independently of the backend/frontend — it only talks to them over
plain HTTP, matching the decoupled camera-node contract in the project README.
"""
import os

# torch and opencv each bundle their own copy of Intel's OpenMP runtime
# (libiomp5md.dll); loading both aborts the process on Windows unless this
# is set before either is imported.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import re
import time

import cv2
import requests
from dotenv import load_dotenv
from ultralytics import YOLO
import easyocr

load_dotenv()

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    r"C:\Users\user\runs\detect\svds-plate-detector-final-2\weights\best.pt",
)
STREAM_URL = os.getenv("PHONE_STREAM_URL", "http://172.20.10.13:8080/video")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CAMERA_ID = os.getenv("CAMERA_ID", "PHONE-NODE-1")
LOCATION_SPOTTED = os.getenv("LOCATION_SPOTTED", "Unknown")
DETECT_CONF = float(os.getenv("DETECT_CONF", "0.4"))
PROCESS_EVERY_N_FRAMES = int(os.getenv("PROCESS_EVERY_N_FRAMES", "5"))
RESEND_COOLDOWN_SECONDS = int(os.getenv("RESEND_COOLDOWN_SECONDS", "15"))
DEVICE = os.getenv("DEVICE", "cuda")

# Zambian plates look like "BAA 1234" — three letters, four digits, no spaces
# once cleaned. Loose on purpose since OCR on a phone feed is noisy.
PLATE_PATTERN = re.compile(r"[A-Z0-9]{5,8}")


def clean_plate_text(raw: str) -> str | None:
    text = re.sub(r"[^A-Z0-9]", "", raw.upper())
    return text if PLATE_PATTERN.fullmatch(text) else None


def report_plate(plate: str, confidence: float) -> None:
    payload = {
        "license_plate": plate,
        "camera_id": CAMERA_ID,
        "confidence_score": confidence,
        "location_spotted": LOCATION_SPOTTED,
    }
    try:
        resp = requests.post(f"{BACKEND_URL}/alerts/check-plate", json=payload, timeout=5)
        resp.raise_for_status()
        print(f"[{plate}] backend status: {resp.json().get('status')}")
    except requests.RequestException as e:
        print(f"[{plate}] failed to reach backend: {e}")


def main() -> None:
    print(f"Loading detector from {MODEL_PATH} on {DEVICE} ...")
    model = YOLO(MODEL_PATH)
    model.to(DEVICE)
    print("Loading OCR reader ...")
    reader = easyocr.Reader(["en"], gpu=(DEVICE == "cuda"))

    print(f"Connecting to phone stream: {STREAM_URL}")
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video stream at {STREAM_URL}. "
            "Check the IP Webcam app is running on the phone, both devices "
            "are on the same Wi-Fi, and PHONE_STREAM_URL in .env matches."
        )

    last_sent: dict[str, float] = {}
    frame_count = 0

    print("Running. Press 'q' in the preview window to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Lost connection to stream, retrying...")
            time.sleep(1)
            cap.release()
            cap = cv2.VideoCapture(STREAM_URL)
            continue

        frame_count += 1
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            for res in model(frame, conf=DETECT_CONF, device=DEVICE, verbose=False):
                for box in res.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    det_conf = float(box.conf[0])
                    crop = frame[max(0, y1):y2, max(0, x1):x2]
                    if crop.size == 0:
                        continue

                    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
                    thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                    ocr_results = reader.readtext(
                        thresh, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
                    )
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    parts = [text.strip() for _, text, conf in ocr_results if conf > 0.3]
                    if not parts:
                        continue

                    plate = clean_plate_text(" ".join(parts))
                    if not plate:
                        continue

                    cv2.putText(frame, plate, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    now = time.time()
                    if now - last_sent.get(plate, 0) > RESEND_COOLDOWN_SECONDS:
                        last_sent[plate] = now
                        report_plate(plate, round(det_conf * 100, 1))

        cv2.imshow("SVDS Plate Node - press q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

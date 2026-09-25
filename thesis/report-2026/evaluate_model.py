"""Re-evaluate the deployed detector weights on the validation and test splits.
Writes eval_results.json next to this script. Run with the GPU env (yolov8-env)."""
import json, os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from pathlib import Path
from ultralytics import YOLO

W = r"C:\Users\user\runs\detect\svds-plate-detector-final-2\weights\best.pt"
D = r"C:\Users\user\zambia-number-plate-detection-3\data.yaml"
out = {}
m = YOLO(W)
for split in ("val", "test"):
    r = m.val(data=D, split=split, imgsz=640, batch=8, workers=0, plots=False,
              verbose=False, project=str(Path(__file__).parent / "assets" / "evalruns"),
              name=split, exist_ok=True)
    b = r.box
    out[split] = {"precision": round(float(b.mp), 4), "recall": round(float(b.mr), 4),
                  "mAP50": round(float(b.map50), 4), "mAP50_95": round(float(b.map), 4),
                  "speed_ms_per_image": {k: round(v, 2) for k, v in r.speed.items()}}
    print(split, out[split], flush=True)
(Path(__file__).parent / "eval_results.json").write_text(json.dumps(out, indent=2))

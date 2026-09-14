import os
from pathlib import Path
from typing import Any

MODEL_PATH = os.getenv("MODEL_PATH", "runs/detect/svds-plate-detector-final-2/weights/best.pt")
MODEL_TYPE = os.getenv("MODEL_TYPE", "yolo")


class ModelWrapper:
    def __init__(self, model: Any, model_type: str):
        self.model = model
        self.type = model_type

    def predict_boxes(self, image_path: str, conf: float = 0.3):
        """Return raw detection results for the given image_path.

        The return value is a list-like object produced by the underlying model.
        """
        if self.type == "yolo":
            return self.model(image_path, conf=conf, verbose=False)
        raise RuntimeError("predict_boxes not supported for this model type")


def load_model():
    """Load and return a ModelWrapper instance.

    Currently supports a YOLOv8 Ultralytics weights file when `MODEL_TYPE` is
    `yolo`. If the ultralytics package is not available the loader returns
    a lightweight dummy wrapper that raises on use.
    """
    if MODEL_TYPE == "yolo":
        try:
            from ultralytics import YOLO

            model = YOLO(MODEL_PATH)
            return ModelWrapper(model, "yolo")
        except Exception as e:
            # Provide a clear error when the optional dependency is missing or fails
            raise RuntimeError("Failed to load YOLO model: " + str(e))

    # Placeholder for other model types (sklearn, torch, tf, etc.)
    raise RuntimeError(f"Unsupported MODEL_TYPE: {MODEL_TYPE}")

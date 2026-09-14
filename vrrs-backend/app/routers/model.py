from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Any, List

router = APIRouter(prefix="/model", tags=["Model"])


class Features(BaseModel):
    features: List[float]


@router.post("/predict")
async def predict_json(payload: Features, request: Request):
    """Simple JSON-based prediction endpoint for small feature vectors.

    This is a generic example; adapt to your model's API.
    """
    model_wrapper = request.app.state.model if hasattr(request.app.state, "model") else None
    if model_wrapper is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Example for sklearn-like models
    try:
        pred = model_wrapper.model.predict([payload.features])
        return {"prediction": pred.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-image")
async def predict_image(file: UploadFile = File(...), request: Request = None):
    """Endpoint placeholder for image-based detectors (e.g., YOLO).

    Returns bounding boxes or labels depending on the loaded model.
    """
    model_wrapper = request.app.state.model if hasattr(request.app.state, "model") else None
    if model_wrapper is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Save uploaded file temporarily and run model.predict
    import tempfile
    import shutil

    try:
        suffix = ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        results = model_wrapper.predict_boxes(tmp_path)
        # Convert results to a simple JSON-friendly structure
        out = []
        for res in results:
            for box in getattr(res, "boxes", []):
                xyxy = box.xyxy[0].tolist()
                out.append({"xyxy": xyxy, "conf": float(box.conf[0]) if hasattr(box, "conf") else None})
        return {"detections": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

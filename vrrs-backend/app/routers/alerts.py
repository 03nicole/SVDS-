from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import json
import re
from app.database import get_db
from app.models import Alert, Report, AuditLog
from app.schemas import AlertCreate, AlertOut
from app.middleware import get_current_user, is_police
from app.auth import decode_token

router = APIRouter(prefix="/alerts", tags=["Alerts"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        message = json.dumps(data)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    payload = decode_token(token) if token else None
    if not payload or payload.get("role") not in ("police", "admin"):
        await websocket.close(code=1008)
        return
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/check-plate")
async def check_plate(data: AlertCreate, db: Session = Depends(get_db)):
    try:
        normalized = re.sub(r"[^A-Z0-9]", "", data.license_plate.upper())
        report = db.query(Report).filter(
            func.regexp_replace(func.upper(Report.license_plate), r"[^A-Z0-9]", "", "g") == normalized,
            Report.status == "missing",
        ).first()
        if not report:
            return {"status": "CLEAR"}
        new_alert = Alert(report_id=report.id, location_spotted=data.location_spotted,
            camera_id=data.camera_id, confidence_score=data.confidence_score, image_path=data.image_path)
        db.add(new_alert); db.commit(); db.refresh(new_alert)
        await manager.broadcast({"type": "STOLEN_DETECTED", "alert_id": new_alert.id,
            "plate": data.license_plate.upper(), "location": data.location_spotted,
            "camera_id": data.camera_id, "confidence": data.confidence_score,
            "vehicle_make": report.vehicle_make, "vehicle_model": report.vehicle_model,
            "vehicle_color": report.vehicle_color, "detected_at": str(new_alert.detected_at)})
        return {"status": "STOLEN", "alert_id": new_alert.id,
            "vehicle": {"make": report.vehicle_make, "model": report.vehicle_model, "color": report.vehicle_color}}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread/count")
async def unread_count(user=Depends(is_police), db: Session = Depends(get_db)):
    count = db.query(Alert).filter(Alert.is_read == False).count()
    return {"unread": count}

@router.patch("/read-all")
async def mark_all_read(user=Depends(is_police), db: Session = Depends(get_db)):
    db.query(Alert).filter(Alert.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All alerts marked as read."}

@router.get("/", response_model=List[AlertOut])
async def get_alerts(is_read: Optional[bool]=Query(None), skip: int=Query(0,ge=0),
    limit: int=Query(30,le=100), user=Depends(is_police), db: Session=Depends(get_db)):
    query = db.query(Alert)
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    return query.order_by(desc(Alert.detected_at)).offset(skip).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(alert_id: int, user=Depends(is_police), db: Session=Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return alert

@router.patch("/{alert_id}/read", response_model=AlertOut)
async def mark_read(alert_id: int, user=Depends(is_police), db: Session=Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.is_read = True; db.commit(); db.refresh(alert)
    return alert

@router.patch("/{alert_id}/false-positive", response_model=AlertOut)
async def flag_false_positive(alert_id: int, user=Depends(is_police), db: Session=Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.is_read = True
    db.commit(); db.refresh(alert)
    db.add(AuditLog(performed_by=user["id"], action=f"Flagged alert #{alert_id} as false positive", target_table="alerts", target_id=alert_id))
    db.commit()
    return alert

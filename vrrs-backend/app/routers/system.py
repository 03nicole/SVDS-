import os
import shutil
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session
from typing import List, Optional
import requests
from app.database import get_db, engine
from app.middleware import is_admin, is_police
from app.models import Alert, AuditLog, Report, User
from app.schemas import AuditLogOut
from app.auth import decode_token

router = APIRouter(prefix="/system", tags=["System"])

CAMERA_STREAM_URL = os.getenv("CAMERA_STREAM_URL")
CAMERA_NODE_ID = os.getenv("CAMERA_NODE_ID", "PHONE-NODE-1")
CAMERA_NODE_LOCATION = os.getenv("CAMERA_NODE_LOCATION", "Live phone camera")
SERVER_START = datetime.utcnow()

def is_camera_online() -> bool:
    if not CAMERA_STREAM_URL:
        return False
    try:
        requests.get(CAMERA_STREAM_URL, timeout=3, stream=True).close()
        return True
    except requests.RequestException:
        return False

@router.get("/audit", response_model=List[AuditLogOut])
async def get_audit_log(
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(is_admin),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    return query.order_by(desc(AuditLog.timestamp)).limit(limit).all()

@router.get("/camera-nodes")
def get_camera_nodes(user=Depends(is_police), db: Session = Depends(get_db)):
    online = is_camera_online()

    stats = (
        db.query(
            func.count(Alert.id).label("detections"),
            func.avg(Alert.confidence_score).label("avg_confidence"),
            func.max(Alert.detected_at).label("last_seen"),
        )
        .filter(Alert.camera_id == CAMERA_NODE_ID)
        .first()
    )

    return [{
        "camera_id": CAMERA_NODE_ID,
        "location": CAMERA_NODE_LOCATION,
        "status": "online" if online else "offline",
        "detections": int(stats.detections) if stats and stats.detections else 0,
        "avg_confidence": round(stats.avg_confidence or 0, 1) if stats else 0,
        "last_seen": stats.last_seen if stats else None,
    }]

@router.get("/live-feed")
def get_live_feed(token: str = Query(...)):
    """Proxies the configured camera's MJPEG stream so the frontend can embed
    it in an <img> tag without exposing the camera's raw network address.
    <img> tags can't send an Authorization header, so the token is passed
    as a query param instead and checked manually here.
    """
    payload = decode_token(token)
    if not payload or payload.get("role") not in ("police", "admin"):
        raise HTTPException(status_code=401, detail="Invalid or unauthorized token.")
    if not CAMERA_STREAM_URL:
        raise HTTPException(status_code=503, detail="No camera stream configured.")
    try:
        upstream = requests.get(CAMERA_STREAM_URL, stream=True, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Camera feed is unreachable.")
    content_type = upstream.headers.get("content-type", "multipart/x-mixed-replace")
    return StreamingResponse(upstream.iter_content(chunk_size=4096), media_type=content_type)

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    total_nodes = 1
    online = 1 if is_camera_online() else 0
    offline = total_nodes - online
    active_sessions = db.query(User).filter(User.is_active == True).count()
    recent_alerts = db.query(Alert).filter(Alert.detected_at >= datetime.utcnow() - timedelta(days=1)).count()
    # Use a column-count aggregate to avoid selecting missing/renamed columns
    total_reports = db.query(func.count(Report.id)).scalar() or 0
    total_users = db.query(User).count()
    audit_events = db.query(AuditLog).filter(AuditLog.timestamp >= datetime.utcnow() - timedelta(days=1)).count()

    db_status = "operational"
    db_detail = "Database reachable"
    start = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "degraded"
        db_detail = str(exc)
    db_response_ms = round((time.perf_counter() - start) * 1000, 1)

    disk_total, _, disk_free = shutil.disk_usage(os.path.abspath(os.sep))
    disk_usage_percent = round((1 - disk_free / disk_total) * 100, 1)
    disk_free_gb = round(disk_free / (1024 ** 3), 1)

    pool = engine.pool
    db_connections_used = pool.checkedout()
    db_connections_max = pool.size() + getattr(pool, "_max_overflow", 0)

    uptime_seconds = int((datetime.utcnow() - SERVER_START).total_seconds())

    return {
        "metrics": {
            "api_response_ms": db_response_ms,
            "db_connections_used": db_connections_used,
            "db_connections_max": db_connections_max,
            "disk_usage_percent": disk_usage_percent,
            "disk_free_gb": disk_free_gb,
            "active_sessions": active_sessions,
            "camera_nodes_online": online,
            "camera_nodes_total": total_nodes,
            "camera_nodes_offline": offline,
            "uptime_seconds": uptime_seconds,
            "audit_events_24h": audit_events,
            "total_reports": total_reports,
        },
        "services": [
            {"name": "FastAPI backend", "detail": "http://127.0.0.1:8000", "status": "operational"},
            {"name": "PostgreSQL database", "detail": db_detail, "status": db_status},
            {"name": "WebSocket alerts", "detail": "/alerts/ws", "status": "operational"},
            {"name": "JWT auth service", "detail": "Bearer token validation", "status": "operational"},
        ],
    }

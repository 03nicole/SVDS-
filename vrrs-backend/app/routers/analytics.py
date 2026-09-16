from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract, case
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Report, Alert, User, AuditLog
from app.middleware import is_police, is_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# Older detections (from a retired standalone OCR script) stored confidence as
# a 0-1 fraction; the current camera-node stores it as a 0-100 percentage.
# Averaging the raw column mixes both scales and skews the result low, so
# every aggregate normalizes fractions to percentages first.
NORMALIZED_CONFIDENCE = case(
    (Alert.confidence_score <= 1, Alert.confidence_score * 100),
    else_=Alert.confidence_score,
)

@router.get("/summary")
async def get_summary(user=Depends(is_police), db: Session=Depends(get_db)):
    # Use aggregate counts on the primary key to avoid selecting possibly-missing columns
    total = db.query(func.count(Report.id)).scalar() or 0
    missing = db.query(func.count(Report.id)).filter(Report.status == "missing").scalar() or 0
    found = db.query(func.count(Report.id)).filter(Report.status == "found").scalar() or 0
    review = db.query(func.count(Report.id)).filter(Report.status == "under_review").scalar() or 0
    unread = db.query(func.count(Alert.id)).filter(Alert.is_read == False).scalar() or 0
    avg_confidence = db.query(func.avg(NORMALIZED_CONFIDENCE)).scalar()
    false_positives = db.query(func.count(AuditLog.id)).filter(AuditLog.action.ilike("%false positive%")).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    police_users = db.query(func.count(User.id)).filter(User.role == "police").scalar() or 0
    police_active = db.query(func.count(User.id)).filter(User.role == "police", User.is_active == True).scalar() or 0
    admin_users = db.query(func.count(User.id)).filter(User.role == "admin").scalar() or 0
    users_new_this_week = db.query(func.count(User.id)).filter(User.created_at >= datetime.utcnow() - timedelta(days=7)).scalar() or 0
    new_this_week = db.query(func.count(Report.id)).filter(Report.report_date >= datetime.utcnow() - timedelta(days=7)).scalar() or 0
    recovery_rate = round((found / total * 100), 1) if total > 0 else 0
    return {"reports": {"total": total, "missing": missing, "found": found, "under_review": review,
        "new_this_week": new_this_week, "recovery_rate": recovery_rate},
        "alerts": {"unread": unread, "avg_confidence": round(avg_confidence, 1) if avg_confidence else 0, "false_positives": false_positives},
        "users": {"total": total_users, "police": police_users, "police_active": police_active, "admin": admin_users, "new_this_week": users_new_this_week}}

@router.get("/reports-per-month")
async def reports_per_month(months: int=Query(6,ge=1,le=24), user=Depends(is_police), db: Session=Depends(get_db)):
    results = (db.query(extract("year",Report.report_date).label("year"),
        extract("month",Report.report_date).label("month"), func.count(Report.id).label("count"))
        .filter(Report.report_date >= datetime.utcnow() - timedelta(days=months*30))
        .group_by("year","month").order_by("year","month").all())
    return [{"label": MONTH_NAMES[int(r.month)-1], "year": int(r.year), "count": r.count} for r in results]

@router.get("/status-breakdown")
async def status_breakdown(user=Depends(is_police), db: Session=Depends(get_db)):
    results = db.query(Report.status, func.count(Report.id).label("count")).group_by(Report.status).all()
    return [{"status": r.status, "count": r.count} for r in results]

@router.get("/detections-per-node")
async def detections_per_node(user=Depends(is_police), db: Session=Depends(get_db)):
    results = (db.query(Alert.camera_id, Alert.location_spotted,
        func.count(Alert.id).label("total_detections"), func.avg(NORMALIZED_CONFIDENCE).label("avg_confidence"))
        .group_by(Alert.camera_id, Alert.location_spotted).order_by(desc("total_detections")).all())
    return [{"camera_id": r.camera_id, "location": r.location_spotted,
        "total_detections": r.total_detections, "avg_confidence": round(r.avg_confidence or 0, 1)} for r in results]

@router.get("/alerts-over-time")
async def alerts_over_time(days: int=Query(30,ge=7,le=90), user=Depends(is_police), db: Session=Depends(get_db)):
    results = (db.query(func.date(Alert.detected_at).label("date"), func.count(Alert.id).label("count"))
        .filter(Alert.detected_at >= datetime.utcnow() - timedelta(days=days))
        .group_by(func.date(Alert.detected_at)).order_by(func.date(Alert.detected_at)).all())
    return [{"date": str(r.date), "count": r.count} for r in results]

@router.get("/recovery-time")
async def avg_recovery_time(user=Depends(is_police), db: Session=Depends(get_db)):
    recovered = db.query(Report).filter(Report.status == "found", Report.resolved_date != None).all()
    if not recovered:
        return {"avg_days": 0, "fastest_days": 0, "slowest_days": 0, "total_recovered": 0}
    days_list = [(r.resolved_date - r.report_date).days for r in recovered if r.resolved_date and r.report_date]
    return {"avg_days": round(sum(days_list)/len(days_list),1), "fastest_days": min(days_list),
        "slowest_days": max(days_list), "total_recovered": len(days_list)}

@router.get("/user-growth")
async def user_growth(months: int=Query(6,ge=1,le=12), user=Depends(is_admin), db: Session=Depends(get_db)):
    results = (db.query(extract("year",User.created_at).label("year"),
        extract("month",User.created_at).label("month"), func.count(User.id).label("count"))
        .filter(User.created_at >= datetime.utcnow() - timedelta(days=months*30))
        .group_by("year","month").order_by("year","month").all())
    return [{"label": MONTH_NAMES[int(r.month)-1], "year": int(r.year), "count": r.count} for r in results]

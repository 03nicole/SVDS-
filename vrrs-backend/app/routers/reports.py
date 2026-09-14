from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models import Report, AuditLog
from app.schemas import ReportCreate, ReportUpdate, ReportOut
from app.middleware import get_current_user, is_police, is_reportee

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=ReportOut, status_code=201)
async def create_report(data: ReportCreate, user=Depends(is_reportee), db: Session = Depends(get_db)):
    existing = db.query(Report).filter(Report.license_plate == data.license_plate.upper().strip(), Report.status == "missing").first()
    if existing:
        raise HTTPException(status_code=409, detail=f"An active report for plate {data.license_plate} already exists.")
    new_report = Report(reported_by=user["id"], owner_name=data.owner_name, license_plate=data.license_plate.upper().strip(),
        vehicle_make=data.vehicle_make, vehicle_model=data.vehicle_model, vehicle_color=data.vehicle_color,
        vehicle_year=data.vehicle_year, chassis_number=data.chassis_number, incident_date=data.incident_date,
        status="under_review", last_seen_location=data.last_seen_location, description=data.description)
    db.add(new_report); db.commit(); db.refresh(new_report)
    db.add(AuditLog(performed_by=user["id"], action=f"Filed vehicle report — {new_report.license_plate}", target_table="reports", target_id=new_report.id))
    db.commit()
    return new_report

@router.get("/", response_model=List[ReportOut])
async def get_reports(status: Optional[str]=Query(None), search: Optional[str]=Query(None),
    skip: int=Query(0,ge=0), limit: int=Query(20,le=100), user=Depends(get_current_user), db: Session=Depends(get_db)):
    query = db.query(Report)
    if user["role"] == "reportee":
        query = query.filter(Report.reported_by == user["id"])
    if status:
        query = query.filter(Report.status == status)
    if search:
        query = query.filter(Report.license_plate.ilike(f"%{search}%") | Report.owner_name.ilike(f"%{search}%"))
    return query.order_by(desc(Report.report_date)).offset(skip).limit(limit).all()

@router.get("/{report_id}", response_model=ReportOut)
async def get_report(report_id: int, user=Depends(get_current_user), db: Session=Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if user["role"] == "reportee" and report.reported_by != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied.")
    return report

@router.patch("/{report_id}", response_model=ReportOut)
async def update_report(report_id: int, data: ReportUpdate, user=Depends(is_police), db: Session=Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    db.commit(); db.refresh(report)
    db.add(AuditLog(performed_by=user["id"], action=f"Updated report #{report_id} — {report.license_plate}", target_table="reports", target_id=report_id))
    db.commit()
    return report

@router.patch("/{report_id}/activate", response_model=ReportOut)
async def activate_report(report_id: int, user=Depends(is_police), db: Session=Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.status != "under_review":
        raise HTTPException(status_code=400, detail=f"Cannot activate a report with status '{report.status}'.")
    report.status = "missing"; db.commit(); db.refresh(report)
    db.add(AuditLog(performed_by=user["id"], action=f"Activated report #{report_id} — {report.license_plate}", target_table="reports", target_id=report_id))
    db.commit()
    return report

@router.patch("/{report_id}/found", response_model=ReportOut)
async def mark_found(report_id: int, user=Depends(is_police), db: Session=Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.status == "found":
        raise HTTPException(status_code=400, detail="This vehicle is already marked as recovered.")
    report.status = "found"; report.resolved_by = user["id"]; report.resolved_date = datetime.utcnow()
    db.commit(); db.refresh(report)
    db.add(AuditLog(performed_by=user["id"], action=f"Marked report #{report_id} as Found — {report.license_plate}", target_table="reports", target_id=report_id))
    db.commit()
    return report

@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: int, user=Depends(get_current_user), db: Session=Depends(get_db)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete reports.")
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    db.delete(report); db.commit()
    db.add(AuditLog(performed_by=user["id"], action=f"Deleted report #{report_id}", target_table="reports", target_id=report_id))
    db.commit()

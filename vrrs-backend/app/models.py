from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    first_name    = Column(String(50), nullable=False)
    last_name     = Column(String(50), nullable=False)
    email         = Column(String(100), unique=True, nullable=False, index=True)
    phone         = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20), default="reportee")
    national_id   = Column(String(50))
    badge_number  = Column(String(50))
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    reports       = relationship("Report", back_populates="reporter", foreign_keys="Report.reported_by")

class Report(Base):
    __tablename__ = "reports"
    id                 = Column(Integer, primary_key=True, index=True)
    reported_by        = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_name         = Column(String(100))
    license_plate      = Column(String(20), nullable=False, index=True)
    vehicle_make       = Column(String(50))
    vehicle_model      = Column(String(50))
    vehicle_color      = Column(String(30))
    vehicle_year       = Column(String(10))
    chassis_number     = Column(String(50))
    incident_date      = Column(DateTime(timezone=True))
    status             = Column(String(20), default="missing")
    last_seen_location = Column(Text)
    description        = Column(Text)
    report_date        = Column(DateTime(timezone=True), server_default=func.now())
    resolved_date      = Column(DateTime(timezone=True))
    resolved_by        = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter           = relationship("User", back_populates="reports", foreign_keys=[reported_by])
    alerts             = relationship("Alert", back_populates="report", cascade="all, delete-orphan", passive_deletes=True)

class Alert(Base):
    __tablename__ = "alerts"
    id               = Column(Integer, primary_key=True, index=True)
    report_id        = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    location_spotted = Column(Text)
    camera_id        = Column(String(50))
    confidence_score = Column(Float)
    image_path       = Column(String(255))
    is_read          = Column(Boolean, default=False)
    detected_at      = Column(DateTime(timezone=True), server_default=func.now())
    report           = relationship("Report", back_populates="alerts")

    @property
    def license_plate(self):
        return self.report.license_plate if self.report else None

class AuditLog(Base):
    __tablename__ = "audit_log"
    id           = Column(Integer, primary_key=True, index=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    action       = Column(String(200))
    target_table = Column(String(50))
    target_id    = Column(Integer)
    timestamp    = Column(DateTime(timezone=True), server_default=func.now())

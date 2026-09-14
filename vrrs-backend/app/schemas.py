from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ── Auth ──────────────────────────────────────────────
class UserRegister(BaseModel):
    first_name:   str
    last_name:    str
    email:        str
    phone:        str = Field(pattern=r"^\+260[\s-]?\d{2}[\s-]?\d{7}$")
    password:     str
    role:         str = "reportee"
    national_id:  str = Field(pattern=r"^\d{6}/\d{2}/\d$")
    badge_number: Optional[str] = None

class UserInvite(BaseModel):
    first_name:  str
    last_name:   str
    email:       str
    phone:       str = Field(pattern=r"^\+260[\s-]?\d{2}[\s-]?\d{7}$")
    password:    str
    badge_number: str

class UserLogin(BaseModel):
    email:    str
    password: str

class UserOut(BaseModel):
    id:         int
    first_name: str
    last_name:  str
    email:      str
    phone:      Optional[str] = None
    role:       str
    is_active:  bool
    created_at: datetime
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    message:  str
    token:    str
    redirect: str
    user:     UserOut

# ── Users ─────────────────────────────────────────────
class UserUpdate(BaseModel):
    first_name:  Optional[str] = None
    last_name:   Optional[str] = None
    email:       Optional[str] = None
    phone:       Optional[str] = None
    national_id: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password:     str

class RoleChange(BaseModel):
    role: str

# ── Reports ───────────────────────────────────────────
class ReportCreate(BaseModel):
    owner_name:         Optional[str] = None
    license_plate:      str
    vehicle_make:       Optional[str] = None
    vehicle_model:      Optional[str] = None
    vehicle_color:      Optional[str] = None
    vehicle_year:       Optional[str] = None
    chassis_number:     Optional[str] = None
    incident_date:      Optional[datetime] = None
    last_seen_location: Optional[str] = None
    description:        Optional[str] = None

class ReportUpdate(BaseModel):
    owner_name:         Optional[str] = None
    vehicle_make:       Optional[str] = None
    vehicle_model:      Optional[str] = None
    vehicle_color:      Optional[str] = None
    incident_date:      Optional[datetime] = None
    status:             Optional[str] = None
    last_seen_location: Optional[str] = None
    description:        Optional[str] = None

class ReportOut(BaseModel):
    id:                 int
    reported_by:        int
    license_plate:      str
    owner_name:         Optional[str]
    vehicle_make:       Optional[str]
    vehicle_model:      Optional[str]
    vehicle_color:      Optional[str]
    vehicle_year:       Optional[str]
    incident_date:      Optional[datetime]
    status:             str
    last_seen_location: Optional[str]
    description:        Optional[str]
    report_date:        datetime
    resolved_date:      Optional[datetime]
    resolved_by:        Optional[int]
    class Config:
        from_attributes = True

# ── Alerts ────────────────────────────────────────────
class AlertCreate(BaseModel):
    license_plate:    str
    location_spotted: Optional[str] = None
    camera_id:        Optional[str] = None
    confidence_score: Optional[float] = None
    image_path:       Optional[str] = None

class AlertOut(BaseModel):
    id:               int
    report_id:        int
    license_plate:    Optional[str] = None
    location_spotted: Optional[str]
    camera_id:        Optional[str]
    confidence_score: Optional[float]
    is_read:          bool
    detected_at:      datetime
    class Config:
        from_attributes = True

# --- System / Admin ---------------------------------------------------------
class AuditLogOut(BaseModel):
    id:           int
    performed_by: Optional[int]
    action:       Optional[str]
    target_table: Optional[str]
    target_id:    Optional[int]
    timestamp:    datetime
    class Config:
        from_attributes = True

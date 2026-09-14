from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AuditLog
from app.schemas import UserRegister, UserLogin, AuthResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

VALID_ROLES  = ["reportee"]
REDIRECT_MAP = {"reportee": "/my", "police": "/police", "admin": "/admin"}

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    if data.role != "reportee":
        raise HTTPException(status_code=400, detail="Public registration is only for reportees. Police and admin accounts are created by administrators.")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    new_user = User(
        first_name=data.first_name.strip(), last_name=data.last_name.strip(),
        email=data.email.lower().strip(), phone=data.phone,
        password_hash=hash_password(data.password), role=data.role,
        national_id=data.national_id, badge_number=data.badge_number,
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    db.add(AuditLog(performed_by=new_user.id, action=f"New account registered — {new_user.first_name} {new_user.last_name} ({new_user.role})", target_table="users", target_id=new_user.id))
    db.commit()
    token = create_access_token(new_user.id, new_user.role)
    return {"message": "Account created successfully.", "token": token, "redirect": REDIRECT_MAP[new_user.role], "user": new_user}

@router.post("/login", response_model=AuthResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been deactivated. Contact the administrator.")
    db.add(AuditLog(performed_by=user.id, action=f"User logged in — {user.first_name} {user.last_name}", target_table="users", target_id=user.id))
    db.commit()
    token = create_access_token(user.id, user.role)
    return {"message": "Login successful.", "token": token, "redirect": REDIRECT_MAP[user.role], "user": user}

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully."}

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.database import get_db
from app.models import User, AuditLog
from app.schemas import UserOut, UserUpdate, PasswordChange, RoleChange, UserInvite
from app.middleware import get_current_user, is_police, is_admin
from app.auth import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/invite", response_model=UserOut, status_code=201)
async def invite_police_officer(data: UserInvite, user=Depends(is_admin), db: Session = Depends(get_db)):
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    email = data.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    new_user = User(
        first_name=data.first_name.strip(), last_name=data.last_name.strip(),
        email=email, phone=data.phone.strip(), password_hash=hash_password(data.password),
        role="police", badge_number=data.badge_number.strip(),
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    db.add(AuditLog(performed_by=user["id"], action=f"Created police account — {new_user.first_name} {new_user.last_name}", target_table="users", target_id=new_user.id))
    db.commit()
    return new_user

@router.get("/me", response_model=UserOut)
async def get_my_profile(user=Depends(get_current_user), db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user["id"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user

@router.patch("/me", response_model=UserOut)
async def update_my_profile(data: UserUpdate, user=Depends(get_current_user), db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user["id"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if data.email and data.email != db_user.email:
        taken = db.query(User).filter(User.email == data.email, User.id != user["id"]).first()
        if taken:
            raise HTTPException(status_code=409, detail="This email is already in use.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit(); db.refresh(db_user)
    db.add(AuditLog(performed_by=user["id"], action=f"Updated profile — {db_user.first_name} {db_user.last_name}", target_table="users", target_id=db_user.id))
    db.commit()
    return db_user

@router.patch("/me/password")
async def change_password(data: PasswordChange, user=Depends(get_current_user), db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user["id"]).first()
    if not verify_password(data.current_password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different.")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    db_user.password_hash = hash_password(data.new_password); db.commit()
    db.add(AuditLog(performed_by=user["id"], action=f"Password changed — {db_user.first_name} {db_user.last_name}", target_table="users", target_id=db_user.id))
    db.commit()
    return {"message": "Password updated successfully."}

@router.get("/", response_model=List[UserOut])
async def get_all_users(role: Optional[str]=Query(None), search: Optional[str]=Query(None),
    active: Optional[bool]=Query(None), skip: int=Query(0,ge=0), limit: int=Query(30,le=100),
    user=Depends(is_police), db: Session=Depends(get_db)):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(User.first_name.ilike(f"%{search}%") | User.last_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    if active is not None:
        query = query.filter(User.is_active == active)
    return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, user=Depends(is_police), db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user

@router.patch("/{user_id}/role", response_model=UserOut)
async def change_role(user_id: int, data: RoleChange, user=Depends(is_admin), db: Session=Depends(get_db)):
    VALID_ROLES = ["reportee", "police", "admin"]
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role.")
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own role.")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if data.role in ["police", "admin"] and not db_user.badge_number:
        raise HTTPException(status_code=400, detail="User must have a badge number before being assigned this role.")
    old_role = db_user.role; db_user.role = data.role; db.commit(); db.refresh(db_user)
    db.add(AuditLog(performed_by=user["id"], action=f"Role changed for {db_user.first_name} {db_user.last_name}: {old_role} → {data.role}", target_table="users", target_id=user_id))
    db.commit()
    return db_user

@router.patch("/{user_id}/toggle-active", response_model=UserOut)
async def toggle_active(user_id: int, user=Depends(is_admin), db: Session=Depends(get_db)):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    db_user.is_active = not db_user.is_active; db.commit(); db.refresh(db_user)
    action = "Activated" if db_user.is_active else "Deactivated"
    db.add(AuditLog(performed_by=user["id"], action=f"{action} account — {db_user.first_name} {db_user.last_name}", target_table="users", target_id=user_id))
    db.commit()
    return db_user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, user=Depends(is_admin), db: Session=Depends(get_db)):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.add(AuditLog(performed_by=user["id"], action=f"Deleted account — {db_user.first_name} {db_user.last_name}", target_table="users", target_id=user_id))
    db.delete(db_user); db.commit()

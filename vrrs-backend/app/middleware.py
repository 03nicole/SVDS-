from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth import decode_token
from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def resolve_token_user(token: str, db: Session):
    payload = decode_token(token) if token else None
    try:
        user_id = int(payload["sub"]) if payload else None
    except (KeyError, ValueError, TypeError):
        user_id = None
    user = db.query(User).filter(User.id == user_id).first() if user_id is not None else None
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"id": user.id, "role": user.role}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return resolve_token_user(token, db)

def require_role(*roles):
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {list(roles)}"
            )
        return user
    return checker

def is_reportee(user=Depends(require_role("reportee", "police", "admin"))):
    return user

def is_police(user=Depends(require_role("police", "admin"))):
    return user

def is_admin(user=Depends(require_role("admin"))):
    return user

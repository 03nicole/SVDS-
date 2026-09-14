import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

os.environ.setdefault("DATABASE_URL", "sqlite:///./vrrs.db")

from app.auth import hash_password
from app.database import SessionLocal, Base, engine
from app.models import User

EMAIL = os.getenv("ADMIN_EMAIL", "admin@vrrs.local")
PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!")
FIRST_NAME = os.getenv("ADMIN_FIRST_NAME", "System")
LAST_NAME = os.getenv("ADMIN_LAST_NAME", "Administrator")


def create_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == EMAIL).first()
        if existing:
            print(f"Admin already exists: {EMAIL}")
            return

        admin = User(
            first_name=FIRST_NAME,
            last_name=LAST_NAME,
            email=EMAIL,
            password_hash=hash_password(PASSWORD),
            role="admin",
            is_active=True,
            badge_number="ADMIN-001",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin created successfully: {EMAIL} / {PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()

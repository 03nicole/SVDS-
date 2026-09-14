from app.database import SessionLocal
from app.models import User, AuditLog
from app.auth import hash_password


def create_admin():
    db = SessionLocal()
    try:
        email = "admin@vrrs.zm"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("Admin already exists:", existing.email, "id=", existing.id)
            return
        admin = User(
            first_name="Admin",
            last_name="User",
            email=email,
            phone="+260971234567",
            password_hash=hash_password("AdminPassword123!"),
            role="admin",
            national_id=None,
            badge_number="ADMIN001",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        db.add(AuditLog(performed_by=admin.id, action=f"Seed admin created — {admin.first_name} {admin.last_name}", target_table="users", target_id=admin.id))
        db.commit()
        print("Admin created:", admin.email, "id=", admin.id)
    finally:
        db.close()

if __name__ == '__main__':
    create_admin()

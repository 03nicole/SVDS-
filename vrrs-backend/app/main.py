import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import engine, Base
from app.routers import auth, reports, alerts, users, analytics, system

load_dotenv()


def get_allowed_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS")
    if configured is not None:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]


from sqlalchemy.exc import IntegrityError

try:
    Base.metadata.create_all(bind=engine)
except IntegrityError as e:
    print("Warning: database objects may already exist — continuing.", e)
except Exception as e:
    print("Warning: error creating DB schema (continuing):", e)

app = FastAPI(
    title="SVDS — Vehicle Registry and Reporting System",
    description="Zambia Police Service Vehicle Reporting API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(alerts.router)
app.include_router(users.router)
app.include_router(analytics.router)
app.include_router(system.router)

@app.get("/")
def root():
    return {
        "system": "SVDS — Vehicle Registry and Reporting System",
        "status": "operational",
        "docs":   "/docs"
    }
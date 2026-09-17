# SVDS — Vehicle Registry and Reporting System
### Zambia Police Service | Built with FastAPI + React + PostgreSQL

---

## Project Structure

```
vrrs/
├── vrrs-backend/       FastAPI backend
├── vrrs-frontend/      React frontend
└── vrrs-node/          Phone-camera detection node (YOLO + EasyOCR)
```

---

## Quick Start

### 1. PostgreSQL — Create the database
```bash
psql -U postgres
CREATE DATABASE vrrs_db;
\q
```

### 2. Backend
```bash
cd vrrs-backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set your DATABASE_URL, SECRET_KEY, and CORS_ORIGINS
uvicorn app.main:app --reload
```
API runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Frontend
```bash
cd vrrs-frontend
npm install
cp .env.example .env
# Edit .env — set VITE_API_BASE_URL and VITE_WS_URL for your deployment target
npm run dev
```
App runs at: http://localhost:5173

### Deployment Notes
- Set the frontend environment variables to your production API domain before building.
- Set backend `CORS_ORIGINS` to the deployed frontend origin(s), separated by commas.
- Build the frontend with `npm run build` and serve the generated files from a static host.

---

## Roles & Access

| Role      | Access                                        |
|-----------|-----------------------------------------------|
| Reportee  | File reports, track own vehicle cases         |
| Police    | Vehicle registry, live alerts, analytics      |
| Admin     | User management, role control, system health  |

---

## API Endpoints

| Router      | Prefix        | Description                        |
|-------------|---------------|------------------------------------|
| Auth        | /auth         | Register, login, logout            |
| Reports     | /reports      | Stolen vehicle CRUD                |
| Alerts      | /alerts       | WebSocket + plate-check endpoint   |
| Users       | /users        | Profile + role management          |
| Analytics   | /analytics    | Stats, charts, node data           |

---

## Camera Node Integration (SVDS)

The edge node Python script calls:
```
POST http://your-server:8000/alerts/check-plate
Body: { "license_plate": "BAA 1234", "camera_id": "NODE-001", "confidence_score": 92.4, "location_spotted": "Lusaka Cairo Rd" }
Response: { "status": "STOLEN" } or { "status": "CLEAR" }
```

---

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT, bcrypt
- **Frontend:** React, React Router, Axios
- **Real-time:** WebSockets (FastAPI native)

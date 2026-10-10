# CodeVita AI Coach — Deployment Guide

## 1. Docker Compose Setup (Single Command Deployment)

Ensure Docker and Docker Compose are installed, then run:

```bash
docker-compose up --build -d
```

This starts:
- **Database**: PostgreSQL 16 on port `5432`
- **Backend API**: FastAPI on port `8000`
- **Frontend Web**: Next.js 14 on port `3000`

---

## 2. Manual Production Deployment

### Backend (FastAPI + Gunicorn / Uvicorn Workers)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head  # or auto-seed via python -m app.seeds.seed_data
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (Next.js Standalone / Vercel / Node)
```bash
cd frontend
npm install
npm run build
npm run start
```

---

## 3. Environment Variables Configuration
Refer to `.env.example` to set database connection strings, JWT secret keys, and AI provider credentials.

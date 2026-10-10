# CodeVita AI Coach

> **"Your adaptive AI coach for competitive programming."**

CodeVita AI Coach is a production-quality, full-stack web platform engineered to prepare students for **TCS CodeVita** and high-stakes algorithmic assessments. Combining deterministic skill scoring, isolated code execution, a Monaco-powered online IDE, server-authoritative timed mock examinations, spaced repetition mistake tracking, and structured AI tutoring.

---

## Key Features

1. **Deterministic Analytics & Priority Engine**:
   - Calculates mathematical skill ratings (0–100) across topics (Graphs, DP, Arrays, Strings, Trees, Math, etc.) based on weighted accuracy, difficulty tolerance, and execution speed.
   - Calculates dynamic study priorities: $\text{Priority} = \text{Weakness} \times 0.55 + \text{ExamRelevance} \times 0.35 + \text{Exploration} \times 0.10$.

2. **Monaco Online IDE & Multi-Language Sandbox**:
   - Write, format, and execute code in **C++17, Python 3, Java 21, and C11**.
   - Subprocess process isolation with strict wall-clock timeouts (2.0s–3.0s), memory limits (256MB), and maximum output buffer bounds.
   - Automatic grading against both public test cases and hidden test cases.

3. **Socratic AI Coach & Complexity Reviewer**:
   - Socratic guidance modes: *Learn Concepts, Debug Runtime Exceptions, Socratic Hints, Complexity Explanations*.
   - Automated code review evaluating time complexity ($O(N)$ vs $O(N^2)$), memory footprint, edge cases, and actionable optimization advice.

4. **Server-Authoritative Mock Simulations**:
   - Support for **Quick Sprints (30 min)**, **Topic Mocks (60 min)**, **Mini Mocks (90 min)**, and **Full CodeVita Simulations (360 min)**.
   - Server-enforced timers resistant to browser refreshes with automatic exam finalization.
   - Comprehensive post-exam AI performance debrief and time-management analysis.

5. **Diagnostic Assessment & Adaptive Study Planner**:
   - Initial 3-problem diagnostic scan calibrating starting skill tiers.
   - Schema-validated day-by-day study roadmap dynamically generated and adapted after every assessment.

6. **Active Retention & Mistake Notebook**:
   - Automatic capture of failed submissions categorized by `LOGIC`, `COMPLEXITY`, `SYNTAX`, `EDGE_CASE`, and `IMPLEMENTATION`.
   - Spaced repetition review queue (1d, 3d, 7d, 14d intervals).

7. **Gamification & Admin CMS**:
   - XP, level progression, streaks, and achievement badges.
   - Admin CMS to author problems with public/hidden test cases, configure mock rounds, and broadcast announcements.

---

## Technology Stack

- **Frontend**: Next.js 14 (App Router), React, TypeScript, Tailwind CSS, Monaco Editor (`@monaco-editor/react`), Lucide Icons, Recharts, Framer Motion.
- **Backend**: FastAPI, Python 3.11+, Async SQLAlchemy 2.0, Pydantic v2, PyJWT, Asyncpg, Aiosqlite, Pytest.
- **Database**: PostgreSQL / SQLite (zero-config local dev fallback).
- **AI Integration**: NVIDIA Nemotron API (`nvidia/llama-3.1-nemotron-70b-instruct`, `nvidia/nemotron-4-340b-instruct`) via NVIDIA NIM endpoint with deterministic heuristic Mock fallback.

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+ (or `uv`)
- Node.js 18+ and `npm`

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate venv:
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# Run database seeder (initializes 50+ problems, mocks, topics, achievements)
python -m app.seeds.seed_data

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://127.0.0.1:8000`. Swagger documentation available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend web application will be live at `http://localhost:3000`.

---

## Demo Credentials

| Role | Email | Password | Access |
|---|---|---|---|
| **Student** | `student@codevita.ai` | `student123` | Practice Arena, Mocks, AI Tutor, Study Plan, Dashboard |
| **Admin** | `admin@codevita.ai` | `admin123` | Full Admin CMS, Problem Authoring, Mock Config, Metrics |

---

## Docker Deployment

To launch the complete multi-container stack with PostgreSQL, FastAPI, and Next.js:
```bash
docker-compose up --build -d
```

---

## Running Backend Tests

```bash
cd backend
pytest tests/
```

---

## Documentation Index

- [System Architecture](docs/architecture.md)
- [Database Schema & Relations](docs/database.md)
- [REST API Reference](docs/api.md)
- [AI Layer & Prompts](docs/ai.md)
- [Code Execution Sandbox](docs/code-execution.md)
- [Security Architecture](docs/security.md)
- [Deployment Guide](docs/deployment.md)

---

## License & Disclaimer
This is an independent competitive programming preparation platform and is not affiliated with or endorsed by Tata Consultancy Services (TCS). All problem statements, test cases, and simulation configurations are original content.

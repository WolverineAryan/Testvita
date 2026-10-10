# CodeVita AI Coach — System Architecture

## 1. High-Level Architecture

CodeVita AI Coach is architected around a dual-engine paradigm:
1. **Deterministic Analytics & Priority Engine**: Mathematically calculates topic skill scores, confidence metrics, difficulty tolerance, and study priorities.
2. **AI Synthesis & Reasoning Layer**: Converts deterministic metrics into structured day-by-day roadmaps, Socratic tutor dialogues, and code quality assessments.

```
+-------------------------------------------------------------------+
|                        Next.js Frontend                           |
|  - App Router (React 18/19, TypeScript, Tailwind CSS, Monaco IDE) |
|  - Server-Authoritative Timers, State Management & Charts         |
+---------------------------------+---------------------------------+
                                  | HTTP / REST (JWT Auth)
                                  v
+-------------------------------------------------------------------+
|                        FastAPI Backend                            |
|  +-------------------------------------------------------------+  |
|  | Routers: /auth, /problems, /execution, /mocks, /skills,     |  |
|  |          /plans, /ai, /recommendations, /analytics, /admin |  |
|  +-------------------------------------------------------------+  |
|  +-------------------------------------------------------------+  |
|  | Core Engines:                                               |  |
|  | - Deterministic Skill Engine                                |  |
|  | - Priority & Weakness Engine                                |  |
|  | - Process-Isolated Code Execution Runner                   |  |
|  | - Multi-Model AI Provider Abstraction (Gemini / Heuristic)  |  |
|  +-------------------------------------------------------------+  |
+---------------------------------+---------------------------------+
                                  | Async SQLAlchemy (ORM / Sessions)
                                  v
+-------------------------------------------------------------------+
|               PostgreSQL / SQLite Database Schema                 |
|  - Users, Profiles, Topics, Problems, Test Cases, Submissions     |
|  - Mocks, Attempts, Skill Scores, Plans, Mistakes, Reviews        |
+-------------------------------------------------------------------+
```

---

## 2. Component Breakdown

### A. Code Execution Isolation
- Subprocess and container sandbox architecture.
- Resource limits enforced: Execution timeout (2.0s - 3.0s), memory limits (256MB), max output character truncation (64KB).
- Zero host filesystem or network access during evaluation.

### B. Server-Authoritative Mock Timers
- Mocks record `started_at` and `expires_at` in the database.
- The remaining time is calculated server-side.
- Submissions after expiration are rejected with automatic exam finalization.

### C. Adaptive AI Roadmap Loop
- **Trigger**: New submissions, completed mocks, or diagnostic assessments.
- **Computation**: Priority Engine recalculates priorities:
  $$\text{Priority} = \text{Weakness} \times 0.55 + \text{Relevance} \times 0.35 + \text{Exploration} \times 0.10$$
- **Synthesis**: AI Provider generates validated JSON task graphs for daily execution.

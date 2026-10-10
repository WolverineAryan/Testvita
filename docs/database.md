# CodeVita AI Coach — Database Schema & Relations

## Database Technology
- **Primary Relational Engine**: PostgreSQL (Supported on Supabase, AWS RDS, GCP Cloud SQL, or local Postgres)
- **Local Fallback**: SQLite via `aiosqlite` for zero-dependency local development and testing.
- **ORM**: Async SQLAlchemy 2.0 with strict relational constraints, foreign keys, and indexes.

---

## Entity Relationship Summary

### 1. `users` & `profiles`
- `users`: Core identity, password hash (PBKDF2-SHA256 with salt), role (`USER`, `ADMIN`, `CONTENT_MANAGER`), XP, level.
- `profiles`: Target competition, target date, preferred language (`cpp`, `python`, `java`, `c`), skill tier, daily available hours, onboarding status, diagnostic status.

### 2. `topics` & `subtopics`
- `topics`: Core competitive programming categories (Arrays, Graphs, Dynamic Programming, Math, etc.), importance weight (1-10), sort order.
- `subtopics`: Specific patterns (BFS Grid, Sliding Window, Monotonic Stack, Dijkstra, etc.).

### 3. `problems`, `test_cases`, `hints`
- `problems`: Algorithmic title, unique slug, statement, input/output specifications, constraints, difficulty (`EASY`, `MEDIUM`, `HARD`), difficulty score (1-100), time limit (s), memory limit (MB), editorial text.
- `test_cases`: Input data, expected output, `is_hidden` boolean flag, order index.
- `hints`: Progressive tiered clues.

### 4. `submissions` & `execution_results`
- `submissions`: Submitted code, language, status (`ACCEPTED`, `WRONG_ANSWER`, `TIME_LIMIT_EXCEEDED`, `COMPILATION_ERROR`, `RUNTIME_ERROR`), time (ms), memory (KB), passed count.
- `execution_results`: Granular per-test-case execution trace.

### 5. `mock_tests`, `mock_problems`, `mock_attempts`, `mock_submissions`
- `mock_tests`: Contest configuration, duration minutes, difficulty distribution, scoring rules.
- `mock_attempts`: Server-authoritative start time, expiration time, submitted flag, final score, accuracy, AI debrief JSON.

### 6. `skill_scores`
- User topic ratings (0-100), confidence factor (0.0-1.0), problems attempted, problems solved, average solve time.

### 7. `study_plans` & `study_tasks`
- Dynamic adaptive roadmap, summary, priority topics, day-by-day tasks with completion tracking.

### 8. `mistakes` & `review_queue`
- Mistake notebook categorization (`LOGIC`, `SYNTAX`, `COMPLEXITY`, `EDGE_CASE`, `IMPLEMENTATION`) and spaced repetition queue (1d, 3d, 7d, 14d).

### 9. `achievements`, `user_achievements`, `streaks`
- Gamified XP rewards, level thresholds, badges, activity streaks.

### 10. `competitions` & `announcements`
- Configurable competition metadata (TCS CodeVita Season 14 2026, rules, eligibility) and platform updates.

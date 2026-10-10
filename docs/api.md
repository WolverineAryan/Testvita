# CodeVita AI Coach — REST API Reference

All APIs are versioned under `/api/v1`. Protected routes require a valid Bearer JWT header: `Authorization: Bearer <token>`.

---

## 1. Authentication (`/api/v1/auth`)
- `POST /register`: Register new student or admin.
- `POST /login`: Authenticate and receive access token.
- `GET /me`: Fetch authenticated user identity and profile.
- `PUT /profile`: Update CP experience, target exam, daily hours, and onboarding flags.

---

## 2. Problems & Practice Arena (`/api/v1/problems`)
- `GET /`: List active problems with search, topic, difficulty, and status filters.
- `GET /topics`: Retrieve topic taxonomy.
- `GET /{slug}`: Retrieve detailed statement, input/output formats, constraints, and public test cases.
- `POST /{problem_id}/bookmark`: Toggle problem bookmark.

---

## 3. Code Execution & Submissions (`/api/v1/execution`)
- `POST /run`: Execute user code in isolated sandbox against custom input or public test suites.
- `POST /submit`: Official submission graded against all public and hidden test cases; updates skill score and records mistakes if failed.
- `GET /submissions`: Retrieve user submission history.

---

## 4. Mock Exams (`/api/v1/mocks`)
- `GET /`: Retrieve available mock exam simulations (Quick, Topic, Mini, Full Simulation).
- `POST /{mock_id}/start`: Start or resume a server-authoritative timed mock attempt.
- `POST /attempts/{attempt_id}/submit`: Submit solution to a mock problem during exam mode.
- `POST /attempts/{attempt_id}/finish`: Finalize mock attempt and generate score + AI debrief.

---

## 5. Skills & Diagnostic Assessment (`/api/v1/skills`)
- `GET /matrix`: Retrieve calibrated topic skill scores (0-100), confidence, and accuracy.
- `GET /diagnostic/problems`: Retrieve diagnostic assessment problem suite.
- `POST /diagnostic/submit`: Submit diagnostic test answers to calibrate starting tier and generate initial AI study plan.

---

## 6. Adaptive Study Planner (`/api/v1/plans`)
- `GET /active`: Retrieve active personalized preparation roadmap.
- `POST /generate`: Recompute priorities and regenerate study tasks with AI reasoning.
- `POST /tasks/{task_id}/toggle`: Toggle task completion state.

---

## 7. AI Socratic Coach & Reviewer (`/api/v1/ai`)
- `POST /tutor`: Socratic tutoring dialogue (Tutor, Debug, Hint, Explain modes).
- `POST /review`: Asymptotic code review (Time/Space complexity, edge cases, quality score).

---

## 8. Retention & Analytics (`/api/v1/analytics`)
- `GET /dashboard`: Aggregate summary for main dashboard.
- `GET /mistakes`: Fetch error notebook items.
- `POST /mistakes/{id}/resolve`: Mark mistake as resolved.
- `GET /reviews`: Fetch spaced repetition review queue items.
- `GET /achievements`: Fetch gamification badges and unlock status.
- `GET /leaderboard`: Fetch global competitive programming rankings.

---

## 9. Administrative CMS (`/api/v1/admin`) — Guarded by `require_admin`
- `GET /metrics`: System operational metrics and active counts.
- `POST /problems`: Publish new problem with test cases and hints.
- `POST /mocks`: Configure mock test rounds.
- `POST /announcements`: Broadcast announcements.

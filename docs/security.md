# CodeVita AI Coach — Security Architecture

## 1. Authentication & Authorization
- **JWT Cryptography**: Signed using HMAC-SHA256 with server-side secret rotation support.
- **Password Protection**: Salted PBKDF2-SHA256 with 100,000 iterations and timing-safe `secrets.compare_digest`.
- **Role-Based Access Control (RBAC)**:
  - `USER`: Standard access to problem practice, mock tests, tutor, and profile.
  - `ADMIN` / `CONTENT_MANAGER`: Access to problem publishing, test case management, competition config, and system analytics. Protected via FastAPI dependency `require_admin`.

---

## 2. API & Injection Protections
- **SQL Injection**: Prevented via SQLAlchemy 2.0 parameterized queries.
- **Cross-Site Scripting (XSS)**: Next.js React JSX output encoding and sanitized DOM renders.
- **Cross-Origin Resource Sharing (CORS)**: Restricted to configured origins in `Settings.BACKEND_CORS_ORIGINS`.
- **Buffer & Output Flooding**: Max output character truncation capped at 65,536 characters.

---

## 3. Exam Integrity & Server-Authoritative Timers
- Exam duration and expiration are stored in the database (`started_at`, `expires_at`).
- Client-side timers are purely presentational; all submission timestamps are validated against server clocks.
- Hidden test cases are never transmitted to client devices or browser network payloads.

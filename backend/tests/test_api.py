import pytest
import asyncio
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_health_and_auth_flow():
    from app.database.session import engine, Base
    from app.seeds.seed_data import seed_database_if_empty
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_database_if_empty()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 1b. Registration flow test (verifies UserResponse serialization and profile eager load)
        import uuid
        test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": "Password123!",
            "full_name": "Test Candidate"
        })
        assert reg_res.status_code == 200
        reg_data = reg_res.json()
        assert reg_data["email"] == test_email
        assert reg_data["profile"] is not None
        assert reg_data["profile"]["skill_level"] == "BEGINNER"

        # 2. Login as demo student
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "student@codevita.ai",
            "password": "student123"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get profile
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "student@codevita.ai"

        # 4. List problems
        probs_res = await client.get("/api/v1/problems", headers=headers)
        assert probs_res.status_code == 200
        probs_data = probs_res.json()
        assert probs_data["total"] > 0
        first_prob = probs_data["problems"][0]

        # 5. Get problem detail
        detail_res = await client.get(f"/api/v1/problems/{first_prob['slug']}", headers=headers)
        assert detail_res.status_code == 200
        prob_detail = detail_res.json()
        assert "statement" in prob_detail

        # 6. Run Python code
        run_res = await client.post("/api/v1/execution/run", headers=headers, json={
            "problem_id": prob_detail["id"],
            "language": "python",
            "code": "import sys\ninput_data = sys.stdin.read().split()\nif input_data:\n    print(input_data[0])\n",
            "custom_input": "42\n"
        })
        assert run_res.status_code == 200
        assert run_res.json()["status"] == "SUCCESS"

        # 7. Get Dashboard Summary
        dash_res = await client.get("/api/v1/analytics/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "stats" in dash_data

        # 8. Start a Mock Test
        mocks_res = await client.get("/api/v1/mocks", headers=headers)
        assert mocks_res.status_code == 200
        mock_list = mocks_res.json()
        assert len(mock_list) > 0
        first_mock = mock_list[0]

        start_mock_res = await client.post(f"/api/v1/mocks/{first_mock['id']}/start", headers=headers)
        assert start_mock_res.status_code == 200
        mock_attempt = start_mock_res.json()
        assert mock_attempt["remaining_seconds"] > 0
        assert len(mock_attempt["problems"]) > 0

        # 9. Get AI Study Plan
        plan_res = await client.get("/api/v1/plans/active", headers=headers)
        assert plan_res.status_code == 200
        plan_data = plan_res.json()
        assert "tasks" in plan_data

        # 10. AI Tutor query
        tutor_res = await client.post("/api/v1/ai/tutor", headers=headers, json={
            "mode": "TUTOR",
            "message": "How do I optimize grid BFS search?",
            "problem_id": prob_detail["id"],
            "language": "cpp"
        })
        assert tutor_res.status_code == 200
        assert "reply" in tutor_res.json()

        # 11. AI Code Review query
        review_res = await client.post("/api/v1/ai/review", headers=headers, json={
            "problem_id": prob_detail["id"],
            "language": "python",
            "code": "def solve():\n    pass\n"
        })
        assert review_res.status_code == 200
        assert "correctness_assessment" in review_res.json()
        assert "time_complexity" in review_res.json()


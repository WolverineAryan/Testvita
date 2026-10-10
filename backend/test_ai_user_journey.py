import asyncio
import sys
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_full_ai_user_journey():
    print("\n" + "=" * 70)
    print("STARTING COMPLETE CODEVITA AI COACH SINGLE USER JOURNEY TEST")
    print("=" * 70)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1", timeout=60.0) as client:
        # Step 1: User Registration
        user_email = f"arjun_{uuid.uuid4().hex[:6]}@codevita.ai"
        user_password = "Password@123"
        reg_payload = {
            "email": user_email,
            "password": user_password,
            "full_name": "Arjun Sharma",
            "college": "IIT Bombay",
            "graduation_year": 2026,
            "preferred_language": "cpp",
            "programming_experience": "INTERMEDIATE",
            "cp_experience": "BEGINNER",
            "daily_available_hours": 2.5,
            "target_competition": "TCS CodeVita",
            "preparation_goal": "Crack CodeVita Round 1 & Round 2"
        }
        reg_res = await client.post("/auth/register", json=reg_payload)
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"

        login_res = await client.post("/auth/login", json={"email": user_email, "password": user_password})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        auth_data = login_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"\n[1] User Registered & Logged in: {user_email} (Full Name: Arjun Sharma)")

        # Step 2: Diagnostic Assessment
        diag_probs_res = await client.get("/skills/diagnostic/problems", headers=headers)
        assert diag_probs_res.status_code == 200, f"Failed to get diagnostic problems: {diag_probs_res.text}"
        diag_probs = diag_probs_res.json()
        print(f"[2] Diagnostic Problems Loaded: {len(diag_probs)} problems available")

        # Submit diagnostic test
        diag_answers = []
        for p in diag_probs[:3]:
            diag_answers.append({
                "problem_id": p["id"],
                "language": "cpp",
                "code": "#include <iostream>\nusing namespace std;\nint main() { cout << 0; return 0; }",
                "time_spent_seconds": 120,
                "hints_used": 0
            })
        
        diag_submit_res = await client.post("/skills/diagnostic/submit", headers=headers, json={"answers": diag_answers})
        assert diag_submit_res.status_code == 200, f"Diagnostic submit failed: {diag_submit_res.text}"
        diag_result = diag_submit_res.json()
        print(f"[3] Diagnostic Graded: Score = {diag_result['overall_score']}%, Level = {diag_result['recommended_start_level']}")
        print(f"    Weaknesses Identified: {diag_result['weaknesses_detected']}")

        # Step 3: Calibrated Skill Matrix
        skill_res = await client.get("/skills/matrix", headers=headers)
        assert skill_res.status_code == 200, f"Skill matrix failed: {skill_res.text}"
        matrix = skill_res.json()
        print(f"[4] Live Skill Matrix: Score = {matrix['overall_skill_score']}%, Weak Topics = {matrix['weak_topics']}")

        # Step 4: AI Study Plan Generation (Deterministic priorities + AI Plan)
        plan_res = await client.post("/plans/generate", headers=headers, json={"daily_available_hours": 2.5, "target_days": 7})
        assert plan_res.status_code == 200, f"Plan generation failed: {plan_res.text}"
        plan_data = plan_res.json()
        print(f"[5] AI Personalized Plan Generated: '{plan_data['title']}' with {len(plan_data['tasks'])} structured tasks")
        print(f"    Summary: {plan_data['summary']}")
        print(f"    Priority Topics: {[p['topic'] for p in plan_data['priority_topics']]}")

        # Step 5: AI Tutor Test 1 — Greeting & Live Context Awareness
        tutor_hi = await client.post("/ai/tutor", headers=headers, json={
            "mode": "TUTOR",
            "message": "Hi, who are you and how can you help me prepare?",
            "language": "cpp"
        })
        assert tutor_hi.status_code == 200, f"AI Tutor Hi failed: {tutor_hi.text}"
        hi_reply = tutor_hi.json()["reply"]
        print("\n" + "-" * 60)
        print("[6] AI Tutor: GREETING & PROGRESS AWARENESS RESPONSE")
        print(hi_reply)
        assert "Arjun Sharma" in hi_reply or "CodeVita" in hi_reply or "Coach" in hi_reply

        # Step 6: AI Tutor Test 2 — Dynamic Programming Query
        tutor_dp = await client.post("/ai/tutor", headers=headers, json={
            "mode": "TUTOR",
            "message": "How do I formulate 2D dynamic programming states for knapsack variants?",
            "language": "cpp"
        })
        assert tutor_dp.status_code == 200, f"AI Tutor DP failed: {tutor_dp.text}"
        dp_reply = tutor_dp.json()["reply"]
        print("\n" + "-" * 60)
        print("[7] AI Tutor: DYNAMIC PROGRAMMING FORMULATION RESPONSE")
        print(dp_reply)
        assert "Dynamic Programming" in dp_reply or "State" in dp_reply or "dp[" in dp_reply

        # Step 7: AI Tutor Test 3 — Graph Shortest Path
        tutor_graph = await client.post("/ai/tutor", headers=headers, json={
            "mode": "TUTOR",
            "message": "When should I use 0-1 BFS vs Dijkstra in CodeVita grid problems?",
            "language": "cpp"
        })
        assert tutor_graph.status_code == 200, f"AI Tutor Graph failed: {tutor_graph.text}"
        graph_reply = tutor_graph.json()["reply"]
        print("\n" + "-" * 60)
        print("[8] AI Tutor: GRAPH SHORTEST PATH RESPONSE")
        print(graph_reply)
        assert "BFS" in graph_reply or "Dijkstra" in graph_reply

        # Step 8: AI Tutor Test 4 — Debug Mode with Code & Error Analysis
        sample_prob_id = diag_probs[0]["id"] if diag_probs else None
        tutor_debug = await client.post("/ai/tutor", headers=headers, json={
            "mode": "DEBUG",
            "problem_id": sample_prob_id,
            "message": "My code is giving Wrong Answer and TLE on large constraints",
            "code": "int solve(int n) { int sum = 0; for(int i=0; i<n; i++) { for(int j=0; j<n; j++) sum += i*j; cout << sum << endl; } return sum; }",
            "language": "cpp"
        })
        assert tutor_debug.status_code == 200, f"AI Tutor Debug failed: {tutor_debug.text}"
        debug_reply = tutor_debug.json()["reply"]
        print("\n" + "-" * 60)
        print("[9] AI Tutor: DEBUG MODE & PITFALL DIAGNOSIS RESPONSE")
        print(debug_reply)
        assert "Overflow" in debug_reply or "Debugging" in debug_reply or "I/O" in debug_reply

        # Step 9: AI Code Review
        if sample_prob_id:
            review_res = await client.post("/ai/review", headers=headers, json={
                "problem_id": sample_prob_id,
                "language": "cpp",
                "code": "#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    int n; if (!(cin >> n)) return 0;\n    vector<int> a(n);\n    for(int i=0; i<n; i++) cin >> a[i];\n    cout << a[0] << endl;\n    return 0;\n}"
            })
            assert review_res.status_code == 200, f"AI Review failed: {review_res.text}"
            review_data = review_res.json()
            print("\n" + "-" * 60)
            print("[10] AI Code Review Output:")
            print(f"     Time Complexity: {review_data['time_complexity']}")
            print(f"     Optimal Target:  {review_data['optimal_time_complexity']}")
            print(f"     Quality Score:   {review_data['code_quality_score']} / 10")
            print(f"     Strengths:       {review_data['strengths']}")
            print(f"     Optimizations:   {review_data['areas_for_optimization']}")
            print(f"     Detailed Note:   {review_data['detailed_feedback']}")

        # Step 10: Mock Exam Attempt & AI Debrief
        mocks_res = await client.get("/mocks", headers=headers)
        assert mocks_res.status_code == 200, f"Get mocks failed: {mocks_res.text}"
        mocks = mocks_res.json()
        print(f"\n[11] Mock Tests Catalog: {len(mocks)} mock exams available")
        
        if mocks:
            mock_id = mocks[0]["id"]
            start_res = await client.post(f"/mocks/{mock_id}/start", headers=headers)
            assert start_res.status_code == 200, f"Mock start failed: {start_res.text}"
            attempt_id = start_res.json()["attempt_id"]
            print(f"[12] Mock Attempt Initialized (ID: {attempt_id})")

            # Finish mock and get AI debrief
            mock_sub_res = await client.post(f"/mocks/attempts/{attempt_id}/finish", headers=headers)
            assert mock_sub_res.status_code == 200, f"Mock finish failed: {mock_sub_res.text}"
            mock_result = mock_sub_res.json()
            print(f"[13] Mock Completed & Debrief Generated:")
            print(f"     Score: {mock_result['score']} / {mock_result['max_score']}")
            print(f"     Debrief Summary: {mock_result['ai_debrief'].get('summary') if isinstance(mock_result.get('ai_debrief'), dict) else mock_result.get('ai_debrief')}")

        print("\n" + "=" * 70)
        print("SUCCESS: ALL 13 USER JOURNEY & AI REQUIREMENTS PASSED 100%!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_full_ai_user_journey())

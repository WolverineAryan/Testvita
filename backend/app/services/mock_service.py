from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.mock import MockTest, MockProblem, MockAttempt, MockSubmission
from app.models.problem import Problem, ProblemTopic
from app.models.submission import Submission
from app.schemas.mock import MockTestResponse, MockProblemItem, MockStartResponse, MockAttemptResult, MockSubmissionRequest
from app.services.submission_service import submission_service
from app.schemas.submission import SubmissionCreate
from app.ai.provider import ai_provider
from app.ai.prompts.review import ANALYSIS_SYSTEM_PROMPT
from app.services.gamification_service import gamification_service
from app.config.settings import settings

class MockService:
    @classmethod
    async def get_mock_tests(cls, db: AsyncSession) -> List[MockTestResponse]:
        stmt = (
            select(MockTest)
            .options(selectinload(MockTest.topic))
            .where(MockTest.is_active == True)
            .order_by(MockTest.created_at.desc())
        )
        res = await db.execute(stmt)
        mocks = res.scalars().all()

        return [
            MockTestResponse(
                id=m.id,
                title=m.title,
                slug=m.slug,
                description=m.description,
                mock_type=m.mock_type,
                topic_name=m.topic.name if m.topic else None,
                duration_minutes=m.duration_minutes,
                total_questions=m.total_questions,
                difficulty_distribution=m.difficulty_distribution or {},
                scoring_rules=m.scoring_rules or {},
                allowed_languages=m.allowed_languages or ["cpp", "python", "java", "c"],
                is_active=m.is_active,
                created_at=m.created_at
            )
            for m in mocks
        ]

    @classmethod
    async def start_mock_attempt(cls, db: AsyncSession, user_id: str, mock_test_id: str) -> MockStartResponse:
        stmt = (
            select(MockTest)
            .options(
                selectinload(MockTest.problems).selectinload(MockProblem.problem)
            )
            .where(MockTest.id == mock_test_id, MockTest.is_active == True)
        )
        res = await db.execute(stmt)
        mock_test = res.scalar_one_or_none()
        if not mock_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock test not found")

        # Check for active ongoing attempt
        ongoing_stmt = (
            select(MockAttempt)
            .where(
                MockAttempt.user_id == user_id,
                MockAttempt.mock_test_id == mock_test_id,
                MockAttempt.is_submitted == False,
                MockAttempt.expires_at > datetime.utcnow()
            )
        )
        ongoing_res = await db.execute(ongoing_stmt)
        attempt = ongoing_res.scalar_one_or_none()

        if not attempt:
            # Create new attempt with server-authoritative timer
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=mock_test.duration_minutes)
            attempt = MockAttempt(
                user_id=user_id,
                mock_test_id=mock_test_id,
                started_at=now,
                expires_at=expires_at,
                is_submitted=False,
                score=0.0,
                accuracy=0.0,
                questions_attempted=0,
                questions_solved=0,
                time_spent_seconds=0
            )
            db.add(attempt)
            await db.flush()

        # Calculate remaining seconds safely
        remaining = max(0, int((attempt.expires_at - datetime.utcnow()).total_seconds()))

        # Fetch attempt submissions to mark problem status
        sub_stmt = select(MockSubmission).where(MockSubmission.mock_attempt_id == attempt.id)
        sub_res = await db.execute(sub_stmt)
        attempt_subs = {s.problem_id: s.status for s in sub_res.scalars().all()}

        problem_items: List[MockProblemItem] = []
        for mp in sorted(mock_test.problems, key=lambda x: x.order_index):
            status_val = attempt_subs.get(mp.problem_id, "UNOPENED")
            problem_items.append(
                MockProblemItem(
                    problem_id=mp.problem.id,
                    title=mp.problem.title,
                    slug=mp.problem.slug,
                    difficulty=mp.problem.difficulty,
                    order_index=mp.order_index,
                    marks=mp.marks,
                    user_status="SOLVED" if status_val == "ACCEPTED" else ("ATTEMPTED" if status_val in ["WRONG_ANSWER", "TIME_LIMIT_EXCEEDED", "RUNTIME_ERROR"] else "UNOPENED")
                )
            )

        return MockStartResponse(
            attempt_id=attempt.id,
            mock_test_id=mock_test.id,
            title=mock_test.title,
            started_at=attempt.started_at,
            expires_at=attempt.expires_at,
            duration_minutes=mock_test.duration_minutes,
            remaining_seconds=remaining,
            problems=problem_items
        )

    @classmethod
    async def submit_mock_problem(
        cls,
        db: AsyncSession,
        user_id: str,
        attempt_id: str,
        data: MockSubmissionRequest
    ) -> Dict[str, Any]:
        attempt_stmt = (
            select(MockAttempt)
            .options(selectinload(MockAttempt.mock_test).selectinload(MockTest.problems))
            .where(MockAttempt.id == attempt_id, MockAttempt.user_id == user_id)
        )
        attempt_res = await db.execute(attempt_stmt)
        attempt = attempt_res.scalar_one_or_none()

        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock attempt not found")

        if attempt.is_submitted or datetime.utcnow() > attempt.expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mock exam session has ended")

        # Submit code via submission service
        sub_res = await submission_service.submit_code(
            db=db,
            user_id=user_id,
            data=SubmissionCreate(
                problem_id=data.problem_id,
                language=data.language,
                code=data.code,
                hints_used=0,
                mock_attempt_id=attempt.id
            )
        )

        # Record or update MockSubmission
        mock_sub_stmt = select(MockSubmission).where(
            MockSubmission.mock_attempt_id == attempt.id,
            MockSubmission.problem_id == data.problem_id
        )
        mock_sub_res = await db.execute(mock_sub_stmt)
        mock_sub = mock_sub_res.scalar_one_or_none()

        # Find marks for this problem
        marks = 100
        for mp in attempt.mock_test.problems:
            if mp.problem_id == data.problem_id:
                marks = mp.marks
                break

        awarded_marks = marks if sub_res.status == "ACCEPTED" else 0.0

        if not mock_sub:
            mock_sub = MockSubmission(
                mock_attempt_id=attempt.id,
                user_id=user_id,
                problem_id=data.problem_id,
                submission_id=sub_res.id,
                status=sub_res.status,
                marks_awarded=awarded_marks,
                time_taken_seconds=int((datetime.utcnow() - attempt.started_at).total_seconds())
            )
            db.add(mock_sub)
        else:
            mock_sub.submission_id = sub_res.id
            mock_sub.status = sub_res.status
            mock_sub.marks_awarded = max(mock_sub.marks_awarded, awarded_marks)
            mock_sub.time_taken_seconds = int((datetime.utcnow() - attempt.started_at).total_seconds())

        await db.flush()

        return {
            "status": sub_res.status,
            "passed_count": sub_res.test_cases_passed,
            "total_count": sub_res.total_test_cases,
            "execution_time_ms": sub_res.execution_time_ms,
            "compiler_output": sub_res.compiler_output,
            "marks_awarded": awarded_marks
        }

    @classmethod
    async def finish_mock_attempt(cls, db: AsyncSession, user_id: str, attempt_id: str) -> MockAttemptResult:
        attempt_stmt = (
            select(MockAttempt)
            .options(
                selectinload(MockAttempt.mock_test).selectinload(MockTest.problems).selectinload(MockProblem.problem).selectinload(Problem.topics).selectinload(ProblemTopic.topic),
                selectinload(MockAttempt.submissions).selectinload(MockSubmission.problem)
            )
            .where(MockAttempt.id == attempt_id, MockAttempt.user_id == user_id)
        )
        attempt_res = await db.execute(attempt_stmt)
        attempt = attempt_res.scalar_one_or_none()

        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock attempt not found")

        if not attempt.is_submitted:
            attempt.is_submitted = True
            attempt.completed_at = datetime.utcnow()
            attempt.time_spent_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())

        # Calculate score and accuracy
        total_score = sum(s.marks_awarded for s in attempt.submissions)
        max_possible_score = sum(mp.marks for mp in attempt.mock_test.problems)
        solved_count = sum(1 for s in attempt.submissions if s.status == "ACCEPTED")
        attempted_count = len(attempt.submissions)
        accuracy = (solved_count / max(1, attempted_count)) * 100.0

        attempt.score = total_score
        attempt.accuracy = accuracy
        attempt.questions_attempted = attempted_count
        attempt.questions_solved = solved_count

        # Topic & Difficulty breakdown
        topic_scores: Dict[str, float] = {}
        diff_scores: Dict[str, float] = {}
        problem_breakdown = []

        sub_map = {s.problem_id: s for s in attempt.submissions}

        for mp in attempt.mock_test.problems:
            p = mp.problem
            sub = sub_map.get(p.id)
            is_solved = (sub and sub.status == "ACCEPTED")
            
            # Difficulty score tracking
            diff_scores[p.difficulty] = diff_scores.get(p.difficulty, 0.0) + (100.0 if is_solved else 0.0)

            # Topic score tracking
            for pt in p.topics:
                if pt.topic:
                    topic_scores[pt.topic.name] = topic_scores.get(pt.topic.name, 0.0) + (100.0 if is_solved else 0.0)

            problem_breakdown.append({
                "problem_id": p.id,
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty,
                "marks": mp.marks,
                "marks_awarded": sub.marks_awarded if sub else 0.0,
                "status": sub.status if sub else "UNATTEMPTED",
                "time_taken_seconds": sub.time_taken_seconds if sub else 0
            })

        # Average out percentages
        num_probs = len(attempt.mock_test.problems) or 1
        for k in diff_scores:
            diff_scores[k] = round(diff_scores[k] / num_probs, 1)
        for k in topic_scores:
            topic_scores[k] = round(topic_scores[k] / num_probs, 1)

        # Generate AI debrief
        ai_prompt = f"""Mock Exam Debrief:
Title: {attempt.mock_test.title}
Score: {total_score} / {max_possible_score}
Accuracy: {accuracy}%
Problems Solved: {solved_count} / {len(attempt.mock_test.problems)}
Time Spent: {attempt.time_spent_seconds} seconds
Topic Performance: {topic_scores}
Difficulty Performance: {diff_scores}
Problem Breakdown: {problem_breakdown}
"""
        ai_debrief = await ai_provider.generate_structured(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=ai_prompt,
            schema_description="JSON with summary, strongAreas, weakAreas, timeManagement, and actionItems"
        )
        attempt.ai_analysis = ai_debrief

        # Award Gamification XP for completing mock
        await gamification_service.add_xp(db, user_id, settings.XP_PER_MOCK_ATTEMPT)

        # Auto-adapt active study plan based on newly identified mock weaknesses
        try:
            from app.services.plan_service import plan_service
            weak_list = ai_debrief.get("weakAreas", []) if isinstance(ai_debrief, dict) else []
            await plan_service.on_mock_completed(db, user_id, weak_list)
        except Exception:
            pass

        await db.flush()

        return MockAttemptResult(
            attempt_id=attempt.id,
            mock_title=attempt.mock_test.title,
            mock_type=attempt.mock_test.mock_type,
            score=total_score,
            max_score=float(max_possible_score),
            accuracy=accuracy,
            questions_attempted=attempted_count,
            questions_solved=solved_count,
            total_questions=len(attempt.mock_test.problems),
            time_spent_seconds=attempt.time_spent_seconds,
            time_management_summary={
                "total_seconds": attempt.time_spent_seconds,
                "avg_per_problem": round(attempt.time_spent_seconds / max(1, attempted_count), 1),
                "speed_rating": "Optimal" if attempt.time_spent_seconds <= (attempt.mock_test.duration_minutes * 50) else "Moderate"
            },
            topic_performance=topic_scores,
            difficulty_performance=diff_scores,
            ai_debrief=ai_debrief,
            problem_breakdown=problem_breakdown
        )

mock_service = MockService()

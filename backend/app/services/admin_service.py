import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.problem import Problem, ProblemTopic, TestCase, Hint
from app.models.topic import Topic
from app.models.mock import MockTest, MockProblem
from app.models.competition import Competition, Announcement
from app.models.user import User
from app.models.submission import Submission
from app.models.mock import MockAttempt
from app.schemas.problem import ProblemCreate
from app.schemas.mock import MockTestCreate

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return re.sub(r'^-+|-+$', '', text)

class AdminService:
    @classmethod
    async def create_problem(cls, db: AsyncSession, data: ProblemCreate) -> Problem:
        slug = slugify(data.title)
        
        # Check uniqueness of slug
        existing = await db.execute(select(Problem).where(Problem.slug == slug))
        if existing.scalar_one_or_none():
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

        problem = Problem(
            title=data.title,
            slug=slug,
            statement=data.statement,
            input_format=data.input_format,
            output_format=data.output_format,
            constraints=data.constraints,
            examples=data.examples,
            difficulty=data.difficulty.upper(),
            difficulty_score=data.difficulty_score,
            estimated_time_minutes=data.estimated_time_minutes,
            supported_languages=data.supported_languages,
            time_limit_seconds=data.time_limit_seconds,
            memory_limit_mb=data.memory_limit_mb,
            editorial=data.editorial,
            is_diagnostic=data.is_diagnostic,
            is_active=True
        )
        db.add(problem)
        await db.flush()

        # Link topics
        for tid in data.topic_ids:
            pt = ProblemTopic(problem_id=problem.id, topic_id=tid, is_primary=(tid == data.topic_ids[0]))
            db.add(pt)

        # Add test cases
        for idx, tc in enumerate(data.public_test_cases, start=1):
            t_case = TestCase(
                problem_id=problem.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                is_hidden=False,
                explanation=tc.explanation,
                order_index=idx
            )
            db.add(t_case)

        for idx, tc in enumerate(data.hidden_test_cases, start=len(data.public_test_cases) + 1):
            t_case = TestCase(
                problem_id=problem.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                is_hidden=True,
                explanation=tc.explanation,
                order_index=idx
            )
            db.add(t_case)

        # Add hints
        for idx, h in enumerate(data.hints, start=1):
            hint_obj = Hint(
                problem_id=problem.id,
                order_index=h.order_index or idx,
                title=h.title,
                content=h.content
            )
            db.add(hint_obj)

        await db.flush()
        return problem

    @classmethod
    async def create_mock_test(cls, db: AsyncSession, data: MockTestCreate) -> MockTest:
        slug = slugify(data.title)
        existing = await db.execute(select(MockTest).where(MockTest.slug == slug))
        if existing.scalar_one_or_none():
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

        mock = MockTest(
            title=data.title,
            slug=slug,
            description=data.description,
            mock_type=data.mock_type.upper(),
            topic_id=data.topic_id,
            duration_minutes=data.duration_minutes,
            total_questions=len(data.problem_ids),
            difficulty_distribution=data.difficulty_distribution,
            scoring_rules=data.scoring_rules,
            allowed_languages=data.allowed_languages,
            is_active=True
        )
        db.add(mock)
        await db.flush()

        for idx, pid in enumerate(data.problem_ids, start=1):
            mp = MockProblem(
                mock_test_id=mock.id,
                problem_id=pid,
                order_index=idx,
                marks=100
            )
            db.add(mp)

        await db.flush()
        return mock

    @classmethod
    async def get_admin_metrics(cls, db: AsyncSession) -> Dict[str, Any]:
        users_count = (await db.execute(select(func.count(User.id)))).scalar_one() or 0
        problems_count = (await db.execute(select(func.count(Problem.id)))).scalar_one() or 0
        submissions_count = (await db.execute(select(func.count(Submission.id)))).scalar_one() or 0
        mocks_count = (await db.execute(select(func.count(MockAttempt.id)))).scalar_one() or 0
        avg_mock_score = (await db.execute(select(func.avg(MockAttempt.score)))).scalar_one() or 0.0

        return {
            "total_users": users_count,
            "active_users": users_count,
            "total_problems": problems_count,
            "total_submissions": submissions_count,
            "total_mocks_taken": mocks_count,
            "average_mock_score": round(avg_mock_score, 1),
            "system_health": "Healthy (All systems operational)"
        }

admin_service = AdminService()

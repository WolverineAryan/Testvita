from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.problem import Problem, ProblemTopic, TestCase, Hint, Bookmark
from app.models.topic import Topic
from app.models.submission import Submission
from app.schemas.problem import ProblemDetail, ProblemListItem, ProblemFilter

class ProblemService:
    @classmethod
    async def get_problems(
        cls,
        db: AsyncSession,
        user_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        topic: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        is_diagnostic: Optional[bool] = False,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        stmt = (
            select(Problem)
            .options(
                selectinload(Problem.topics).selectinload(ProblemTopic.topic)
            )
            .where(Problem.is_active == True)
        )

        if is_diagnostic is not None:
            stmt = stmt.where(Problem.is_diagnostic == is_diagnostic)

        if difficulty:
            stmt = stmt.where(Problem.difficulty == difficulty.upper())

        if topic:
            clean_topic = topic.strip()
            stmt = stmt.join(ProblemTopic, Problem.id == ProblemTopic.problem_id).join(Topic, ProblemTopic.topic_id == Topic.id)
            stmt = stmt.where(or_(
                Topic.slug == clean_topic.lower(),
                Topic.slug == clean_topic.lower().replace(' ', '-'),
                Topic.name.ilike(f"%{clean_topic}%"),
                Topic.id == clean_topic
            ))

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(or_(Problem.title.ilike(search_term), Problem.statement.ilike(search_term)))

        # Fetch solved problems for user if authenticated
        solved_ids = set()
        attempted_ids = set()
        bookmarked_ids = set()

        if user_id:
            sub_stmt = select(Submission.problem_id, Submission.status).where(Submission.user_id == user_id)
            sub_res = await db.execute(sub_stmt)
            for pid, p_status in sub_res.all():
                attempted_ids.add(pid)
                if p_status == "ACCEPTED":
                    solved_ids.add(pid)

            bm_stmt = select(Bookmark.problem_id).where(Bookmark.user_id == user_id)
            bm_res = await db.execute(bm_stmt)
            bookmarked_ids = set(bm_res.scalars().all())

        # Execute query
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(total_stmt)
        total_count = total_res.scalar_one() or 0

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        res = await db.execute(stmt)
        problems = res.scalars().all()

        items = []
        for p in problems:
            is_solved = p.id in solved_ids
            is_attempted = p.id in attempted_ids
            is_bookmarked = p.id in bookmarked_ids

            if status_filter == "solved" and not is_solved:
                continue
            if status_filter == "unsolved" and is_solved:
                continue
            if status_filter == "attempted" and not (is_attempted and not is_solved):
                continue

            items.append({
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "difficulty": p.difficulty,
                "difficulty_score": p.difficulty_score,
                "estimated_time_minutes": p.estimated_time_minutes,
                "topics": [pt.topic.name for pt in p.topics if pt.topic],
                "is_diagnostic": p.is_diagnostic,
                "is_solved": is_solved,
                "is_bookmarked": is_bookmarked,
                "submissions_count": 0,
                "acceptance_rate": 78.5
            })

        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "problems": items
        }

    @classmethod
    async def get_problem_by_slug(cls, db: AsyncSession, slug: str, user_id: Optional[str] = None) -> ProblemDetail:
        stmt = (
            select(Problem)
            .options(
                selectinload(Problem.topics).selectinload(ProblemTopic.topic),
                selectinload(Problem.test_cases),
                selectinload(Problem.hints)
            )
            .where(Problem.slug == slug, Problem.is_active == True)
        )
        res = await db.execute(stmt)
        problem = res.scalar_one_or_none()

        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

        is_bookmarked = False
        user_status = "UNSOLVED"

        if user_id:
            bm_stmt = select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.problem_id == problem.id)
            bm_res = await db.execute(bm_stmt)
            is_bookmarked = bm_res.scalar_one_or_none() is not None

            sub_stmt = select(Submission.status).where(Submission.user_id == user_id, Submission.problem_id == problem.id)
            sub_res = await db.execute(sub_stmt)
            statuses = sub_res.scalars().all()
            if "ACCEPTED" in statuses:
                user_status = "SOLVED"
            elif len(statuses) > 0:
                user_status = "ATTEMPTED"

        # Filter public test cases only
        public_tests = [tc for tc in problem.test_cases if not tc.is_hidden]

        # Topics mapped
        topics_list = [{"id": pt.topic.id, "name": pt.topic.name, "slug": pt.topic.slug, "category": pt.topic.category} for pt in problem.topics if pt.topic]

        # Sorted hints
        hints_list = sorted(
            [{"id": h.id, "order_index": h.order_index, "title": h.title, "content": h.content} for h in problem.hints],
            key=lambda x: x["order_index"]
        )

        return ProblemDetail(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            statement=problem.statement,
            input_format=problem.input_format,
            output_format=problem.output_format,
            constraints=problem.constraints,
            examples=problem.examples or [],
            difficulty=problem.difficulty,
            difficulty_score=problem.difficulty_score,
            estimated_time_minutes=problem.estimated_time_minutes,
            supported_languages=problem.supported_languages or ["cpp", "python", "java", "c"],
            time_limit_seconds=problem.time_limit_seconds,
            memory_limit_mb=problem.memory_limit_mb,
            editorial=problem.editorial,
            source_type=problem.source_type,
            source_url=problem.source_url,
            is_active=problem.is_active,
            is_diagnostic=problem.is_diagnostic,
            topics=topics_list,
            public_test_cases=public_tests,
            hints=hints_list,
            is_bookmarked=is_bookmarked,
            user_status=user_status,
            created_at=problem.created_at
        )

    @classmethod
    async def toggle_bookmark(cls, db: AsyncSession, user_id: str, problem_id: str) -> bool:
        stmt = select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.problem_id == problem_id)
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            await db.delete(existing)
            await db.flush()
            return False
        else:
            bm = Bookmark(user_id=user_id, problem_id=problem_id)
            db.add(bm)
            await db.flush()
            return True

problem_service = ProblemService()

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload
from app.models.user import User, Profile
from app.models.submission import Submission
from app.models.mock import MockAttempt, MockTest
from app.models.mistake import Mistake, ReviewQueue
from app.models.problem import Problem, ProblemTopic
from app.models.skill import SkillScore
from app.models.gamification import Streak, Achievement, UserAchievement

class AnalyticsService:
    @classmethod
    async def get_dashboard_summary(cls, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        # User details
        user_stmt = select(User).options(selectinload(User.profile), selectinload(User.streak)).where(User.id == user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        # Solved problems count
        solved_stmt = select(func.count(func.distinct(Submission.problem_id))).where(
            Submission.user_id == user_id,
            Submission.status == "ACCEPTED"
        )
        solved_res = await db.execute(solved_stmt)
        problems_solved = solved_res.scalar_one() or 0

        # Submissions total & accuracy
        subs_stmt = select(
            func.count(Submission.id),
            func.sum(case((Submission.status == "ACCEPTED", 1), else_=0))
        ).where(Submission.user_id == user_id)
        subs_res = await db.execute(subs_stmt)
        total_subs, accepted_subs = subs_res.one()
        total_subs = total_subs or 0
        accepted_subs = accepted_subs or 0
        accuracy = round((accepted_subs / max(1, total_subs)) * 100.0, 1)

        # Mocks completed
        mocks_stmt = select(
            func.count(MockAttempt.id),
            func.max(MockAttempt.score)
        ).where(MockAttempt.user_id == user_id, MockAttempt.is_submitted == True)
        mocks_res = await db.execute(mocks_stmt)
        mocks_count, best_mock_score = mocks_res.one()
        mocks_count = mocks_count or 0
        best_mock_score = best_mock_score or 0.0

        # Unresolved mistakes count
        mistakes_stmt = select(func.count(Mistake.id)).where(Mistake.user_id == user_id, Mistake.is_resolved == False)
        mistakes_res = await db.execute(mistakes_stmt)
        unresolved_mistakes = mistakes_res.scalar_one() or 0

        # Due reviews count
        reviews_stmt = select(func.count(ReviewQueue.id)).where(
            ReviewQueue.user_id == user_id,
            ReviewQueue.next_review_at <= datetime.utcnow()
        )
        reviews_res = await db.execute(reviews_stmt)
        due_reviews = reviews_res.scalar_one() or 0

        # Overall skill score
        skills_stmt = select(func.avg(SkillScore.score)).where(SkillScore.user_id == user_id)
        skills_res = await db.execute(skills_stmt)
        avg_skill = skills_res.scalar_one() or 25.0

        return {
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "xp": user.xp,
                "level": user.level,
                "role": user.role,
                "onboarding_completed": user.profile.onboarding_completed if user.profile else False,
                "diagnostic_completed": user.profile.diagnostic_completed if user.profile else False,
                "target_competition": user.profile.target_competition if user.profile else "TCS CodeVita",
                "skill_level": user.profile.skill_level if user.profile else "BEGINNER"
            },
            "stats": {
                "overall_score": round(avg_skill, 1),
                "problems_solved": problems_solved,
                "total_submissions": total_subs,
                "accuracy_percentage": accuracy,
                "mocks_completed": mocks_count,
                "best_mock_score": best_mock_score,
                "current_streak": user.streak.current_streak if user.streak else 0,
                "longest_streak": user.streak.longest_streak if user.streak else 0,
                "unresolved_mistakes": unresolved_mistakes,
                "due_reviews": due_reviews
            }
        }

    @classmethod
    async def get_mistakes(cls, db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(Mistake)
            .options(selectinload(Mistake.problem))
            .where(Mistake.user_id == user_id)
            .order_by(Mistake.created_at.desc())
        )
        res = await db.execute(stmt)
        mistakes = res.scalars().all()

        return [
            {
                "id": m.id,
                "problem_id": m.problem_id,
                "problem_title": m.problem.title if m.problem else "Unknown",
                "problem_slug": m.problem.slug if m.problem else "",
                "category": m.category,
                "failure_type": m.failure_type,
                "user_notes": m.user_notes,
                "ai_insight": m.ai_insight,
                "is_resolved": m.is_resolved,
                "created_at": m.created_at
            }
            for m in mistakes
        ]

    @classmethod
    async def get_reviews(cls, db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(ReviewQueue)
            .options(selectinload(ReviewQueue.problem))
            .where(ReviewQueue.user_id == user_id)
            .order_by(ReviewQueue.next_review_at.asc())
        )
        res = await db.execute(stmt)
        reviews = res.scalars().all()

        return [
            {
                "id": r.id,
                "problem_id": r.problem_id,
                "problem_title": r.problem.title if r.problem else "Unknown",
                "problem_slug": r.problem.slug if r.problem else "",
                "difficulty": r.problem.difficulty if r.problem else "MEDIUM",
                "interval_days": r.interval_days,
                "repetitions": r.repetitions,
                "next_review_at": r.next_review_at,
                "is_due": r.next_review_at <= datetime.utcnow()
            }
            for r in reviews
        ]

    @classmethod
    async def get_achievements(cls, db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        # All achievements
        all_ach_res = await db.execute(select(Achievement))
        all_ach = all_ach_res.scalars().all()

        # Unlocked by user
        user_ach_res = await db.execute(select(UserAchievement).where(UserAchievement.user_id == user_id))
        user_unlocked = {ua.achievement_id: ua.unlocked_at for ua in user_ach_res.scalars().all()}

        return [
            {
                "id": a.id,
                "code": a.code,
                "title": a.title,
                "description": a.description,
                "icon": a.icon,
                "xp_reward": a.xp_reward,
                "category": a.category,
                "is_unlocked": a.id in user_unlocked,
                "unlocked_at": user_unlocked.get(a.id)
            }
            for a in all_ach
        ]

    @classmethod
    async def get_leaderboard(cls, db: AsyncSession, limit: int = 25) -> List[Dict[str, Any]]:
        stmt = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.xp.desc(), User.level.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        users = res.scalars().all()

        return [
            {
                "rank": idx,
                "user_id": u.id,
                "display_name": u.full_name,
                "xp": u.xp,
                "level": u.level,
                "role": u.role
            }
            for idx, u in enumerate(users, start=1)
        ]

analytics_service = AnalyticsService()

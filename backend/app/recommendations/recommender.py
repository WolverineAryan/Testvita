from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, not_
from sqlalchemy.orm import selectinload
from app.models.problem import Problem, ProblemTopic
from app.models.submission import Submission
from app.models.skill import SkillScore
from app.analytics.priority_engine import priority_engine

class ProblemRecommender:
    @classmethod
    async def get_recommended_problems(
        cls,
        db: AsyncSession,
        user_id: str,
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        # 1. Get solved problem IDs for the user
        solved_stmt = select(Submission.problem_id).where(
            Submission.user_id == user_id,
            Submission.status == "ACCEPTED"
        ).distinct()
        solved_res = await db.execute(solved_stmt)
        solved_ids = set(solved_res.scalars().all())

        # 2. Get top priority topics
        priorities = await priority_engine.compute_topic_priorities(db, user_id)
        if not priorities:
            return []

        top_priority_topics = priorities[:4]
        topic_map = {p["topic_id"]: p for p in top_priority_topics}
        target_topic_ids = list(topic_map.keys())

        # 3. Query problems belonging to top priority topics that are unsolved
        stmt = (
            select(Problem)
            .join(ProblemTopic, Problem.id == ProblemTopic.problem_id)
            .options(
                selectinload(Problem.topics).selectinload(ProblemTopic.topic)
            )
            .where(
                Problem.is_active == True,
                Problem.is_diagnostic == False,
                ProblemTopic.topic_id.in_(target_topic_ids),
                not_(Problem.id.in_(solved_ids)) if solved_ids else True
            )
            .distinct()
            .limit(limit * 2)
        )
        res = await db.execute(stmt)
        problems = res.scalars().all()

        recommended: List[Dict[str, Any]] = []
        for prob in problems:
            # Determine reason
            primary_topic = prob.topics[0].topic.name if prob.topics else "General"
            topic_obj = prob.topics[0].topic if prob.topics else None
            p_info = topic_map.get(topic_obj.id) if topic_obj else None
            
            if p_info:
                reason = f"Targeted practice to boost your {primary_topic} score (Current: {p_info['score']}%)"
            else:
                reason = f"Recommended based on your current skill level in {primary_topic}"

            recommended.append({
                "id": prob.id,
                "title": prob.title,
                "slug": prob.slug,
                "difficulty": prob.difficulty,
                "difficulty_score": prob.difficulty_score,
                "estimated_time_minutes": prob.estimated_time_minutes,
                "topics": [pt.topic.name for pt in prob.topics],
                "is_diagnostic": prob.is_diagnostic,
                "is_solved": False,
                "is_bookmarked": False,
                "recommendation_reason": reason
            })
            if len(recommended) >= limit:
                break

        # Fallback if not enough problems found
        if len(recommended) < limit:
            fallback_stmt = (
                select(Problem)
                .options(selectinload(Problem.topics).selectinload(ProblemTopic.topic))
                .where(
                    Problem.is_active == True,
                    Problem.is_diagnostic == False,
                    not_(Problem.id.in_(solved_ids)) if solved_ids else True
                )
                .limit(limit - len(recommended))
            )
            fallback_res = await db.execute(fallback_stmt)
            for prob in fallback_res.scalars().all():
                if not any(r["id"] == prob.id for r in recommended):
                    primary_topic = prob.topics[0].topic.name if prob.topics else "General"
                    recommended.append({
                        "id": prob.id,
                        "title": prob.title,
                        "slug": prob.slug,
                        "difficulty": prob.difficulty,
                        "difficulty_score": prob.difficulty_score,
                        "estimated_time_minutes": prob.estimated_time_minutes,
                        "topics": [pt.topic.name for pt in prob.topics],
                        "is_diagnostic": prob.is_diagnostic,
                        "is_solved": False,
                        "is_bookmarked": False,
                        "recommendation_reason": f"Algorithmic practice in {primary_topic}"
                    })

        return recommended[:limit]

problem_recommender = ProblemRecommender()

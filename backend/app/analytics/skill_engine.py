from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.skill import SkillScore
from app.models.topic import Topic
from app.models.submission import Submission
from app.models.problem import Problem, ProblemTopic

class SkillEngine:
    @staticmethod
    def calculate_topic_score(
        problems_attempted: int,
        problems_solved: int,
        easy_solved: int,
        medium_solved: int,
        hard_solved: int,
        avg_time_seconds: float,
        recent_accuracy: float = 0.5
    ) -> float:
        if problems_attempted == 0:
            return 0.0  # Uncalibrated / Unassessed baseline

        # 1. Base Accuracy (40%)
        accuracy = problems_solved / max(1, problems_attempted)
        acc_component = accuracy * 40.0

        # 2. Difficulty Component (35%)
        # Weighted points: Easy=1, Medium=2.5, Hard=5.0
        diff_points = (easy_solved * 1.0) + (medium_solved * 2.5) + (hard_solved * 5.0)
        # Cap difficulty component at 35 points (e.g., reaching 15 diff_points gives full score)
        diff_component = min(35.0, (diff_points / 15.0) * 35.0)

        # 3. Speed Component (15%)
        # Benchmarks: <= 900s (15 min) is optimal (15 pts), > 2400s (40 min) is low (5 pts)
        if avg_time_seconds <= 900:
            speed_component = 15.0
        elif avg_time_seconds <= 1800:
            speed_component = 10.0
        else:
            speed_component = 5.0

        # 4. Recent Performance Component (10%)
        recency_component = recent_accuracy * 10.0

        total_score = acc_component + diff_component + speed_component + recency_component
        return min(100.0, max(0.0, round(total_score, 1)))

    @classmethod
    async def update_user_skill(
        cls,
        db: AsyncSession,
        user_id: str,
        topic_id: str,
        is_correct: bool,
        difficulty: str,
        time_spent_seconds: float
    ) -> SkillScore:
        # Fetch or create skill score
        stmt = select(SkillScore).where(
            SkillScore.user_id == user_id,
            SkillScore.topic_id == topic_id
        )
        res = await db.execute(stmt)
        skill_record = res.scalar_one_or_none()

        if not skill_record:
            skill_record = SkillScore(
                user_id=user_id,
                topic_id=topic_id,
                score=30.0 if is_correct else 15.0,
                confidence=0.2,
                problems_solved=1 if is_correct else 0,
                problems_attempted=1,
                average_time_seconds=time_spent_seconds,
                last_updated=datetime.utcnow()
            )
            db.add(skill_record)
            await db.flush()
            return skill_record

        # Update running stats
        skill_record.problems_attempted += 1
        if is_correct:
            skill_record.problems_solved += 1

        # Running average time
        prev_avg = skill_record.average_time_seconds
        n = skill_record.problems_attempted
        skill_record.average_time_seconds = ((prev_avg * (n - 1)) + time_spent_seconds) / n

        # Confidence increases with sample size (max 1.0 at 10 problems)
        skill_record.confidence = min(1.0, round(n / 10.0, 2))

        # Recompute score
        accuracy = skill_record.problems_solved / skill_record.problems_attempted
        diff_multiplier = 1.0 if difficulty == "EASY" else (1.4 if difficulty == "MEDIUM" else 2.0)
        
        # Delta adjustment
        delta = (15.0 * diff_multiplier) if is_correct else (-8.0)
        new_score = skill_record.score + (delta * (1.0 - (skill_record.confidence * 0.4)))
        skill_record.score = min(100.0, max(5.0, round(new_score, 1)))
        skill_record.last_updated = datetime.utcnow()

        await db.flush()
        return skill_record

skill_engine = SkillEngine()

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.topic import Topic
from app.models.skill import SkillScore

class TopicPriority:
    def __init__(
        self,
        topic_id: str,
        topic_name: str,
        topic_slug: str,
        score: float,
        priority: float,
        relevance_weight: int,
        recommended_focus: str,
        reason: str
    ):
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.topic_slug = topic_slug
        self.score = score
        self.priority = priority
        self.relevance_weight = relevance_weight
        self.recommended_focus = recommended_focus
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "topic": self.topic_name,
            "topic_slug": self.topic_slug,
            "score": self.score,
            "priority": round(self.priority, 3),
            "relevance_weight": self.relevance_weight,
            "recommended_focus": self.recommended_focus,
            "reason": self.reason
        }

class PriorityEngine:
    @classmethod
    async def compute_topic_priorities(
        cls,
        db: AsyncSession,
        user_id: str
    ) -> List[Dict[str, Any]]:
        # Fetch all topics
        topics_stmt = select(Topic).order_by(Topic.sort_order.asc())
        topics_res = await db.execute(topics_stmt)
        topics = topics_res.scalars().all()

        # Fetch user's current skill scores
        skills_stmt = select(SkillScore).where(SkillScore.user_id == user_id)
        skills_res = await db.execute(skills_stmt)
        user_skills = {s.topic_id: s for s in skills_res.scalars().all()}

        priorities: List[TopicPriority] = []

        for topic in topics:
            skill = user_skills.get(topic.id)
            score = skill.score if skill else 25.0
            relevance = topic.importance_weight or 5 # 1 - 10 scale

            # Weakness Factor (higher when score is lower: 0 to 1)
            weakness_factor = (100.0 - score) / 100.0

            # Relevance Factor (0.1 to 1.0)
            relevance_factor = relevance / 10.0

            # Confidence penalty (if low confidence, slightly boost exploratory practice)
            confidence = skill.confidence if skill else 0.1
            exploration_boost = (1.0 - confidence) * 0.15

            # Priority formula
            # Priority = (Weakness * 0.55 + Relevance * 0.35 + Exploration * 0.10)
            raw_priority = (weakness_factor * 0.55) + (relevance_factor * 0.35) + exploration_boost
            normalized_priority = min(1.0, max(0.05, raw_priority))

            # Focus strategy recommendation
            if score < 40:
                focus = "Core Fundamentals & Easy Drills"
                reason = f"High priority: Foundational gap in {topic.name} (Score: {score}%)."
            elif score < 70:
                focus = "Pattern Practice & Medium Challenges"
                reason = f"Medium priority: Solidify intermediate patterns in {topic.name}."
            else:
                focus = "Speed Optimization & Advanced Edge Cases"
                reason = f"Maintenance: High proficiency in {topic.name} (Score: {score}%)."

            priorities.append(
                TopicPriority(
                    topic_id=topic.id,
                    topic_name=topic.name,
                    topic_slug=topic.slug,
                    score=score,
                    priority=normalized_priority,
                    relevance_weight=relevance,
                    recommended_focus=focus,
                    reason=reason
                )
            )

        # Sort by priority descending
        priorities.sort(key=lambda x: x.priority, reverse=True)
        return [p.to_dict() for p in priorities]

priority_engine = PriorityEngine()

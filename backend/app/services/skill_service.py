from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.skill import SkillScore
from app.models.topic import Topic
from app.models.user import User, Profile
from app.models.problem import Problem, ProblemTopic
from app.schemas.skill import SkillMatrixResponse, TopicSkillScore, DiagnosticSubmitRequest, DiagnosticResultResponse
from app.services.submission_service import submission_service
from app.schemas.submission import SubmissionCreate

class SkillService:
    @classmethod
    async def get_skill_matrix(cls, db: AsyncSession, user_id: str) -> SkillMatrixResponse:
        # Fetch all topics
        topics_stmt = select(Topic).order_by(Topic.sort_order.asc())
        topics_res = await db.execute(topics_stmt)
        topics = topics_res.scalars().all()

        # Fetch user skill records
        skills_stmt = select(SkillScore).where(SkillScore.user_id == user_id)
        skills_res = await db.execute(skills_stmt)
        user_skills = {s.topic_id: s for s in skills_res.scalars().all()}

        topic_scores_list: List[TopicSkillScore] = []
        total_score_sum = 0.0
        total_problems_solved = 0
        total_problems_attempted = 0
        strong_topics = []
        weak_topics = []

        for t in topics:
            skill = user_skills.get(t.id)
            if skill:
                score = skill.score
                conf = skill.confidence
                solved = skill.problems_solved
                attempted = skill.problems_attempted
                avg_time = skill.average_time_seconds
                last_up = skill.last_updated
            else:
                score = 0.0 # Unassessed baseline
                conf = 0.0
                solved = 0
                attempted = 0
                avg_time = 0.0
                last_up = datetime.utcnow()

            total_score_sum += score
            total_problems_solved += solved
            total_problems_attempted += attempted

            if attempted > 0:
                if score >= 65.0:
                    strong_topics.append(t.name)
                elif score < 45.0:
                    weak_topics.append(t.name)

            topic_scores_list.append(TopicSkillScore(
                topic_id=t.id,
                topic_name=t.name,
                topic_slug=t.slug,
                category=t.category,
                score=score,
                confidence=conf,
                problems_solved=solved,
                problems_attempted=attempted,
                average_time_seconds=avg_time,
                last_updated=last_up
            ))

        num_topics = max(1, len(topics))
        overall_score = round(total_score_sum / num_topics, 1) if total_problems_attempted > 0 else 0.0
        accuracy = round((total_problems_solved / max(1, total_problems_attempted)) * 100.0, 1) if total_problems_attempted > 0 else 0.0

        return SkillMatrixResponse(
            overall_skill_score=overall_score,
            total_problems_solved=total_problems_solved,
            accuracy_percentage=accuracy,
            strong_topics=strong_topics,
            weak_topics=weak_topics,
            topic_scores=topic_scores_list
        )

    @classmethod
    async def grade_diagnostic(cls, db: AsyncSession, user_id: str, data: DiagnosticSubmitRequest) -> DiagnosticResultResponse:
        solved_count = 0
        total_count = len(data.answers)
        topic_accuracies: Dict[str, float] = {}
        difficulty_accuracies: Dict[str, float] = {}
        total_time = 0

        for item in data.answers:
            total_time += item.time_spent_seconds
            # Submit to submission engine
            sub_res = await submission_service.submit_code(
                db=db,
                user_id=user_id,
                data=SubmissionCreate(
                    problem_id=item.problem_id,
                    language=item.language,
                    code=item.code,
                    hints_used=item.hints_used
                )
            )

            # Check problem difficulty and topics
            p_stmt = select(Problem).options(selectinload(Problem.topics).selectinload(ProblemTopic.topic)).where(Problem.id == item.problem_id)
            p_res = await db.execute(p_stmt)
            prob = p_res.scalar_one_or_none()

            is_correct = (sub_res.status == "ACCEPTED")
            if is_correct:
                solved_count += 1

            if prob:
                diff = prob.difficulty
                difficulty_accuracies[diff] = difficulty_accuracies.get(diff, 0.0) + (100.0 if is_correct else 0.0)
                for pt in prob.topics:
                    if pt.topic:
                        t_name = pt.topic.name
                        topic_accuracies[t_name] = topic_accuracies.get(t_name, 0.0) + (100.0 if is_correct else 0.0)

        # Normalize percentages
        for k in difficulty_accuracies:
            difficulty_accuracies[k] = round(difficulty_accuracies[k] / max(1, total_count), 1)
        for k in topic_accuracies:
            topic_accuracies[k] = round(topic_accuracies[k] / max(1, total_count), 1)

        overall_score = round((solved_count / max(1, total_count)) * 100.0, 1)

        # Update profile
        prof_stmt = select(Profile).where(Profile.user_id == user_id)
        prof_res = await db.execute(prof_stmt)
        profile = prof_res.scalar_one_or_none()
        if profile:
            profile.diagnostic_completed = True
            profile.skill_level = "ADVANCED" if overall_score >= 75 else ("INTERMEDIATE" if overall_score >= 45 else "BEGINNER")
            await db.flush()

        weaknesses = [k for k, v in topic_accuracies.items() if v < 50.0]

        return DiagnosticResultResponse(
            overall_score=overall_score,
            solved_count=solved_count,
            total_count=total_count,
            topic_accuracies=topic_accuracies,
            difficulty_accuracies=difficulty_accuracies,
            average_time_per_problem_seconds=round(total_time / max(1, total_count), 1),
            recommended_start_level=profile.skill_level if profile else "INTERMEDIATE",
            weaknesses_detected=weaknesses,
            generated_plan_summary=f"Diagnostic complete with {overall_score}% accuracy. Tailored study plan prioritizing {', '.join(weaknesses[:2]) if weaknesses else 'advanced algorithms'} is now generated."
        )

skill_service = SkillService()

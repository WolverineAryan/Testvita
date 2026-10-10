from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models.plan import StudyPlan, StudyTask
from app.models.user import User, Profile
from app.models.topic import Topic
from app.models.problem import Problem, ProblemTopic
from app.schemas.skill import StudyPlanResponse, StudyTaskResponse, PlanRegenerateRequest
from app.analytics.priority_engine import priority_engine
from app.ai.provider import ai_provider
from app.ai.prompts.planner import PLANNER_SYSTEM_PROMPT, build_planner_prompt
from app.resources.topic_resources import get_topic_resource

class PlanService:
    @classmethod
    async def get_active_plan(cls, db: AsyncSession, user_id: str) -> Optional[StudyPlanResponse]:
        stmt = (
            select(StudyPlan)
            .options(
                selectinload(StudyPlan.tasks).selectinload(StudyTask.topic),
                selectinload(StudyPlan.tasks).selectinload(StudyTask.target_problem)
            )
            .where(StudyPlan.user_id == user_id, StudyPlan.is_active == True)
            .order_by(StudyPlan.created_at.desc())
        )
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan:
            # Auto-generate initial plan if none exists
            return await cls.generate_plan(db, user_id)

        # Build task responses with actual curated learning resources and progressive day locking
        task_responses = []
        completed_count = 0
        sorted_tasks = sorted(plan.tasks, key=lambda x: (x.day_number, x.id))

        days_map: Dict[int, List[StudyTask]] = {}
        for t in sorted_tasks:
            days_map.setdefault(t.day_number, []).append(t)

        unlocked_days = {1}
        all_day_nums = sorted(days_map.keys())
        for d in all_day_nums:
            if d == 1:
                continue
            all_prev_completed = True
            for prev_d in range(1, d):
                if prev_d in days_map:
                    if not all(pt.is_completed for pt in days_map[prev_d]):
                        all_prev_completed = False
                        break
            if all_prev_completed:
                unlocked_days.add(d)

        current_unlocked_day = 1
        for d in all_day_nums:
            if d in unlocked_days:
                if any(not pt.is_completed for pt in days_map[d]):
                    current_unlocked_day = d
                    break
                current_unlocked_day = d

        for t in sorted_tasks:
            if t.is_completed:
                completed_count += 1

            topic_name = t.topic.name if t.topic else "Graphs"
            resource_data = get_topic_resource(topic_name, t.subtopic_name, t.task_type)
            is_locked = (t.day_number not in unlocked_days)

            task_responses.append(StudyTaskResponse(
                id=t.id,
                day_number=t.day_number,
                topic_name=topic_name,
                subtopic_name=t.subtopic_name,
                task_type=t.task_type,
                title=t.title,
                description=t.description,
                duration_minutes=t.duration_minutes,
                target_problem_count=t.target_problem_count,
                target_difficulty=t.target_difficulty,
                target_problem_id=t.target_problem_id,
                target_problem_slug=t.target_problem.slug if t.target_problem else None,
                is_completed=t.is_completed,
                is_locked=is_locked,
                completed_at=t.completed_at,
                resource=resource_data
            ))

        total_tasks = len(task_responses)
        pct = round((completed_count / max(1, total_tasks)) * 100.0, 1)

        return StudyPlanResponse(
            id=plan.id,
            title=plan.title,
            summary=plan.summary,
            priority_topics=plan.priority_topics or [],
            is_active=plan.is_active,
            created_at=plan.created_at,
            tasks=task_responses,
            completion_percentage=pct,
            current_unlocked_day=current_unlocked_day
        )

    @classmethod
    async def generate_plan(
        cls,
        db: AsyncSession,
        user_id: str,
        params: Optional[PlanRegenerateRequest] = None
    ) -> StudyPlanResponse:
        # 1. Fetch user & profile
        prof_stmt = select(Profile).where(Profile.user_id == user_id)
        prof_res = await db.execute(prof_stmt)
        profile = prof_res.scalar_one_or_none()

        prof_dict = {
            "target_competition": profile.target_competition if profile else "TCS CodeVita",
            "skill_level": profile.skill_level if profile else "INTERMEDIATE",
            "daily_available_hours": params.daily_available_hours if (params and params.daily_available_hours) else (profile.daily_available_hours if profile else 2.0),
            "preferred_language": profile.preferred_language if profile else "C++"
        }

        # 2. Compute topic priorities
        priorities = await priority_engine.compute_topic_priorities(db, user_id)

        # 3. Call AI Planner
        prompt_text = build_planner_prompt(
            user_profile=prof_dict,
            topic_priorities=priorities[:5],
            available_days=7
        )

        ai_plan = await ai_provider.generate_structured(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=prompt_text,
            schema_description="JSON with summary, priorityTopics list, and dailyPlan list"
        )

        # 4. Deactivate existing active plans
        old_plans_stmt = select(StudyPlan).where(StudyPlan.user_id == user_id, StudyPlan.is_active == True)
        old_plans_res = await db.execute(old_plans_stmt)
        for op in old_plans_res.scalars().all():
            op.is_active = False

        # 5. Save new StudyPlan
        new_plan = StudyPlan(
            user_id=user_id,
            title=f"Personalized CodeVita Plan ({datetime.utcnow().strftime('%b %d')})",
            generated_by="AI",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
            summary=ai_plan.get("summary", "Personalized study roadmap generated based on your diagnostic and performance metrics."),
            priority_topics=ai_plan.get("priorityTopics", priorities[:4]),
            is_active=True
        )
        db.add(new_plan)
        await db.flush()

        # 6. Map topics to attach actual problem links where possible
        topics_res = await db.execute(select(Topic))
        topic_lookup = {t.name.lower(): t for t in topics_res.scalars().all()}

        # Fetch active problems to link to tasks
        probs_res = await db.execute(select(Problem).options(selectinload(Problem.topics).selectinload(ProblemTopic.topic)).where(Problem.is_active == True))
        all_probs = probs_res.scalars().all()

        daily_list = ai_plan.get("dailyPlan", [])
        for day_entry in daily_list:
            day_num = day_entry.get("day", 1)
            tasks_list = day_entry.get("tasks", [])
            for task_data in tasks_list:
                t_name = task_data.get("topic", "")
                matched_topic = topic_lookup.get(t_name.lower())

                # Find a suitable problem if practice
                target_prob = None
                if matched_topic:
                    for p in all_probs:
                        if any(pt.topic_id == matched_topic.id for pt in p.topics):
                            target_prob = p
                            break

                task = StudyTask(
                    study_plan_id=new_plan.id,
                    day_number=day_num,
                    topic_id=matched_topic.id if matched_topic else None,
                    subtopic_name=task_data.get("subtopic", ""),
                    task_type=task_data.get("task_type", "PRACTICE"),
                    title=task_data.get("title", f"Practice {t_name}"),
                    description=task_data.get("description", ""),
                    duration_minutes=task_data.get("durationMinutes", 45),
                    target_problem_count=task_data.get("problemCount", 2),
                    target_difficulty=task_data.get("difficulty", "MEDIUM"),
                    target_problem_id=target_prob.id if target_prob else None,
                    is_completed=False
                )
                db.add(task)

        await db.flush()
        return await cls.get_active_plan(db, user_id)

    @classmethod
    async def toggle_task_completion(cls, db: AsyncSession, user_id: str, task_id: str) -> bool:
        stmt = (
            select(StudyTask)
            .join(StudyPlan, StudyTask.study_plan_id == StudyPlan.id)
            .where(StudyTask.id == task_id, StudyPlan.user_id == user_id)
        )
        res = await db.execute(stmt)
        task = res.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study task not found")

        # If marking complete for a task in Day > 1, verify earlier days are fully complete
        if not task.is_completed and task.day_number > 1:
            all_tasks_stmt = select(StudyTask).where(StudyTask.study_plan_id == task.study_plan_id)
            all_tasks_res = await db.execute(all_tasks_stmt)
            all_plan_tasks = all_tasks_res.scalars().all()
            earlier_incomplete = any(
                t.day_number < task.day_number and not t.is_completed
                for t in all_plan_tasks
            )
            if earlier_incomplete:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Day {task.day_number} is locked. Complete all previous days' tasks first to unlock this day."
                )

        task.is_completed = not task.is_completed
        task.completed_at = datetime.utcnow() if task.is_completed else None
        await db.flush()
        return task.is_completed

    @classmethod
    async def on_problem_solved(cls, db: AsyncSession, user_id: str, problem_id: str, topic_ids: List[str]):
        """
        Auto-completes corresponding roadmap tasks and triggers dynamic daily plan progression
        as the student grows throughout the platform.
        """
        stmt = (
            select(StudyPlan)
            .options(selectinload(StudyPlan.tasks))
            .where(StudyPlan.user_id == user_id, StudyPlan.is_active == True)
            .order_by(StudyPlan.created_at.desc())
        )
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan:
            return

        updated_any = False
        for task in plan.tasks:
            if not task.is_completed:
                if task.target_problem_id == problem_id or (task.topic_id and task.topic_id in topic_ids):
                    task.is_completed = True
                    task.completed_at = datetime.utcnow()
                    updated_any = True
                    break

        if updated_any:
            await db.flush()

    @classmethod
    async def on_mock_completed(cls, db: AsyncSession, user_id: str, weak_topics: List[str]):
        """
        Adapts the next day's preparation roadmap following a mock test attempt,
        prioritizing newly discovered weak spots.
        """
        if not weak_topics:
            return

        stmt = (
            select(StudyPlan)
            .options(selectinload(StudyPlan.tasks))
            .where(StudyPlan.user_id == user_id, StudyPlan.is_active == True)
            .order_by(StudyPlan.created_at.desc())
        )
        res = await db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan:
            return

        # Find incomplete future tasks and realign with weak topics
        for task in plan.tasks:
            if not task.is_completed and task.day_number >= 2:
                task.subtopic_name = f"Reinforcement: {weak_topics[0]}"
                task.title = f"Drill: {weak_topics[0]} Weak-Area Mastery"
                task.description = f"Reinforce core algorithmic transitions for {weak_topics[0]} identified from recent mock analysis."
                break

        await db.flush()

plan_service = PlanService()

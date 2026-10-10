from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User, Profile
from app.models.problem import Problem
from app.schemas.skill import AITutorRequest, AITutorResponse, AICodeReviewRequest, AICodeReviewResponse
from app.ai.provider import ai_provider
from app.ai.prompts.tutor import TUTOR_SYSTEM_PROMPT, build_tutor_prompt
from app.ai.prompts.review import REVIEW_SYSTEM_PROMPT
from app.services.skill_service import skill_service

router = APIRouter(prefix="/ai", tags=["AI Coach & Tutor"])

@router.post("/tutor", response_model=AITutorResponse)
async def ask_ai_tutor(
    data: AITutorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch user's live progress context & topic mastery
    user_progress = {
        "name": current_user.full_name,
        "level": current_user.level,
        "xp": current_user.xp,
        "streak": current_user.streak.current_streak if getattr(current_user, "streak", None) else 0,
        "tier": "BEGINNER",
        "weak_topics": [],
        "strong_topics": [],
        "solved": 0,
        "overall_score": 0
    }

    try:
        # Load profile
        prof_stmt = select(Profile).where(Profile.user_id == current_user.id)
        prof_res = await db.execute(prof_stmt)
        profile = prof_res.scalar_one_or_none()
        if profile:
            user_progress["tier"] = profile.skill_level

        # Load skill matrix
        matrix = await skill_service.get_skill_matrix(db, current_user.id)
        user_progress["weak_topics"] = matrix.weak_topics
        user_progress["strong_topics"] = matrix.strong_topics
        user_progress["solved"] = matrix.total_problems_solved
        user_progress["overall_score"] = int(matrix.overall_score)
    except Exception:
        pass

    # 2. Fetch problem context if problem_id is given
    problem_ctx = {}
    if data.problem_id:
        p_stmt = select(Problem).where(Problem.id == data.problem_id)
        p_res = await db.execute(p_stmt)
        problem = p_res.scalar_one_or_none()
        if problem:
            problem_ctx = {
                "title": problem.title,
                "difficulty": problem.difficulty,
                "statement": problem.statement,
                "constraints": problem.constraints,
                "language": data.language or "cpp"
            }

    prompt_text = build_tutor_prompt(
        mode=data.mode,
        message=data.message,
        problem_context=problem_ctx,
        user_progress=user_progress,
        code=data.code or "",
        error_message=data.error_message or ""
    )

    reply_text = await ai_provider.generate_text(
        system_prompt=TUTOR_SYSTEM_PROMPT,
        user_prompt=prompt_text
    )

    # Dynamic suggestions based on mode and weak topics
    suggestions = [
        "Can you explain the optimal time complexity?",
        "What are common edge cases for this problem?",
        "How would I formulate state transitions for DP?"
    ]
    if user_progress["weak_topics"]:
        suggestions[2] = f"How can I improve my intuition for {user_progress['weak_topics'][0]}?"

    if data.mode == "DEBUG":
        suggestions = [
            "Why am I getting a Time Limit Exceeded error?",
            "Could this cause integer overflow on large N?",
            "How do I trace my state transitions step by step?"
        ]

    return AITutorResponse(
        reply=reply_text,
        mode=data.mode,
        suggested_questions=suggestions
    )

@router.post("/review", response_model=AICodeReviewResponse)
async def review_solution_code(
    data: AICodeReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    p_stmt = select(Problem).where(Problem.id == data.problem_id)
    p_res = await db.execute(p_stmt)
    problem = p_res.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    # Fetch user skill tier
    prof_stmt = select(Profile).where(Profile.user_id == current_user.id)
    prof_res = await db.execute(prof_stmt)
    profile = prof_res.scalar_one_or_none()
    tier = profile.skill_level if profile else "INTERMEDIATE"

    user_prompt = f"""Student Profile: {current_user.full_name} (Skill Tier: {tier}, Level {current_user.level})
Problem: {problem.title}
Difficulty: {problem.difficulty}
Time Limit: {problem.time_limit_seconds}s
Memory Limit: {problem.memory_limit_mb}MB
Statement:
{problem.statement}
Constraints:
{problem.constraints}

User Code ({data.language}):
```{data.language}
{data.code}
```
"""

    structured_res = await ai_provider.generate_structured(
        system_prompt=REVIEW_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema_description="JSON with correctness_assessment, time_complexity, space_complexity, optimal_time_complexity, code_quality_score, strengths, areas_for_optimization, edge_cases_considered, detailed_feedback"
    )

    return AICodeReviewResponse(
        correctness_assessment=structured_res.get("correctness_assessment", "Code appears logically structured."),
        time_complexity=structured_res.get("time_complexity", "O(N)"),
        space_complexity=structured_res.get("space_complexity", "O(1)"),
        optimal_time_complexity=structured_res.get("optimal_time_complexity", "O(N)"),
        code_quality_score=int(structured_res.get("code_quality_score", 8)),
        strengths=structured_res.get("strengths", ["Clear logic flow"]),
        areas_for_optimization=structured_res.get("areas_for_optimization", ["Optimize memory footprint"]),
        edge_cases_considered=structured_res.get("edge_cases_considered", ["Empty array", "Max bounds"]),
        detailed_feedback=structured_res.get("detailed_feedback", "Overall solid implementation matching constraints.")
    )

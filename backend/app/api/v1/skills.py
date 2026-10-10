from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.problem import Problem, TestCase
from app.schemas.skill import SkillMatrixResponse, DiagnosticSubmitRequest, DiagnosticResultResponse
from app.services.skill_service import skill_service

router = APIRouter(prefix="/skills", tags=["Skills & Diagnostic"])

@router.get("/matrix", response_model=SkillMatrixResponse)
async def get_my_skill_matrix(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await skill_service.get_skill_matrix(db, current_user.id)

@router.get("/diagnostic/problems", response_model=List[dict])
async def get_diagnostic_problems(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Problem)
        .options(selectinload(Problem.test_cases))
        .where(Problem.is_diagnostic == True, Problem.is_active == True)
        .order_by(Problem.difficulty_score.asc())
    )
    res = await db.execute(stmt)
    problems = res.scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "statement": p.statement,
            "input_format": p.input_format,
            "output_format": p.output_format,
            "constraints": p.constraints,
            "examples": p.examples,
            "difficulty": p.difficulty,
            "estimated_time_minutes": p.estimated_time_minutes,
            "public_test_cases": [
                {"input_data": tc.input_data, "expected_output": tc.expected_output, "explanation": tc.explanation}
                for tc in p.test_cases if not tc.is_hidden
            ]
        }
        for p in problems
    ]

@router.post("/diagnostic/submit", response_model=DiagnosticResultResponse)
async def submit_diagnostic_test(
    data: DiagnosticSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await skill_service.grade_diagnostic(db, current_user.id, data)

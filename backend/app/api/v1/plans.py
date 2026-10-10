from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.skill import StudyPlanResponse, PlanRegenerateRequest
from app.services.plan_service import plan_service

router = APIRouter(prefix="/plans", tags=["Study Planner"])

@router.get("/active", response_model=Optional[StudyPlanResponse])
async def get_active_study_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    plan = await plan_service.get_active_plan(db, current_user.id)
    if not plan:
        # Auto generate first plan if not exists
        return await plan_service.generate_plan(db, current_user.id)
    return plan

@router.post("/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    params: Optional[PlanRegenerateRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await plan_service.generate_plan(db, current_user.id, params)

@router.post("/tasks/{task_id}/toggle", response_model=dict)
async def toggle_task_completion(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    completed = await plan_service.toggle_task_completion(db, current_user.id, task_id)
    return {"task_id": task_id, "is_completed": completed}

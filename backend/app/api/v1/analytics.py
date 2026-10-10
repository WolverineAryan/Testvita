from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.mistake import Mistake, ReviewQueue
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics & User Metrics"])

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_dashboard_summary(db, current_user.id)

@router.get("/mistakes", response_model=List[Dict[str, Any]])
async def get_my_mistakes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_mistakes(db, current_user.id)

@router.post("/mistakes/{mistake_id}/resolve", response_model=dict)
async def resolve_mistake(
    mistake_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Mistake).where(Mistake.id == mistake_id, Mistake.user_id == current_user.id)
    res = await db.execute(stmt)
    mistake = res.scalar_one_or_none()
    if not mistake:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mistake record not found")
    mistake.is_resolved = True
    await db.flush()
    return {"success": True, "mistake_id": mistake_id}

@router.get("/reviews", response_model=List[Dict[str, Any]])
async def get_my_review_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_reviews(db, current_user.id)

@router.get("/achievements", response_model=List[Dict[str, Any]])
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await analytics_service.get_achievements(db, current_user.id)

@router.get("/leaderboard", response_model=List[Dict[str, Any]])
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_leaderboard(db)

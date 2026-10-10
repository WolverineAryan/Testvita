from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.recommendations.recommender import problem_recommender

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("", response_model=List[dict])
async def get_personalized_recommendations(
    limit: int = Query(6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await problem_recommender.get_recommended_problems(db, current_user.id, limit=limit)

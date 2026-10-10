from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.auth.dependencies import get_current_user_optional, get_current_user
from app.models.user import User
from app.models.topic import Topic
from app.schemas.problem import ProblemListItem, ProblemDetail, TopicBase
from app.services.problem_service import problem_service

router = APIRouter(prefix="/problems", tags=["Problems"])

@router.get("", response_model=dict)
async def list_problems(
    difficulty: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    return await problem_service.get_problems(
        db=db,
        user_id=user_id,
        difficulty=difficulty,
        topic=topic,
        status_filter=status,
        search=search,
        is_diagnostic=False,
        page=page,
        page_size=page_size
    )

@router.get("/topics", response_model=List[TopicBase])
async def list_topics(db: AsyncSession = Depends(get_db)):
    stmt = select(Topic).order_by(Topic.sort_order.asc())
    res = await db.execute(stmt)
    topics = res.scalars().all()
    return topics

@router.get("/{slug}", response_model=ProblemDetail)
async def get_problem_detail(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    return await problem_service.get_problem_by_slug(db, slug, user_id)

@router.post("/{problem_id}/bookmark", response_model=dict)
async def toggle_problem_bookmark(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    bookmarked = await problem_service.toggle_bookmark(db, current_user.id, problem_id)
    return {"bookmarked": bookmarked}

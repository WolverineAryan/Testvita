from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.auth.dependencies import require_admin
from app.models.user import User
from app.models.problem import Problem
from app.models.mock import MockTest
from app.models.competition import Competition, Announcement
from app.schemas.problem import ProblemCreate
from app.schemas.mock import MockTestCreate
from app.services.admin_service import admin_service

router = APIRouter(prefix="/admin", tags=["Admin Management"], dependencies=[Depends(require_admin)])

@router.get("/metrics", response_model=Dict[str, Any])
async def get_admin_metrics(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    return await admin_service.get_admin_metrics(db)

@router.post("/problems", response_model=dict)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    problem = await admin_service.create_problem(db, data)
    return {"success": True, "id": problem.id, "slug": problem.slug, "title": problem.title}

@router.post("/mocks", response_model=dict)
async def create_mock_test(
    data: MockTestCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    mock = await admin_service.create_mock_test(db, data)
    return {"success": True, "id": mock.id, "slug": mock.slug, "title": mock.title}

@router.post("/announcements", response_model=dict)
async def create_announcement(
    title: str,
    content: str,
    announcement_type: str = "PLATFORM_UPDATE",
    is_pinned: bool = False,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    ann = Announcement(
        title=title,
        content=content,
        type=announcement_type,
        is_pinned=is_pinned,
        is_active=True
    )
    db.add(ann)
    await db.flush()
    return {"success": True, "id": ann.id, "title": ann.title}

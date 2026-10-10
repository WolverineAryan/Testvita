from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.competition import Competition, Announcement

router = APIRouter(tags=["Competitions & Announcements"])

@router.get("/competitions", response_model=List[dict])
async def list_competitions(db: AsyncSession = Depends(get_db)):
    stmt = select(Competition).where(Competition.is_active == True)
    res = await db.execute(stmt)
    comps = res.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "season": c.season,
            "year": c.year,
            "description": c.description,
            "official_url": c.official_url,
            "duration_minutes": c.duration_minutes,
            "num_rounds": c.num_rounds,
            "eligibility": c.eligibility,
            "rules": c.rules or [],
            "allowed_languages": c.allowed_languages or ["C", "C++", "Java", "Python"]
        }
        for c in comps
    ]

@router.get("/announcements", response_model=List[dict])
async def list_announcements(db: AsyncSession = Depends(get_db)):
    stmt = select(Announcement).where(Announcement.is_active == True).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
    res = await db.execute(stmt)
    announcements = res.scalars().all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "type": a.type,
            "is_pinned": a.is_pinned,
            "created_at": a.created_at
        }
        for a in announcements
    ]

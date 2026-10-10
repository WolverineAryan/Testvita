from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.submission import CodeRunRequest, CodeRunResponse, SubmissionCreate, SubmissionResponse
from app.services.submission_service import submission_service

router = APIRouter(prefix="/execution", tags=["Code Execution"])

@router.post("/run", response_model=CodeRunResponse)
async def run_code(
    data: CodeRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await submission_service.run_code(db, data)

@router.post("/submit", response_model=SubmissionResponse)
async def submit_code(
    data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await submission_service.submit_code(db, current_user.id, data)

@router.get("/submissions", response_model=List[dict])
async def get_my_submissions(
    problem_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await submission_service.get_user_submissions(db, current_user.id, problem_id)

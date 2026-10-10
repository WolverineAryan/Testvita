from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.mock import MockTestResponse, MockStartResponse, MockAttemptResult, MockSubmissionRequest
from app.services.mock_service import mock_service

router = APIRouter(prefix="/mocks", tags=["Mock Examinations"])

@router.get("", response_model=List[MockTestResponse])
async def list_mock_tests(db: AsyncSession = Depends(get_db)):
    return await mock_service.get_mock_tests(db)

@router.post("/{mock_id}/start", response_model=MockStartResponse)
async def start_mock_test(
    mock_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await mock_service.start_mock_attempt(db, current_user.id, mock_id)

@router.post("/attempts/{attempt_id}/submit", response_model=dict)
async def submit_mock_problem(
    attempt_id: str,
    data: MockSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await mock_service.submit_mock_problem(db, current_user.id, attempt_id, data)

@router.post("/attempts/{attempt_id}/finish", response_model=MockAttemptResult)
async def finish_mock_test(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await mock_service.finish_mock_attempt(db, current_user.id, attempt_id)

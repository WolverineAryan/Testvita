from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.problem import ProblemDetail, ProblemListItem

class MockProblemItem(BaseModel):
    problem_id: str
    title: str
    slug: str
    difficulty: str
    order_index: int
    marks: int
    user_status: Optional[str] = "UNOPENED" # UNOPENED, VIEWED, ATTEMPTED, SOLVED, FAILED

class MockTestResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: Optional[str] = None
    mock_type: str
    topic_name: Optional[str] = None
    duration_minutes: int
    total_questions: int
    difficulty_distribution: Dict[str, Any]
    scoring_rules: Dict[str, Any]
    allowed_languages: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MockTestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    mock_type: str = "FULL"
    topic_id: Optional[str] = None
    duration_minutes: int = 180
    problem_ids: List[str] = []
    difficulty_distribution: Dict[str, int] = {}
    scoring_rules: Dict[str, Any] = {"type": "codevita_relative"}
    allowed_languages: List[str] = ["cpp", "python", "java", "c"]

class MockStartResponse(BaseModel):
    attempt_id: str
    mock_test_id: str
    title: str
    started_at: datetime
    expires_at: datetime
    duration_minutes: int
    remaining_seconds: int
    problems: List[MockProblemItem]

class MockSubmissionRequest(BaseModel):
    problem_id: str
    language: str
    code: str

class MockAttemptResult(BaseModel):
    attempt_id: str
    mock_title: str
    mock_type: str
    score: float
    max_score: float
    accuracy: float
    questions_attempted: int
    questions_solved: int
    total_questions: int
    time_spent_seconds: int
    time_management_summary: Dict[str, Any]
    topic_performance: Dict[str, float]
    difficulty_performance: Dict[str, float]
    ai_debrief: Optional[Dict[str, Any]] = None
    problem_breakdown: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True

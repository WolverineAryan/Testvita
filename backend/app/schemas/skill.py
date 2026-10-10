from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Skill Schemas
class TopicSkillScore(BaseModel):
    topic_id: str
    topic_name: str
    topic_slug: str
    category: str
    score: float
    confidence: float
    problems_solved: int
    problems_attempted: int
    average_time_seconds: float
    last_updated: datetime

    class Config:
        from_attributes = True

class SkillMatrixResponse(BaseModel):
    overall_skill_score: float
    total_problems_solved: int
    accuracy_percentage: float
    strong_topics: List[str]
    weak_topics: List[str]
    topic_scores: List[TopicSkillScore]

class DiagnosticAnswerItem(BaseModel):
    problem_id: str
    language: str
    code: str
    time_spent_seconds: int
    hints_used: int = 0

class DiagnosticSubmitRequest(BaseModel):
    answers: List[DiagnosticAnswerItem]

class DiagnosticResultResponse(BaseModel):
    overall_score: float
    solved_count: int
    total_count: int
    topic_accuracies: Dict[str, float]
    difficulty_accuracies: Dict[str, float]
    average_time_per_problem_seconds: float
    recommended_start_level: str
    weaknesses_detected: List[str]
    generated_plan_summary: str

# Plan Schemas
class StudyTaskResponse(BaseModel):
    id: str
    day_number: int
    topic_name: Optional[str] = None
    subtopic_name: Optional[str] = None
    task_type: str # LEARN, PRACTICE, TIMED_CHALLENGE, REVIEW_MISTAKES
    title: str
    description: Optional[str] = None
    duration_minutes: int
    target_problem_count: int
    target_difficulty: str
    target_problem_id: Optional[str] = None
    target_problem_slug: Optional[str] = None
    is_completed: bool
    is_locked: bool = False
    completed_at: Optional[datetime] = None
    resource: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class StudyPlanResponse(BaseModel):
    id: str
    title: str
    summary: str
    priority_topics: List[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    tasks: List[StudyTaskResponse] = []
    completion_percentage: float = 0.0
    current_unlocked_day: int = 1

    class Config:
        from_attributes = True

class PlanRegenerateRequest(BaseModel):
    target_date: Optional[datetime] = None
    daily_available_hours: Optional[float] = None
    focus_areas: Optional[List[str]] = None

# AI Schemas
class AITutorRequest(BaseModel):
    mode: str = "TUTOR" # TUTOR, DEBUG, HINT, EXPLAIN, REVIEW
    message: str
    problem_id: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = "cpp"
    error_message: Optional[str] = None

class AITutorResponse(BaseModel):
    reply: str
    mode: str
    suggested_questions: List[str] = []

class AICodeReviewRequest(BaseModel):
    problem_id: str
    code: str
    language: str

class AICodeReviewResponse(BaseModel):
    correctness_assessment: str
    time_complexity: str
    space_complexity: str
    optimal_time_complexity: str
    code_quality_score: int # 1 to 10
    strengths: List[str]
    areas_for_optimization: List[str]
    edge_cases_considered: List[str]
    detailed_feedback: str

# Admin Schemas
class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_problems: int
    total_submissions: int
    total_mocks_taken: int
    average_mock_score: float
    system_health: str

from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class TopicBase(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class TestCaseBase(BaseModel):
    id: Optional[str] = None
    input_data: str
    expected_output: str
    is_hidden: bool = True
    explanation: Optional[str] = None
    order_index: int = 0

    class Config:
        from_attributes = True

class HintBase(BaseModel):
    id: Optional[str] = None
    order_index: int
    title: str
    content: str

    class Config:
        from_attributes = True

class ProblemListItem(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    difficulty_score: int
    estimated_time_minutes: int
    topics: List[str] = []
    is_diagnostic: bool = False
    is_solved: bool = False
    is_bookmarked: bool = False
    submissions_count: int = 0
    acceptance_rate: float = 0.0
    recommendation_reason: Optional[str] = None

    class Config:
        from_attributes = True

class ProblemDetail(BaseModel):
    id: str
    title: str
    slug: str
    statement: str
    input_format: str
    output_format: str
    constraints: str
    examples: List[Dict[str, Any]]
    difficulty: str
    difficulty_score: int
    estimated_time_minutes: int
    supported_languages: List[str]
    time_limit_seconds: float
    memory_limit_mb: int
    editorial: Optional[str] = None
    source_type: str
    source_url: Optional[str] = None
    is_active: bool
    is_diagnostic: bool
    topics: List[TopicBase] = []
    public_test_cases: List[TestCaseBase] = []
    hints: List[HintBase] = []
    is_bookmarked: bool = False
    user_status: Optional[str] = None # UNSOLVED, ATTEMPTED, SOLVED
    created_at: datetime

    class Config:
        from_attributes = True

class ProblemCreate(BaseModel):
    title: str
    statement: str
    input_format: str
    output_format: str
    constraints: str
    examples: List[Dict[str, Any]]
    difficulty: str = "MEDIUM"
    difficulty_score: int = 50
    estimated_time_minutes: int = 30
    supported_languages: List[str] = ["cpp", "python", "java", "c"]
    time_limit_seconds: float = 2.0
    memory_limit_mb: int = 256
    editorial: Optional[str] = None
    topic_ids: List[str] = []
    is_diagnostic: bool = False
    public_test_cases: List[TestCaseBase] = []
    hidden_test_cases: List[TestCaseBase] = []
    hints: List[HintBase] = []

class ProblemFilter(BaseModel):
    difficulty: Optional[str] = None
    topic: Optional[str] = None
    status: Optional[str] = None # solved, unsolved, attempted
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20

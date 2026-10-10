from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class CodeRunRequest(BaseModel):
    problem_id: str
    language: str # cpp, python, java, c
    code: str
    custom_input: Optional[str] = None

class TestCaseResult(BaseModel):
    test_case_id: Optional[str] = None
    order_index: int
    status: str # PASSED, WRONG_ANSWER, TIME_LIMIT_EXCEEDED, RUNTIME_ERROR
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    execution_time_ms: float
    memory_kb: int
    is_hidden: bool = False
    stderr: Optional[str] = None

class CodeRunResponse(BaseModel):
    status: str # SUCCESS, COMPILATION_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compiler_output: Optional[str] = None
    execution_time_ms: float = 0.0
    memory_kb: int = 0
    test_case_results: List[TestCaseResult] = []
    passed_count: int = 0
    total_count: int = 0

class SubmissionCreate(BaseModel):
    problem_id: str
    language: str
    code: str
    hints_used: int = 0
    mock_attempt_id: Optional[str] = None

class SubmissionResponse(BaseModel):
    id: str
    user_id: str
    problem_id: str
    problem_title: Optional[str] = None
    language: str
    code: str
    status: str
    execution_time_ms: float
    memory_kb: int
    test_cases_passed: int
    total_test_cases: int
    compiler_output: Optional[str] = None
    runtime_error: Optional[str] = None
    is_mock: bool
    created_at: datetime
    test_case_results: List[TestCaseResult] = []

    class Config:
        from_attributes = True

class SubmissionAnalytics(BaseModel):
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    status_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    average_time_ms: float

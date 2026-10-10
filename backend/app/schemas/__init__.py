from app.schemas.auth import Token, TokenPayload, UserRegister, UserLogin, ProfileUpdate, ProfileResponse, UserResponse
from app.schemas.problem import TopicBase, TestCaseBase, HintBase, ProblemListItem, ProblemDetail, ProblemCreate, ProblemFilter
from app.schemas.submission import CodeRunRequest, TestCaseResult, CodeRunResponse, SubmissionCreate, SubmissionResponse, SubmissionAnalytics
from app.schemas.mock import MockProblemItem, MockTestResponse, MockTestCreate, MockStartResponse, MockSubmissionRequest, MockAttemptResult
from app.schemas.skill import (
    TopicSkillScore, SkillMatrixResponse, DiagnosticAnswerItem, DiagnosticSubmitRequest, DiagnosticResultResponse,
    StudyTaskResponse, StudyPlanResponse, PlanRegenerateRequest,
    AITutorRequest, AITutorResponse, AICodeReviewRequest, AICodeReviewResponse, AdminStatsResponse
)

__all__ = [
    "Token", "TokenPayload", "UserRegister", "UserLogin", "ProfileUpdate", "ProfileResponse", "UserResponse",
    "TopicBase", "TestCaseBase", "HintBase", "ProblemListItem", "ProblemDetail", "ProblemCreate", "ProblemFilter",
    "CodeRunRequest", "TestCaseResult", "CodeRunResponse", "SubmissionCreate", "SubmissionResponse", "SubmissionAnalytics",
    "MockProblemItem", "MockTestResponse", "MockTestCreate", "MockStartResponse", "MockSubmissionRequest", "MockAttemptResult",
    "TopicSkillScore", "SkillMatrixResponse", "DiagnosticAnswerItem", "DiagnosticSubmitRequest", "DiagnosticResultResponse",
    "StudyTaskResponse", "StudyPlanResponse", "PlanRegenerateRequest",
    "AITutorRequest", "AITutorResponse", "AICodeReviewRequest", "AICodeReviewResponse", "AdminStatsResponse"
]

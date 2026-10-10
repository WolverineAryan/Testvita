from app.services.auth_service import auth_service, AuthService
from app.services.problem_service import problem_service, ProblemService
from app.services.submission_service import submission_service, SubmissionService
from app.services.mock_service import mock_service, MockService
from app.services.skill_service import skill_service, SkillService
from app.services.plan_service import plan_service, PlanService
from app.services.analytics_service import analytics_service, AnalyticsService
from app.services.gamification_service import gamification_service, GamificationService
from app.services.admin_service import admin_service, AdminService

__all__ = [
    "auth_service", "AuthService",
    "problem_service", "ProblemService",
    "submission_service", "SubmissionService",
    "mock_service", "MockService",
    "skill_service", "SkillService",
    "plan_service", "PlanService",
    "analytics_service", "AnalyticsService",
    "gamification_service", "GamificationService",
    "admin_service", "AdminService"
]

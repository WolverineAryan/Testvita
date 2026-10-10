from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.problems import router as problems_router
from app.api.v1.execution import router as execution_router
from app.api.v1.mocks import router as mocks_router
from app.api.v1.skills import router as skills_router
from app.api.v1.plans import router as plans_router
from app.api.v1.ai import router as ai_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.competitions import router as competitions_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(problems_router)
api_router.include_router(execution_router)
api_router.include_router(mocks_router)
api_router.include_router(skills_router)
api_router.include_router(plans_router)
api_router.include_router(ai_router)
api_router.include_router(recommendations_router)
api_router.include_router(analytics_router)
api_router.include_router(competitions_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]

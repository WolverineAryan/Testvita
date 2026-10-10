from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User, Profile
from app.models.gamification import Streak
from app.schemas.auth import UserRegister, UserLogin, ProfileUpdate
from app.auth.security import get_password_hash, verify_password, create_access_token

class AuthService:
    @classmethod
    async def register_user(cls, db: AsyncSession, data: UserRegister) -> User:
        # Check if email exists
        stmt = select(User).where(User.email == data.email.lower().strip())
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists"
            )

        # Create user
        user = User(
            email=data.email.lower().strip(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name.strip(),
            role=data.role if data.role in ["USER", "ADMIN", "CONTENT_MANAGER"] else "USER",
            is_active=True,
            is_verified=True,
            xp=0,
            level=1
        )
        db.add(user)
        await db.flush()

        # Create default profile
        profile = Profile(
            user_id=user.id,
            preferred_language="cpp",
            programming_experience="INTERMEDIATE",
            cp_experience="BEGINNER",
            daily_available_hours=2.0,
            preferred_study_time="EVENING",
            target_competition="TCS CodeVita",
            skill_level="BEGINNER",
            preparation_goal="Crack CodeVita Round 1 & 2",
            onboarding_completed=False,
            diagnostic_completed=False
        )
        db.add(profile)

        # Create default streak record
        streak = Streak(
            user_id=user.id,
            current_streak=0,
            longest_streak=0,
            total_active_days=0
        )
        db.add(streak)
        await db.commit()

        # Reload user with profile explicitly loaded
        user_stmt = select(User).options(selectinload(User.profile)).where(User.id == user.id)
        user_res = await db.execute(user_stmt)
        return user_res.scalar_one()

    @classmethod
    async def login_user(cls, db: AsyncSession, data: UserLogin) -> Dict[str, Any]:
        stmt = select(User).options(selectinload(User.profile)).where(User.email == data.email.lower().strip())
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is disabled"
            )

        token = create_access_token(subject=user.id, role=user.role)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }

    @classmethod
    async def update_profile(cls, db: AsyncSession, user_id: str, data: ProfileUpdate) -> Profile:
        stmt = select(Profile).where(Profile.user_id == user_id)
        res = await db.execute(stmt)
        profile = res.scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(profile, key, val)

        profile.updated_at = datetime.utcnow()
        await db.flush()
        return profile

auth_service = AuthService()

from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.gamification import Achievement, UserAchievement, Streak

class GamificationService:
    @staticmethod
    def calculate_level(xp: int) -> int:
        # Level 1 at 0 XP, Level 2 at 100 XP, Level 3 at 250 XP, etc. (Level = 1 + floor(sqrt(XP / 50)))
        import math
        return max(1, int(1 + math.floor(math.sqrt(max(0, xp) / 50.0))))

    @classmethod
    async def add_xp(cls, db: AsyncSession, user_id: str, xp_amount: int) -> int:
        user_stmt = select(User).where(User.id == user_id)
        res = await db.execute(user_stmt)
        user = res.scalar_one_or_none()
        if not user:
            return 0

        user.xp += xp_amount
        user.level = cls.calculate_level(user.xp)
        await db.flush()
        return user.xp

    @classmethod
    async def update_streak(cls, db: AsyncSession, user_id: str) -> Streak:
        stmt = select(Streak).where(Streak.user_id == user_id)
        res = await db.execute(stmt)
        streak = res.scalar_one_or_none()

        today = date.today()
        if not streak:
            streak = Streak(
                user_id=user_id,
                current_streak=1,
                longest_streak=1,
                last_activity_date=today,
                total_active_days=1
            )
            db.add(streak)
            await db.flush()
            return streak

        if streak.last_activity_date == today:
            return streak # Already updated today

        yesterday = today - timedelta(days=1)
        if streak.last_activity_date == yesterday:
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        else:
            streak.current_streak = 1 # Streak broken, restart

        streak.last_activity_date = today
        streak.total_active_days += 1
        await db.flush()
        return streak

    @classmethod
    async def check_and_unlock_achievements(
        cls,
        db: AsyncSession,
        user_id: str,
        solved_count: int,
        mock_count: int,
        streak_days: int
    ) -> List[Achievement]:
        # Fetch existing unlocked achievements
        unlocked_stmt = select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
        unlocked_res = await db.execute(unlocked_stmt)
        unlocked_ids = set(unlocked_res.scalars().all())

        # Fetch all achievements
        achieve_stmt = select(Achievement)
        achieve_res = await db.execute(achieve_stmt)
        all_achievements = achieve_res.scalars().all()

        newly_unlocked = []
        for ach in all_achievements:
            if ach.id in unlocked_ids:
                continue

            should_unlock = False
            if ach.condition_type == "SOLVE_COUNT" and solved_count >= ach.condition_value:
                should_unlock = True
            elif ach.condition_type == "MOCK_COUNT" and mock_count >= ach.condition_value:
                should_unlock = True
            elif ach.condition_type == "STREAK_DAYS" and streak_days >= ach.condition_value:
                should_unlock = True

            if should_unlock:
                user_ach = UserAchievement(
                    user_id=user_id,
                    achievement_id=ach.id,
                    unlocked_at=datetime.utcnow()
                )
                db.add(user_ach)
                await cls.add_xp(db, user_id, ach.xp_reward)
                newly_unlocked.append(ach)

        if newly_unlocked:
            await db.flush()
        return newly_unlocked

gamification_service = GamificationService()

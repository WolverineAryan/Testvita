from datetime import datetime, date
from sqlalchemy import Column, String, Integer, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True) # FIRST_SOLVE, TEN_SOLVES, STREAK_7, etc.
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(64), default="Trophy", nullable=False)
    xp_reward = Column(Integer, default=50, nullable=False)
    category = Column(String(64), default="SOLVING", nullable=False) # SOLVING, MOCKS, STREAKS, TOPICS
    condition_type = Column(String(64), nullable=False) # SOLVE_COUNT, MOCK_COUNT, STREAK_DAYS, TOPIC_SCORE
    condition_value = Column(Integer, default=1, nullable=False)

    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(String(36), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class Streak(Base):
    __tablename__ = "streaks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    total_active_days = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="streak")

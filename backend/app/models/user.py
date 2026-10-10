import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer, Float
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(32), default="USER", nullable=False)  # USER, ADMIN, CONTENT_MANAGER
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    mock_attempts = relationship("MockAttempt", back_populates="user", cascade="all, delete-orphan")
    skill_scores = relationship("SkillScore", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")
    mistakes = relationship("Mistake", back_populates="user", cascade="all, delete-orphan")
    review_queue = relationship("ReviewQueue", back_populates="user", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    streak = relationship("Streak", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    college = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    preferred_language = Column(String(32), default="cpp", nullable=False)
    programming_experience = Column(String(64), default="INTERMEDIATE", nullable=False) # BEGINNER, INTERMEDIATE, ADVANCED
    cp_experience = Column(String(64), default="BEGINNER", nullable=False)
    daily_available_hours = Column(Float, default=2.0, nullable=False)
    preferred_study_time = Column(String(64), default="EVENING", nullable=False) # MORNING, AFTERNOON, EVENING, NIGHT
    target_competition = Column(String(128), default="TCS CodeVita", nullable=False)
    target_date = Column(DateTime, nullable=True)
    skill_level = Column(String(32), default="BEGINNER", nullable=False) # BEGINNER, INTERMEDIATE, ADVANCED
    preparation_goal = Column(String(255), default="Crack CodeVita Round 1 & 2", nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    diagnostic_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile", lazy="selectin")

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, JSON
from app.database.session import Base
from app.models.user import generate_uuid

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), nullable=False) # e.g. "TCS CodeVita"
    season = Column(String(64), default="Season 14", nullable=False)
    year = Column(Integer, default=2026, nullable=False)
    description = Column(Text, nullable=True)
    official_url = Column(String(512), default="https://codevita.tcsapps.com", nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=360, nullable=False) # 6 hours for round 1
    num_rounds = Column(Integer, default=3, nullable=False)
    eligibility = Column(Text, nullable=True)
    rules = Column(JSON, default=list, nullable=False) # Configurable rules list
    allowed_languages = Column(JSON, default=["C", "C++", "Java", "Python"], nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(64), default="PLATFORM_UPDATE", nullable=False) 
    # EXAM_UPDATE, MOCK_RELEASE, NEW_PROBLEMS, PLATFORM_UPDATE
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    problem_id = Column(String(36), nullable=True, index=True)
    interaction_type = Column(String(64), nullable=False) # TUTOR, REVIEW, HINT, PLANNER, DEBUG, EXPLAIN
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_name = Column(String(64), default="gemini-1.5-pro", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

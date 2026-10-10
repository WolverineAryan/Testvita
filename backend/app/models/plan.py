from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Adaptive CodeVita Roadmap", nullable=False)
    generated_by = Column(String(32), default="AI", nullable=False) # AI, DETERMINISTIC
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=False)
    priority_topics = Column(JSON, default=list, nullable=False) # [{topic: "Graphs", priority: 0.92, reason: "..."}]
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="study_plans")
    tasks = relationship("StudyTask", back_populates="study_plan", cascade="all, delete-orphan")

class StudyTask(Base):
    __tablename__ = "study_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    study_plan_id = Column(String(36), ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, default=1, nullable=False) # Day 1, Day 2, etc.
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    subtopic_name = Column(String(100), nullable=True)
    task_type = Column(String(64), default="PRACTICE", nullable=False) # LEARN, PRACTICE, TIMED_CHALLENGE, REVIEW_MISTAKES
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=45, nullable=False)
    target_problem_count = Column(Integer, default=3, nullable=False)
    target_difficulty = Column(String(32), default="MEDIUM", nullable=False) # EASY, MEDIUM, HARD
    target_problem_id = Column(String(36), ForeignKey("problems.id", ondelete="SET NULL"), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    study_plan = relationship("StudyPlan", back_populates="tasks")
    topic = relationship("Topic")
    target_problem = relationship("Problem")

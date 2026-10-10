from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(64), default="LOGIC", nullable=False) # LOGIC, SYNTAX, COMPLEXITY, EDGE_CASE, IMPLEMENTATION, CONCEPT
    failure_type = Column(String(64), nullable=False) # WRONG_ANSWER, TLE, RUNTIME_ERROR, COMPILATION_ERROR
    user_notes = Column(Text, nullable=True)
    ai_insight = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="mistakes")
    problem = relationship("Problem")
    submission = relationship("Submission")

class ReviewQueue(Base):
    __tablename__ = "review_queue"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    interval_days = Column(Integer, default=1, nullable=False) # 1, 3, 7, 14, 30
    repetitions = Column(Integer, default=0, nullable=False)
    ease_factor = Column(Float, default=2.5, nullable=False)
    next_review_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="review_queue")
    problem = relationship("Problem")

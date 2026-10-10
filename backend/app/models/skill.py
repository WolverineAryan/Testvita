from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class SkillScore(Base):
    __tablename__ = "skill_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, default=0.0, nullable=False) # 0 to 100
    confidence = Column(Float, default=0.1, nullable=False) # 0.0 to 1.0
    problems_solved = Column(Integer, default=0, nullable=False)
    problems_attempted = Column(Integer, default=0, nullable=False)
    average_time_seconds = Column(Float, default=0.0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="skill_scores")
    topic = relationship("Topic", back_populates="skill_scores")

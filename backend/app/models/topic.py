from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), default="Core DSA", nullable=False) # Fundamentals, Data Structures, Algorithms, Advanced
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    importance_weight = Column(Integer, default=5, nullable=False) # 1 to 10 for CodeVita

    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")
    problem_associations = relationship("ProblemTopic", back_populates="topic", cascade="all, delete-orphan")
    skill_scores = relationship("SkillScore", back_populates="topic", cascade="all, delete-orphan")

class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    topic = relationship("Topic", back_populates="subtopics")

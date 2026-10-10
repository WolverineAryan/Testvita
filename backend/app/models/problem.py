from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class Problem(Base):
    __tablename__ = "problems"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    statement = Column(Text, nullable=False)
    input_format = Column(Text, nullable=False)
    output_format = Column(Text, nullable=False)
    constraints = Column(Text, nullable=False)
    examples = Column(JSON, default=list, nullable=False) # list of {input, output, explanation}
    difficulty = Column(String(32), default="MEDIUM", nullable=False, index=True) # EASY, MEDIUM, HARD
    difficulty_score = Column(Integer, default=50, nullable=False) # 1-100
    estimated_time_minutes = Column(Integer, default=30, nullable=False)
    supported_languages = Column(JSON, default=["cpp", "python", "java", "c"], nullable=False)
    time_limit_seconds = Column(Float, default=2.0, nullable=False)
    memory_limit_mb = Column(Integer, default=256, nullable=False)
    editorial = Column(Text, nullable=True)
    source_type = Column(String(64), default="ORIGINAL", nullable=False) # ORIGINAL, ADMIN_CREATED, OFFICIAL_REFERENCE
    source_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_diagnostic = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    topics = relationship("ProblemTopic", back_populates="problem", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    hints = relationship("Hint", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="problem", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="problem", cascade="all, delete-orphan")
    mock_problems = relationship("MockProblem", back_populates="problem", cascade="all, delete-orphan")

class ProblemTopic(Base):
    __tablename__ = "problem_topics"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    problem = relationship("Problem", back_populates="topics")
    topic = relationship("Topic", back_populates="problem_associations")

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=True, nullable=False)
    explanation = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)

    problem = relationship("Problem", back_populates="test_cases")

class Hint(Base):
    __tablename__ = "hints"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    problem = relationship("Problem", back_populates="hints")

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookmarks")
    problem = relationship("Problem", back_populates="bookmarks")

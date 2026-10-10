from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class MockTest(Base):
    __tablename__ = "mock_tests"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    mock_type = Column(String(32), default="FULL", nullable=False) # QUICK, TOPIC, MINI, FULL, WEAKNESS
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    duration_minutes = Column(Integer, default=180, nullable=False)
    total_questions = Column(Integer, default=6, nullable=False)
    difficulty_distribution = Column(JSON, default=dict, nullable=False) # {"EASY": 2, "MEDIUM": 3, "HARD": 1}
    scoring_rules = Column(JSON, default=dict, nullable=False) # {"type": "codevita_relative", "penalty_per_wrong": 0}
    allowed_languages = Column(JSON, default=["cpp", "python", "java", "c"], nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    topic = relationship("Topic")
    problems = relationship("MockProblem", back_populates="mock_test", cascade="all, delete-orphan")
    attempts = relationship("MockAttempt", back_populates="mock_test", cascade="all, delete-orphan")

class MockProblem(Base):
    __tablename__ = "mock_problems"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    mock_test_id = Column(String(36), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    marks = Column(Integer, default=100, nullable=False)

    mock_test = relationship("MockTest", back_populates="problems")
    problem = relationship("Problem", back_populates="mock_problems")

class MockAttempt(Base):
    __tablename__ = "mock_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mock_test_id = Column(String(36), ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    is_submitted = Column(Boolean, default=False, nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    accuracy = Column(Float, default=0.0, nullable=False)
    questions_attempted = Column(Integer, default=0, nullable=False)
    questions_solved = Column(Integer, default=0, nullable=False)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    ai_analysis = Column(JSON, default=dict, nullable=True)
    integrity_status = Column(String(32), default="CLEAN", nullable=False)

    user = relationship("User", back_populates="mock_attempts")
    mock_test = relationship("MockTest", back_populates="attempts")
    submissions = relationship("MockSubmission", back_populates="mock_attempt", cascade="all, delete-orphan")

class MockSubmission(Base):
    __tablename__ = "mock_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    mock_attempt_id = Column(String(36), ForeignKey("mock_attempts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(64), default="PENDING", nullable=False)
    marks_awarded = Column(Float, default=0.0, nullable=False)
    time_taken_seconds = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    mock_attempt = relationship("MockAttempt", back_populates="submissions")
    problem = relationship("Problem")
    submission = relationship("Submission")

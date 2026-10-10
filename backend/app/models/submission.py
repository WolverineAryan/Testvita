from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.user import generate_uuid

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(32), nullable=False) # cpp, python, java, c
    code = Column(Text, nullable=False)
    status = Column(String(64), default="PENDING", nullable=False, index=True) 
    # ACCEPTED, WRONG_ANSWER, TIME_LIMIT_EXCEEDED, MEMORY_LIMIT_EXCEEDED, COMPILATION_ERROR, RUNTIME_ERROR, PENDING
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    memory_kb = Column(Integer, default=0, nullable=False)
    test_cases_passed = Column(Integer, default=0, nullable=False)
    total_test_cases = Column(Integer, default=0, nullable=False)
    compiler_output = Column(Text, nullable=True)
    runtime_error = Column(Text, nullable=True)
    hints_used = Column(Integer, default=0, nullable=False)
    is_mock = Column(Boolean, default=False, nullable=False)
    mock_attempt_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    execution_results = relationship("ExecutionResult", back_populates="submission", cascade="all, delete-orphan")

class ExecutionResult(Base):
    __tablename__ = "execution_results"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=True)
    status = Column(String(64), nullable=False) # PASSED, WRONG_ANSWER, TLE, RUNTIME_ERROR
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    memory_kb = Column(Integer, default=0, nullable=False)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    is_hidden = Column(Boolean, default=True, nullable=False)

    submission = relationship("Submission", back_populates="execution_results")

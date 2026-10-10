from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.models.problem import Problem, TestCase, ProblemTopic
from app.models.submission import Submission, ExecutionResult
from app.models.mistake import Mistake, ReviewQueue
from app.schemas.submission import CodeRunRequest, CodeRunResponse, TestCaseResult, SubmissionCreate, SubmissionResponse
from app.execution.runner import execution_engine
from app.analytics.skill_engine import skill_engine
from app.services.gamification_service import gamification_service
from app.config.settings import settings

class SubmissionService:
    @classmethod
    async def run_code(cls, db: AsyncSession, data: CodeRunRequest) -> CodeRunResponse:
        # Fetch problem & public test cases
        stmt = (
            select(Problem)
            .options(selectinload(Problem.test_cases))
            .where(Problem.id == data.problem_id)
        )
        res = await db.execute(stmt)
        problem = res.scalar_one_or_none()
        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

        # If custom input is provided, run just once
        if data.custom_input is not None:
            exec_res = await execution_engine.execute_code(
                language=data.language,
                code=data.code,
                input_data=data.custom_input,
                timeout_seconds=problem.time_limit_seconds
            )
            return CodeRunResponse(
                status=exec_res.status,
                stdout=exec_res.stdout,
                stderr=exec_res.stderr,
                compiler_output=exec_res.compiler_output,
                execution_time_ms=exec_res.execution_time_ms,
                memory_kb=exec_res.memory_kb,
                test_case_results=[],
                passed_count=1 if exec_res.status == "SUCCESS" else 0,
                total_count=1
            )

        # Run against public test cases
        public_tests = [tc for tc in problem.test_cases if not tc.is_hidden]
        if not public_tests:
            # Fallback to example input if no explicit test case
            public_tests = [TestCase(input_data="", expected_output="", is_hidden=False, order_index=1)]

        results: List[TestCaseResult] = []
        passed_count = 0
        overall_status = "SUCCESS"

        for idx, tc in enumerate(public_tests, start=1):
            exec_res = await execution_engine.execute_code(
                language=data.language,
                code=data.code,
                input_data=tc.input_data,
                timeout_seconds=problem.time_limit_seconds
            )

            if exec_res.status == "COMPILATION_ERROR":
                return CodeRunResponse(
                    status="COMPILATION_ERROR",
                    compiler_output=exec_res.compiler_output or exec_res.stderr,
                    execution_time_ms=0.0,
                    memory_kb=0,
                    test_case_results=[],
                    passed_count=0,
                    total_count=len(public_tests)
                )

            # Compare output
            norm_actual = execution_engine.normalize_output(exec_res.stdout)
            norm_expected = execution_engine.normalize_output(tc.expected_output)

            if exec_res.status != "SUCCESS":
                case_status = exec_res.status
                overall_status = exec_res.status
            elif norm_actual == norm_expected:
                case_status = "PASSED"
                passed_count += 1
            else:
                case_status = "WRONG_ANSWER"
                if overall_status == "SUCCESS":
                    overall_status = "WRONG_ANSWER"

            results.append(TestCaseResult(
                test_case_id=tc.id,
                order_index=idx,
                status=case_status,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                actual_output=exec_res.stdout,
                execution_time_ms=exec_res.execution_time_ms,
                memory_kb=exec_res.memory_kb,
                is_hidden=False,
                stderr=exec_res.stderr
            ))

        return CodeRunResponse(
            status=overall_status,
            stdout="",
            stderr="",
            compiler_output="",
            execution_time_ms=max((r.execution_time_ms for r in results), default=0.0),
            memory_kb=max((r.memory_kb for r in results), default=0),
            test_case_results=results,
            passed_count=passed_count,
            total_count=len(public_tests)
        )

    @classmethod
    async def submit_code(cls, db: AsyncSession, user_id: str, data: SubmissionCreate) -> SubmissionResponse:
        stmt = (
            select(Problem)
            .options(
                selectinload(Problem.test_cases),
                selectinload(Problem.topics).selectinload(ProblemTopic.topic)
            )
            .where(Problem.id == data.problem_id)
        )
        res = await db.execute(stmt)
        problem = res.scalar_one_or_none()
        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

        all_test_cases = sorted(problem.test_cases, key=lambda x: x.order_index)
        if not all_test_cases:
            all_test_cases = [TestCase(input_data="", expected_output="", is_hidden=False, order_index=1)]

        submission = Submission(
            user_id=user_id,
            problem_id=problem.id,
            language=data.language,
            code=data.code,
            status="PENDING",
            hints_used=data.hints_used,
            is_mock=bool(data.mock_attempt_id),
            mock_attempt_id=data.mock_attempt_id,
            total_test_cases=len(all_test_cases)
        )
        db.add(submission)
        await db.flush()

        results: List[TestCaseResult] = []
        passed_count = 0
        overall_status = "ACCEPTED"
        total_time_ms = 0.0
        max_mem_kb = 0
        compiler_out = None
        runtime_err = None

        for idx, tc in enumerate(all_test_cases, start=1):
            exec_res = await execution_engine.execute_code(
                language=data.language,
                code=data.code,
                input_data=tc.input_data,
                timeout_seconds=problem.time_limit_seconds
            )

            if exec_res.status == "COMPILATION_ERROR":
                overall_status = "COMPILATION_ERROR"
                compiler_out = exec_res.compiler_output or exec_res.stderr
                break

            total_time_ms = max(total_time_ms, exec_res.execution_time_ms)
            max_mem_kb = max(max_mem_kb, exec_res.memory_kb)

            norm_actual = execution_engine.normalize_output(exec_res.stdout)
            norm_expected = execution_engine.normalize_output(tc.expected_output)

            if exec_res.status == "TIME_LIMIT_EXCEEDED":
                case_status = "TIME_LIMIT_EXCEEDED"
                if overall_status == "ACCEPTED":
                    overall_status = "TIME_LIMIT_EXCEEDED"
            elif exec_res.status == "RUNTIME_ERROR":
                case_status = "RUNTIME_ERROR"
                runtime_err = exec_res.stderr
                if overall_status == "ACCEPTED":
                    overall_status = "RUNTIME_ERROR"
            elif norm_actual == norm_expected:
                case_status = "PASSED"
                passed_count += 1
            else:
                case_status = "WRONG_ANSWER"
                if overall_status == "ACCEPTED":
                    overall_status = "WRONG_ANSWER"

            # Save execution result record
            exec_record = ExecutionResult(
                submission_id=submission.id,
                test_case_id=tc.id,
                status=case_status,
                execution_time_ms=exec_res.execution_time_ms,
                memory_kb=exec_res.memory_kb,
                stdout=exec_res.stdout if not tc.is_hidden else None,
                stderr=exec_res.stderr if not tc.is_hidden else None,
                is_hidden=tc.is_hidden
            )
            db.add(exec_record)

            results.append(TestCaseResult(
                test_case_id=tc.id,
                order_index=idx,
                status=case_status,
                input_data=tc.input_data if not tc.is_hidden else None,
                expected_output=tc.expected_output if not tc.is_hidden else None,
                actual_output=exec_res.stdout if not tc.is_hidden else None,
                execution_time_ms=exec_res.execution_time_ms,
                memory_kb=exec_res.memory_kb,
                is_hidden=tc.is_hidden,
                stderr=exec_res.stderr if not tc.is_hidden else None
            ))

        # Update submission summary
        submission.status = overall_status
        submission.test_cases_passed = passed_count
        submission.execution_time_ms = total_time_ms
        submission.memory_kb = max_mem_kb
        submission.compiler_output = compiler_out
        submission.runtime_error = runtime_err

        # Skill & Analytics Updates
        is_correct = (overall_status == "ACCEPTED")
        for pt in problem.topics:
            if pt.topic_id:
                await skill_engine.update_user_skill(
                    db=db,
                    user_id=user_id,
                    topic_id=pt.topic_id,
                    is_correct=is_correct,
                    difficulty=problem.difficulty,
                    time_spent_seconds=max(30.0, total_time_ms / 1000.0)
                )

        # Gamification: Award XP & Streak
        if is_correct:
            xp_gain = settings.XP_PER_EASY_SOLVE if problem.difficulty == "EASY" else (
                settings.XP_PER_MEDIUM_SOLVE if problem.difficulty == "MEDIUM" else settings.XP_PER_HARD_SOLVE
            )
            await gamification_service.add_xp(db, user_id, xp_gain)
            streak = await gamification_service.update_streak(db, user_id)

            # Count total solved
            solved_stmt = select(func.count(func.distinct(Submission.problem_id))).where(
                Submission.user_id == user_id,
                Submission.status == "ACCEPTED"
            )
            solved_res = await db.execute(solved_stmt)
            solved_count = solved_res.scalar_one() or 1

            await gamification_service.check_and_unlock_achievements(
                db=db,
                user_id=user_id,
                solved_count=solved_count,
                mock_count=0,
                streak_days=streak.current_streak
            )

            # Auto-progress and check off active roadmap tasks
            try:
                from app.services.plan_service import plan_service
                await plan_service.on_problem_solved(
                    db=db,
                    user_id=user_id,
                    problem_id=problem.id,
                    topic_ids=[pt.topic_id for pt in problem.topics if pt.topic_id]
                )
            except Exception:
                pass
        else:
            # Record Mistake for Mistake Notebook and Spaced Repetition Queue
            mistake_category = "LOGIC" if overall_status == "WRONG_ANSWER" else (
                "COMPLEXITY" if overall_status == "TIME_LIMIT_EXCEEDED" else (
                    "SYNTAX" if overall_status == "COMPILATION_ERROR" else "IMPLEMENTATION"
                )
            )
            mistake = Mistake(
                user_id=user_id,
                problem_id=problem.id,
                submission_id=submission.id,
                category=mistake_category,
                failure_type=overall_status,
                user_notes=None,
                ai_insight=f"Encountered {overall_status} on problem '{problem.title}'."
            )
            db.add(mistake)

            # Add to Review Queue
            rq_stmt = select(ReviewQueue).where(ReviewQueue.user_id == user_id, ReviewQueue.problem_id == problem.id)
            rq_res = await db.execute(rq_stmt)
            rq = rq_res.scalar_one_or_none()
            if not rq:
                rq = ReviewQueue(
                    user_id=user_id,
                    problem_id=problem.id,
                    interval_days=1,
                    repetitions=0,
                    next_review_at=datetime.utcnow() + timedelta(days=1)
                )
                db.add(rq)

        await db.flush()

        return SubmissionResponse(
            id=submission.id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            problem_title=problem.title,
            language=submission.language,
            code=submission.code,
            status=submission.status,
            execution_time_ms=submission.execution_time_ms,
            memory_kb=submission.memory_kb,
            test_cases_passed=submission.test_cases_passed,
            total_test_cases=submission.total_test_cases,
            compiler_output=submission.compiler_output,
            runtime_error=submission.runtime_error,
            is_mock=submission.is_mock,
            created_at=submission.created_at,
            test_case_results=results
        )

    @classmethod
    async def get_user_submissions(
        cls,
        db: AsyncSession,
        user_id: str,
        problem_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(Submission)
            .options(selectinload(Submission.problem))
            .where(Submission.user_id == user_id)
            .order_by(Submission.created_at.desc())
        )
        if problem_id:
            stmt = stmt.where(Submission.problem_id == problem_id)

        stmt = stmt.limit(limit)
        res = await db.execute(stmt)
        submissions = res.scalars().all()

        return [
            {
                "id": s.id,
                "problem_id": s.problem_id,
                "problem_title": s.problem.title if s.problem else "Unknown",
                "problem_slug": s.problem.slug if s.problem else "",
                "language": s.language,
                "code": s.code,
                "status": s.status,
                "execution_time_ms": s.execution_time_ms,
                "memory_kb": s.memory_kb,
                "test_cases_passed": s.test_cases_passed,
                "total_test_cases": s.total_test_cases,
                "is_mock": s.is_mock,
                "created_at": s.created_at
            }
            for s in submissions
        ]

submission_service = SubmissionService()

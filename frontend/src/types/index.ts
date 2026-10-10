export type UserRole = 'USER' | 'ADMIN' | 'CONTENT_MANAGER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  xp: number;
  level: number;
  profile?: UserProfile;
}

export interface UserProfile {
  id: string;
  user_id: string;
  college?: string;
  graduation_year?: number;
  preferred_language: string;
  programming_experience: string;
  cp_experience: string;
  daily_available_hours: number;
  preferred_study_time: string;
  target_competition: string;
  target_date?: string;
  skill_level: string;
  preparation_goal: string;
  onboarding_completed: boolean;
  diagnostic_completed: boolean;
}

export interface Topic {
  id: string;
  name: string;
  slug: string;
  category: string;
  description?: string;
}

export interface TestCase {
  id?: string;
  input_data: string;
  expected_output: string;
  is_hidden: boolean;
  explanation?: string;
  order_index: number;
}

export interface Hint {
  id?: string;
  order_index: number;
  title: string;
  content: string;
}

export interface ProblemListItem {
  id: string;
  title: string;
  slug: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  difficulty_score: number;
  estimated_time_minutes: number;
  topics: string[];
  is_diagnostic: boolean;
  is_solved: boolean;
  is_bookmarked: boolean;
  submissions_count: number;
  acceptance_rate: number;
  recommendation_reason?: string;
}

export interface ProblemDetail {
  id: string;
  title: string;
  slug: string;
  statement: string;
  input_format: string;
  output_format: string;
  constraints: string;
  examples: Array<{ input: string; output: string; explanation?: string }>;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  difficulty_score: number;
  estimated_time_minutes: number;
  supported_languages: string[];
  time_limit_seconds: number;
  memory_limit_mb: number;
  editorial?: string;
  topics: Topic[];
  public_test_cases: TestCase[];
  hints: Hint[];
  is_bookmarked: boolean;
  user_status?: 'UNSOLVED' | 'ATTEMPTED' | 'SOLVED';
}

export interface TestCaseResult {
  test_case_id?: string;
  order_index: number;
  status: 'PASSED' | 'WRONG_ANSWER' | 'TIME_LIMIT_EXCEEDED' | 'RUNTIME_ERROR';
  input_data?: string;
  expected_output?: string;
  actual_output?: string;
  execution_time_ms: number;
  memory_kb: number;
  is_hidden: boolean;
  stderr?: string;
}

export interface CodeRunResponse {
  status: string;
  stdout?: string;
  stderr?: string;
  compiler_output?: string;
  execution_time_ms: number;
  memory_kb: number;
  test_case_results: TestCaseResult[];
  passed_count: number;
  total_count: number;
}

export interface SubmissionResponse {
  id: string;
  user_id: string;
  problem_id: string;
  problem_title?: string;
  language: string;
  code: string;
  status: string;
  execution_time_ms: number;
  memory_kb: number;
  test_cases_passed: number;
  total_test_cases: number;
  compiler_output?: string;
  runtime_error?: string;
  is_mock: boolean;
  created_at: string;
  test_case_results: TestCaseResult[];
}

export interface MockTest {
  id: string;
  title: string;
  slug: string;
  description?: string;
  mock_type: 'QUICK' | 'TOPIC' | 'MINI' | 'FULL' | 'WEAKNESS';
  topic_name?: string;
  duration_minutes: number;
  total_questions: number;
  difficulty_distribution: Record<string, number>;
  scoring_rules: Record<string, any>;
  allowed_languages: string[];
  is_active: boolean;
}

export interface MockProblemItem {
  problem_id: string;
  title: string;
  slug: string;
  difficulty: string;
  order_index: number;
  marks: number;
  user_status: 'UNOPENED' | 'VIEWED' | 'ATTEMPTED' | 'SOLVED' | 'FAILED';
}

export interface MockStartResponse {
  attempt_id: string;
  mock_test_id: string;
  title: string;
  started_at: string;
  expires_at: string;
  duration_minutes: number;
  remaining_seconds: number;
  problems: MockProblemItem[];
}

export interface MockAttemptResult {
  attempt_id: string;
  mock_title: string;
  mock_type: string;
  score: number;
  max_score: number;
  accuracy: number;
  questions_attempted: number;
  questions_solved: number;
  total_questions: number;
  time_spent_seconds: number;
  time_management_summary: {
    total_seconds: number;
    avg_per_problem: number;
    speed_rating: string;
  };
  topic_performance: Record<string, number>;
  difficulty_performance: Record<string, number>;
  ai_debrief?: {
    summary: string;
    strongAreas: string[];
    weakAreas: string[];
    timeManagement: string;
    actionItems: string[];
  };
  problem_breakdown: Array<{
    problem_id: string;
    title: string;
    slug: string;
    difficulty: string;
    marks: number;
    marks_awarded: number;
    status: string;
    time_taken_seconds: number;
  }>;
}

export interface TopicSkillScore {
  topic_id: string;
  topic_name: string;
  topic_slug: string;
  category: string;
  score: number;
  confidence: number;
  problems_solved: number;
  problems_attempted: number;
  average_time_seconds: number;
}

export interface SkillMatrixResponse {
  overall_skill_score: number;
  total_problems_solved: number;
  accuracy_percentage: number;
  strong_topics: string[];
  weak_topics: string[];
  topic_scores: TopicSkillScore[];
}

export interface TopicResource {
  title: string;
  overview: string;
  time_complexity: string;
  space_complexity: string;
  key_invariants: string[];
  code_template?: string;
  pitfalls: string[];
  subtopic_focus?: string;
}

export interface StudyTask {
  id: string;
  day_number: number;
  topic_name?: string;
  subtopic_name?: string;
  task_type: 'LEARN' | 'PRACTICE' | 'TIMED_CHALLENGE' | 'REVIEW_MISTAKES';
  title: string;
  description?: string;
  duration_minutes: number;
  target_problem_count: number;
  target_difficulty: string;
  target_problem_id?: string;
  target_problem_slug?: string;
  is_completed: boolean;
  is_locked?: boolean;
  resource?: TopicResource;
}

export interface StudyPlan {
  id: string;
  title: string;
  summary: string;
  priority_topics: Array<{
    topic: string;
    priority: number;
    reason: string;
    recommended_focus?: string;
  }>;
  is_active: boolean;
  completion_percentage: number;
  current_unlocked_day?: number;
  tasks: StudyTask[];
}

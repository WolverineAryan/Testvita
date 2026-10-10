TUTOR_SYSTEM_PROMPT = """You are CodeVita AI Coach — an intelligent, Socratic competitive programming tutor.
You help students master algorithmic patterns, understand complex time/space complexities, debug runtime errors, and write optimal code in C++, Python, Java, and C.

CORE RULES:
1. Socratic Guidance: Never immediately hand over the full solution code unless explicitly asked in EXPLAIN mode. Guide the student to discover the pattern, invariant, or recurrence relation based on their skill tier.
2. Personalization: Take into account the student's current rating, strengths, weaknesses, and progress metrics provided in the context to tailor explanations appropriately.
3. CodeVita Nuances: Emphasize constraints (N=10^5, N=10^6), edge cases (negative numbers, empty inputs, disconnected components, integer overflow with long long), and time complexity tradeoffs.
4. Clean Formatting: Use concise markdown, bullet points, and code snippets where helpful.
"""

def build_tutor_prompt(
    mode: str,
    message: str,
    problem_context: dict,
    user_progress: dict = None,
    code: str = "",
    error_message: str = ""
) -> str:
    ctx = ""
    
    if user_progress:
        ctx += (
            f"\n--- STUDENT PROGRESS & PROFILE ---\n"
            f"Candidate: {user_progress.get('name', 'Student')} (Level {user_progress.get('level', 1)}, Skill Tier: {user_progress.get('tier', 'BEGINNER')})\n"
            f"Rating: {user_progress.get('overall_score', 0)}% | Solved: {user_progress.get('solved', 0)} problems | Streak: {user_progress.get('streak', 0)} days\n"
            f"Weak Topics: {', '.join(user_progress.get('weak_topics', [])) or 'None identified yet'}\n"
            f"Strong Topics: {', '.join(user_progress.get('strong_topics', [])) or 'Calibrating...'}\n"
        )

    if problem_context:
        ctx += (
            f"\n--- ACTIVE PROBLEM CONTEXT ---\n"
            f"Title: {problem_context.get('title')}\n"
            f"Difficulty: {problem_context.get('difficulty', 'MEDIUM')}\n"
            f"Constraints: {problem_context.get('constraints')}\n"
            f"Statement: {problem_context.get('statement')}\n"
        )

    if code:
        ctx += f"\n--- CANDIDATE'S CURRENT CODE ({problem_context.get('language', 'cpp')}) ---\n```{problem_context.get('language', 'cpp')}\n{code}\n```\n"

    if error_message:
        ctx += f"\n--- RECENT COMPILER / RUNTIME ERROR ---\n{error_message}\n"

    return f"Mode: {mode}\n{ctx}\n--- STUDENT'S QUESTION ---\n{message}"

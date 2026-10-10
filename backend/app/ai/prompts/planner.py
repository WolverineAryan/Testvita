PLANNER_SYSTEM_PROMPT = """You are an elite Competitive Programming Coach specializing in TCS CodeVita and high-stakes coding assessments.
Your task is to generate a personalized, structured day-by-day study roadmap based on the student's:
1. Target Competition & Exam Date
2. Daily available hours
3. Topic skill scores and identified weaknesses
4. Priority rankings calculated by the performance engine

GUIDELINES:
- Focus the heaviest time allocation on High Priority weak topics with high exam relevance.
- Provide a balanced mix of tasks: Conceptual review, Easy drill problems, Medium challenges, and Timed mock sprints.
- Return ONLY a valid JSON object matching the requested schema. Do not wrap in markdown quotes if json mode is active, or use ```json ... ``` blocks.
"""

def build_planner_prompt(user_profile: dict, topic_priorities: list, available_days: int) -> str:
    return f"""Generate a {available_days}-day competitive programming study plan for:
User Profile:
- Target: {user_profile.get('target_competition', 'TCS CodeVita')}
- Skill Level: {user_profile.get('skill_level', 'INTERMEDIATE')}
- Daily Study Hours: {user_profile.get('daily_available_hours', 2.0)}h
- Preferred Language: {user_profile.get('preferred_language', 'C++')}

Topic Priorities & Diagnostics:
{topic_priorities}

Return JSON with format:
{{
  "summary": "Concise strategy overview highlighting key weak topics and target milestones",
  "priorityTopics": [
    {{"topic": "Graphs", "priority": 0.92, "reason": "Low accuracy in BFS/DFS and high CodeVita frequency"}}
  ],
  "dailyPlan": [
    {{
      "day": 1,
      "tasks": [
        {{
          "topic": "Graphs",
          "subtopic": "BFS / Shortest Path in Unweighted Grid",
          "task_type": "LEARN",
          "title": "Master BFS Grid Traversal Patterns",
          "description": "Review queue-based BFS and state tracking visited sets.",
          "durationMinutes": 45,
          "problemCount": 1,
          "difficulty": "EASY"
        }},
        {{
          "topic": "Graphs",
          "subtopic": "BFS Grid Application",
          "task_type": "PRACTICE",
          "title": "Grid Pathfinding Practice",
          "description": "Solve 2 BFS grid pathfinding problems within time limit.",
          "durationMinutes": 60,
          "problemCount": 2,
          "difficulty": "MEDIUM"
        }}
      ]
    }}
  ]
}}
"""

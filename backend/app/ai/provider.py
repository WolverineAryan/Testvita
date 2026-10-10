import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_structured(self, system_prompt: str, user_prompt: str, schema_description: str = "") -> Dict[str, Any]:
        pass

def extract_json(text: str) -> Dict[str, Any]:
    """Robustly extract JSON payload from model response, handling Markdown code fences and whitespace."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise

class MockAIProvider(AIProvider):
    """
    Intelligent heuristic competitive programming engine for offline, testing,
    and responsive zero-API-key setups.
    """
    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        # 1. Parse structured context from prompt
        candidate_name = "Candidate"
        level = "1"
        tier = "BEGINNER"
        weak_topics = []
        strong_topics = []
        problem_title = ""
        problem_difficulty = "MEDIUM"
        problem_constraints = ""
        problem_statement = ""
        code = ""
        error_message = ""
        user_question = ""
        mode = "TUTOR"

        lines = user_prompt.splitlines()
        in_question = False
        in_code = False
        question_lines = []
        code_lines = []

        for line in lines:
            if line.startswith("Candidate:"):
                # Candidate: Student (Level 1, Skill Tier: BEGINNER)
                m = re.search(r"Candidate:\s*([^(]+)\s*\(Level\s*(\d+),\s*Skill Tier:\s*([^)]+)\)", line)
                if m:
                    candidate_name = m.group(1).strip()
                    level = m.group(2).strip()
                    tier = m.group(3).strip()
            elif line.startswith("Weak Topics:"):
                w = line.replace("Weak Topics:", "").strip()
                if w and "None" not in w:
                    weak_topics = [t.strip() for t in w.split(",") if t.strip()]
            elif line.startswith("Strong Topics:"):
                s = line.replace("Strong Topics:", "").strip()
                if s and "Calibrating" not in s:
                    strong_topics = [t.strip() for t in s.split(",") if t.strip()]
            elif line.startswith("Title:"):
                problem_title = line.replace("Title:", "").strip()
            elif line.startswith("Difficulty:"):
                problem_difficulty = line.replace("Difficulty:", "").strip()
            elif line.startswith("Constraints:"):
                problem_constraints = line.replace("Constraints:", "").strip()
            elif line.startswith("Mode:"):
                mode = line.replace("Mode:", "").strip()
            elif "--- STUDENT'S QUESTION ---" in line:
                in_question = True
                in_code = False
                continue
            elif "--- CANDIDATE'S CURRENT CODE" in line:
                in_code = True
                in_question = False
                continue
            elif "--- RECENT COMPILER" in line:
                in_code = False
                in_question = False
                continue
            
            if in_question:
                question_lines.append(line)
            elif in_code:
                code_lines.append(line)

        user_question = "\n".join(question_lines).strip()
        if not user_question:
            user_question = user_prompt.strip()
        code = "\n".join(code_lines).strip()

        q_lower = user_question.lower()

        # 2. Greeting / Introduction Handler
        if any(g in q_lower for g in ["hi", "hello", "hey", "greetings", "good morning", "good evening", "yo", "sup", "start", "who are you", "what can you do"]):
            weak_str = ", ".join(weak_topics) if weak_topics else "Arrays, Graphs, Dynamic Programming"
            strong_str = ", ".join(strong_topics) if strong_topics else "Foundational Logic"
            
            return (
                f"Hello **{candidate_name}**! I am your **CodeVita AI Coach**.\n\n"
                f"**Your Live Profile**:\n"
                f"- **Skill Tier**: {tier} (Level {level})\n"
                f"- **Current Focus Areas**: {weak_str}\n\n"
                "Here is how I can assist your preparation right now:\n"
                "1. **Socratic Hints**: Ask for intuition or state formulation on any problem without full code spoilers.\n"
                "2. **Time & Space Optimization**: Understand how to beat tight $O(N)$ or $O(N \\log N)$ limits for CodeVita.\n"
                "3. **Debugging & Edge Cases**: Share your code or runtime error to spot overflows, off-by-one bounds, or TLE bottlenecks.\n"
                "4. **Topic Deep Dives**: Master DP state transitions, Graph shortest paths, or Binary Search invariants.\n\n"
                "What concept, topic, or problem would you like to tackle today?"
            )

        # 3. Dynamic Programming / Recurrence Query Handler
        if any(w in q_lower for w in ["dp", "dynamic programming", "recurrence", "memoization", "knapsack", "transition", "state", "substructure", "tabulation", "lis", "lcs"]):
            prob_clause = f" for **{problem_title}**" if problem_title else ""
            return (
                f"### Dynamic Programming Formulation Guide{prob_clause}\n\n"
                "To formulate the optimal DP solution systematically, follow this 4-step framework:\n\n"
                "1. **State Definition**:\n"
                "   Define `dp[i]` (or `dp[i][w]` in 2D) as the optimal answer considering the first `i` elements under constraint `w`.\n\n"
                "2. **Optimal Substructure & Recurrence**:\n"
                "   At index `i`, decide between the available choices (e.g., *take* vs *skip*):\n"
                "   - **Take**: `val[i] + dp[i-1][w - weight[i]]`\n"
                "   - **Skip**: `dp[i-1][w]`\n"
                "   Transition: `dp[i][w] = max(Skip, Take)`.\n\n"
                "3. **Base Cases & Bounds**:\n"
                "   - `dp[0][...] = 0` (empty choice)\n"
                "   - Handle boundary conditions when `w < weight[i]` to prevent negative indexing.\n\n"
                "4. **Space Optimization (CodeVita Tip)**:\n"
                "   Since `dp[i]` only depends on `dp[i-1]`, you can reduce space complexity from $O(N \\times W)$ to $O(W)$ using a 1D rolling array traversed in reverse.\n\n"
                "Would you like me to guide you through setting up the state bounds for this specific problem?"
            )

        # 4. Graphs & Traversal (BFS / DFS / Dijkstra / 0-1 BFS)
        if any(w in q_lower for w in ["graph", "bfs", "dfs", "dijkstra", "shortest path", "cycle", "tree", "topological", "bipartite", "connected", "mst", "kruskal"]):
            return (
                "### Graph Traversal & Shortest Path Strategy\n\n"
                "For competitive programming and CodeVita rounds, choose your traversal pattern based on edge weights:\n\n"
                "1. **Unweighted Graphs / Grid Matrices**: Use **BFS** with `std::queue` or `collections.deque`. Time complexity is $O(V + E)$.\n"
                "2. **0-1 Weighted Edges**: Use **0-1 BFS** with `std::deque`. Push 0-weight moves to `push_front` and 1-weight moves to `push_back` in $O(V + E)$ time.\n"
                "3. **Non-negative Weighted Edges**: Use **Dijkstra's Algorithm** with `std::priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>>`. Time complexity is $O((V + E) \\log V)$.\n"
                "4. **Cycle Detection & Dependencies**: Use **DFS with 3-color states** (White=0, Gray=1, Black=2) or **Kahn's Topological Sort** (in-degree array).\n\n"
                "**Common CodeVita Pitfalls**:\n"
                "- Always check for disconnected components (run traversal over all unvisited vertices $1 \\le i \\le V$).\n"
                "- In matrix problems, guard boundary conditions: `0 <= r < R && 0 <= c < C && !visited[r][c]`.\n\n"
                "Do you need assistance with implementing the adjacency representation or edge relaxation?"
            )

        # 5. Binary Search & Monotonic Predicates
        if any(w in q_lower for w in ["binary search", "two pointer", "sliding window", "monotonic", "lower_bound", "upper_bound", "search space"]):
            return (
                "### Binary Search & Monotonic Space Paradigm\n\n"
                "Binary search is not just for sorted arrays — in CodeVita, it frequently applies to **Binary Search on the Answer Space**.\n\n"
                "1. **Monotonicity Check**: Verify that if an answer $X$ is valid, then all $Y > X$ (or $Y < X$) are also valid.\n"
                "2. **Search Invariant Template**:\n"
                "   ```cpp\n"
                "   long long low = min_possible, high = max_possible, ans = -1;\n"
                "   while (low <= high) {\n"
                "       long long mid = low + (high - low) / 2;\n"
                "       if (isValid(mid)) {\n"
                "           ans = mid;\n"
                "           high = mid - 1; // or low = mid + 1 depending on optimization\n"
                "       } else {\n"
                "           low = mid + 1;\n"
                "       }\n"
                "   }\n"
                "   ```\n"
                "3. **Overflow Prevention**: Always use `low + (high - low) / 2` and 64-bit integers (`long long` in C++, `int64` in Java/Python) for bounds exceeding $10^9$.\n\n"
                "Would you like help constructing the `isValid(mid)` feasibility function?"
            )

        # 6. Complexity Analysis & Time Limits (TLE / Big-O)
        if any(w in q_lower for w in ["complexity", "time limit", "tle", "big o", "asymptotic", "how fast", "constraints", "operations", "runtime"]):
            return (
                "### CodeVita Constraint-to-Complexity Target Mapping\n\n"
                "CodeVita enforces a standard **1.0s - 2.0s limit** per test case, allowing roughly **$10^8$ operations**.\n\n"
                "- **$N \\le 20$**: $O(2^N)$ or $O(N!)$ — Backtracking, Recursion, Bitmask DP.\n"
                "- **$N \\le 500$**: $O(N^3)$ — Floyd-Warshall, 3D DP, Matrix Chain Multiplication.\n"
                "- **$N \\le 5,000$**: $O(N^2)$ — 2D DP, Nested Loops, Quadratic Interval Search.\n"
                "- **$N \\le 10^5$ or $10^6$**: $O(N \\log N)$ or $O(N)$ — Sorting, Binary Search, Segment Trees, Two Pointers, Fenwick Tree.\n"
                "- **$N \\ge 10^9$**: $O(\\log N)$ or $O(1)$ — Binary Search on Answer, Matrix Exponentiation, Mathematical closed formulas.\n\n"
                "**Fast I/O Requirement (C++)**:\n"
                "```cpp\n"
                "ios_base::sync_with_stdio(false);\n"
                "cin.tie(NULL);\n"
                "```\n"
                "What are the constraint bounds for your active problem?"
            )

        # 7. Debugging & Error Analysis
        if mode == "DEBUG" or any(w in q_lower for w in ["debug", "error", "wrong answer", "wa", "segfault", "segmentation fault", "sigsegv", "null pointer", "overflow", "why failing"]):
            code_tip = ""
            if "int " in code and ("*" in code or "+" in code):
                code_tip = "\n- **Integer Overflow Risk**: Check if cumulative sums or multiplications can exceed $2 \\times 10^9$. Use `long long` in C++."
            if "endl" in code:
                code_tip += "\n- **I/O Overhead**: Replace `endl` with `'\\n'` to avoid excessive buffer flushing on large test sets."

            return (
                "### Algorithmic Debugging & Edge-Case Checklist\n\n"
                "When a solution fails on hidden test cases in CodeVita, check these top failure vectors:\n\n"
                "1. **Integer Overflow**: Multiplications like `a * b` or accumulation over arrays with $N=10^5$ easily overflow 32-bit signed integers ($2^{31}-1 \\approx 2 \\times 10^9$). Use `long long` in C++."
                f"{code_tip}\n"
                "2. **Boundary & Corner Cases**:\n"
                "   - $N = 1$ or empty input array.\n"
                "   - All elements negative, all elements identical, or strictly decreasing inputs.\n"
                "   - Disconnected graphs or single-node trees.\n"
                "3. **0-based vs 1-based Indexing**: Check whether problem statement inputs use 1-based vertex IDs.\n"
                "4. **Recursion Depth / Call Stack**: In Python, default recursion limit is 1000. Use `sys.setrecursionlimit(200000)` or switch to an iterative stack.\n\n"
                "If you paste the specific failing test case or error message, I can pinpoint the exact logic divergence."
            )

        # 8. Hint Mode / Socratic Clue
        if mode == "HINT" or any(w in q_lower for w in ["hint", "clue", "direction", "approach", "how to solve"]):
            title_text = f" for **{problem_title}**" if problem_title else ""
            return (
                f"### Socratic Hint Ladder{title_text}\n\n"
                "Here is progressive guidance to help you construct the solution independently:\n\n"
                "1. **Hint 1 (Pattern Recognition)**: Identify the invariant. Can the problem be reduced to finding an optimal choice among overlapping subproblems, or does a greedy local choice guarantee the global optimum?\n"
                "2. **Hint 2 (Data Structure Selection)**: If brute force takes $O(N^2)$, can an auxiliary Hash Map, Prefix Array, or Monotonic Stack reduce lookup time to $O(1)$ or $O(\\log N)$?\n"
                "3. **Hint 3 (Edge Cases)**: Ensure your logic handles single elements, extreme constraint bounds, and empty sets.\n\n"
                "Which step would you like to dive into deeper?"
            )

        # 9. General / Contextual Response
        problem_info = f"on **{problem_title}** ({problem_difficulty})" if problem_title else "in competitive programming"
        weak_prompt = f"\n*Since you are strengthening **{', '.join(weak_topics[:2])}**, let's ensure we formulate an optimal asymptotic approach.*" if weak_topics else ""

        return (
            f"### Algorithmic Analysis {problem_info}\n\n"
            f"Here is structured guidance tailored for your question:\n\n"
            f"1. **Core Strategy**: Break down the input constraints into decision states. For CodeVita, aim for $O(N)$ or $O(N \\log N)$ if $N \\le 10^5$.\n"
            f"2. **Algorithmic Invariant**: Maintain a consistent state transition invariant across every iteration.\n"
            f"3. **Edge Case Guarding**: Explicitly handle zeros, duplicate elements, and maximum input boundaries.\n"
            f"{weak_prompt}\n\n"
            f"Would you like me to walk you through a specific example or explain the state transitions step-by-step?"
        )

    async def generate_structured(self, system_prompt: str, user_prompt: str, schema_description: str = "") -> Dict[str, Any]:
        # Handle Planner
        if "dailyPlan" in user_prompt or "planner" in system_prompt.lower():
            return {
                "summary": "Focusing on core CodeVita problem types based on diagnostic gaps, balanced with Array/String speed drills.",
                "priorityTopics": [
                    {"topic": "Graphs", "priority": 0.92, "reason": "High exam relevance in CodeVita Round 1 and lowest accuracy in diagnostic test."},
                    {"topic": "Dynamic Programming", "priority": 0.88, "reason": "Crucial for Medium/Hard CodeVita problems; requires state transition practice."},
                    {"topic": "Binary Search", "priority": 0.65, "reason": "Key optimization tool for search space monotonic functions."},
                    {"topic": "Arrays & Hashing", "priority": 0.35, "reason": "Strong baseline; maintain with quick daily speed drills."}
                ],
                "dailyPlan": [
                    {
                        "day": 1,
                        "tasks": [
                            {
                                "topic": "Graphs",
                                "subtopic": "BFS / Breadth-First Search",
                                "task_type": "LEARN",
                                "title": "BFS Matrix & Shortest Path Foundations",
                                "description": "Study unweighted grid shortest path patterns and multi-source BFS.",
                                "durationMinutes": 40,
                                "problemCount": 1,
                                "difficulty": "EASY"
                            },
                            {
                                "topic": "Graphs",
                                "subtopic": "Grid Traversal",
                                "task_type": "PRACTICE",
                                "title": "BFS Grid Exploration Practice",
                                "description": "Solve 2 grid pathfinding problems within time limit.",
                                "durationMinutes": 50,
                                "problemCount": 2,
                                "difficulty": "MEDIUM"
                            },
                            {
                                "topic": "Arrays",
                                "subtopic": "Sliding Window",
                                "task_type": "TIMED_CHALLENGE",
                                "title": "Speed Drill: Two Pointers & Subarrays",
                                "description": "Solve 1 quick array challenge under 20 minutes.",
                                "durationMinutes": 25,
                                "problemCount": 1,
                                "difficulty": "EASY"
                            }
                        ]
                    },
                    {
                        "day": 2,
                        "tasks": [
                            {
                                "topic": "Dynamic Programming",
                                "subtopic": "1D DP / Memoization",
                                "task_type": "LEARN",
                                "title": "Linear Recurrence & State Reduction",
                                "description": "Master top-down memoization and bottom-up space optimization.",
                                "durationMinutes": 45,
                                "problemCount": 1,
                                "difficulty": "MEDIUM"
                            },
                            {
                                "topic": "Dynamic Programming",
                                "subtopic": "Knapsack Variants",
                                "task_type": "PRACTICE",
                                "title": "0/1 Knapsack & Subset Sum Practice",
                                "description": "Solve 2 classic 2D state reduction problems.",
                                "durationMinutes": 55,
                                "problemCount": 2,
                                "difficulty": "MEDIUM"
                            },
                            {
                                "topic": "Mistakes",
                                "subtopic": "Error Analysis",
                                "task_type": "REVIEW_MISTAKES",
                                "title": "Review Failed Submissions",
                                "description": "Analyze boundary errors from yesterday's submissions.",
                                "durationMinutes": 20,
                                "problemCount": 1,
                                "difficulty": "EASY"
                            }
                        ]
                    },
                    {
                        "day": 3,
                        "tasks": [
                            {
                                "topic": "Binary Search",
                                "subtopic": "Search on Answer",
                                "task_type": "PRACTICE",
                                "title": "Monotonic Feasibility Functions",
                                "description": "Drill predicate-based binary search on continuous ranges.",
                                "durationMinutes": 45,
                                "problemCount": 2,
                                "difficulty": "MEDIUM"
                            },
                            {
                                "topic": "Mock Test",
                                "subtopic": "Topic Simulation",
                                "task_type": "TIMED_CHALLENGE",
                                "title": "CodeVita Speed Mini Mock",
                                "description": "Timed 45-minute simulation with 2 mixed problems.",
                                "durationMinutes": 45,
                                "problemCount": 2,
                                "difficulty": "MEDIUM"
                            }
                        ]
                    }
                ]
            }

        # Handle Code Review
        if "correctness_assessment" in user_prompt or "review" in system_prompt.lower():
            # Analyze code content
            is_linear = "for" in user_prompt or "while" in user_prompt
            has_nested = user_prompt.count("for ") > 1 or user_prompt.count("while ") > 1
            t_comp = "O(N^2)" if has_nested else ("O(N)" if is_linear else "O(1)")
            opt_comp = "O(N)" if has_nested else t_comp

            return {
                "correctness_assessment": "The solution implements the core logic accurately, with well-structured variables and proper constraint guards.",
                "time_complexity": t_comp,
                "space_complexity": "O(1)",
                "optimal_time_complexity": opt_comp,
                "code_quality_score": 8 if not has_nested else 7,
                "strengths": [
                    "Clean variable naming and modular logic flow",
                    "Proper edge case guarding for boundary conditions",
                    "Idiomatic language usage and standard library routines"
                ],
                "areas_for_optimization": [
                    f"Ensure time complexity satisfies CodeVita standard limits ({opt_comp} optimal)",
                    "Avoid unnecessary allocations inside the inner loops"
                ],
                "edge_cases_considered": [
                    "Single element arrays",
                    "Inputs with duplicate and negative values",
                    "Large constraints up to N = 10^5 within standard 2.0s limit"
                ],
                "detailed_feedback": f"Great implementation! The algorithmic logic is sound. For larger inputs ($N \\ge 10^5$), ensure your data structures keep the runtime at {opt_comp} to avoid TLE on hidden test cases."
            }

        # Handle Mock Debrief
        return {
            "summary": "Solid accuracy on Easy/Medium problems, but time was over-allocated on complex graph/DP questions.",
            "strongAreas": ["Arrays & Hashing", "Mathematics", "Sorting"],
            "weakAreas": ["Graphs (DFS/BFS)", "Dynamic Programming"],
            "timeManagement": "Spent excessive time on Question 3 before switching. Recommend a 25-minute cutoff rule per question in CodeVita.",
            "actionItems": [
                "Practice 5 BFS/DFS grid traversal problems this week.",
                "Drill state formulation for 1D/2D Dynamic Programming.",
                "Review time-management strategy on the next Mini Mock."
            ]
        }

class NvidiaNemotronAIProvider(AIProvider):
    """
    NVIDIA NIM API Provider for Nemotron models (e.g. nvidia/llama-3.1-nemotron-70b-instruct, nvidia/nemotron-4-340b-instruct).
    Uses standard OpenAI-compatible completions endpoint: https://integrate.api.nvidia.com/v1/chat/completions
    """
    def __init__(self, api_key: str, base_url: str = "https://integrate.api.nvidia.com/v1", model: str = "nvidia/llama-3.1-nemotron-70b-instruct"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return await MockAIProvider().generate_text(system_prompt, user_prompt)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                else:
                    logger.error(f"NVIDIA Nemotron API error HTTP {res.status_code}: {res.text}")
            except Exception as e:
                logger.error(f"NVIDIA Nemotron API request failed: {e}")
        return await MockAIProvider().generate_text(system_prompt, user_prompt)

    async def generate_structured(self, system_prompt: str, user_prompt: str, schema_description: str = "") -> Dict[str, Any]:
        if not self.api_key:
            return await MockAIProvider().generate_structured(system_prompt, user_prompt, schema_description)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        formatted_system = (
            f"{system_prompt}\n\n"
            "CRITICAL REQUIREMENT: You MUST respond ONLY with a single valid JSON object strictly conforming to the following structure:\n"
            f"{schema_description}\n"
            "Do NOT include conversational preamble or explanation. Output ONLY the JSON."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": formatted_system},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "top_p": 0.7,
            "max_tokens": 3072,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        return extract_json(content)
                else:
                    logger.error(f"NVIDIA Nemotron API error HTTP {res.status_code}: {res.text}")
            except Exception as e:
                logger.error(f"NVIDIA Nemotron structured generation parsing failed: {e}")
        return await MockAIProvider().generate_structured(system_prompt, user_prompt, schema_description)

def get_ai_provider() -> AIProvider:
    if settings.NVIDIA_API_KEY:
        return NvidiaNemotronAIProvider(
            api_key=settings.NVIDIA_API_KEY,
            base_url=settings.NVIDIA_BASE_URL,
            model=settings.NVIDIA_MODEL
        )
    return MockAIProvider()

ai_provider = get_ai_provider()

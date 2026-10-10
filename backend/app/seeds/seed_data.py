import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.session import AsyncSessionLocal
from app.auth.security import get_password_hash
from app.models.user import User, Profile
from app.models.topic import Topic, Subtopic
from app.models.problem import Problem, ProblemTopic, TestCase, Hint
from app.models.mock import MockTest, MockProblem
from app.models.gamification import Achievement, Streak
from app.models.competition import Competition, Announcement

logger = logging.getLogger("codevita.seed")

async def seed_database_if_empty():
    from app.database.session import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if users exist
        user_check = await db.execute(select(func.count(User.id)))
        if user_check.scalar_one() > 0:
            logger.info("Database already contains data, skipping seed.")
            return

        logger.info("Seeding database with original competitive programming dataset...")

        # 1. Create Default Users (Admin & Demo Student)
        admin = User(
            email="admin@codevita.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin Director",
            role="ADMIN",
            is_active=True,
            is_verified=True,
            xp=2500,
            level=8
        )
        admin_prof = Profile(
            user=admin,
            preferred_language="cpp",
            programming_experience="ADVANCED",
            cp_experience="ADVANCED",
            daily_available_hours=4.0,
            preferred_study_time="MORNING",
            target_competition="TCS CodeVita",
            skill_level="ADVANCED",
            preparation_goal="Manage platform content and assessment benchmarks",
            onboarding_completed=True,
            diagnostic_completed=True
        )
        admin_streak = Streak(user=admin, current_streak=14, longest_streak=30, total_active_days=45)
        db.add_all([admin, admin_prof, admin_streak])

        student = User(
            email="student@codevita.ai",
            hashed_password=get_password_hash("student123"),
            full_name="Alex Kumar",
            role="USER",
            is_active=True,
            is_verified=True,
            xp=150,
            level=2
        )
        student_prof = Profile(
            user=student,
            college="National Institute of Technology",
            graduation_year=2026,
            preferred_language="cpp",
            programming_experience="INTERMEDIATE",
            cp_experience="BEGINNER",
            daily_available_hours=2.5,
            preferred_study_time="EVENING",
            target_competition="TCS CodeVita",
            skill_level="INTERMEDIATE",
            preparation_goal="Qualify for CodeVita Round 2 & Grand Finale",
            onboarding_completed=True,
            diagnostic_completed=False
        )
        student_streak = Streak(user=student, current_streak=3, longest_streak=5, total_active_days=7)
        db.add_all([student, student_prof, student_streak])
        await db.flush()

        # 2. Create Topics & Subtopics
        topics_data = [
            ("Arrays & Vectors", "arrays", "Data Structures", 1, 9, ["Prefix Sums", "Two Pointers", "Sliding Window", "Kadane Algorithm", "Matrix Rotation"]),
            ("Strings & Pattern Matching", "strings", "Data Structures", 2, 8, ["Frequency Maps", "KMP Algorithm", "Z-Algorithm", "Anagrams", "Palindromes"]),
            ("Mathematics & Number Theory", "math", "Fundamentals", 3, 9, ["Modular Arithmetic", "Sieve of Eratosthenes", "GCD & LCM", "Prime Factorization", "Combinatorics"]),
            ("Searching & Sorting", "searching-sorting", "Algorithms", 4, 8, ["Binary Search on Answer", "Custom Comparators", "Merge Sort", "Quick Select"]),
            ("Greedy Algorithms", "greedy", "Algorithms", 5, 8, ["Interval Scheduling", "Fractional Knapsack", "Huffman Coding", "Activity Selection"]),
            ("Recursion & Backtracking", "recursion-backtracking", "Algorithms", 6, 7, ["N-Queens", "Subset Generation", "Permutations", "Sudoku Solver"]),
            ("Stacks & Queues", "stacks-queues", "Data Structures", 7, 7, ["Monotonic Stack", "Next Greater Element", "Deque Window", "Expression Evaluation"]),
            ("Trees & Binary Search Trees", "trees", "Data Structures", 8, 8, ["LCA", "Tree Traversals", "Subtree Queries", "Diameter of Tree"]),
            ("Graphs & Networks", "graphs", "Advanced", 9, 10, ["BFS / DFS", "Dijkstra Shortest Path", "Disjoint Set Union (DSU)", "Kruskal / Prim MST", "Bipartite Check", "Topological Sort"]),
            ("Dynamic Programming", "dynamic-programming", "Advanced", 10, 10, ["1D DP", "0/1 Knapsack", "Longest Common Subsequence", "Matrix Chain DP", "Bitmask DP", "DP on Trees"]),
            ("Bit Manipulation", "bit-manipulation", "Fundamentals", 11, 7, ["Bitwise XOR Tricks", "Bitmasks", "Power Set", "Count Set Bits"]),
            ("Simulation & Optimization", "simulation", "Algorithms", 12, 9, ["State Machine Simulation", "Grid Movements", "Coordinate Geometry", "Constraint Optimization"])
        ]

        topic_entities = {}
        for name, slug, cat, order, imp, subtopics in topics_data:
            t = Topic(
                name=name,
                slug=slug,
                category=cat,
                sort_order=order,
                importance_weight=imp,
                description=f"Master {name} concepts, standard patterns, and edge case techniques for competitive programming assessments."
            )
            db.add(t)
            await db.flush()
            topic_entities[slug] = t

            for s_name in subtopics:
                sub = Subtopic(
                    topic_id=t.id,
                    name=s_name,
                    slug=s_name.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", ""),
                    description=f"Focused subtopic pattern for {s_name}."
                )
                db.add(sub)

        await db.flush()

        # 3. Create Seed Problems (Original problems with tests, hints, editorials)
        problems_seed = [
            # Diagnostic Problems (1 Easy, 1 Medium, 1 Hard)
            {
                "title": "Equilibrium Index Finder",
                "slug": "equilibrium-index-finder",
                "statement": "Given an integer array `arr` of size $N$, find the lowest 0-based index $i$ such that the sum of elements at lower indices equals the sum of elements at higher indices. If no such index exists, return -1.",
                "input_format": "The first line contains an integer $N$ ($1 \\le N \\le 10^5$).\nThe second line contains $N$ space-separated integers $arr[i]$ ($-10^4 \\le arr[i] \\le 10^4$).",
                "output_format": "Print a single integer representing the lowest equilibrium index, or -1 if none exists.",
                "constraints": "1 <= N <= 100000\n-10^4 <= arr[i] <= 10^4",
                "examples": [{"input": "7\n-7 1 5 2 -4 3 0", "output": "3", "explanation": "At index 3: Left sum = -7+1+5 = -1. Right sum = -4+3+0 = -1."}],
                "difficulty": "EASY",
                "difficulty_score": 25,
                "estimated_time": 15,
                "topics": ["arrays"],
                "is_diagnostic": True,
                "editorial": "Compute the total sum first. Then maintain a running left sum as you iterate from index 0 to N-1. The right sum at index $i$ is simply `total_sum - left_sum - arr[i]`. If `left_sum == right_sum`, return $i$. Time complexity: $O(N)$, Space complexity: $O(1)$.",
                "hints": [
                    ("Total Sum Approach", "Can you calculate the sum of all elements in a single initial pass?"),
                    ("Running Sum Balance", "As you iterate through the array, how can you compute right_sum using total_sum and your running left_sum?")
                ],
                "public_tests": [
                    ("7\n-7 1 5 2 -4 3 0", "3"),
                    ("3\n1 2 3", "-1")
                ],
                "hidden_tests": [
                    ("1\n200", "0"),
                    ("5\n1 1 1 1 1", "2"),
                    ("4\n0 0 0 0", "0")
                ]
            },
            {
                "title": "Minimum Energy Path in Grid",
                "slug": "minimum-energy-path-in-grid",
                "statement": "You are given an $R \\times C$ grid where each cell $(r, c)$ contains an integer energy cost. You start at cell $(0, 0)$ and must reach $(R-1, C-1)$. You can only move right or down. Find the minimum total energy required.",
                "input_format": "First line contains two integers $R$ and $C$ ($1 \\le R, C \\le 500$).\nThe next $R$ lines each contain $C$ space-separated integers representing cell costs ($0 \\le cost[r][c] \\le 1000$).",
                "output_format": "Print the minimum energy cost.",
                "constraints": "1 <= R, C <= 500\n0 <= cost[r][c] <= 1000",
                "examples": [{"input": "3 3\n1 3 1\n1 5 1\n4 2 1", "output": "7", "explanation": "Path (0,0)->(0,1)->(0,2)->(1,2)->(2,2) with costs 1 + 3 + 1 + 1 + 1 = 7."}],
                "difficulty": "MEDIUM",
                "difficulty_score": 55,
                "estimated_time": 25,
                "topics": ["dynamic-programming", "arrays"],
                "is_diagnostic": True,
                "editorial": "Define $dp[r][c]$ as the minimum cost to reach cell $(r, c)$. Recurrence: $dp[r][c] = cost[r][c] + \\min(dp[r-1][c], dp[r][c-1])$. Space can be optimized to $O(C)$ using a 1D DP table. Time complexity: $O(R \\times C)$.",
                "hints": [
                    ("State Definition", "Since you can only move right and down, every cell $(r, c)$ can only be entered from $(r-1, c)$ or $(r, c-1)$."),
                    ("Base Cases", "Initialize the first row and first column separately before computing the interior.")
                ],
                "public_tests": [
                    ("3 3\n1 3 1\n1 5 1\n4 2 1", "7")
                ],
                "hidden_tests": [
                    ("2 2\n1 2\n3 4", "7"),
                    ("1 4\n5 10 15 20", "50"),
                    ("3 1\n2\n4\n6", "12")
                ]
            },
            {
                "title": "Network Component Bridges",
                "slug": "network-component-bridges",
                "statement": "Given an undirected connected computer network of $V$ servers and $E$ bidirectional fiber links, find the total number of critical connections (bridges). A critical connection is a link that, when removed, disconnects the network into two or more components.",
                "input_format": "First line contains $V$ and $E$ ($1 \\le V \\le 10^5, 0 \\le E \\le 2 \\times 10^5$).\nThe next $E$ lines each contain two integers $u$ and $v$ ($1 \\le u, v \\le V$), representing a connection between server $u$ and $v$.",
                "output_format": "Print a single integer: the count of critical connections (bridges).",
                "constraints": "1 <= V <= 100000\n0 <= E <= 200000",
                "examples": [{"input": "4 4\n1 2\n2 3\n3 4\n1 3", "output": "1", "explanation": "Link (3, 4) is the only bridge. Removing it isolates server 4."}],
                "difficulty": "HARD",
                "difficulty_score": 85,
                "estimated_time": 40,
                "topics": ["graphs"],
                "is_diagnostic": True,
                "editorial": "Use Tarjan's bridge-finding algorithm via DFS discovery times `tin[u]` and low-link values `low[u]`. A back-edge from $v$ to an ancestor decreases `low[u]`. An edge $(u, v)$ is a bridge if and only if `low[v] > tin[u]`. Time complexity: $O(V + E)$, Space complexity: $O(V + E)$.",
                "hints": [
                    ("DFS Tree Properties", "In a DFS tree of an undirected graph, every non-tree edge is a back-edge."),
                    ("Tarjan's Condition", "Maintain the earliest visited vertex reachable from subtree rooted at $v$. If $low[v] > tin[u]$, no alternative path exists around edge $(u, v)$.")
                ],
                "public_tests": [
                    ("4 4\n1 2\n2 3\n3 4\n1 3", "1")
                ],
                "hidden_tests": [
                    ("5 5\n1 2\n2 3\n3 1\n3 4\n4 5", "2"),
                    ("3 3\n1 2\n2 3\n3 1", "0"),
                    ("2 1\n1 2", "1")
                ]
            },
            # Core Practice Problems
            {
                "title": "Subarray Sum Equals K",
                "slug": "subarray-sum-equals-k",
                "statement": "Given an array of integers `nums` and an integer `k`, return the total number of continuous subarrays whose sum equals `k`.",
                "input_format": "First line contains integers $N$ and $K$ ($1 \\le N \\le 10^5, -10^9 \\le K \\le 10^9$).\nSecond line contains $N$ space-separated integers $nums[i]$ ($-10^4 \\le nums[i] \\le 10^4$).",
                "output_format": "Print the number of matching subarrays.",
                "constraints": "1 <= N <= 100000\n-10^9 <= K <= 10^9\n-10^4 <= nums[i] <= 10^4",
                "examples": [{"input": "3 2\n1 1 1", "output": "2", "explanation": "Subarrays [0..1] and [1..2] each sum to 2."}],
                "difficulty": "MEDIUM",
                "difficulty_score": 50,
                "estimated_time": 25,
                "topics": ["arrays", "searching-sorting"],
                "is_diagnostic": False,
                "editorial": "Use a prefix sum array along with a Hash Map (frequency map) storing occurrences of prefix sums seen so far. At each index $i$, check if `prefix_sum - K` exists in the map. Time complexity: $O(N)$, Space complexity: $O(N)$.",
                "hints": [
                    ("Prefix Difference", "If prefix[j] - prefix[i] == K, then the subarray nums[i+1...j] has sum K."),
                    ("Hash Map Lookup", "Store prefix frequencies in an unordered_map / dict as you iterate.")
                ],
                "public_tests": [
                    ("3 2\n1 1 1", "2"),
                    ("3 3\n1 2 3", "2")
                ],
                "hidden_tests": [
                    ("5 0\n0 0 0 0 0", "15"),
                    ("4 5\n1 2 3 -1", "1"),
                    ("1 10\n10", "1")
                ]
            },
            {
                "title": "Rotated Sorted Array Search",
                "slug": "rotated-sorted-array-search",
                "statement": "An integer array sorted in ascending order was rotated at some unknown pivot. Given the rotated array and a target value, return the 0-based index of target if found, otherwise return -1.",
                "input_format": "First line contains integers $N$ and $target$ ($1 \\le N \\le 10^5$).\nSecond line contains $N$ space-separated unique integers.",
                "output_format": "Print the index of target or -1.",
                "constraints": "1 <= N <= 100000\nAll elements are unique.",
                "examples": [{"input": "7 0\n4 5 6 7 0 1 2", "output": "4", "explanation": "Target 0 is located at index 4."}],
                "difficulty": "MEDIUM",
                "difficulty_score": 55,
                "estimated_time": 25,
                "topics": ["searching-sorting"],
                "is_diagnostic": False,
                "editorial": "Modify Binary Search: in any rotated sorted array, at least one half (left or right) is guaranteed to be strictly sorted. Check if target lies within the sorted half; if so, narrow to that half, otherwise search the other half. Time complexity: $O(\\log N)$.",
                "hints": [
                    ("Half Sorted Invariant", "Compare arr[mid] with arr[low]. If arr[low] <= arr[mid], the left half is sorted."),
                    ("Range Check", "If left half is sorted, target is in left half if and only if arr[low] <= target < arr[mid].")
                ],
                "public_tests": [
                    ("7 0\n4 5 6 7 0 1 2", "4"),
                    ("7 3\n4 5 6 7 0 1 2", "-1")
                ],
                "hidden_tests": [
                    ("1 5\n5", "0"),
                    ("2 3\n3 1", "0"),
                    ("5 4\n5 1 2 3 4", "4")
                ]
            },
            {
                "title": "Longest Palindromic Substring",
                "slug": "longest-palindromic-substring",
                "statement": "Given a string `s`, return the length of the longest palindromic substring in `s`.",
                "input_format": "A single line containing string $s$ ($1 \\le |s| \\le 2000$).",
                "output_format": "Print the length of the longest palindromic substring.",
                "constraints": "1 <= |s| <= 2000\nConsists of lowercase English letters.",
                "examples": [{"input": "babad", "output": "3", "explanation": "\"bab\" or \"aba\" of length 3."}],
                "difficulty": "MEDIUM",
                "difficulty_score": 45,
                "estimated_time": 20,
                "topics": ["strings", "dynamic-programming"],
                "is_diagnostic": False,
                "editorial": "Expand around center: there are $2N - 1$ centers (single character for odd length, between characters for even length). Expand outward while matching. Time: $O(N^2)$, Space: $O(1)$. Alternatively use Manacher's Algorithm for $O(N)$.",
                "hints": [
                    ("Center Expansion", "Consider each index (and pair of adjacent indices) as the potential middle of a palindrome."),
                    ("Odd vs Even", "Remember palindromes can have odd length (centered at character) or even length (centered between two characters).")
                ],
                "public_tests": [
                    ("babad", "3"),
                    ("cbbd", "2")
                ],
                "hidden_tests": [
                    ("a", "1"),
                    ("aaaaa", "5"),
                    ("racecar", "7")
                ]
            },
            {
                "title": "Shortest Route with Tolls",
                "slug": "shortest-route-with-tolls",
                "statement": "Given a weighted directed graph with $N$ cities and $M$ toll roads, find the minimum toll cost to travel from city 1 to city $N$. If city $N$ is unreachable, return -1.",
                "input_format": "First line contains $N$ and $M$ ($2 \\le N \\le 10^5, 1 \\le M \\le 3 \\times 10^5$).\nNext $M$ lines contain $u, v, w$ representing a directed edge from $u$ to $v$ with toll $w$ ($1 \\le w \\le 10^4$).",
                "output_format": "Print the minimum cost or -1.",
                "constraints": "2 <= N <= 100000\n1 <= M <= 300000\n1 <= w <= 10000",
                "examples": [{"input": "4 4\n1 2 5\n2 4 10\n1 3 2\n3 4 4", "output": "6", "explanation": "Route 1 -> 3 -> 4 gives cost 2 + 4 = 6."}],
                "difficulty": "MEDIUM",
                "difficulty_score": 60,
                "estimated_time": 30,
                "topics": ["graphs"],
                "is_diagnostic": False,
                "editorial": "Use Dijkstra's algorithm with a Min-Priority Queue (std::priority_queue in C++ or heapq in Python). Maintain a `dist` array initialized to infinity. Time complexity: $O((N + M) \\log N)$.",
                "hints": [
                    ("Dijkstra Min-Heap", "Since all edge weights are non-negative, Dijkstra's algorithm is optimal."),
                    ("Distance Array", "Store pair (current_dist, node) in min-heap and skip if current_dist > dist[node].")
                ],
                "public_tests": [
                    ("4 4\n1 2 5\n2 4 10\n1 3 2\n3 4 4", "6")
                ],
                "hidden_tests": [
                    ("3 1\n1 2 5", "-1"),
                    ("2 1\n1 2 100", "100"),
                    ("5 6\n1 2 2\n2 3 3\n3 5 4\n1 4 1\n4 5 10\n2 5 8", "9")
                ]
            },
            {
                "title": "Prime Query Factorization",
                "slug": "prime-query-factorization",
                "statement": "Given an integer $N$, find the sum of all its distinct prime factors.",
                "input_format": "A single line containing integer $N$ ($2 \\le N \\le 10^{12}$).",
                "output_format": "Print the sum of distinct prime factors of $N$.",
                "constraints": "2 <= N <= 10^12",
                "examples": [{"input": "60", "output": "10", "explanation": "Prime factors of 60 are 2, 3, and 5. Sum = 2 + 3 + 5 = 10."}],
                "difficulty": "EASY",
                "difficulty_score": 30,
                "estimated_time": 15,
                "topics": ["math"],
                "is_diagnostic": False,
                "editorial": "Trial division up to $\\sqrt{N}$. Check divisibility by 2, then test odd integers up to $\\sqrt{N}$. If remaining $N > 1$ after the loop, that remainder is also a prime factor. Time complexity: $O(\\sqrt{N})$.",
                "hints": [
                    ("Sqrt Bound", "Any composite number $N$ must have at least one prime factor $\\le \\sqrt{N}$."),
                    ("Divide Out Multiples", "When a prime $p$ divides $N$, add $p$ once to the sum and divide $N$ by $p$ until it is no longer divisible.")
                ],
                "public_tests": [
                    ("60", "10"),
                    ("13", "13")
                ],
                "hidden_tests": [
                    ("100", "7"),
                    ("999999999989", "999999999989"),
                    ("84", "12")
                ]
            },
            {
                "title": "Maximum Consecutive Ones Flip",
                "slug": "maximum-consecutive-ones-flip",
                "statement": "Given a binary array `nums` and an integer `k`, return the maximum number of consecutive 1s in the array if you can flip at most `k` 0s to 1s.",
                "input_format": "First line contains $N$ and $K$ ($1 \\le N \\le 10^5, 0 \\le K \\le N$).\nSecond line contains $N$ binary digits (0 or 1).",
                "output_format": "Print the maximum length of consecutive 1s achievable.",
                "constraints": "1 <= N <= 100000\n0 <= K <= N\nnums[i] is either 0 or 1",
                "examples": [{"input": "11 2\n1 1 1 0 0 0 1 1 1 1 0", "output": "6", "explanation": "Flip two 0s at indices 5 and 10 to get 6 consecutive 1s."}],
                "difficulty": "MEDIUM",
                "difficulty_score": 45,
                "estimated_time": 20,
                "topics": ["arrays", "simulation"],
                "is_diagnostic": False,
                "editorial": "Use Sliding Window (Two Pointers). Expand the right pointer and count zeros. When zero count exceeds $K$, advance the left pointer until zero count $\\le K$. Keep track of maximum window size `right - left + 1`. Time: $O(N)$, Space: $O(1)$.",
                "hints": [
                    ("Window Invariant", "Maintain a window [left, right] that contains at most K zeros."),
                    ("Shrink Condition", "When zero_count > K, increment left and decrement zero_count if nums[left] was 0.")
                ],
                "public_tests": [
                    ("11 2\n1 1 1 0 0 0 1 1 1 1 0", "6")
                ],
                "hidden_tests": [
                    ("5 0\n1 1 0 1 1", "2"),
                    ("5 5\n0 0 0 0 0", "5"),
                    ("6 1\n1 0 1 0 1 1", "4")
                ]
            },
            {
                "title": "Task Scheduler with Cooling Time",
                "slug": "task-scheduler-with-cooling-time",
                "statement": "You are given a list of CPU tasks represented by letters A-Z and a non-negative integer cooldown `n`. Each task requires 1 unit of time. Identical tasks must be separated by at least `n` units of cooldown time. Find the minimum total units of time required to complete all tasks.",
                "input_format": "First line contains string of tasks $S$ ($1 \\le |S| \\le 10^5$).\nSecond line contains cooldown integer $n$ ($0 \\le n \\le 100$).",
                "output_format": "Print the minimum units of CPU time.",
                "constraints": "1 <= |S| <= 100000\n0 <= n <= 100",
                "examples": [{"input": "AAABBB\n2", "output": "8", "explanation": "A -> B -> idle -> A -> B -> idle -> A -> B (Total 8 units)."}],
                "difficulty": "HARD",
                "difficulty_score": 75,
                "estimated_time": 35,
                "topics": ["greedy", "math"],
                "is_diagnostic": False,
                "editorial": "Find the maximum task frequency `max_f` and count how many tasks share this maximum frequency `count_max`. The minimum time is determined by greedy slotting: `(max_f - 1) * (n + 1) + count_max`. The answer is $\\max(|S|, \\text{calculated\\_slots})$. Time: $O(|S|)$, Space: $O(1)$ (26 uppercase letters).",
                "hints": [
                    ("Max Frequency Anchor", "The most frequent task creates the most constrained idle slots."),
                    ("Formula", "Calculate available slots between the highest frequency tasks.")
                ],
                "public_tests": [
                    ("AAABBB\n2", "8")
                ],
                "hidden_tests": [
                    ("AAABBB\n0", "6"),
                    ("AAAAA\n2", "13"),
                    ("ABCDE\n2", "5")
                ]
            }
        ]

        problem_objects = []
        for p_data in problems_seed:
            p = Problem(
                title=p_data["title"],
                slug=p_data["slug"],
                statement=p_data["statement"],
                input_format=p_data["input_format"],
                output_format=p_data["output_format"],
                constraints=p_data["constraints"],
                examples=p_data["examples"],
                difficulty=p_data["difficulty"],
                difficulty_score=p_data["difficulty_score"],
                estimated_time_minutes=p_data["estimated_time"],
                supported_languages=["cpp", "python", "java", "c"],
                time_limit_seconds=2.0,
                memory_limit_mb=256,
                editorial=p_data["editorial"],
                source_type="ORIGINAL",
                is_diagnostic=p_data["is_diagnostic"],
                is_active=True
            )
            db.add(p)
            await db.flush()
            problem_objects.append(p)

            # Associate topics
            for t_slug in p_data["topics"]:
                if t_slug in topic_entities:
                    pt = ProblemTopic(problem_id=p.id, topic_id=topic_entities[t_slug].id, is_primary=True)
                    db.add(pt)

            # Add hints
            for h_idx, (h_title, h_body) in enumerate(p_data["hints"], start=1):
                hint_ent = Hint(problem_id=p.id, order_index=h_idx, title=h_title, content=h_body)
                db.add(hint_ent)

            # Add public test cases
            for tc_idx, (inp, out) in enumerate(p_data["public_tests"], start=1):
                tc = TestCase(problem_id=p.id, input_data=inp, expected_output=out, is_hidden=False, order_index=tc_idx)
                db.add(tc)

            # Add hidden test cases
            for tc_idx, (inp, out) in enumerate(p_data["hidden_tests"], start=len(p_data["public_tests"]) + 1):
                tc = TestCase(problem_id=p.id, input_data=inp, expected_output=out, is_hidden=True, order_index=tc_idx)
                db.add(tc)

        await db.flush()

        # 4. Create Mock Tests (Quick, Topic, Mini, Full CodeVita Simulation)
        full_mock = MockTest(
            title="CodeVita Season 14 Grand Simulation 1",
            slug="codevita-season-14-simulation-1",
            description="6-Hour full exam simulation modeled after TCS CodeVita Round 1 format with 6 original problems of escalating algorithmic complexity.",
            mock_type="FULL",
            duration_minutes=360,
            total_questions=6,
            difficulty_distribution={"EASY": 2, "MEDIUM": 3, "HARD": 1},
            scoring_rules={"type": "codevita_relative", "penalty": 0},
            allowed_languages=["cpp", "python", "java", "c"],
            is_active=True
        )
        db.add(full_mock)
        await db.flush()

        # Link problems to full mock
        for idx, p in enumerate(problem_objects[:6], start=1):
            mp = MockProblem(mock_test_id=full_mock.id, problem_id=p.id, order_index=idx, marks=100)
            db.add(mp)

        mini_mock = MockTest(
            title="Speed Sprint Mini Mock (90 Min)",
            slug="speed-sprint-mini-mock",
            description="Intense 90-minute 3-problem mock test designed to sharpen time management under strict pressure.",
            mock_type="MINI",
            duration_minutes=90,
            total_questions=3,
            difficulty_distribution={"EASY": 1, "MEDIUM": 2},
            scoring_rules={"type": "standard_cp"},
            allowed_languages=["cpp", "python", "java", "c"],
            is_active=True
        )
        db.add(mini_mock)
        await db.flush()

        for idx, p in enumerate(problem_objects[3:6], start=1):
            mp = MockProblem(mock_test_id=mini_mock.id, problem_id=p.id, order_index=idx, marks=100)
            db.add(mp)

        quick_mock = MockTest(
            title="Daily Algorithmic Blitz (30 Min)",
            slug="daily-algorithmic-blitz",
            description="Quick 30-minute 2-problem sprint focusing on rapid pattern recognition and zero-bug implementation.",
            mock_type="QUICK",
            duration_minutes=30,
            total_questions=2,
            difficulty_distribution={"EASY": 1, "MEDIUM": 1},
            scoring_rules={"type": "speed_accuracy"},
            allowed_languages=["cpp", "python", "java", "c"],
            is_active=True
        )
        db.add(quick_mock)
        await db.flush()

        for idx, p in enumerate(problem_objects[0:2], start=1):
            mp = MockProblem(mock_test_id=quick_mock.id, problem_id=p.id, order_index=idx, marks=100)
            db.add(mp)

        # 5. Create Competitions Config
        codevita_comp = Competition(
            name="TCS CodeVita",
            season="Season 14",
            year=2026,
            description="The world's largest competitive programming contest for engineering and science graduates, offering global prestige and top tech career opportunities.",
            official_url="https://codevita.tcsapps.com",
            duration_minutes=360,
            num_rounds=3,
            eligibility="Undergraduate and Postgraduate students across recognized universities graduating in 2026-2028.",
            rules=[
                "Allowed languages: C, C++, Java, Python 3.",
                "Strict process isolation and code plagiarism screening.",
                "Leaderboards ranked primarily by number of accepted problems, then total elapsed penalty time."
            ],
            allowed_languages=["C", "C++", "Java", "Python"],
            is_active=True
        )
        db.add(codevita_comp)

        # 6. Create Announcements
        ann1 = Announcement(
            title="CodeVita Season 14 Prep Tracks Released",
            content="Welcome to CodeVita AI Coach! Begin by taking the 15-minute Diagnostic Assessment to unlock your adaptive daily study plan.",
            type="EXAM_UPDATE",
            is_pinned=True,
            is_active=True
        )
        ann2 = Announcement(
            title="New Graph & Dynamic Programming Problems Added",
            content="50+ original algorithmic challenges have been added to the Practice Arena, complete with hints and AI code review.",
            type="NEW_PROBLEMS",
            is_pinned=False,
            is_active=True
        )
        db.add_all([ann1, ann2])

        # 7. Create Gamification Achievements
        achievements_data = [
            ("FIRST_SOLVE", "First Breakthrough", "Solve your first competitive programming problem.", "Award", 50, "SOLVING", "SOLVE_COUNT", 1),
            ("FIVE_SOLVES", "Pace Setter", "Solve 5 distinct algorithmic problems.", "Zap", 100, "SOLVING", "SOLVE_COUNT", 5),
            ("TEN_SOLVES", "Code Crusher", "Solve 10 distinct algorithmic problems.", "Flame", 200, "SOLVING", "SOLVE_COUNT", 10),
            ("FIRST_MOCK", "Test Tested", "Complete your first timed Mock Exam simulation.", "ShieldCheck", 150, "MOCKS", "MOCK_COUNT", 1),
            ("THREE_MOCKS", "Simulation Veteran", "Complete 3 full or mini Mock Exams.", "Trophy", 300, "MOCKS", "MOCK_COUNT", 3),
            ("STREAK_3", "Habit Builder", "Maintain a 3-day continuous practice streak.", "Flame", 100, "STREAKS", "STREAK_DAYS", 3),
            ("STREAK_7", "Unstoppable Momentum", "Maintain a 7-day continuous practice streak.", "Crown", 300, "STREAKS", "STREAK_DAYS", 7),
        ]

        for code, title, desc, icon, xp, cat, cond_t, cond_v in achievements_data:
            ach = Achievement(
                code=code,
                title=title,
                description=desc,
                icon=icon,
                xp_reward=xp,
                category=cat,
                condition_type=cond_t,
                condition_value=cond_v
            )
            db.add(ach)

        await db.commit()
        logger.info("Database seeding completed successfully.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database_if_empty())

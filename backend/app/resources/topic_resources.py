from typing import Dict, Any, Optional, List

TOPIC_RESOURCES: Dict[str, Dict[str, Any]] = {
    "graphs": {
        "title": "Graphs & Grid Traversals (BFS, DFS, Dijkstra, 0-1 BFS)",
        "overview": (
            "Graphs represent interconnected states, networks, and grid matrices. In CodeVita, graph problems frequently "
            "appear as 2D grid pathfinding, unweighted shortest paths, component counting, or state transition networks. "
            "Choosing the right traversal pattern is essential for staying within the 1.0s–2.0s execution time limit."
        ),
        "time_complexity": "O(V + E) for BFS/DFS; O((V + E) log V) for Dijkstra; O(V + E) for 0-1 BFS",
        "space_complexity": "O(V) for visited array & state queue",
        "key_invariants": [
            "BFS Guarantees Shortest Path: In unweighted graphs or 2D grids with uniform movement cost (1 step), BFS visiting node X for the first time gives the exact minimum distance.",
            "0-1 BFS with Deque: If edge weights are exclusively 0 or 1, use std::deque. Push 0-weight edges to front and 1-weight to back for O(V + E) shortest path.",
            "State Relaxation: In Dijkstra, only push to priority queue if new_dist < dist[neighbor].",
            "Multi-source BFS: Initialize the queue with ALL starting nodes at distance 0 simultaneously to find shortest distance to any source."
        ],
        "code_template": """// Fast C++ Grid BFS Template
#include <iostream>
#include <vector>
#include <queue>
using namespace std;

const int dx[4] = {-1, 1, 0, 0};
const int dy[4] = {0, 0, -1, 1};

int bfs(int R, int C, pair<int,int> start, pair<int,int> target, const vector<vector<int>>& grid) {
    vector<vector<int>> dist(R, vector<int>(C, -1));
    queue<pair<int,int>> q;

    q.push(start);
    dist[start.first][start.second] = 0;

    while (!q.empty()) {
        auto [r, c] = q.front();
        q.pop();

        if (r == target.first && c == target.second) return dist[r][c];

        for (int i = 0; i < 4; i++) {
            int nr = r + dx[i], nc = c + dy[i];
            if (nr >= 0 && nr < R && nc >= 0 && nc < C && grid[nr][nc] == 0 && dist[nr][nc] == -1) {
                dist[nr][nc] = dist[r][c] + 1;
                q.push({nr, nc});
            }
        }
    }
    return -1; // Unreachable
}""",
        "pitfalls": [
            "Boundary Check Order: Always check 0 <= nr < R && 0 <= nc < C BEFORE indexing into grid[nr][nc] to prevent SegFault.",
            "Mark Visited on Push: Mark nodes as visited immediately when pushing to the queue, NOT when popping, to prevent exponential duplicate queue entries.",
            "Disconnected Components: Always loop over all 1 <= i <= V to process disconnected nodes."
        ]
    },
    "dynamic programming": {
        "title": "Dynamic Programming (State Transitions, Knapsack & Subsequence)",
        "overview": (
            "Dynamic Programming solves optimization problems by breaking them into overlapping subproblems with optimal substructure. "
            "In CodeVita, DP is prominent in Medium and Hard questions involving constrained selection (Knapsack variants), string edits (LCS), "
            "and grid cost minimization."
        ),
        "time_complexity": "O(N * W) for Knapsack; O(N^2) for Matrix / LCS / LIS; O(N log N) for binary-search optimized LIS",
        "space_complexity": "O(W) using 1D rolling array space reduction",
        "key_invariants": [
            "State Representation: dp[i][w] = optimal value considering first i items with remaining capacity w.",
            "Subproblem Transition: dp[i][w] = max(dp[i-1][w], val[i] + dp[i-1][w - weight[i]]).",
            "1D Space Optimization: When optimizing 0/1 Knapsack to 1D array dp[w], traverse capacity BACKWARDS from W down to weight[i] to ensure each item is used at most once.",
            "Unbounded Knapsack: Traverse capacity FORWARDS from weight[i] to W if items can be reused infinitely."
        ],
        "code_template": """// Space-Optimized 0/1 Knapsack (C++)
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

long long knapsack(int W, const vector<int>& weights, const vector<long long>& values) {
    int n = weights.size();
    vector<long long> dp(W + 1, 0);

    for (int i = 0; i < n; i++) {
        for (int w = W; w >= weights[i]; w--) {
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]]);
        }
    }
    return dp[W];
}""",
        "pitfalls": [
            "Integer Overflow: Accumulating large values in DP table can exceed 2*10^9. Always use long long for dp arrays.",
            "Base Case Setup: For minimization problems (e.g. Coin Change), initialize dp array with a safe infinity (1e18 or 1e9), NOT INT_MAX to avoid addition overflow.",
            "Negative Weights: Standard array indexing fails on negative states. Offset indices by +offset if negative sums are possible."
        ]
    },
    "binary search": {
        "title": "Binary Search on Answer & Monotonic Feasibility",
        "overview": (
            "Binary Search extends far beyond finding keys in sorted arrays. In competitive programming, it is primarily used "
            "for 'Binary Search on the Answer Space' — optimizing a metric (e.g., minimum maximum capacity, maximum throughput) "
            "when a monotonic boolean predicate isValid(X) can be evaluated in O(N) time."
        ),
        "time_complexity": "O(N * log(search_space_range))",
        "space_complexity": "O(1) auxiliary space",
        "key_invariants": [
            "Monotonicity Property: If predicate isValid(K) is true for K, then it is guaranteed true for all K' >= K (or vice versa).",
            "Search Space Bounds: Set low = min possible answer, high = max possible answer (often sum of array or 10^18).",
            "Safe Mid Calculation: Use mid = low + (high - low) / 2 to eliminate 32-bit integer overflow.",
            "Optimal Feasibility: The predicate function isValid(mid) typically runs a Greedy single-pass in O(N) time."
        ],
        "code_template": """// Binary Search on Answer Space (C++)
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
using namespace std;

bool isValid(long long mid, int k, const vector<int>& nums) {
    int count = 1;
    long long current_sum = 0;
    for (int x : nums) {
        if (x > mid) return false;
        if (current_sum + x > mid) {
            count++;
            current_sum = x;
        } else {
            current_sum += x;
        }
    }
    return count <= k;
}

long long binarySearchAnswer(int k, const vector<int>& nums) {
    long long low = *max_element(nums.begin(), nums.end());
    long long high = accumulate(nums.begin(), nums.end(), 0LL);
    long long ans = high;

    while (low <= high) {
        long long mid = low + (high - low) / 2;
        if (isValid(mid, k, nums)) {
            ans = mid;
            high = mid - 1; // Seek smaller maximum
        } else {
            low = mid + 1;
        }
    }
    return ans;
}""",
        "pitfalls": [
            "Lower Bound Misconfiguration: Setting low = 0 when single element nums[i] > 0 will cause isValid to loop improperly.",
            "Off-by-One Infinite Loops: Ensure while condition is low <= high with high = mid - 1 and low = mid + 1.",
            "Precision in Floating Point BS: When binary searching floats, run for fixed 80-100 iterations (for (int iter = 0; iter < 80; iter++)) instead of while (high - low > eps)."
        ]
    },
    "arrays": {
        "title": "Arrays, Two Pointers, Sliding Window & Prefix Transforms",
        "overview": (
            "Arrays are the foundational data structure of competitive programming. Mastering Two Pointers, Sliding Window, "
            "and Prefix Sum / Difference Array techniques allows transforming O(N^2) brute force algorithms into optimal O(N) single-pass solutions."
        ),
        "time_complexity": "O(N) for Two Pointers / Sliding Window / Prefix Sums",
        "space_complexity": "O(1) for Two Pointers; O(N) for Prefix Arrays",
        "key_invariants": [
            "Two Pointers on Sorted Data: Left and right pointers converge inward based on comparison with target sum in O(N).",
            "Sliding Window (Variable Size): Expand right pointer to include elements; shrink left pointer while window condition is violated.",
            "Prefix Sum Range Queries: sum(L, R) = prefix[R] - prefix[L - 1] in O(1) query time.",
            "Difference Array: Add +V at index L and -V at index R + 1 to perform multiple range update operations in O(1) each."
        ],
        "code_template": """// Variable Sliding Window Template (C++)
#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

int longestSubarrayWithKDistinct(const vector<int>& a, int k) {
    unordered_map<int, int> freq;
    int left = 0, max_len = 0;

    for (int right = 0; right < (int)a.size(); right++) {
        freq[a[right]]++;

        while ((int)freq.size() > k) {
            freq[a[left]]--;
            if (freq[a[left]] == 0) freq.erase(a[left]);
            left++;
        }

        max_len = max(max_len, right - left + 1);
    }
    return max_len;
}""",
        "pitfalls": [
            "Map Lookup Overhead: Using std::map (Red-Black tree, O(log N)) inside sliding window can cause TLE. Use std::unordered_map (O(1) average) or flat frequency vector if values are small.",
            "1-based Prefix Indices: Always allocate prefix array with size N + 1 and prefix[0] = 0 to avoid checking L == 0."
        ]
    },
    "trees": {
        "title": "Trees, Disjoint Set Union (DSU) & Minimum Spanning Trees",
        "overview": (
            "Trees represent hierarchical acyclic graphs with V nodes and V - 1 edges. DSU (Union-Find) enables dynamic "
            "connectivity checks and Kruskal's Minimum Spanning Tree algorithm in near-constant inverse Ackermann O(alpha(N)) time."
        ),
        "time_complexity": "O(N) for Tree DFS/BFS; O(E log E) for Kruskal's MST; O(alpha(N)) per DSU operation",
        "space_complexity": "O(N) for parent and rank arrays",
        "key_invariants": [
            "DSU Path Compression: parent[i] = find(parent[i]) flattens tree structure to O(1) amortized depth.",
            "Union by Rank: Attach smaller tree root under larger tree root to prevent degenerate linked-list trees.",
            "Tree Diameter Invariant: Run BFS/DFS from arbitrary node A to find furthest node B; run second BFS/DFS from B to find furthest node C. Distance(B, C) is the exact tree diameter."
        ],
        "code_template": """// Disjoint Set Union (DSU) with Path Compression & Rank (C++)
#include <vector>
#include <numeric>
using namespace std;

struct DSU {
    vector<int> parent, rank;
    DSU(int n) {
        parent.resize(n + 1);
        iota(parent.begin(), parent.end(), 0);
        rank.assign(n + 1, 0);
    }
    int find(int i) {
        if (parent[i] == i) return i;
        return parent[i] = find(parent[i]); // Path compression
    }
    bool unite(int i, int j) {
        int root_i = find(i), root_j = find(j);
        if (root_i == root_j) return false;
        if (rank[root_i] < rank[root_j]) swap(root_i, root_j);
        parent[root_j] = root_i;
        if (rank[root_i] == rank[root_j]) rank[root_i]++;
        return true;
    }
};""",
        "pitfalls": [
            "1-based vs 0-based DSU Size: Allocate DSU arrays with size N + 1 to support 1-based indexing without index shifts.",
            "Kruskal Sorting: Remember to sort edges by weight ascending before iterating through DSU unite."
        ]
    },
    "math": {
        "title": "Number Theory, Modular Arithmetic & Combinatorics",
        "overview": (
            "CodeVita problems often require results modulo 10^9+7 or finding primes/factors up to 10^12. "
            "Modular arithmetic, Fast Exponentiation (Binary Exponentiation), Sieve of Eratosthenes, and GCD/LCM are standard toolsets."
        ),
        "time_complexity": "O(log B) for (A^B)%MOD; O(N log log N) for Sieve up to N; O(log(min(A,B))) for GCD",
        "space_complexity": "O(N) for prime sieve boolean vector",
        "key_invariants": [
            "Modular Subtraction Guard: (A - B) % MOD can be negative in C++. Always compute ((A - B) % MOD + MOD) % MOD.",
            "Fermat's Little Theorem: If MOD is prime, modular inverse of A is (A^(MOD-2)) % MOD.",
            "Fast Power: Compute A^B by squaring base when B is even and multiplying when B is odd in O(log B)."
        ],
        "code_template": """// Fast Power & Modular Inverse (C++)
#include <iostream>
using namespace std;

const long long MOD = 1e9 + 7;

long long power(long long base, long long exp) {
    long long res = 1;
    base %= MOD;
    while (exp > 0) {
        if (exp % 2 == 1) res = (__int128)res * base % MOD;
        base = (__int128)base * base % MOD;
        exp /= 2;
    }
    return res;
}

long long modInverse(long long n) {
    return power(n, MOD - 2);
}""",
        "pitfalls": [
            "Intermediate Product Overflow: (A * B) % MOD overflows 32-bit int if A, B ~ 10^9. Cast to (1LL * A * B) or __int128.",
            "Division under Modulo: Never write (A / B) % MOD. Must write (A * modInverse(B)) % MOD."
        ]
    }
}

def get_topic_resource(topic_name: Optional[str], subtopic_name: Optional[str] = "", task_type: str = "PRACTICE") -> Dict[str, Any]:
    key = (topic_name or "").lower()
    
    # Map synonyms to known resource keys
    matched_key = "graphs"
    if "dp" in key or "dynamic" in key or "knapsack" in key or "subsequence" in key:
        matched_key = "dynamic programming"
    elif "graph" in key or "bfs" in key or "dfs" in key or "dijkstra" in key or "network" in key:
        matched_key = "graphs"
    elif "binary search" in key or "search" in key or "monotonic" in key:
        matched_key = "binary search"
    elif "array" in key or "two pointer" in key or "sliding window" in key or "prefix" in key or "hash" in key:
        matched_key = "arrays"
    elif "tree" in key or "dsu" in key or "disjoint" in key or "mst" in key:
        matched_key = "trees"
    elif "math" in key or "number" in key or "prime" in key or "modulo" in key:
        matched_key = "math"

    res = TOPIC_RESOURCES.get(matched_key, TOPIC_RESOURCES["graphs"]).copy()

    # Custom title if subtopic is given
    if subtopic_name:
        res["subtopic_focus"] = subtopic_name
        res["title"] = f"{subtopic_name} — {res['title']}"

    res["task_type"] = task_type
    return res

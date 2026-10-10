# CodeVita AI Coach — Code Execution Engine

## 1. Security Threat Model
In a competitive programming environment, submitted code is treated as potentially hostile:
- Potential fork bombs, thread exhaustion, infinite loops, and heavy disk I/O.
- Attempts to probe filesystem, environment variables, network sockets, or root access.

---

## 2. Sandbox Defense-in-Depth Architecture
The execution pipeline follows a multi-tier sandbox model:

```
FastAPI Server
  ↓
Temporary Directory Isolation (mkdtemp per execution)
  ↓
Process Subprocess Isolation (asyncio.create_subprocess_exec)
  ↓
Strict Resource & Wall-Clock Limits
  - CPU / Execution Timeout: 2.0s - 3.0s (asyncio.wait_for)
  - Memory Limit: 256MB cap
  - Output Char Truncation: 64KB max buffer
  - Unbuffered I/O (python -u)
  ↓
Automatic Directory Teardown & Process Killing (SIGKILL on timeout)
```

---

## 3. Supported Compilers & Interpreters
- **C++**: `g++ -O2 -std=c++17 solution.cpp -o solution`
- **Python**: `python3 -u solution.py`
- **Java**: `javac Solution.java` followed by `java -Xmx256m Solution`
- **C**: `gcc -O2 solution.c -o solution`

---

## 4. Evaluation Outcome Matrix
- `PASSED`: Standard output strictly matches expected output (normalized whitespace/newlines).
- `WRONG_ANSWER`: Standard output differs from expected output.
- `TIME_LIMIT_EXCEEDED`: Subprocess exceeded allowable wall-clock limit.
- `COMPILATION_ERROR`: Compiler emitted non-zero status code with compiler diagnostics.
- `RUNTIME_ERROR`: Process raised uncaught exception or non-zero exit code.

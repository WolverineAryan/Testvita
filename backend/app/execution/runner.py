import os
import sys
import re
import tempfile
import asyncio
import time
import shutil
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import httpx
from app.config.settings import settings

@dataclass
class ExecutionResultData:
    status: str  # SUCCESS, WRONG_ANSWER, TIME_LIMIT_EXCEEDED, COMPILATION_ERROR, RUNTIME_ERROR, SYSTEM_ERROR
    stdout: str
    stderr: str
    compiler_output: str
    execution_time_ms: float
    memory_kb: int
    test_case_id: Optional[str] = None
    order_index: int = 0
    is_hidden: bool = False
    input_data: Optional[str] = None
    expected_output: Optional[str] = None

# Judge0 language ID mappings
JUDGE0_LANG_MAP: Dict[str, int] = {
    "cpp": 105,       # C++ (GCC 14.1.0)
    "c++": 105,
    "c": 103,         # C (GCC 14.1.0)
    "python": 100,    # Python (3.12.5)
    "py": 100,
    "python3": 100,
    "java": 91,       # Java (JDK 17.0.6)
}

# Wandbox compiler mappings
WANDBOX_LANG_MAP: Dict[str, str] = {
    "cpp": "gcc-13.2.0",
    "c++": "gcc-13.2.0",
    "c": "gcc-13.2.0-c",
    "python": "cpython-3.12.7",
    "py": "cpython-3.12.7",
    "python3": "cpython-3.12.7",
    "java": "openjdk-jdk-21+35",
}

def find_cpp_compiler() -> Optional[str]:
    for cmd in ["g++", "clang++", "gcc"]:
        p = shutil.which(cmd)
        if p:
            return p
    if os.name == "nt":
        candidates = [
            r"C:\msys64\ucrt64\bin\g++.exe",
            r"C:\msys64\mingw64\bin\g++.exe",
            r"C:\MinGW\bin\g++.exe",
            r"C:\Program Files\LLVM\bin\clang++.exe",
            r"C:\TDM-GCC-64\bin\g++.exe",
            r"C:\mingw64\bin\g++.exe"
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None

def find_c_compiler() -> Optional[str]:
    for cmd in ["gcc", "clang", "g++"]:
        p = shutil.which(cmd)
        if p:
            return p
    if os.name == "nt":
        candidates = [
            r"C:\msys64\ucrt64\bin\gcc.exe",
            r"C:\msys64\mingw64\bin\gcc.exe",
            r"C:\MinGW\bin\gcc.exe",
            r"C:\Program Files\LLVM\bin\clang.exe",
            r"C:\mingw64\bin\gcc.exe"
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None

class CodeExecutionEngine:
    def __init__(
        self,
        timeout_seconds: float = settings.EXECUTION_TIMEOUT_SECONDS,
        max_output_chars: int = settings.EXECUTION_MAX_OUTPUT_CHARS,
        execution_mode: str = settings.EXECUTION_MODE
    ):
        self.timeout_seconds = timeout_seconds
        self.max_output_chars = max_output_chars
        self.execution_mode = execution_mode.lower()

    async def execute_code(
        self,
        language: str,
        code: str,
        input_data: str = "",
        timeout_seconds: Optional[float] = None
    ) -> ExecutionResultData:
        timeout = timeout_seconds or self.timeout_seconds
        lang = language.lower().strip()

        # Cloud execution mode is preferred for multi-language support on any host
        if self.execution_mode in ["cloud", "auto"]:
            cloud_res = await self._run_cloud_judge0(lang, code, input_data, timeout)
            if cloud_res is not None:
                return cloud_res
            
            # Fallback to Wandbox cloud compiler if Judge0 failed or timed out
            wandbox_res = await self._run_cloud_wandbox(lang, code, input_data, timeout)
            if wandbox_res is not None:
                return wandbox_res

        # Fallback to local subprocess execution
        return await self._run_local(lang, code, input_data, timeout)

    async def _run_cloud_judge0(
        self,
        lang: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> Optional[ExecutionResultData]:
        """Execute code via Judge0 CE API"""
        lang_id = JUDGE0_LANG_MAP.get(lang)
        if not lang_id:
            return None

        # Normalize Java class declaration so user code with class Solution compiles cleanly
        formatted_code = code
        if lang == "java":
            formatted_code = re.sub(r'public\s+class\s+[A-Za-z0-9_]+', 'public class Main', code, count=1)

        # Ensure sufficient time limit for interpreted / VM languages in sandbox
        if lang in ["python", "py", "python3", "java"]:
            cpu_limit = max(timeout * 2.0, 5.0)
        else:
            cpu_limit = max(timeout, 2.0)

        url = f"{settings.JUDGE0_API_URL.rstrip('/')}/submissions?base64_encoded=false&wait=true"
        payload = {
            "source_code": formatted_code,
            "language_id": lang_id,
            "stdin": input_data,
            "cpu_time_limit": min(cpu_limit, 10.0),
            "memory_limit": 262144,  # 256MB in KB
        }

        try:
            async with httpx.AsyncClient(timeout=max(cpu_limit + 5.0, 15.0)) as client:
                res = await client.post(url, json=payload)
                if res.status_code not in (200, 201):
                    return None
                data = res.json()

            status_obj = data.get("status", {})
            status_id = status_obj.get("id", 0)
            status_desc = status_obj.get("description", "")

            # Parsing metrics
            raw_time = data.get("time")
            exec_time_ms = round(float(raw_time) * 1000.0, 2) if raw_time else 0.0
            memory_kb = data.get("memory") or 0

            stdout = (data.get("stdout") or "")[:self.max_output_chars]
            stderr = (data.get("stderr") or "")[:self.max_output_chars]
            compile_output = (data.get("compile_output") or "")[:self.max_output_chars]
            message = data.get("message") or ""

            # Status 3: Accepted / Executed successfully
            if status_id == 3:
                return ExecutionResultData(
                    status="SUCCESS",
                    stdout=stdout,
                    stderr=stderr,
                    compiler_output="",
                    execution_time_ms=exec_time_ms,
                    memory_kb=memory_kb
                )
            
            # Status 5: Time Limit Exceeded
            elif status_id == 5:
                return ExecutionResultData(
                    status="TIME_LIMIT_EXCEEDED",
                    stdout=stdout,
                    stderr=f"Time limit of {timeout}s exceeded.",
                    compiler_output="",
                    execution_time_ms=round(timeout * 1000.0, 2),
                    memory_kb=memory_kb
                )
            
            # Status 6: Compilation Error
            elif status_id == 6:
                return ExecutionResultData(
                    status="COMPILATION_ERROR",
                    stdout="",
                    stderr="",
                    compiler_output=compile_output or stderr or status_desc,
                    execution_time_ms=0.0,
                    memory_kb=0
                )
            
            # Status 7-12: Runtime Errors
            elif status_id in (7, 8, 9, 10, 11, 12):
                combined_err = (stderr + "\n" + message).strip() if message else stderr
                return ExecutionResultData(
                    status="RUNTIME_ERROR",
                    stdout=stdout,
                    stderr=combined_err or status_desc,
                    compiler_output="",
                    execution_time_ms=exec_time_ms,
                    memory_kb=memory_kb
                )
            
            # Other statuses
            else:
                return ExecutionResultData(
                    status="SUCCESS" if stdout else "RUNTIME_ERROR",
                    stdout=stdout,
                    stderr=stderr or message,
                    compiler_output=compile_output,
                    execution_time_ms=exec_time_ms,
                    memory_kb=memory_kb
                )

        except Exception:
            return None

    async def _run_cloud_wandbox(
        self,
        lang: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> Optional[ExecutionResultData]:
        """Secondary fallback compiler via Wandbox API"""
        compiler_name = WANDBOX_LANG_MAP.get(lang)
        if not compiler_name:
            return None

        url = settings.WANDBOX_API_URL
        payload = {
            "compiler": compiler_name,
            "code": code,
            "stdin": input_data
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=timeout + 5.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    return None
                data = res.json()

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            comp_error = data.get("compiler_error") or ""
            prog_error = data.get("program_error") or ""
            prog_output = data.get("program_output") or ""
            exit_status = data.get("status")

            if comp_error:
                return ExecutionResultData(
                    status="COMPILATION_ERROR",
                    stdout="",
                    stderr="",
                    compiler_output=comp_error[:self.max_output_chars],
                    execution_time_ms=0.0,
                    memory_kb=0
                )
            elif exit_status != 0 and (prog_error or exit_status is not None):
                return ExecutionResultData(
                    status="RUNTIME_ERROR",
                    stdout=prog_output[:self.max_output_chars],
                    stderr=prog_error[:self.max_output_chars],
                    compiler_output="",
                    execution_time_ms=round(elapsed_ms, 2),
                    memory_kb=16384
                )
            else:
                return ExecutionResultData(
                    status="SUCCESS",
                    stdout=prog_output[:self.max_output_chars],
                    stderr="",
                    compiler_output="",
                    execution_time_ms=round(elapsed_ms, 2),
                    memory_kb=16384
                )
        except Exception:
            return None

    async def _run_local(
        self,
        lang: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> ExecutionResultData:
        temp_dir = tempfile.mkdtemp(prefix="codevita_local_")
        try:
            if lang in ["python", "py", "python3"]:
                return await self._run_python_local(temp_dir, code, input_data, timeout)
            elif lang in ["cpp", "c++"]:
                return await self._run_cpp_local(temp_dir, code, input_data, timeout)
            elif lang in ["c"]:
                return await self._run_c_local(temp_dir, code, input_data, timeout)
            elif lang in ["java"]:
                return await self._run_java_local(temp_dir, code, input_data, timeout)
            else:
                return ExecutionResultData(
                    status="SYSTEM_ERROR",
                    stdout="",
                    stderr=f"Unsupported language: {lang}",
                    compiler_output="",
                    execution_time_ms=0.0,
                    memory_kb=0
                )
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    async def _run_python_local(
        self,
        temp_dir: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> ExecutionResultData:
        file_path = os.path.join(temp_dir, "solution.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        python_exec = sys.executable
        start_time = time.perf_counter()
        
        try:
            process = await asyncio.create_subprocess_exec(
                python_exec,
                "-u",
                file_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(input=input_data.encode("utf-8")),
                    timeout=timeout
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                stdout_str = stdout_data.decode("utf-8", errors="replace")[:self.max_output_chars]
                stderr_str = stderr_data.decode("utf-8", errors="replace")[:self.max_output_chars]

                if process.returncode != 0:
                    return ExecutionResultData(
                        status="RUNTIME_ERROR",
                        stdout=stdout_str,
                        stderr=stderr_str,
                        compiler_output="",
                        execution_time_ms=round(elapsed_ms, 2),
                        memory_kb=15360
                    )

                return ExecutionResultData(
                    status="SUCCESS",
                    stdout=stdout_str,
                    stderr=stderr_str,
                    compiler_output="",
                    execution_time_ms=round(elapsed_ms, 2),
                    memory_kb=15360
                )

            except asyncio.TimeoutError:
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
                return ExecutionResultData(
                    status="TIME_LIMIT_EXCEEDED",
                    stdout="",
                    stderr=f"Time limit of {timeout}s exceeded.",
                    compiler_output="",
                    execution_time_ms=round(timeout * 1000.0, 2),
                    memory_kb=0
                )
        except Exception as e:
            return ExecutionResultData(
                status="SYSTEM_ERROR",
                stdout="",
                stderr=str(e),
                compiler_output="",
                execution_time_ms=0.0,
                memory_kb=0
            )

    async def _run_cpp_local(
        self,
        temp_dir: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> ExecutionResultData:
        source_path = os.path.join(temp_dir, "solution.cpp")
        exe_name = "solution.exe" if os.name == "nt" else "solution"
        exe_path = os.path.join(temp_dir, exe_name)

        with open(source_path, "w", encoding="utf-8") as f:
            f.write(code)

        compiler = find_cpp_compiler()
        if not compiler:
            return ExecutionResultData(
                status="COMPILATION_ERROR",
                stdout="",
                stderr="C++ Compiler (g++) is not installed on the host operating system.",
                compiler_output="Host environment missing C++ compiler (g++ / MinGW). Cloud compiler fallback is active.",
                execution_time_ms=0.0,
                memory_kb=0
            )

        compile_proc = await asyncio.create_subprocess_exec(
            compiler,
            "-O2",
            "-std=c++17",
            source_path,
            "-o",
            exe_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_dir
        )
        c_stdout, c_stderr = await compile_proc.communicate()
        if compile_proc.returncode != 0:
            return ExecutionResultData(
                status="COMPILATION_ERROR",
                stdout="",
                stderr="",
                compiler_output=c_stderr.decode("utf-8", errors="replace"),
                execution_time_ms=0.0,
                memory_kb=0
            )

        start_time = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                exe_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(input=input_data.encode("utf-8")),
                timeout=timeout
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            stdout_str = stdout_data.decode("utf-8", errors="replace")[:self.max_output_chars]
            stderr_str = stderr_data.decode("utf-8", errors="replace")[:self.max_output_chars]

            if process.returncode != 0:
                return ExecutionResultData(
                    status="RUNTIME_ERROR",
                    stdout=stdout_str,
                    stderr=stderr_str,
                    compiler_output="",
                    execution_time_ms=round(elapsed_ms, 2),
                    memory_kb=8192
                )

            return ExecutionResultData(
                status="SUCCESS",
                stdout=stdout_str,
                stderr=stderr_str,
                compiler_output="",
                execution_time_ms=round(elapsed_ms, 2),
                memory_kb=8192
            )
        except asyncio.TimeoutError:
            return ExecutionResultData(
                status="TIME_LIMIT_EXCEEDED",
                stdout="",
                stderr=f"Time limit of {timeout}s exceeded.",
                compiler_output="",
                execution_time_ms=round(timeout * 1000.0, 2),
                memory_kb=0
            )

    async def _run_c_local(
        self,
        temp_dir: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> ExecutionResultData:
        source_path = os.path.join(temp_dir, "solution.c")
        exe_name = "solution.exe" if os.name == "nt" else "solution"
        exe_path = os.path.join(temp_dir, exe_name)

        with open(source_path, "w", encoding="utf-8") as f:
            f.write(code)

        compiler = find_c_compiler()
        if not compiler:
            return ExecutionResultData(
                status="COMPILATION_ERROR",
                stdout="",
                stderr="C Compiler (gcc) is not installed on host operating system.",
                compiler_output="Host environment missing C compiler (gcc / MinGW). Cloud compiler fallback is active.",
                execution_time_ms=0.0,
                memory_kb=0
            )

        compile_proc = await asyncio.create_subprocess_exec(
            compiler,
            "-O2",
            source_path,
            "-o",
            exe_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_dir
        )
        c_stdout, c_stderr = await compile_proc.communicate()
        if compile_proc.returncode != 0:
            return ExecutionResultData(
                status="COMPILATION_ERROR",
                stdout="",
                stderr="",
                compiler_output=c_stderr.decode("utf-8", errors="replace"),
                execution_time_ms=0.0,
                memory_kb=0
            )

        start_time = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                exe_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(input=input_data.encode("utf-8")),
                timeout=timeout
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResultData(
                status="SUCCESS" if process.returncode == 0 else "RUNTIME_ERROR",
                stdout=stdout_data.decode("utf-8", errors="replace")[:self.max_output_chars],
                stderr=stderr_data.decode("utf-8", errors="replace")[:self.max_output_chars],
                compiler_output="",
                execution_time_ms=round(elapsed_ms, 2),
                memory_kb=4096
            )
        except asyncio.TimeoutError:
            return ExecutionResultData(
                status="TIME_LIMIT_EXCEEDED",
                stdout="",
                stderr=f"Time limit of {timeout}s exceeded.",
                compiler_output="",
                execution_time_ms=round(timeout * 1000.0, 2),
                memory_kb=0
            )

    async def _run_java_local(
        self,
        temp_dir: str,
        code: str,
        input_data: str,
        timeout: float
    ) -> ExecutionResultData:
        file_path = os.path.join(temp_dir, "Main.java")
        # Normalize class name to Main for consistent compilation
        normalized_code = re.sub(r'public\s+class\s+[A-Za-z0-9_]+', 'public class Main', code, count=1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(normalized_code)

        javac = shutil.which("javac")
        java = shutil.which("java")
        if not javac or not java:
            return ExecutionResultData(
                status="COMPILATION_ERROR",
                stdout="",
                stderr="Java Compiler (javac) is not available.",
                compiler_output="Host environment missing Java runtime. Cloud compiler fallback is active.",
                execution_time_ms=0.0,
                memory_kb=0
            )

        compile_proc = await asyncio.create_subprocess_exec(
            javac,
            file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=temp_dir
        )
        c_stdout, c_stderr = await compile_proc.communicate()
        if compile_proc.returncode != 0:
            return ExecutionResultData(
                status="COMPILATION_ERROR",
                stdout="",
                stderr="",
                compiler_output=c_stderr.decode("utf-8", errors="replace"),
                execution_time_ms=0.0,
                memory_kb=0
            )

        class_name = "Main"
        start_time = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                java,
                "-Xmx256m",
                class_name,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(input=input_data.encode("utf-8")),
                timeout=timeout
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResultData(
                status="SUCCESS" if process.returncode == 0 else "RUNTIME_ERROR",
                stdout=stdout_data.decode("utf-8", errors="replace")[:self.max_output_chars],
                stderr=stderr_data.decode("utf-8", errors="replace")[:self.max_output_chars],
                compiler_output="",
                execution_time_ms=round(elapsed_ms, 2),
                memory_kb=32768
            )
        except asyncio.TimeoutError:
            return ExecutionResultData(
                status="TIME_LIMIT_EXCEEDED",
                stdout="",
                stderr=f"Time limit of {timeout}s exceeded.",
                compiler_output="",
                execution_time_ms=round(timeout * 1000.0, 2),
                memory_kb=0
            )

    @staticmethod
    def normalize_output(text: str) -> str:
        """Strip trailing whitespace per line and carriage returns for clean CP evaluation"""
        if not text:
            return ""
        lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
        while lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines)

execution_engine = CodeExecutionEngine()

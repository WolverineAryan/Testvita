import pytest
from app.execution.runner import execution_engine

@pytest.mark.asyncio
async def test_python_cloud_execution():
    res = await execution_engine.execute_code(
        language="python",
        code="x = int(input())\nprint(x * 5)",
        input_data="8\n"
    )
    assert res.status == "SUCCESS"
    assert res.stdout.strip() == "40"

@pytest.mark.asyncio
async def test_cpp_cloud_execution():
    cpp_code = """
#include <iostream>
int main() {
    int a;
    if (std::cin >> a) {
        std::cout << (a + 10) << std::endl;
    }
    return 0;
}
"""
    res = await execution_engine.execute_code(
        language="cpp",
        code=cpp_code,
        input_data="15\n"
    )
    assert res.status == "SUCCESS"
    assert res.stdout.strip() == "25"

@pytest.mark.asyncio
async def test_compilation_error_handling():
    res = await execution_engine.execute_code(
        language="cpp",
        code="#include <iostream>\nint main() { invalid_syntax_here; return 0; }",
        input_data=""
    )
    assert res.status == "COMPILATION_ERROR"
    assert len(res.compiler_output) > 0

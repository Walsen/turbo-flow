"""
Custom tools example: add project-specific tools to an agent.

Usage:
  cd agent-adapter/python
  uv run python examples/custom_tools.py
"""

import subprocess

from strands import tool
from turboflow_adapter.strands import create_agent


@tool(name="run_python", description="Run a Python script and return its output.")
def run_python(code: str) -> str:
    """Execute Python code in a subprocess."""
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout
    if result.stderr:
        output += f"\nSTDERR: {result.stderr}"
    return output


@tool(name="check_syntax", description="Check Python file for syntax errors.")
def check_syntax(path: str) -> str:
    """Run py_compile on a file."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", path],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 0:
        return f"✓ {path} — no syntax errors"
    return f"✗ {path} — {result.stderr}"


if __name__ == "__main__":
    print("🔧 Creating coder agent with custom tools (run_python, check_syntax)\n")

    coder = create_agent("coder", model_tier="haiku", extra_tools=[run_python, check_syntax])
    result = coder(
        "Write a Python script that prints the first 20 Fibonacci numbers. "
        "Save it to /tmp/fib.py, check its syntax, then run it."
    )

    print("\n" + "=" * 60)
    print(result)

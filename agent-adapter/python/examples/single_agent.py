"""
Single agent example: create a coder and give it a task.

Usage:
  cd agent-adapter/python
  uv run python examples/single_agent.py
"""

from turboflow_adapter.strands import create_agent, select_tier

TASK = "Write a Python function that validates email addresses using regex. Include type hints and docstring."

if __name__ == "__main__":
    tier = select_tier(TASK)
    print(f"Auto-selected model tier: {tier.value}\n")

    coder = create_agent("coder", model_tier=tier)
    result = coder(TASK)

    print("\n" + "=" * 60)
    print(result)

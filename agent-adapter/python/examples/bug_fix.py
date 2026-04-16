"""
Bug fix example: researcher investigates, coder fixes, tester writes regression test.

Usage:
  cd agent-adapter/python
  uv run python examples/bug_fix.py
"""

from turboflow_adapter.strands import create_team

BUG_REPORT = """
Bug: The /api/users endpoint returns 500 when the database connection pool is exhausted.
Observed under load testing with 100 concurrent requests.
Expected: should return 503 Service Unavailable with a retry-after header.
Stack trace points to: connection timeout in pg_pool.acquire()
"""

if __name__ == "__main__":
    print("🐛 Starting bug-fix team (researcher + coder + tester)\n")

    team = create_team("bug-fix")
    result = team(BUG_REPORT)

    print("\n" + "=" * 60)
    print("BUG FIX RESULT")
    print("=" * 60)
    print(result)

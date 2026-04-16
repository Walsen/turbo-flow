"""
Full-build example: design → code → QE in one call.

Usage:
  cd agent-adapter/python
  uv run python examples/full_build.py

Or from repo root:
  uv run --project agent-adapter/python python agent-adapter/python/examples/full_build.py

Requires:
  CLAUDE_CODE_USE_BEDROCK=1
  AWS_REGION=us-east-1
"""

from turboflow_adapter.strands import create_team

APP_DESCRIPTION = """
Build a bookmark manager API:
- CRUD for bookmarks (url, title, description, tags)
- Tag-based filtering and full-text search
- User authentication with JWT
- REST API with proper error responses
- SQLite database (for simplicity)
- Python / FastAPI
- Include OpenAPI docs at /docs
"""

if __name__ == "__main__":
    print("🚀 Starting full-build team (architect + coder + tester + reviewer + security)")
    print("   This will take a few minutes — 5 agents across 3 phases.\n")

    team = create_team("full-build")
    result = team(APP_DESCRIPTION)

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result)

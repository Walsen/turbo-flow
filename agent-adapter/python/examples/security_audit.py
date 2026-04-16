"""
Security audit example: security architect + researcher + reviewer audit a module.

Usage:
  cd agent-adapter/python
  uv run python examples/security_audit.py
"""

from turboflow_adapter.strands import create_team

AUDIT_TARGET = """
Audit the authentication module in this project:
- Check for OWASP Top 10 vulnerabilities
- Review JWT implementation (signing, expiry, refresh flow)
- Check password hashing (algorithm, salt, rounds)
- Verify input validation on all auth endpoints
- Check for rate limiting on login attempts
- Review session management
- Check for sensitive data in logs or error responses
"""

if __name__ == "__main__":
    print("🔒 Starting security audit team (security architect + researcher + reviewer)\n")

    team = create_team("security-audit")
    result = team(AUDIT_TARGET)

    print("\n" + "=" * 60)
    print("SECURITY AUDIT REPORT")
    print("=" * 60)
    print(result)

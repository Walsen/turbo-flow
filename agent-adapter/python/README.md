# TurboFlow Agent Adapter (Python)

Provider-independent agent abstraction with native Strands Agents support.

```bash
# Install with uv
uv sync --extra strands

# CLI
tf-adapter status
tf-adapter exec "implement the login feature"
tf-adapter exec --backend strands --model sonnet "add error handling"

# Programmatic
from turboflow_adapter import AgentAdapter
adapter = AgentAdapter("strands")
result = await adapter.exec("implement login", ExecOptions(model="sonnet"))
```

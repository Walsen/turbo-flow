"""
AgentDB — vector memory for Strands agents.

Semantic search over past patterns, decisions, code snippets, and lessons.
Replaces Ruflo's `ruv-remember` / `ruv-recall` with a Strands-native
implementation backed by SQLite + Bedrock Titan Embeddings.

Storage: ~/.turboflow/memory/agentdb.sqlite (portable, gitignored)
Embeddings: Amazon Bedrock Titan Embeddings (or falls back to keyword search)

Usage:
    from turboflow_adapter.strands.memory import memory_tools

    agent = create_agent("coder", extra_tools=memory_tools())
    # Agent can now call: agentdb_remember, agentdb_recall, agentdb_stats
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from turboflow_adapter.logger import get_logger

log = get_logger("tf-adapter.strands.memory")

try:
    from strands import tool as strands_tool

    _HAS_STRANDS = True
except ImportError:
    _HAS_STRANDS = False

    def strands_tool(fn: Any = None, **kwargs: Any) -> Any:  # type: ignore
        def wrapper(f: Any) -> Any:
            return f

        return wrapper(fn) if fn else wrapper


# ── Database ─────────────────────────────────────────────────────────────

_DB_DIR = Path.home() / ".turboflow" / "memory"
_DB_PATH = _DB_DIR / "agentdb.sqlite"
_EMBEDDING_DIM = 1024  # Titan Embeddings v2 dimension


def _get_db() -> sqlite3.Connection:
    """Get or create the SQLite database."""
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            embedding TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            access_count INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
    conn.commit()
    return conn


# ── Embeddings ───────────────────────────────────────────────────────────


def _get_embedding(text: str) -> list[float] | None:
    """Get embedding from Bedrock Titan Embeddings. Returns None if unavailable."""
    try:
        import boto3

        client = boto3.client(
            "bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        response = client.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": text[:8000]}),  # Titan limit
        )
        result = json.loads(response["body"].read())
        embedding: list[float] = result["embedding"]
        return embedding
    except Exception as e:
        log.debug("Embedding generation failed (falling back to keyword search): %s", e)
        return None


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Core operations ──────────────────────────────────────────────────────


def remember(key: str, value: str, category: str = "general") -> str:
    """Store a memory with optional embedding."""
    conn = _get_db()
    now = time.time()

    # Check if key exists — update if so
    existing = conn.execute("SELECT id FROM memories WHERE key = ?", (key,)).fetchone()

    embedding = _get_embedding(f"{key}: {value}")
    embedding_json = json.dumps(embedding) if embedding else None

    if existing:
        conn.execute(
            "UPDATE memories SET value = ?, category = ?, embedding = ?, updated_at = ? WHERE key = ?",
            (value, category, embedding_json, now, key),
        )
        conn.commit()
        return f"Updated memory: {key}"
    else:
        conn.execute(
            "INSERT INTO memories (key, value, category, embedding, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (key, value, category, embedding_json, now, now),
        )
        conn.commit()
        return f"Stored memory: {key}"


def recall(query: str, limit: int = 5, category: str | None = None) -> list[dict[str, Any]]:
    """Search memories by semantic similarity or keyword match."""
    conn = _get_db()

    # Try semantic search first
    query_embedding = _get_embedding(query)

    if query_embedding:
        # Fetch all memories with embeddings
        if category:
            rows = conn.execute(
                "SELECT key, value, category, embedding, created_at, access_count FROM memories WHERE category = ? AND embedding IS NOT NULL",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT key, value, category, embedding, created_at, access_count FROM memories WHERE embedding IS NOT NULL"
            ).fetchall()

        # Score by cosine similarity
        scored = []
        for row in rows:
            emb = json.loads(row[3])
            score = _cosine_similarity(query_embedding, emb)
            scored.append(
                {
                    "key": row[0],
                    "value": row[1],
                    "category": row[2],
                    "score": round(score, 4),
                    "created_at": row[4],
                    "access_count": row[5],
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        results = scored[:limit]
    else:
        # Fallback: keyword search
        search_term = f"%{query}%"
        if category:
            rows = conn.execute(
                "SELECT key, value, category, created_at, access_count FROM memories WHERE category = ? AND (key LIKE ? OR value LIKE ?) ORDER BY updated_at DESC LIMIT ?",
                (category, search_term, search_term, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT key, value, category, created_at, access_count FROM memories WHERE key LIKE ? OR value LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (search_term, search_term, limit),
            ).fetchall()

        results = [
            {
                "key": row[0],
                "value": row[1],
                "category": row[2],
                "score": 1.0,  # keyword match
                "created_at": row[3],
                "access_count": row[4],
            }
            for row in rows
        ]

    # Update access counts
    for r in results:
        conn.execute(
            "UPDATE memories SET access_count = access_count + 1 WHERE key = ?",
            (r["key"],),
        )
    conn.commit()

    return results


def stats() -> dict[str, Any]:
    """Get memory statistics."""
    conn = _get_db()
    total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    with_embeddings = conn.execute(
        "SELECT COUNT(*) FROM memories WHERE embedding IS NOT NULL"
    ).fetchone()[0]
    categories = conn.execute(
        "SELECT category, COUNT(*) FROM memories GROUP BY category ORDER BY COUNT(*) DESC"
    ).fetchall()
    most_accessed = conn.execute(
        "SELECT key, access_count FROM memories ORDER BY access_count DESC LIMIT 5"
    ).fetchall()

    return {
        "total_memories": total,
        "with_embeddings": with_embeddings,
        "categories": {row[0]: row[1] for row in categories},
        "most_accessed": [{"key": row[0], "count": row[1]} for row in most_accessed],
        "db_path": str(_DB_PATH),
    }


# ── Strands tools ────────────────────────────────────────────────────────


@strands_tool(
    name="agentdb_remember",
    description=(
        "Store a pattern, lesson, or decision in AgentDB for future recall. "
        "Use categories: pattern, lesson, decision, snippet, config. "
        "Key should be descriptive (e.g. 'pattern/retry-with-backoff')."
    ),
)
def agentdb_remember(key: str, value: str, category: str = "general") -> str:
    """Store a memory."""
    return remember(key, value, category)


@strands_tool(
    name="agentdb_recall",
    description=(
        "Search AgentDB for relevant memories by meaning (semantic search) or keywords. "
        "Use before starting work to find known solutions and patterns. "
        "Optionally filter by category: pattern, lesson, decision, snippet, config."
    ),
)
def agentdb_recall(query: str, category: str = "") -> str:
    """Search memories."""
    results = recall(query, limit=5, category=category if category else None)
    if not results:
        return "No matching memories found."

    lines = [f"Found {len(results)} memories:\n"]
    for r in results:
        lines.append(f"  [{r['category']}] {r['key']} (score: {r['score']})")
        lines.append(f"    {r['value'][:200]}")
        lines.append("")
    return "\n".join(lines)


@strands_tool(
    name="agentdb_stats",
    description="Show AgentDB memory statistics: total memories, categories, most accessed.",
)
def agentdb_stats() -> str:
    """Get memory stats."""
    s = stats()
    lines = [
        "AgentDB Statistics:",
        f"  Total memories: {s['total_memories']}",
        f"  With embeddings: {s['with_embeddings']}",
        f"  Categories: {s['categories']}",
        f"  Most accessed: {s['most_accessed']}",
        f"  DB path: {s['db_path']}",
    ]
    return "\n".join(lines)


def memory_tools() -> list[Any]:
    """Get all AgentDB memory tools."""
    if not _HAS_STRANDS:
        return []
    return [agentdb_remember, agentdb_recall, agentdb_stats]

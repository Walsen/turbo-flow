"""Tests for AgentDB vector memory."""

import os
import tempfile
from unittest import mock

from turboflow_adapter.strands.memory import remember, recall, stats, memory_tools, _DB_DIR


class TestMemoryOperations:
    def setup_method(self) -> None:
        """Use a temp directory for the test database."""
        self._tmpdir = tempfile.mkdtemp()
        self._patcher = mock.patch(
            "turboflow_adapter.strands.memory._DB_DIR",
            type(
                "Path",
                (),
                {
                    "__truediv__": lambda s, n: type(
                        "P",
                        (),
                        {
                            "__str__": lambda s2: os.path.join(self._tmpdir, n),
                            "mkdir": lambda s2, **kw: os.makedirs(self._tmpdir, exist_ok=True),
                        },
                    )()
                },
            )(),
        )
        # Simpler approach: just patch the DB path
        import turboflow_adapter.strands.memory as mem

        self._orig_path = mem._DB_PATH
        mem._DB_PATH = type(
            "P", (), {"__str__": lambda s: os.path.join(self._tmpdir, "test.sqlite")}
        )()
        mem._DB_DIR = type(
            "P",
            (),
            {
                "mkdir": lambda s, **kw: os.makedirs(self._tmpdir, exist_ok=True),
            },
        )()

    def teardown_method(self) -> None:
        import turboflow_adapter.strands.memory as mem

        mem._DB_PATH = self._orig_path
        mem._DB_DIR = _DB_DIR
        import shutil

        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_remember_and_recall_keyword(self) -> None:
        result = remember("pattern/retry", "Use exponential backoff with jitter", "pattern")
        assert "Stored" in result

        results = recall("retry")
        assert len(results) >= 1
        assert results[0]["key"] == "pattern/retry"
        assert "backoff" in results[0]["value"]

    def test_remember_update(self) -> None:
        remember("test/key", "value 1")
        remember("test/key", "value 2")

        results = recall("test/key")
        assert len(results) == 1
        assert results[0]["value"] == "value 2"

    def test_recall_no_results(self) -> None:
        results = recall("nonexistent query xyz")
        assert len(results) == 0

    def test_recall_category_filter(self) -> None:
        remember("lesson/a", "lesson value", "lesson")
        remember("pattern/b", "pattern value", "pattern")

        lessons = recall("value", category="lesson")
        assert all(r["category"] == "lesson" for r in lessons)

    def test_stats(self) -> None:
        remember("key1", "value1", "pattern")
        remember("key2", "value2", "lesson")

        s = stats()
        assert s["total_memories"] == 2
        assert "pattern" in s["categories"]
        assert "lesson" in s["categories"]

    def test_access_count_increments(self) -> None:
        remember("popular/key", "popular value")
        recall("popular")
        recall("popular")

        s = stats()
        most_accessed = s["most_accessed"]
        assert any(m["key"] == "popular/key" and m["count"] >= 2 for m in most_accessed)


class TestMemoryTools:
    def test_memory_tools_count(self) -> None:
        tools = memory_tools()
        assert len(tools) == 3  # remember, recall, stats

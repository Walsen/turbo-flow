"""Tests for TurboFlow tools."""

import os
import tempfile

from turboflow_adapter.strands.tools import (
    beads_tools,
    file_tools,
    all_tools,
    read_file,
    write_file,
    list_directory,
)


class TestToolCollections:
    def test_beads_tools_count(self) -> None:
        tools = beads_tools()
        assert len(tools) == 4

    def test_file_tools_count(self) -> None:
        tools = file_tools()
        assert len(tools) == 4

    def test_all_tools_count(self) -> None:
        tools = all_tools()
        assert len(tools) == 8

    def test_no_duplicates(self) -> None:
        tools = all_tools()
        names = [getattr(t, "__name__", str(t)) for t in tools]
        assert len(names) == len(set(names))


class TestFileTools:
    def test_read_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello world")
            f.flush()
            result = read_file(f.name)
            assert result == "hello world"
        os.unlink(f.name)

    def test_read_file_not_found(self) -> None:
        result = read_file("/nonexistent/path/file.txt")
        assert "Error" in result

    def test_write_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            result = write_file(path, "test content")
            assert "Written" in result
            assert os.path.exists(path)
            with open(path) as f:
                assert f.read() == "test content"

    def test_list_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "a.txt"), "w").close()
            open(os.path.join(tmpdir, "b.txt"), "w").close()
            result = list_directory(tmpdir)
            assert "a.txt" in result
            assert "b.txt" in result

    def test_list_directory_not_found(self) -> None:
        result = list_directory("/nonexistent/path")
        assert "Error" in result

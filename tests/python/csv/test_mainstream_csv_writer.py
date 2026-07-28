"""
test_mainstream_csv_writer.py — CSV writer tests for mainstream mega-train.

Sprint: MAINSTREAM-MEGATRAIN-20260610
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ff_csv.csv_writer import (
    write_csv,
    write_csv_to_file,
    parse_and_rewrite,
    CsvWriteError,
    _escape_field,
)
from src.python.ff_csv.csv_parser import parse_csv_strict


class TestEscapeField:
    def test_none_returns_empty(self):
        assert _escape_field(None) == ""

    def test_empty_string(self):
        assert _escape_field("") == ""

    def test_plain_text(self):
        assert _escape_field("hello") == "hello"

    def test_comma_quoted(self):
        assert _escape_field("a,b") == '"a,b"'

    def test_quotes_doubled(self):
        assert _escape_field('say "hi"') == '"say ""hi"""'

    def test_newline_quoted(self):
        assert _escape_field("line1\nline2") == '"line1\nline2"'

    def test_cr_quoted(self):
        assert _escape_field("a\rb") == '"a\rb"'


class TestWriteCsv:
    def test_simple_rows(self):
        result = write_csv([["a", "b"], ["1", "2"]])
        assert result == "a,b\n1,2\n"

    def test_with_headers(self):
        result = write_csv([["1", "2"]], headers=["x", "y"])
        assert result == "x,y\n1,2\n"

    def test_empty_rows(self):
        result = write_csv([])
        assert result == ""

    def test_none_rows_raises(self):
        with pytest.raises(CsvWriteError):
            write_csv(None)

    def test_quoting_in_output(self):
        result = write_csv([["hello, world", "ok"]])
        assert '"hello, world"' in result

    def test_semicolon_delimiter(self):
        result = write_csv([["a", "b"]], delimiter=";")
        assert result == "a;b\n"

    def test_none_field_becomes_empty(self):
        result = write_csv([["a", None, "c"]])
        assert result == "a,,c\n"


class TestWriteCsvToFile:
    def test_file_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            path = f.name
        try:
            write_csv_to_file([["name", "age"], ["Alice", "30"]], path)
            content = Path(path).read_text(encoding="utf-8")
            assert "name,age" in content
            assert "Alice,30" in content
        finally:
            Path(path).unlink(missing_ok=True)

    def test_empty_path_raises(self):
        with pytest.raises(CsvWriteError):
            write_csv_to_file([], "")

    def test_creates_parent_dirs(self):
        import shutil
        tmpdir = Path(tempfile.mkdtemp()) / "sub" / "dir"
        try:
            path = tmpdir / "test.csv"
            write_csv_to_file([["a"]], path)
            assert path.exists()
        finally:
            shutil.rmtree(tmpdir.parent, ignore_errors=True)


class TestParseAndRewrite:
    def test_roundtrip_no_transform(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("name,age\nAlice,30\nBob,25\n")
            src = f.name
        dst = src + ".out.csv"
        try:
            result = parse_and_rewrite(src, dst)
            assert result["row_count"] == 2
            assert result["column_count"] == 2
            # Verify the output can be parsed back
            parsed = parse_csv_strict(dst)
            assert parsed["row_count"] == 2
        finally:
            Path(src).unlink(missing_ok=True)
            Path(dst).unlink(missing_ok=True)

    def test_roundtrip_with_transform(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            f.write("x,y\n1,2\n3,4\n")
            src = f.name
        dst = src + ".out.csv"
        try:
            # Transform: reverse rows
            result = parse_and_rewrite(
                src, dst,
                transform=lambda rows, headers: (list(reversed(rows)), headers),
            )
            assert result["row_count"] == 2
            parsed = parse_csv_strict(dst)
            assert parsed["rows"][0] == ["3", "4"]
        finally:
            Path(src).unlink(missing_ok=True)
            Path(dst).unlink(missing_ok=True)

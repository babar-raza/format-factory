"""Tests for TSV get_column and write_tsv_strict.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-2-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.tsv.tsv_parser import (
    get_column,
    write_tsv_strict,
    load_tsv,
    TsvError,
)


TSV_CONTENT = b"name\tage\tcity\nAlice\t30\tLondon\nBob\t25\tParis\nCarol\t35\tTokyo\n"


# ---------------------------------------------------------------------------
# get_column
# ---------------------------------------------------------------------------

class TestGetColumn:
    def test_basic_column(self):
        result = get_column(TSV_CONTENT, "name")
        assert result == ["Alice", "Bob", "Carol"]

    def test_second_column(self):
        result = get_column(TSV_CONTENT, "age")
        assert result == ["30", "25", "35"]

    def test_third_column(self):
        result = get_column(TSV_CONTENT, "city")
        assert result == ["London", "Paris", "Tokyo"]

    def test_nonexistent_column_returns_empty(self):
        result = get_column(TSV_CONTENT, "country")
        assert result == []

    def test_returns_list(self):
        result = get_column(TSV_CONTENT, "name")
        assert isinstance(result, list)

    def test_all_strings(self):
        result = get_column(TSV_CONTENT, "name")
        assert all(isinstance(v, str) for v in result)

    def test_file_source(self, tmp_path):
        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_bytes(TSV_CONTENT)
        result = get_column(tsv_file, "city")
        assert result == ["London", "Paris", "Tokyo"]

    def test_single_row(self):
        content = b"col1\tcol2\nval1\tval2\n"
        result = get_column(content, "col1")
        assert result == ["val1"]

    def test_empty_file_returns_empty(self):
        result = get_column(b"", "col")
        assert result == []


# ---------------------------------------------------------------------------
# write_tsv_strict
# ---------------------------------------------------------------------------

class TestWriteTsvStrict:
    def test_basic_write(self, tmp_path):
        dest = tmp_path / "out.tsv"
        write_tsv_strict([["Alice", "30"], ["Bob", "25"]], dest, headers=["name", "age"])
        model = load_tsv(dest)
        assert model["headers"] == ["name", "age"]
        assert model["row_count"] == 2

    def test_roundtrip_values(self, tmp_path):
        dest = tmp_path / "out.tsv"
        rows = [["x", "y", "z"], ["a", "b", "c"]]
        write_tsv_strict(rows, dest, headers=["h1", "h2", "h3"])
        model = load_tsv(dest)
        assert model["rows"][0] == ["x", "y", "z"]

    def test_raises_on_tab_in_cell(self, tmp_path):
        dest = tmp_path / "out.tsv"
        with pytest.raises(TsvError, match="tab"):
            write_tsv_strict([["bad\tvalue"]], dest)

    def test_raises_on_newline_in_cell(self, tmp_path):
        dest = tmp_path / "out.tsv"
        with pytest.raises(TsvError, match="newline"):
            write_tsv_strict([["bad\nvalue"]], dest)

    def test_raises_on_tab_in_header(self, tmp_path):
        dest = tmp_path / "out.tsv"
        with pytest.raises(TsvError, match="tab"):
            write_tsv_strict([["ok"]], dest, headers=["head\ter"])

    def test_no_header(self, tmp_path):
        dest = tmp_path / "out.tsv"
        write_tsv_strict([["a", "b"], ["c", "d"]], dest)
        content = dest.read_text(encoding="utf-8")
        assert content == "a\tb\nc\td\n"

    def test_empty_rows(self, tmp_path):
        dest = tmp_path / "out.tsv"
        write_tsv_strict([], dest)
        content = dest.read_text(encoding="utf-8")
        assert content == ""

    def test_numeric_values_coerced_to_str(self, tmp_path):
        dest = tmp_path / "out.tsv"
        write_tsv_strict([[1, 2, 3]], dest)
        content = dest.read_text(encoding="utf-8")
        assert "1\t2\t3" in content

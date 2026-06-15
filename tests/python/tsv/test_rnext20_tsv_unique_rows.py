"""
test_rnext20_tsv_unique_rows.py

Sprint: FORMAT-FACTORY-CAPABILITY-REFRESH-AND-ADVANCE-RNEXT20-001
Gap IDs: GAP-TSV-FOSS-UNIQUE_COLUMN-001, GAP-TSV-FOSS-FIND_ROWS_C-001

Tests for:
- unique_column_values(source, col_name): Return sorted unique values in a column.
- find_rows_containing(source, text, case_sensitive=True): Return 0-based row indices
  where any cell contains the given text.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.tsv.tsv_parser import find_rows_containing, unique_column_values


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_tsv(tmp_path: Path, rows: list[list[str]], filename: str = "data.tsv") -> str:
    p = tmp_path / filename
    p.write_text("\n".join("\t".join(row) for row in rows) + "\n", encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# unique_column_values
# ---------------------------------------------------------------------------


class TestUniqueColumnValues:

    def test_returns_sorted_unique_strings(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["name", "score"],
            ["Bob", "10"],
            ["Alice", "20"],
            ["Bob", "30"],
            ["Carol", "40"],
        ])
        result = unique_column_values(path, "name")
        assert result == ["Alice", "Bob", "Carol"]

    def test_single_unique_value(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["status"],
            ["active"],
            ["active"],
            ["active"],
        ])
        result = unique_column_values(path, "status")
        assert result == ["active"]

    def test_all_distinct_values(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["color"],
            ["red"],
            ["green"],
            ["blue"],
        ])
        result = unique_column_values(path, "color")
        assert result == ["blue", "green", "red"]

    def test_numeric_strings_sorted_lexicographically(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["val"],
            ["10"],
            ["2"],
            ["1"],
            ["10"],
        ])
        result = unique_column_values(path, "val")
        assert result == ["1", "10", "2"]

    def test_empty_string_values_included(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["tag"],
            ["foo"],
            [""],
            ["foo"],
        ])
        result = unique_column_values(path, "tag")
        assert "" in result
        assert "foo" in result

    def test_column_with_mixed_types_as_strings(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["x"],
            ["1"],
            ["true"],
            ["1"],
            ["true"],
        ])
        result = unique_column_values(path, "x")
        assert len(result) == 2
        assert "1" in result
        assert "true" in result


# ---------------------------------------------------------------------------
# find_rows_containing
# ---------------------------------------------------------------------------


class TestFindRowsContaining:

    def test_finds_rows_with_exact_text_case_sensitive(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["name", "city"],
            ["Alice", "New York"],
            ["Bob", "Boston"],
            ["Carol", "New York"],
        ])
        result = find_rows_containing(path, "Alice")
        assert 0 in result

    def test_returns_zero_based_row_indices(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["name"],
            ["Alice"],
            ["Bob"],
            ["Alice"],
        ])
        result = find_rows_containing(path, "Alice")
        assert 0 in result
        assert 2 in result
        assert 1 not in result

    def test_case_sensitive_no_match(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["name"],
            ["Alice"],
            ["Bob"],
        ])
        result = find_rows_containing(path, "alice", case_sensitive=True)
        assert result == []

    def test_case_insensitive_matches(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["name"],
            ["Alice"],
            ["ALICE"],
            ["Bob"],
        ])
        result = find_rows_containing(path, "alice", case_sensitive=False)
        assert 0 in result
        assert 1 in result
        assert 2 not in result

    def test_no_match_returns_empty(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["name"],
            ["Alice"],
            ["Bob"],
        ])
        result = find_rows_containing(path, "Zara")
        assert result == []

    def test_partial_text_match(self, tmp_path):
        path = _write_tsv(tmp_path, [
            ["city"],
            ["New York"],
            ["Newark"],
            ["Boston"],
        ])
        result = find_rows_containing(path, "New")
        assert 0 in result
        assert 1 in result
        assert 2 not in result

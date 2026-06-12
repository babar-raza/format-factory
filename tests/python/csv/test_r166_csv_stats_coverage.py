"""
test_r166_csv_stats_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT5-001
Added: 2026-06-11

Tests for CSV stats functions: column_value_counts, csv_field_type_summary,
csv_empty_row_count, csv_max_field_length.
Closes gaps: GAP-CSV-FOSS-COLUMN_VALUE-001, GAP-CSV-FOSS-CSV_FIELD_TY-001,
             GAP-CSV-FOSS-CSV_MAX_FIEL-001.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_stats import (
    column_value_counts,
    csv_field_type_summary,
    csv_empty_row_count,
    csv_max_field_length,
)


# ── column_value_counts ───────────────────────────────────────────────────

class TestColumnValueCounts:

    def _make_doc(self, rows):
        return {"rows": rows, "format": "csv"}

    def test_returns_dict(self):
        doc = self._make_doc([["a"], ["b"], ["a"]])
        result = column_value_counts(doc, 0)
        assert isinstance(result, dict)

    def test_counts_distinct_values(self):
        doc = self._make_doc([["x"], ["y"], ["x"], ["z"], ["x"]])
        result = column_value_counts(doc, 0)
        assert result["x"] == 3
        assert result["y"] == 1
        assert result["z"] == 1

    def test_empty_rows(self):
        doc = self._make_doc([])
        result = column_value_counts(doc, 0)
        assert result == {}

    def test_multi_column_second_col(self):
        doc = self._make_doc([["a", "cat"], ["b", "dog"], ["c", "cat"]])
        result = column_value_counts(doc, 1)
        assert result["cat"] == 2
        assert result["dog"] == 1

    def test_out_of_bounds_column(self):
        doc = self._make_doc([["a"], ["b"]])
        result = column_value_counts(doc, 5)
        # Should handle gracefully (empty string counted)
        assert isinstance(result, dict)

    def test_whitespace_stripped(self):
        doc = self._make_doc([[" hello "], ["hello"]])
        result = column_value_counts(doc, 0)
        assert result.get("hello", 0) == 2


# ── csv_field_type_summary ────────────────────────────────────────────────

class TestCsvFieldTypeSummary:

    def test_returns_dict(self):
        result = csv_field_type_summary([["a", "1", "2.5"]])
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = csv_field_type_summary([["a", "1"]])
        assert "numeric" in result
        assert "empty" in result
        assert "text" in result

    def test_numeric_count(self):
        rows = [["1", "2.5", "3"]]
        result = csv_field_type_summary(rows)
        assert result["numeric"] == 3

    def test_text_count(self):
        rows = [["hello", "world", "foo"]]
        result = csv_field_type_summary(rows)
        assert result["text"] == 3

    def test_empty_count(self):
        rows = [["", None, "  "]]
        result = csv_field_type_summary(rows)
        assert result["empty"] == 3

    def test_mixed_types(self):
        rows = [["hello", "42", "", "3.14", "world"]]
        result = csv_field_type_summary(rows)
        assert result["text"] == 2
        assert result["numeric"] == 2
        assert result["empty"] == 1

    def test_empty_rows(self):
        result = csv_field_type_summary([])
        assert result == {"numeric": 0, "empty": 0, "text": 0}

    def test_total_matches_fields(self):
        rows = [["a", "1", ""], ["b", "2.5", "x"]]
        result = csv_field_type_summary(rows)
        total = result["numeric"] + result["empty"] + result["text"]
        assert total == 6  # 2 rows × 3 fields


# ── csv_empty_row_count ───────────────────────────────────────────────────

class TestCsvEmptyRowCount:

    def test_no_empty_rows(self):
        rows = [["a", "b"], ["c", "d"]]
        assert csv_empty_row_count(rows) == 0

    def test_all_empty_rows(self):
        rows = [["", ""], ["", ""]]
        assert csv_empty_row_count(rows) == 2

    def test_mixed_rows(self):
        rows = [["a", "b"], ["", ""], ["c", "d"], ["", ""]]
        assert csv_empty_row_count(rows) == 2

    def test_empty_list(self):
        assert csv_empty_row_count([]) == 0

    def test_none_fields(self):
        rows = [[None, None], ["a", "b"]]
        assert csv_empty_row_count(rows) == 1


# ── csv_max_field_length ──────────────────────────────────────────────────

class TestCsvMaxFieldLength:

    def test_returns_int(self):
        rows = [["hello", "world"]]
        result = csv_max_field_length(rows)
        assert isinstance(result, int)

    def test_correct_max(self):
        rows = [["hi", "hello", "hey"]]
        result = csv_max_field_length(rows)
        assert result == 5  # "hello" is 5 chars

    def test_multi_row_max(self):
        rows = [["short"], ["much longer string"], ["medium"]]
        result = csv_max_field_length(rows)
        assert result == len("much longer string")

    def test_empty_rows(self):
        result = csv_max_field_length([])
        assert result == 0

    def test_empty_fields(self):
        rows = [["", "", ""]]
        result = csv_max_field_length(rows)
        assert result == 0

    def test_unicode_characters(self):
        rows = [["\u4e2d\u6587\u5185\u5bb9"]]  # 4 Unicode chars
        result = csv_max_field_length(rows)
        assert result == 4

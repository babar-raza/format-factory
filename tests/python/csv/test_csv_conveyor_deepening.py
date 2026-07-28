"""
test_csv_conveyor_deepening.py -- CSV product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-2
Tests writer, stats, and roundtrip for CSV codec.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_writer import write_csv, write_csv_to_file, parse_and_rewrite
from src.python.ff_csv.csv_stats import (
    table_stats,
    column_value_counts,
    csv_row_length_distribution,
    csv_field_type_summary,
    csv_empty_row_count,
    csv_max_field_length,
)
from src.python.ff_csv.csv_parser import parse_csv_strict


def test_write_csv_basic():
    result = write_csv([["a", "b"], ["c", "d"]], headers=["h1", "h2"])
    assert "h1,h2" in result
    assert "a,b" in result


def test_write_csv_quoting():
    result = write_csv([['has,comma', 'has"quote']])
    assert '"has,comma"' in result
    assert '"has""quote"' in result


def test_write_csv_to_file(tmp_path):
    fp = tmp_path / "out.csv"
    write_csv_to_file([["x", "y"]], str(fp), headers=["col1", "col2"])
    content = fp.read_text(encoding="utf-8")
    assert "col1,col2" in content


def test_parse_and_rewrite_roundtrip(tmp_path):
    src = tmp_path / "in.csv"
    src.write_text("name,value\nalice,100\nbob,200\n", encoding="utf-8")
    dest = tmp_path / "out.csv"
    info = parse_and_rewrite(str(src), str(dest))
    assert info["row_count"] == 2
    assert dest.exists()


def test_table_stats():
    doc = {"rows": [["a", "1"], ["b", "2"]], "headers": ["name", "val"],
           "column_count": 2, "has_header": True}
    stats = table_stats(doc)
    assert stats["row_count"] == 2
    assert stats["column_count"] == 2
    assert stats["has_header"] is True
    assert stats["total_cells"] == 4


def test_column_value_counts():
    doc = {"rows": [["a", "1"], ["b", "1"], ["a", "2"]]}
    counts = column_value_counts(doc, 0)
    assert counts["a"] == 2
    assert counts["b"] == 1


def test_row_length_distribution():
    doc = {"rows": [["a", "b"], ["c", "d", "e"], ["f"]]}
    dist = csv_row_length_distribution(doc)
    assert dist["is_uniform"] is False
    assert dist["min_length"] == 1
    assert dist["max_length"] == 3


def test_field_type_summary():
    rows = [["hello", "42"], ["", "3.14"], [None, "world"]]
    summary = csv_field_type_summary(rows)
    assert summary["numeric"] == 2
    assert summary["text"] == 2
    assert summary["empty"] == 2


def test_empty_row_count():
    rows = [["a", "b"], ["", ""], [None, None], ["x", "y"]]
    assert csv_empty_row_count(rows) == 2


def test_max_field_length():
    rows = [["short", "a longer field value"], ["x", "y"]]
    assert csv_max_field_length(rows) == 20


def test_parse_csv_strict_basic(tmp_path):
    fp = tmp_path / "test.csv"
    fp.write_text("col1,col2\na,b\nc,d\n", encoding="utf-8")
    result = parse_csv_strict(str(fp))
    assert result["row_count"] >= 2

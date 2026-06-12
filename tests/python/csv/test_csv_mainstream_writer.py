"""
test_csv_mainstream_writer.py -- CSV writer content verification tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-10
Tests write_csv and parse_and_rewrite with strong content assertions.
Addresses W9-CSV-ADVANCED advisory: verifies actual field values,
quoting, headers, and roundtrip row/column counts.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_writer import write_csv, parse_and_rewrite


def test_write_csv_field_values_present():
    rows = [["Alice", "90"], ["Bob", "85"]]
    result = write_csv(rows)
    assert "Alice" in result
    assert "Bob" in result
    assert "90" in result
    assert "85" in result


def test_write_csv_with_headers_first_line():
    rows = [["Alice", "90"], ["Bob", "85"]]
    result = write_csv(rows, headers=["name", "score"])
    lines = result.strip().splitlines()
    assert lines[0] == "name,score"
    assert lines[1] == "Alice,90"
    assert len(lines) == 3


def test_write_csv_quotes_comma_in_field():
    rows = [["Smith, John", "100"]]
    result = write_csv(rows)
    assert '"Smith, John"' in result


def test_write_csv_null_field_is_empty():
    rows = [[None, "value"]]
    result = write_csv(rows)
    lines = result.strip().splitlines()
    assert lines[0] == ",value"


def test_parse_and_rewrite_row_count(tmp_path):
    src = tmp_path / "input.csv"
    src.write_text("name,score\nAlice,90\nBob,85\nCarol,78\n", encoding="utf-8")
    dest = tmp_path / "output.csv"
    result = parse_and_rewrite(str(src), str(dest))
    assert result["row_count"] == 3


def test_parse_and_rewrite_column_count(tmp_path):
    src = tmp_path / "input.csv"
    src.write_text("name,score,dept\nAlice,90,eng\nBob,85,mkt\n", encoding="utf-8")
    dest = tmp_path / "output.csv"
    result = parse_and_rewrite(str(src), str(dest))
    assert result["column_count"] == 3

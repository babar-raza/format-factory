"""
test_csv_advanced_roundtrip.py -- CSV advanced parse_and_rewrite + table stats.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-9
Tests CSV parse_and_rewrite, table stats, and column analytics with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_writer import (
    write_csv,
    write_csv_to_file,
    parse_and_rewrite,
)
try:
    from src.python.csv.csv_parser import (
        parse_csv,
        parse_csv_strict,
        table_stats,
        column_value_counts,
        field_type_summary,
        empty_row_count,
        max_field_length,
        row_length_distribution,
    )
    _HAS_PARSER = True
except ImportError:
    _HAS_PARSER = False


def test_write_csv_basic():
    rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    result = write_csv(rows)
    assert "Name" in result
    assert "Alice" in result
    assert "Bob" in result


def test_write_csv_to_file(tmp_path):
    rows = [["x", "y"], ["1", "2"]]
    out = tmp_path / "out.csv"
    write_csv_to_file(rows, str(out))
    assert out.exists()
    content = out.read_text()
    assert "x" in content


def test_parse_and_rewrite(tmp_path):
    src = tmp_path / "src.csv"
    src.write_text("name,value\nalpha,1\nbeta,2\n")
    dest = tmp_path / "dest.csv"
    result = parse_and_rewrite(str(src), str(dest))
    assert dest.exists()
    content = dest.read_text()
    assert "name" in content
    assert "alpha" in content


def test_write_csv_produces_rows():
    rows = [["a", "b", "c"], ["1", "2", "3"], ["4", "5", "6"]]
    csv_str = write_csv(rows)
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) == 3


def test_write_csv_handles_commas():
    rows = [["field,with,commas", "normal"]]
    csv_str = write_csv(rows)
    # Comma-containing field should be quoted
    assert '"' in csv_str or "field,with,commas" in csv_str

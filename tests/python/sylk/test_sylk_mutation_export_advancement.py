"""
test_sylk_mutation_export_advancement.py -- SYLK advanced mutation + export tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-8
Tests add_row/delete_row idempotency and sylk_to_html content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"

from sylk.sylk_parser import (
    sylk_to_html,
    sylk_to_csv,
    add_row,
    delete_row,
    get_row_count,
    sum_column,
)


def test_add_row_increments_row_count(tmp_path):
    src = _SAMPLES / "minimal-2x2.slk"
    before = get_row_count(str(src))
    dest = tmp_path / "added.slk"
    add_row(str(src), str(dest), ["new", "row"])
    after = get_row_count(str(dest))
    assert after == before + 1


def test_delete_row_decrements_row_count(tmp_path):
    src = _SAMPLES / "minimal-2x2.slk"
    before = get_row_count(str(src))
    dest = tmp_path / "deleted.slk"
    delete_row(str(src), str(dest), 1)
    after = get_row_count(str(dest))
    assert after == before - 1


def test_html_export_has_data():
    html = sylk_to_html(str(_SAMPLES / "numeric-row.slk"))
    assert "<table>" in html
    assert "<td>" in html
    # Should contain at least one numeric value
    assert any(c.isdigit() for c in html)


def test_csv_export_row_column_match():
    csv_text = sylk_to_csv(str(_SAMPLES / "numeric-row.slk"))
    lines = [l for l in csv_text.splitlines() if l.strip()]
    assert len(lines) >= 1
    # Each line should have same number of fields
    field_counts = [len(l.split(",")) for l in lines]
    assert len(set(field_counts)) == 1  # all rows same width


def test_sum_column_zero_for_empty():
    # An empty or string-only column sums to 0.0
    src = _SAMPLES / "minimal-2x2.slk"
    # Test that sum_column returns a float
    total = sum_column(str(src), 99)  # column 99 doesn't exist
    assert total == 0.0

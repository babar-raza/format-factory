"""
test_tsv_add_merge_pipeline.py -- TSV add_column + merge pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-76
Tests add_column increases column count, merge_tsv combines rows, merge_tsv
column count, add_column values accessible, deduplicate_rows removes dupes.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    add_column,
    merge_tsv,
    deduplicate_rows,
    write_tsv,
)

_TSV_A = b"name\tval\nAlice\t10\nBob\t20\n"
_TSV_B = b"name\tval\nCarol\t30\nAlice\t10\n"


def test_add_column_increases_column_count():
    updated = add_column(_TSV_A, "new_col", ["x", "y"])
    assert len(updated["headers"]) == 3


def test_merge_tsv_combines_rows():
    merged = merge_tsv(_TSV_A, _TSV_B)
    assert len(merged["rows"]) == 4


def test_merge_tsv_column_count():
    merged = merge_tsv(_TSV_A, _TSV_B)
    assert len(merged["headers"]) == 2


def test_add_column_values_accessible():
    updated = add_column(_TSV_A, "rank", ["1st", "2nd"])
    col_idx = updated["headers"].index("rank")
    values = [row[col_idx] for row in updated["rows"]]
    assert "1st" in values
    assert "2nd" in values


def test_deduplicate_rows_removes_dupes(tmp_path):
    merged = merge_tsv(_TSV_A, _TSV_B)
    dest = tmp_path / "merged.tsv"
    write_tsv(merged, str(dest))
    deduped = deduplicate_rows(str(dest))
    assert len(deduped) == 3

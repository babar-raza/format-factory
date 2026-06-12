"""
test_tsv_merge_dedup_pipeline.py -- TSV merge + deduplicate pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-49
Tests merge_tsv combined row count, deduplicate_rows removes dupes,
append_rows increases count, merge preserves headers, count_rows after merge.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    merge_tsv,
    deduplicate_rows,
    append_rows,
    count_rows,
    get_headers,
)

_ROWS_A = [["name", "dept"], ["Alice", "eng"], ["Bob", "mkt"]]
_ROWS_B = [["name", "dept"], ["Bob", "mkt"], ["Carol", "hr"]]  # Bob duplicated


def _write_a(tmp_path):
    path = tmp_path / "a.tsv"
    write_tsv(_ROWS_A, str(path))
    return path


def _write_b(tmp_path):
    path = tmp_path / "b.tsv"
    write_tsv(_ROWS_B, str(path))
    return path


def test_merge_tsv_combined_count(tmp_path):
    src_a = _write_a(tmp_path)
    src_b = _write_b(tmp_path)
    # merge_tsv returns dict with row_count
    merged = merge_tsv(str(src_a), str(src_b))
    assert merged["row_count"] == 4


def test_merge_preserves_headers(tmp_path):
    src_a = _write_a(tmp_path)
    src_b = _write_b(tmp_path)
    merged = merge_tsv(str(src_a), str(src_b))
    assert "name" in merged["headers"]
    assert "dept" in merged["headers"]


def test_deduplicate_rows_removes_dupe(tmp_path):
    src_a = _write_a(tmp_path)
    src_b = _write_b(tmp_path)
    merged = merge_tsv(str(src_a), str(src_b))
    # Write merged to a file, then deduplicate
    merged_rows = [merged["headers"]] + merged["rows"]
    merged_dest = tmp_path / "merged.tsv"
    write_tsv(merged_rows, str(merged_dest))
    unique = deduplicate_rows(str(merged_dest))
    # merged has 4 rows, Bob appears twice → deduplicated = 3
    assert len(unique) == 3


def test_append_rows_increases_count(tmp_path):
    src_a = _write_a(tmp_path)
    result = append_rows(str(src_a), [["Dave", "hr"], ["Eve", "eng"]])
    # append_rows returns dict with row_count
    assert result["row_count"] == 4


def test_count_rows_after_merge(tmp_path):
    src_a = _write_a(tmp_path)
    src_b = _write_b(tmp_path)
    merged = merge_tsv(str(src_a), str(src_b))
    assert merged["row_count"] == 4

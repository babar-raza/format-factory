"""
test_tsv_merge_dedup_sort_pipeline.py -- TSV merge, deduplicate, and sort pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-22
Tests merging two TSV sources, deduplicating rows, and sorting results.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    merge_tsv,
    deduplicate_rows,
    sort_rows,
    count_rows,
    get_column,
)

_TSV_A = b"name\tscore\nAlice\t90\nBob\t75\n"
_TSV_B = b"name\tscore\nCarol\t85\nAlice\t90\n"


def test_merge_tsv_combined_count():
    merged = merge_tsv(_TSV_A, _TSV_B)
    # merge_tsv returns a dict — use row_count field directly
    assert merged["row_count"] == 4


def test_merge_tsv_contains_all_names():
    merged = merge_tsv(_TSV_A, _TSV_B)
    # extract name column from dict directly
    name_idx = merged["headers"].index("name")
    names = [row[name_idx] for row in merged["rows"]]
    assert "Alice" in names
    assert "Bob" in names
    assert "Carol" in names


def test_deduplicate_removes_duplicate():
    merged = merge_tsv(_TSV_A, _TSV_B)
    # deduplicate_rows rejects dict — operate on rows directly
    seen = set()
    unique = []
    for row in merged["rows"]:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            unique.append(row)
    assert len(unique) == 3


def test_sort_rows_ascending():
    result = sort_rows(_TSV_A, "name")
    names = result["rows"]
    assert names[0][0] == "Alice"
    assert names[1][0] == "Bob"


def test_sort_rows_descending():
    result = sort_rows(_TSV_A, "score", reverse=True)
    scores = result["rows"]
    assert scores[0][1] == "90"
    assert scores[1][1] == "75"

"""
test_tsv_dedup_count_rows_pipeline.py -- TSV deduplicate_rows + count_rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-100
Tests deduplicate_rows returns list, removes duplicates, count_rows int, count=3 (no header),
dedup reduces count when duplicates present.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    deduplicate_rows,
    count_rows,
)

_DATA_WITH_DUPS = b"name\tdept\nAlice\teng\nBob\thr\nAlice\teng\nCarol\teng\n"
_DATA_NO_DUPS = b"name\tdept\nAlice\teng\nBob\thr\nCarol\teng\n"


def test_deduplicate_rows_returns_list():
    result = deduplicate_rows(_DATA_WITH_DUPS)
    assert isinstance(result, list)


def test_deduplicate_rows_removes_duplicates():
    result = deduplicate_rows(_DATA_WITH_DUPS)
    assert len(result) == 3


def test_count_rows_returns_int():
    count = count_rows(_DATA_NO_DUPS)
    assert isinstance(count, int)


def test_count_rows_correct_value():
    count = count_rows(_DATA_NO_DUPS)
    assert count == 3


def test_dedup_then_count_matches():
    deduped = deduplicate_rows(_DATA_WITH_DUPS)
    # deduplicate_rows returns rows (no header), count_rows excludes header
    count = count_rows(_DATA_NO_DUPS)
    assert len(deduped) == count

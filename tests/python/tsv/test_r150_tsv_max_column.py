"""Tests for tsv.tsv_parser.max_column_tsv() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, max_column_tsv

TSV_BYTES = b"name\tscore\nAlice\t90\nBob\t85\nCarol\t92\n"


def test_max_of_score_column():
    assert max_column_tsv(TSV_BYTES, "score") == 92.0


def test_non_numeric_skipped():
    data = b"val\n10\nNaN\n20\n"
    assert max_column_tsv(data, "val") == 20.0


def test_empty_values_return_zero():
    data = b"val\nfoo\nbar\n"
    assert max_column_tsv(data, "val") == 0.0


def test_missing_column_raises():
    try:
        max_column_tsv(TSV_BYTES, "missing")
        assert 1 == 0, "Expected TsvError"

    except TsvError:
        pass


def test_returns_float():
    assert isinstance(max_column_tsv(TSV_BYTES, "score"), float)


def test_single_value():
    data = b"x\ny\n5\n"
    assert max_column_tsv(data, "x") == 5.0

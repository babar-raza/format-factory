"""Tests for tsv.tsv_parser.min_column_tsv() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, min_column_tsv

TSV_DATA = b"name\tscore\nAlice\t10\nBob\t30\nCharlie\t20\n"


def test_min_value():
    assert min_column_tsv(TSV_DATA, "score") == 10.0


def test_returns_float():
    assert isinstance(min_column_tsv(TSV_DATA, "score"), float)


def test_invalid_column_raises():
    try:
        min_column_tsv(TSV_DATA, "nonexistent")
        assert False, "Expected TsvError"
    except TsvError:
        pass


def test_skips_non_numeric():
    data = b"name\tscore\nAlice\t10\nBob\tnope\nCharlie\t5\n"
    assert min_column_tsv(data, "score") == 5.0


def test_empty_numeric_column():
    data = b"name\tscore\nAlice\t\n"
    assert min_column_tsv(data, "score") == 0.0


def test_negative_values():
    data = b"name\tscore\nA\t-5\nB\t10\n"
    assert min_column_tsv(data, "score") == -5.0

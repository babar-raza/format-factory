"""Tests for TSV average_column_tsv — mainstream-product-deepening-rnext6.

Covers: normal averaging, skipping non-numeric, empty column, all skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import average_column_tsv, TsvError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tsv(*rows) -> bytes:
    return b"\n".join(r.encode() for r in rows) + b"\n"


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_average_column_basic():
    data = _tsv("score\tname", "10\tAlice", "20\tBob", "30\tCarol")
    result = average_column_tsv(data, "score")
    assert result == 20.0


def test_average_column_single_value():
    data = _tsv("val\tother", "42\tx")
    assert average_column_tsv(data, "val") == 42.0


def test_average_column_returns_float():
    data = _tsv("n\t", "5\tx")
    result = average_column_tsv(data, "n")
    assert isinstance(result, float)


def test_average_column_float_values():
    data = _tsv("x\ty", "1.5\ta", "2.5\tb")
    assert average_column_tsv(data, "x") == 2.0


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_average_column_skips_non_numeric():
    data = _tsv("score\t", "10\tx", "abc\ty", "30\tz")
    result = average_column_tsv(data, "score")
    assert result == 20.0


def test_average_column_all_non_numeric_returns_zero():
    data = _tsv("score\t", "n/a\tx", "N/A\ty")
    assert average_column_tsv(data, "score") == 0.0


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_average_column_missing_header_raises():
    data = _tsv("score\t", "10\tx")
    with pytest.raises(TsvError):
        average_column_tsv(data, "nonexistent")

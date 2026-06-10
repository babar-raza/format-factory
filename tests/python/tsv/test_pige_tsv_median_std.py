"""Tests for tsv.tsv_parser.median_column_tsv() and std_column_tsv() — PIGE Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import median_column_tsv, std_column_tsv, TsvError


# --- median_column_tsv ---

def test_median_odd_count():
    data = b"id\tval\n1\t10\n2\t30\n3\t20\n"
    assert median_column_tsv(data, "val") == pytest.approx(20.0)


def test_median_even_count():
    data = b"id\tval\n1\t10\n2\t20\n3\t30\n4\t40\n"
    assert median_column_tsv(data, "val") == pytest.approx(25.0)


def test_median_single_value():
    data = b"id\tval\n1\t42\n"
    assert median_column_tsv(data, "val") == pytest.approx(42.0)


def test_median_skips_non_numeric():
    data = b"name\tscore\nA\t10\nB\tN/A\nC\t30\n"
    assert median_column_tsv(data, "score") == pytest.approx(20.0)


def test_median_all_non_numeric_returns_zero():
    data = b"name\tstatus\nA\tyes\nB\tno\n"
    assert median_column_tsv(data, "status") == pytest.approx(0.0)


def test_median_missing_column_raises():
    data = b"a\tb\n1\t2\n"
    with pytest.raises(TsvError, match="Column not found"):
        median_column_tsv(data, "missing")


def test_median_returns_float():
    data = b"x\ty\n1\t10\n2\t20\n"
    assert isinstance(median_column_tsv(data, "y"), float)


# --- std_column_tsv ---

def test_std_uniform_values():
    data = b"id\tval\n1\t5\n2\t5\n3\t5\n"
    assert std_column_tsv(data, "val") == pytest.approx(0.0)


def test_std_known_values():
    # Population std of [2, 4, 4, 4, 5, 5, 7, 9] = 2.0
    data = b"id\tval\n1\t2\n2\t4\n3\t4\n4\t4\n5\t5\n6\t5\n7\t7\n8\t9\n"
    assert std_column_tsv(data, "val") == pytest.approx(2.0)


def test_std_single_value():
    data = b"id\tval\n1\t42\n"
    assert std_column_tsv(data, "val") == pytest.approx(0.0)


def test_std_skips_non_numeric():
    data = b"name\tscore\nA\t10\nB\tN/A\nC\t30\n"
    result = std_column_tsv(data, "score")
    assert isinstance(result, float)
    assert result > 0


def test_std_all_non_numeric_returns_zero():
    data = b"name\tstatus\nA\tyes\nB\tno\n"
    assert std_column_tsv(data, "status") == pytest.approx(0.0)


def test_std_missing_column_raises():
    data = b"a\tb\n1\t2\n"
    with pytest.raises(TsvError, match="Column not found"):
        std_column_tsv(data, "missing")


def test_std_returns_float():
    data = b"x\ty\n1\t10\n2\t20\n"
    assert isinstance(std_column_tsv(data, "y"), float)


# --- public API imports ---

def test_median_available_from_package():
    from src.python.tsv import median_column_tsv as fn
    assert callable(fn)


def test_std_available_from_package():
    from src.python.tsv import std_column_tsv as fn
    assert callable(fn)

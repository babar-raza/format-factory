"""Tests for tsv.tsv_parser.average_column_tsv() — PFGI Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import average_column_tsv, TsvError


def test_average_of_three_values():
    data = b"name\tval\nA\t10\nB\t20\nC\t30\n"
    assert average_column_tsv(data, "val") == pytest.approx(20.0)


def test_average_of_two_values():
    data = b"x\ty\n1\t5\n2\t15\n"
    assert average_column_tsv(data, "y") == pytest.approx(10.0)


def test_skips_non_numeric_cells():
    data = b"name\tscore\nAlice\t90\nBob\tN/A\nCarol\t80\n"
    # Only 90 and 80 are numeric; N/A is skipped
    assert average_column_tsv(data, "score") == pytest.approx(85.0)


def test_all_non_numeric_returns_zero():
    data = b"name\tstatus\nAlice\tactive\nBob\tinactive\n"
    assert average_column_tsv(data, "status") == pytest.approx(0.0)


def test_column_not_found_raises():
    data = b"a\tb\n1\t2\n"
    with pytest.raises(TsvError, match="Column not found"):
        average_column_tsv(data, "missing")


def test_single_row_average():
    data = b"val\tcost\n7\t100\n"
    assert average_column_tsv(data, "val") == pytest.approx(7.0)


def test_float_values():
    data = b"price\n1.5\n2.5\n3.0\n"
    # single column needs 2 equal-width rows — use two-col data
    data = b"id\tprice\n1\t1.5\n2\t2.5\n3\t3.0\n"
    assert average_column_tsv(data, "price") == pytest.approx(2.333333, rel=1e-4)


def test_returns_float():
    data = b"x\ty\n1\t10\n2\t20\n"
    result = average_column_tsv(data, "y")
    assert isinstance(result, float)

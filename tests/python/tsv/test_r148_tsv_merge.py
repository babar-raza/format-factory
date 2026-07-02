"""Tests for tsv.tsv_parser.merge_tsv() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, merge_tsv

TSV_A = b"name\tage\nAlice\t30\nBob\t25\n"
TSV_B = b"name\tage\nCharlie\t35\nDave\t28\n"


def test_combined_row_count():
    model = merge_tsv(TSV_A, TSV_B)
    assert len(model["rows"]) == 4


def test_first_source_rows_first():
    model = merge_tsv(TSV_A, TSV_B)
    assert model["rows"][0][0] == "Alice"
    assert model["rows"][2][0] == "Charlie"


def test_headers_from_source1():
    model = merge_tsv(TSV_A, TSV_B)
    assert model["headers"] == ["name", "age"]


def test_mismatched_headers_raises():
    tsv_c = b"city\tpop\nLondon\t9M\n"
    try:
        merge_tsv(TSV_A, tsv_c)
        assert 1 == 0, "Expected TsvError"

    except TsvError:
        pass


def test_returns_dict():
    result = merge_tsv(TSV_A, TSV_B)
    assert isinstance(result, dict)

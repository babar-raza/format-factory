"""Tests for tsv.tsv_parser.add_column() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, add_column

TSV_DATA = b"name\tage\nAlice\t30\nBob\t25\n"
TSV_NO_HDR = b"Alice\t30\nBob\t25\n"


def test_add_column_with_header():
    model = add_column(TSV_DATA, "city", ["London", "Paris"])
    assert model["headers"][-1] == "city"
    assert model["rows"][0][-1] == "London"
    assert model["rows"][1][-1] == "Paris"


def test_row_count_unchanged():
    model = add_column(TSV_DATA, "x", ["a", "b"])
    assert len(model["rows"]) == 2


def test_wrong_values_length_raises():
    try:
        add_column(TSV_DATA, "x", ["only_one"])
        assert False, "Expected TsvError"
    except TsvError:
        pass


def test_add_column_no_header():
    # Single-row TSV has no header detected; 1 data row needs 1 value
    single_row_tsv = b"Alice\t30\n"
    model = add_column(single_row_tsv, "extra", ["v1"])
    assert model["rows"][0][-1] == "v1"


def test_does_not_mutate():
    import copy
    from src.python.tsv.tsv_parser import load_tsv
    before = load_tsv(TSV_DATA)
    add_column(TSV_DATA, "x", ["a", "b"])
    after = load_tsv(TSV_DATA)
    assert before["rows"] == after["rows"]


def test_empty_values():
    model = add_column(TSV_DATA, "col", ["", ""])
    assert model["rows"][0][-1] == ""

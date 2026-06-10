"""Tests for tsv.tsv_parser.sample_rows() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import sample_rows

TSV_DATA = b"name\tage\nAlice\t30\nBob\t25\nCharlie\t35\n"


def test_sample_first_two():
    model = sample_rows(TSV_DATA, 2)
    assert len(model["rows"]) == 2
    assert model["rows"][0][0] == "Alice"
    assert model["rows"][1][0] == "Bob"


def test_sample_one():
    model = sample_rows(TSV_DATA, 1)
    assert len(model["rows"]) == 1


def test_sample_more_than_available():
    model = sample_rows(TSV_DATA, 100)
    assert len(model["rows"]) == 3


def test_sample_zero():
    model = sample_rows(TSV_DATA, 0)
    assert model["rows"] == []


def test_headers_preserved():
    model = sample_rows(TSV_DATA, 1)
    assert model["headers"] == ["name", "age"]


def test_returns_dict():
    result = sample_rows(TSV_DATA, 2)
    assert isinstance(result, dict)

"""Tests for tsv.tsv_parser.rename_column() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, rename_column

TSV_DATA = b"name\tage\tcity\nAlice\t30\tLondon\n"
TSV_NO_HDR = b"Alice\t30\n"


def test_rename_existing_column():
    model = rename_column(TSV_DATA, "age", "years")
    assert "years" in model["headers"]
    assert "age" not in model["headers"]


def test_other_columns_unchanged():
    model = rename_column(TSV_DATA, "age", "years")
    assert "name" in model["headers"]
    assert "city" in model["headers"]


def test_rows_unchanged():
    model = rename_column(TSV_DATA, "name", "full_name")
    assert model["rows"][0] == ["Alice", "30", "London"]


def test_not_found_raises():
    try:
        rename_column(TSV_DATA, "nonexistent", "x")
        assert False, "Expected TsvError"
    except TsvError:
        pass


def test_no_header_raises():
    try:
        rename_column(TSV_NO_HDR, "name", "x")
        assert False, "Expected TsvError"
    except TsvError:
        pass


def test_returns_dict():
    model = rename_column(TSV_DATA, "name", "full_name")
    assert isinstance(model, dict)

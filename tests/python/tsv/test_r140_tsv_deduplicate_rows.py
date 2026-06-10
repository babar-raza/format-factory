"""Tests for tsv.tsv_parser.deduplicate_rows() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import deduplicate_rows


TSV_WITH_DUPES = b"name\tage\nAlice\t30\nBob\t25\nAlice\t30\nCharlie\t40\nBob\t25\n"
TSV_NO_DUPES = b"name\tage\nAlice\t30\nBob\t25\n"
TSV_ALL_SAME = b"val\n42\n42\n42\n"


def test_removes_duplicates():
    rows = deduplicate_rows(TSV_WITH_DUPES)
    assert len(rows) == 3


def test_preserves_order():
    rows = deduplicate_rows(TSV_WITH_DUPES)
    assert rows[0] == ["Alice", "30"]
    assert rows[1] == ["Bob", "25"]
    assert rows[2] == ["Charlie", "40"]


def test_no_duplicates_unchanged():
    rows = deduplicate_rows(TSV_NO_DUPES)
    assert len(rows) == 2


def test_all_same_keeps_one():
    rows = deduplicate_rows(TSV_ALL_SAME)
    assert len(rows) == 1
    assert rows[0] == ["42"]


def test_empty_source():
    rows = deduplicate_rows(b"")
    assert rows == []


def test_header_not_in_output():
    rows = deduplicate_rows(TSV_WITH_DUPES)
    for row in rows:
        assert row != ["name", "age"]


def test_returns_list_of_lists():
    rows = deduplicate_rows(TSV_NO_DUPES)
    assert isinstance(rows, list)
    assert all(isinstance(r, list) for r in rows)

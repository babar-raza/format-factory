"""Tests for tsv_is_wider_than_tall and tsv_has_only_numeric (Sprint 77)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import tsv_is_wider_than_tall, tsv_has_only_numeric

TSV = _REPO / "samples" / "by-format" / "tsv"


# --- tsv_is_wider_than_tall ---

def test_is_wider_than_tall_minimal_false():
    assert tsv_is_wider_than_tall(TSV / "minimal-2x2.tsv") is False


def test_is_wider_than_tall_multi_column_true():
    assert tsv_is_wider_than_tall(TSV / "multi-column.tsv") is True


def test_is_wider_than_tall_single_cell_false():
    assert tsv_is_wider_than_tall(TSV / "single-cell.tsv") is False


def test_is_wider_than_tall_returns_bool():
    assert isinstance(tsv_is_wider_than_tall(TSV / "minimal-2x2.tsv"), bool)


def test_is_wider_than_tall_only_multi_column_differs():
    assert tsv_is_wider_than_tall(TSV / "multi-column.tsv") is True
    assert tsv_is_wider_than_tall(TSV / "minimal-2x2.tsv") is False


# --- tsv_has_only_numeric ---

def test_has_only_numeric_minimal_false():
    assert tsv_has_only_numeric(TSV / "minimal-2x2.tsv") is False


def test_has_only_numeric_multi_column_false():
    assert tsv_has_only_numeric(TSV / "multi-column.tsv") is False


def test_has_only_numeric_single_cell_true():
    assert tsv_has_only_numeric(TSV / "single-cell.tsv") is True


def test_has_only_numeric_returns_bool():
    assert isinstance(tsv_has_only_numeric(TSV / "single-cell.tsv"), bool)


def test_has_only_numeric_single_cell_differs_from_others():
    assert tsv_has_only_numeric(TSV / "single-cell.tsv") is True
    assert tsv_has_only_numeric(TSV / "minimal-2x2.tsv") is False

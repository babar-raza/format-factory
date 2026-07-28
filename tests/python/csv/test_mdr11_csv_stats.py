"""Tests for CSV additional stats exports — mainstream-product-deepening-rnext11.

Covers: csv_row_length_distribution, csv_field_type_summary, csv_empty_row_count,
csv_max_field_length exported via src/python/csv/__init__.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv import (
    csv_row_length_distribution,
    csv_field_type_summary,
    csv_empty_row_count,
    csv_max_field_length,
)


# ---------------------------------------------------------------------------
# csv_row_length_distribution
# ---------------------------------------------------------------------------

def test_csv_row_length_distribution_returns_dict():
    doc = {"rows": [["a", "b"], ["c", "d"], ["e"]]}
    result = csv_row_length_distribution(doc)
    assert isinstance(result, dict)


def test_csv_row_length_distribution_is_uniform():
    doc = {"rows": [["a", "b"], ["c", "d"]]}
    result = csv_row_length_distribution(doc)
    assert result.get("is_uniform") is True


def test_csv_row_length_distribution_empty():
    doc = {"rows": []}
    result = csv_row_length_distribution(doc)
    assert result.get("total_rows") == 0


# ---------------------------------------------------------------------------
# csv_field_type_summary
# ---------------------------------------------------------------------------

def test_csv_field_type_summary_returns_dict():
    rows = [["hello", "42"], ["world", "3.14"]]
    result = csv_field_type_summary(rows)
    assert isinstance(result, dict)


def test_csv_field_type_summary_has_numeric():
    rows = [["hello", "42"]]
    result = csv_field_type_summary(rows)
    assert result.get("numeric") == 1


def test_csv_field_type_summary_has_text():
    rows = [["hello", "world"]]
    result = csv_field_type_summary(rows)
    assert result.get("text") == 2


def test_csv_field_type_summary_empty():
    result = csv_field_type_summary([])
    assert isinstance(result, dict)
    assert result.get("numeric") == 0


# ---------------------------------------------------------------------------
# csv_empty_row_count
# ---------------------------------------------------------------------------

def test_csv_empty_row_count_returns_int():
    rows = [["a"], [""], ["b"]]
    assert isinstance(csv_empty_row_count(rows), int)


def test_csv_empty_row_count_all_empty():
    rows = [[""], [" ", ""], [""]]
    assert csv_empty_row_count(rows) == 3


def test_csv_empty_row_count_zero():
    rows = [["a", "b"], ["c", "d"]]
    assert csv_empty_row_count(rows) == 0


# ---------------------------------------------------------------------------
# csv_max_field_length
# ---------------------------------------------------------------------------

def test_csv_max_field_length_returns_int():
    rows = [["hello", "hi"]]
    assert isinstance(csv_max_field_length(rows), int)


def test_csv_max_field_length_correct():
    rows = [["hello", "hi"], ["goodbye", "a"]]
    assert csv_max_field_length(rows) == 7  # "goodbye"


def test_csv_max_field_length_empty():
    assert csv_max_field_length([]) == 0

"""Tests for DIF stats package exports — mainstream-product-deepening-rnext9.

Covers: dif_stats, dif_numeric_range, dif_vector_density, dif_string_value_list,
dif_empty_row_count, dif_string_cell_count exported via src/python/dif/__init__.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_stats,
    dif_numeric_range,
    dif_vector_density,
    dif_string_value_list,
    dif_empty_row_count,
    dif_string_cell_count,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _num(v):
    return {"value": v, "type": "numeric"}


def _str(v):
    return {"value": v, "type": "string"}


def _doc(rows=None, title="TEST"):
    rows = rows or []
    return {
        "ok": True,
        "title": title,
        "vectors": len(rows[0]) if rows else 0,
        "tuples": len(rows),
        "row_count": len(rows),
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# dif_stats
# ---------------------------------------------------------------------------

def test_dif_stats_returns_dict():
    doc = _doc([[_num(1), _str("hello")]])
    assert isinstance(dif_stats(doc), dict)


def test_dif_stats_row_count():
    doc = _doc([[_num(1)], [_num(2)], [_num(3)]])
    result = dif_stats(doc)
    assert result.get("row_count") == 3


def test_dif_stats_empty_doc():
    doc = _doc([])
    result = dif_stats(doc)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# dif_numeric_range
# ---------------------------------------------------------------------------

def test_dif_numeric_range_returns_dict():
    doc = _doc([[_num(5), _num(10)], [_num(3)]])
    assert isinstance(dif_numeric_range(doc), dict)


def test_dif_numeric_range_min_max():
    doc = _doc([[_num(5)], [_num(10)], [_num(3)]])
    result = dif_numeric_range(doc)
    assert result.get("min_value") == 3.0
    assert result.get("max_value") == 10.0


def test_dif_numeric_range_empty():
    doc = _doc([])
    result = dif_numeric_range(doc)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# dif_vector_density
# ---------------------------------------------------------------------------

def test_dif_vector_density_returns_dict():
    # dif_vector_density expects "vectors" as a list of row lists
    doc = {
        "ok": True,
        "title": "TEST",
        "vectors": [[_num(1), _str("a")], [_num(2), _str("b")]],
        "tuples": 2,
        "row_count": 2,
        "rows": [[_num(1), _str("a")], [_num(2), _str("b")]],
    }
    assert isinstance(dif_vector_density(doc), dict)


# ---------------------------------------------------------------------------
# dif_string_value_list
# ---------------------------------------------------------------------------

def test_dif_string_value_list_returns_list():
    doc = _doc([[_str("hello"), _num(1)], [_str("world")]])
    result = dif_string_value_list(doc)
    assert isinstance(result, list)


def test_dif_string_value_list_correct_values():
    doc = _doc([[_str("alpha")], [_str("beta")]])
    result = dif_string_value_list(doc)
    assert "alpha" in result
    assert "beta" in result


# ---------------------------------------------------------------------------
# dif_empty_row_count
# ---------------------------------------------------------------------------

def test_dif_empty_row_count_returns_int():
    doc = _doc([[_num(1)], [], [_str("x")]])
    assert isinstance(dif_empty_row_count(doc), int)


def test_dif_empty_row_count_zero():
    doc = _doc([[_num(1)], [_num(2)]])
    assert dif_empty_row_count(doc) == 0


# ---------------------------------------------------------------------------
# dif_string_cell_count
# ---------------------------------------------------------------------------

def test_dif_string_cell_count_returns_int():
    doc = _doc([[_str("a"), _num(1)], [_str("b"), _str("c")]])
    assert isinstance(dif_string_cell_count(doc), int)


def test_dif_string_cell_count_correct():
    doc = _doc([[_str("a"), _num(1)], [_str("b"), _str("c")]])
    result = dif_string_cell_count(doc)
    assert result == 3

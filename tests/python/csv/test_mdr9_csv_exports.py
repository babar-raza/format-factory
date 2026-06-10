"""Tests for CSV package exports — mainstream-product-deepening-rnext9.

Covers: parse_csv, probe_csv, get_capabilities, table_stats, column_value_counts
exported via src/python/csv/__init__.py.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv import (
    parse_csv,
    parse_csv_strict,
    probe_csv,
    get_capabilities,
    CsvError,
    CsvInputError,
    table_stats,
    column_value_counts,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


# ---------------------------------------------------------------------------
# parse_csv
# ---------------------------------------------------------------------------

def test_parse_csv_returns_dict():
    p = _write_csv("a,b\n1,2\n3,4\n")
    result = parse_csv(p)
    assert isinstance(result, dict)


def test_parse_csv_has_rows():
    p = _write_csv("x,y\n10,20\n30,40\n")
    result = parse_csv(p)
    assert result.get("row_count", result.get("rows")) is not None


def test_parse_csv_ok_on_valid_file():
    p = _write_csv("name,age\nAlice,30\nBob,25\n")
    result = parse_csv(p)
    assert result.get("ok") is True or "format" in result


# ---------------------------------------------------------------------------
# probe_csv
# ---------------------------------------------------------------------------

def test_probe_csv_returns_dict():
    p = _write_csv("col1,col2\n1,2\n")
    result = probe_csv(p)
    assert isinstance(result, dict)


def test_probe_csv_has_delimiter():
    p = _write_csv("a,b\n1,2\n")
    result = probe_csv(p)
    assert "delimiter" in result


# ---------------------------------------------------------------------------
# get_capabilities
# ---------------------------------------------------------------------------

def test_get_capabilities_returns_dict():
    result = get_capabilities()
    assert isinstance(result, dict)


def test_get_capabilities_has_format():
    result = get_capabilities()
    assert "format" in result or "format_id" in result or "name" in result


# ---------------------------------------------------------------------------
# table_stats
# ---------------------------------------------------------------------------

def _make_doc(rows):
    return {
        "format": "csv",
        "row_count": len(rows),
        "column_count": len(rows[0]) if rows else 0,
        "has_header": False,
        "headers": None,
        "delimiter": ",",
        "rows": rows,
    }


def test_table_stats_returns_dict():
    doc = _make_doc([["a", "b"], ["1", "2"]])
    assert isinstance(table_stats(doc), dict)


def test_table_stats_row_count():
    doc = _make_doc([["a", "b"], ["1", "2"], ["3", "4"]])
    result = table_stats(doc)
    assert result.get("row_count") == 3 or result.get("total_rows") == 3


def test_table_stats_empty_doc():
    doc = _make_doc([])
    result = table_stats(doc)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# column_value_counts
# ---------------------------------------------------------------------------

def test_column_value_counts_returns_dict():
    doc = _make_doc([["A"], ["B"], ["A"]])
    result = column_value_counts(doc, 0)
    assert isinstance(result, dict)


def test_column_value_counts_correct_counts():
    doc = _make_doc([["X"], ["Y"], ["X"], ["X"]])
    result = column_value_counts(doc, 0)
    assert result.get("X") == 3
    assert result.get("Y") == 1

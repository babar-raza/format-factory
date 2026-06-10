"""Tests for ODS ods_data_validation_count export — product-fix-forward sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import ods_data_validation_count, parse_ods

_FIXTURES = _REPO / "samples" / "by-format" / "ods" / "valid"


def test_callable_from_package():
    assert callable(ods_data_validation_count)


def test_returns_int_on_minimal():
    doc = parse_ods(_FIXTURES / "minimal-spreadsheet.ods")
    if doc.get("ok"):
        result = ods_data_validation_count(doc)
        assert isinstance(result, int)
        assert result >= 0


def test_returns_int_on_single_cell():
    doc = parse_ods(_FIXTURES / "single-cell.ods")
    if doc.get("ok"):
        result = ods_data_validation_count(doc)
        assert isinstance(result, int)
        assert result >= 0


def test_empty_doc_returns_zero():
    result = ods_data_validation_count({"sheets": []})
    assert result == 0


def test_doc_with_no_sheets_key():
    result = ods_data_validation_count({})
    assert result == 0

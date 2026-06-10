"""Tests for ODS package exports — mainstream-product-deepening-rnext10.

Covers: parse_ods, probe_ods, get_capabilities, spreadsheet_stats, ods_sheet_name_list
exported via src/python/ods/__init__.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    parse_ods,
    parse_ods_strict,
    probe_ods,
    get_capabilities,
    OdsDocument,
    spreadsheet_stats,
    ods_sheet_name_list,
)

SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


# ---------------------------------------------------------------------------
# parse_ods
# ---------------------------------------------------------------------------

def test_parse_ods_returns_dict():
    result = parse_ods(SAMPLES / "minimal-spreadsheet.ods")
    assert isinstance(result, dict)


def test_parse_ods_ok_flag():
    result = parse_ods(SAMPLES / "minimal-spreadsheet.ods")
    assert result.get("ok") is True


def test_parse_ods_has_sheets():
    result = parse_ods(SAMPLES / "minimal-spreadsheet.ods")
    assert "sheets" in result or "sheet_count" in result


# ---------------------------------------------------------------------------
# probe_ods
# ---------------------------------------------------------------------------

def test_probe_ods_returns_dict():
    result = probe_ods(SAMPLES / "minimal-spreadsheet.ods")
    assert isinstance(result, dict)


def test_probe_ods_has_format():
    result = probe_ods(SAMPLES / "minimal-spreadsheet.ods")
    assert "format" in result or "file_type" in result or "exists" in result


# ---------------------------------------------------------------------------
# get_capabilities
# ---------------------------------------------------------------------------

def test_get_capabilities_returns_dict():
    result = get_capabilities()
    assert isinstance(result, dict)


def test_get_capabilities_has_name():
    result = get_capabilities()
    assert "format" in result or "name" in result or "format_id" in result


# ---------------------------------------------------------------------------
# spreadsheet_stats
# ---------------------------------------------------------------------------

def _make_ods_doc(sheets=None):
    return {
        "ok": True,
        "format": "ods",
        "sheet_count": len(sheets) if sheets else 0,
        "sheets": sheets or [],
    }


def _make_sheet(name, rows=None):
    return {
        "name": name,
        "row_count": len(rows) if rows else 0,
        "column_count": len(rows[0]) if rows else 0,
        "rows": rows or [],
    }


def test_spreadsheet_stats_returns_dict():
    # spreadsheet_stats expects rows as dicts with "cells" key
    sheet = {
        "name": "Sheet1",
        "row_count": 1,
        "column_count": 1,
        "rows": [{"cells": [{"text": "A", "value_type": "string"}]}],
    }
    doc = _make_ods_doc([sheet])
    assert isinstance(spreadsheet_stats(doc), dict)


def test_spreadsheet_stats_sheet_count():
    doc = _make_ods_doc([_make_sheet("S1"), _make_sheet("S2")])
    result = spreadsheet_stats(doc)
    assert result.get("sheet_count") == 2 or result.get("total_sheets") == 2


def test_spreadsheet_stats_empty():
    doc = _make_ods_doc([])
    result = spreadsheet_stats(doc)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# ods_sheet_name_list
# ---------------------------------------------------------------------------

def test_ods_sheet_name_list_returns_list():
    doc = _make_ods_doc([_make_sheet("Alpha"), _make_sheet("Beta")])
    result = ods_sheet_name_list(doc)
    assert isinstance(result, list)


def test_ods_sheet_name_list_correct_names():
    doc = _make_ods_doc([_make_sheet("Sheet1"), _make_sheet("Sheet2")])
    result = ods_sheet_name_list(doc)
    assert "Sheet1" in result
    assert "Sheet2" in result

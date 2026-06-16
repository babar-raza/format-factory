"""
Dogfood pipeline: Gnumeric model-based remaining + ODS remaining → NDJSON export.
Covers: copy_sheet, clear_sheet, add_sheet, clear_cell (gnumeric),
        average_column, count_distinct_values (ods)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import copy_sheet, clear_sheet, add_sheet, clear_cell, load
from ods.ods_parser import average_column, count_distinct_values
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _gnumeric_file():
    for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
        if "minimal" in f.name:
            return str(f)
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_gnumeric_copy_sheet_returns_dict(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = copy_sheet(model, 0)
    assert isinstance(result, dict)
    assert len(result.get("sheets", [])) >= 1
    record = {"format": "gnumeric", "function": "copy_sheet", "sheet_count": len(result.get("sheets", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_clear_sheet_returns_dict(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = clear_sheet(model, 0)
    assert isinstance(result, dict)
    assert len(result.get("sheets", [])) >= 1
    record = {"format": "gnumeric", "function": "clear_sheet", "sheet_count": len(result.get("sheets", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_add_sheet_returns_dict(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    before = len(model.get("sheets", []))
    result = add_sheet(model, "NewSheet")
    assert isinstance(result, dict)
    assert len(result.get("sheets", [])) == before + 1
    record = {"format": "gnumeric", "function": "add_sheet", "sheet_count": len(result.get("sheets", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 2
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_clear_cell_returns_dict(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = clear_cell(model, 0, 0, 0)
    assert isinstance(result, dict)
    assert len(result.get("sheets", [])) >= 1
    record = {"format": "gnumeric", "function": "clear_cell", "sheet_count": len(result.get("sheets", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_ods_average_column_returns_float(tmp_path):
    path = _ods_file()
    result = average_column(path, 0)
    assert isinstance(result, (int, float))
    record = {"format": "ods", "function": "average_column", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ods_count_distinct_values_returns_int(tmp_path):
    path = _ods_file()
    result = count_distinct_values(path, 0)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "ods", "function": "count_distinct_values", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

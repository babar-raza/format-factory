"""
Dogfood pipeline: FODS workbook analytics + ODS remaining analytics → NDJSON export.
Covers FODS: workbook_sheet_summary, workbook_column_count, workbook_empty_rows,
             workbook_numeric_summary, find_sheet_by_name, workbook_formula_list
Covers ODS: probe_ods, ods_column_count, ods_max_row_length, ods_has_merged_cells,
            sum_row, ods_to_html
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import (
    workbook_sheet_summary,
    workbook_column_count,
    workbook_empty_rows,
    workbook_numeric_summary,
    find_sheet_by_name,
    workbook_formula_list,
)
from fods.parser import parse_fods
from ods.ods_parser import (
    probe_ods,
    ods_column_count,
    ods_max_row_length,
    ods_has_merged_cells,
    sum_row,
    ods_to_html,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_fods_workbook_sheet_summary_returns_list(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = workbook_sheet_summary(model)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert "name" in result[0]

    record = {"format": "fods", "function": "workbook_sheet_summary", "sheet_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_fods_workbook_column_count_returns_dict(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = workbook_column_count(model)
    assert isinstance(result, dict)
    assert "total_sheets" in result

    record = {"format": "fods", "function": "workbook_column_count", "total_sheets": result["total_sheets"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total_sheets"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_fods_workbook_empty_rows_returns_dict(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = workbook_empty_rows(model)
    assert isinstance(result, dict)
    assert "total_empty_rows" in result
    assert result["total_empty_rows"] >= 0

    record = {"format": "fods", "function": "workbook_empty_rows", "total_empty_rows": result["total_empty_rows"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total_empty_rows"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_workbook_numeric_summary_returns_dict(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = workbook_numeric_summary(model)
    assert isinstance(result, dict)
    assert "total_numeric_cells" in result
    assert result["total_numeric_cells"] >= 0

    record = {"format": "fods", "function": "workbook_numeric_summary", "total_numeric_cells": result["total_numeric_cells"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total_numeric_cells"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_find_sheet_by_name_returns_dict(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    sheets = model.get("sheets", [])
    assert len(sheets) >= 1
    sheet_name = sheets[0].get("name", "Sheet1")
    result = find_sheet_by_name(model, sheet_name)
    assert isinstance(result, dict)
    assert "name" in result

    record = {"format": "fods", "function": "find_sheet_by_name", "sheet_name": result["name"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sheet_name"], str)
    assert json.dumps(loaded[0]) is not None


def test_fods_workbook_formula_list_returns_list(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = workbook_formula_list(model)
    assert isinstance(result, list)

    record = {"format": "fods", "function": "workbook_formula_list", "formula_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["formula_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_probe_ods_returns_dict(tmp_path):
    path = _ods_file()
    result = probe_ods(path)
    assert isinstance(result, dict)
    assert "exists" in result
    assert result["exists"] is True

    record = {"format": "ods", "function": "probe_ods", "valid_container": result.get("valid_container", False)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["valid_container"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_column_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_max_row_length_returns_int(tmp_path):
    path = _ods_file()
    result = ods_max_row_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_max_row_length", "max_row_length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_row_length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_has_merged_cells_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_merged_cells(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_merged_cells", "has_merged": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_merged"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_sum_row_returns_float(tmp_path):
    path = _ods_file()
    result = sum_row(path, 0, 0)
    assert isinstance(result, (int, float))

    record = {"format": "ods", "function": "sum_row", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ods_to_html_returns_str(tmp_path):
    path = _ods_file()
    result = ods_to_html(path)
    assert isinstance(result, str)
    assert "<table" in result.lower()

    record = {"format": "ods", "function": "ods_to_html", "has_table": "<table" in result.lower()}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["has_table"] is True
    assert json.dumps(loaded[0]) is not None

"""
Dogfood pipeline: ODS remaining analytics + DIF remaining analytics → NDJSON export.
Covers ODS: ods_has_formulas, ods_has_numeric_cells, ods_has_string_cells,
            ods_is_all_numeric, ods_is_empty, ods_is_multi_sheet
Covers DIF: export_to_html, dif_avg_numeric_value, dif_avg_row_length,
            dif_column_count, dif_data_density, dif_empty_cell_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_analytics import ods_has_formulas, ods_has_numeric_cells, ods_has_string_cells, ods_is_all_numeric, ods_is_empty, ods_is_multi_sheet
from dif.dif_parser import (
    export_to_html as dif_export_to_html,
    dif_avg_numeric_value,
    dif_avg_row_length,
    dif_column_count,
    dif_data_density,
    dif_empty_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_ods_has_formulas_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_formulas(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_formulas", "has_formulas": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_formulas"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_has_numeric_cells_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_numeric_cells(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_numeric_cells", "has_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_has_string_cells_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_string_cells(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_string_cells", "has_strings": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_strings"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_is_all_numeric_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_all_numeric(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_all_numeric", "all_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_is_empty_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_empty(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_empty", "is_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_empty"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_is_multi_sheet_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_multi_sheet(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_multi_sheet", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_export_to_html_returns_str(tmp_path):
    path = _dif_file()
    result = dif_export_to_html(path)
    assert isinstance(result, str)
    assert "<table>" in result.lower() or "<tr>" in result.lower()

    record = {"format": "dif", "function": "export_to_html", "length": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_avg_numeric_value_returns_float(tmp_path):
    path = _dif_file()
    result = dif_avg_numeric_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "dif_avg_numeric_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_avg_row_length_returns_float(tmp_path):
    path = _dif_file()
    result = dif_avg_row_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "dif", "function": "dif_avg_row_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_dif_column_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_column_count", "col_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["col_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_data_density_returns_float(tmp_path):
    path = _dif_file()
    result = dif_data_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "dif", "function": "dif_data_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_dif_empty_cell_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_empty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_empty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

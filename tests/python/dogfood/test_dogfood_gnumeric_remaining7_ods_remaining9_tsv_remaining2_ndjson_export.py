"""
Dogfood pipeline: Gnumeric remaining + ODS remaining + TSV remaining analytics → NDJSON export.
Covers Gnumeric: gnumeric_max_row_length, gnumeric_total_numeric_sum, gnumeric_distinct_value_count,
                 gnumeric_avg_cells_per_row, gnumeric_has_formulas
Covers ODS: ods_string_column_count, ods_max_cell_text_length
Covers TSV: tsv_is_single_row, tsv_empty_cell_ratio, tsv_numeric_field_ratio, tsv_is_square,
            tsv_avg_field_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_max_row_length,
    gnumeric_total_numeric_sum,
    gnumeric_distinct_value_count,
    gnumeric_avg_cells_per_row,
    gnumeric_has_formulas,
)
from ods.ods_parser import (
    ods_string_column_count,
    ods_max_cell_text_length,
)
from tsv.tsv_parser import (
    tsv_is_single_row,
    tsv_empty_cell_ratio,
    tsv_numeric_field_ratio,
    tsv_is_square,
    tsv_avg_field_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _gnumeric_file():
    for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
        if "minimal-spreadsheet" in f.name:
            return str(f)
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _tsv_file():
    for f in sorted(_TSV_DIR.glob("*.tsv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_TSV_DIR.glob("*.tsv")))))


def test_gnumeric_max_row_length_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_max_row_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_max_row_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_total_numeric_sum_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_total_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "gnumeric_total_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_distinct_value_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_distinct_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_distinct_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_cells_per_row_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_avg_cells_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_avg_cells_per_row", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_has_formulas_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_has_formulas(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_has_formulas", "has_formulas": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_formulas"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_string_column_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_string_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_string_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_max_cell_text_length_returns_int(tmp_path):
    path = _ods_file()
    result = ods_max_cell_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_max_cell_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_is_single_row_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_is_single_row(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_is_single_row", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_empty_cell_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_empty_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_empty_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_numeric_field_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_numeric_field_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_numeric_field_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_is_square_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_is_square(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_is_square", "is_square": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_square"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_avg_field_length_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_avg_field_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_avg_field_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None

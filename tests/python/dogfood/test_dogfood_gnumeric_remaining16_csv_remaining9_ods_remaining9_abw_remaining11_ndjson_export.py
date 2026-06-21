"""
Dogfood pipeline: Gnumeric remaining + CSV remaining + ODS remaining + ABW remaining -> NDJSON export.
Covers Gnumeric: gnumeric_cell_density, gnumeric_max_column_index, gnumeric_unique_sheet_count, gnumeric_value_type_count
Covers CSV: csv_avg_row_width, csv_string_field_ratio, csv_total_field_length_sum, csv_total_value_count
Covers ODS: ods_min_cell_count_per_sheet, ods_total_cell_count_all
Covers ABW: abw_consonant_ratio, abw_letter_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import (
    gnumeric_cell_density,
    gnumeric_max_column_index,
    gnumeric_unique_sheet_count,
    gnumeric_value_type_count,
)
from src.python.csv.csv_parser import (
    csv_avg_row_width,
    csv_string_field_ratio,
    csv_total_field_length_sum,
    csv_total_value_count,
)
from ods.ods_parser import ods_min_cell_count_per_sheet, ods_total_cell_count_all
from abw.abw_codec import abw_consonant_ratio, abw_letter_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _csv_file():
    files = [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]
    return str(files[0])


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


# --- Gnumeric ---

def test_gnumeric_cell_density_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cell_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cell_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_max_column_index_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_max_column_index(path)
    assert isinstance(result, int)

    record = {"format": "gnumeric", "function": "gnumeric_max_column_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["index"], int)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_unique_sheet_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_unique_sheet_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_unique_sheet_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_value_type_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_value_type_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_value_type_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- CSV ---

def test_csv_avg_row_width_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_row_width(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_avg_row_width", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_string_field_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_string_field_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_string_field_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_total_field_length_sum_returns_int(tmp_path):
    path = _csv_file()
    result = csv_total_field_length_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_total_field_length_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_total_value_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_total_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_total_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ODS ---

def test_ods_min_cell_count_per_sheet_returns_int(tmp_path):
    path = _ods_file()
    result = ods_min_cell_count_per_sheet(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_min_cell_count_per_sheet", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_total_cell_count_all_returns_int(tmp_path):
    path = _ods_file()
    result = ods_total_cell_count_all(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_total_cell_count_all", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ABW ---

def test_abw_consonant_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_consonant_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_consonant_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_abw_letter_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_letter_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_letter_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None

"""
Dogfood pipeline: final cleanup sprint covering all remaining unused analytics functions.
Covers XCF: xcf_is_square_canvas, xcf_total_layer_area
Covers TSV: tsv_distinct_field_count, tsv_empty_field_count
Covers ABW: abw_avg_paragraph_length, abw_empty_paragraph_ratio, abw_longest_word_length
Covers CSV: csv_distinct_header_count, csv_max_string_field_length, csv_row_width_avg, csv_string_field_count
Covers Gnumeric: gnumeric_nonempty_cell_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from xcf.xcf_parser import xcf_is_square_canvas, xcf_total_layer_area
from tsv.tsv_parser import tsv_distinct_field_count, tsv_empty_field_count
from abw.abw_codec import abw_avg_paragraph_length, abw_empty_paragraph_ratio, abw_longest_word_length
from src.python.csv.csv_parser import (
    csv_distinct_header_count,
    csv_max_string_field_length,
    csv_row_width_avg,
    csv_string_field_count,
)
from gnumeric.gnumeric_codec import gnumeric_nonempty_cell_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_TSV_FILE = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_ABW_FILE = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_GNUMERIC_FILE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _csv_file():
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_CSV_DIR.glob("*.csv")))))


def test_xcf_is_square_canvas_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_square_canvas(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_square_canvas", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_xcf_total_layer_area_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_total_layer_area(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_total_layer_area", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_distinct_field_count_returns_int(tmp_path):
    path = str(_TSV_FILE)
    result = tsv_distinct_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_distinct_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_empty_field_count_returns_int(tmp_path):
    path = str(_TSV_FILE)
    result = tsv_empty_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_empty_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_paragraph_length_returns_float(tmp_path):
    path = str(_ABW_FILE)
    result = abw_avg_paragraph_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_paragraph_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_empty_paragraph_ratio_returns_float(tmp_path):
    path = str(_ABW_FILE)
    result = abw_empty_paragraph_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_empty_paragraph_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_abw_longest_word_length_returns_int(tmp_path):
    path = str(_ABW_FILE)
    result = abw_longest_word_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_longest_word_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_distinct_header_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_distinct_header_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_distinct_header_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_max_string_field_length_returns_int(tmp_path):
    path = _csv_file()
    result = csv_max_string_field_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_max_string_field_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_row_width_avg_returns_float(tmp_path):
    path = _csv_file()
    result = csv_row_width_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_row_width_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_string_field_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_string_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_string_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_nonempty_cell_count_returns_int(tmp_path):
    path = str(_GNUMERIC_FILE)
    result = gnumeric_nonempty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_nonempty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

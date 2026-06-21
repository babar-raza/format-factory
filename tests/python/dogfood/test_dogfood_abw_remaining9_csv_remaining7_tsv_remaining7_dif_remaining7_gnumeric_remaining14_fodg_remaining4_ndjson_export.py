"""
Dogfood pipeline: ABW remaining + CSV remaining + TSV remaining +
                  DIF remaining + Gnumeric remaining + FODG remaining -> NDJSON export.
Covers ABW: abw_digit_ratio, abw_has_single_paragraph
Covers CSV: csv_avg_field_length, csv_nonempty_field_count
Covers TSV: tsv_has_header_row, tsv_nonempty_field_count, tsv_row_field_variance
Covers DIF: dif_unique_row_count
Covers Gnumeric: gnumeric_cell_text_sum, gnumeric_row_fill_variance
Covers FODG: fodg_has_text_content, fodg_max_shape_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import abw_digit_ratio, abw_has_single_paragraph
from src.python.csv.csv_parser import csv_avg_field_length, csv_nonempty_field_count
from tsv.tsv_parser import tsv_has_header_row, tsv_nonempty_field_count, tsv_row_field_variance
from dif.dif_parser import dif_unique_row_count
from gnumeric.gnumeric_codec import gnumeric_cell_text_sum, gnumeric_row_fill_variance
from fodg.fodg_codec import fodg_has_text_content, fodg_max_shape_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _abw_file():
    return str(_ABW_DIR / "two-paragraphs.abw")


def _csv_file():
    files = [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]
    return str(files[0])


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name and "binary" not in f.name]
    return str(files[0])


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _fodg_file():
    return str(next(iter(sorted(_FODG_DIR.glob("*.fodg")))))


def test_abw_digit_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_digit_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_digit_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_single_paragraph_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_has_single_paragraph(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_single_paragraph", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_avg_field_length_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_field_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_avg_field_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_nonempty_field_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_nonempty_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_nonempty_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_has_header_row_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_has_header_row(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_has_header_row", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_nonempty_field_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_nonempty_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_nonempty_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_row_field_variance_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_row_field_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_row_field_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_unique_row_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_unique_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_unique_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_cell_text_sum_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cell_text_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cell_text_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_row_fill_variance_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_row_fill_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_row_fill_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_has_text_content_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_has_text_content(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_has_text_content", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodg_max_shape_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_max_shape_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_max_shape_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

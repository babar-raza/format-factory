"""
Dogfood pipeline: ABW remaining analytics + ODS remaining analytics → NDJSON export.
Covers ABW: abw_line_count, abw_uppercase_ratio, abw_avg_word_length, abw_has_headings
Covers ODS: ods_max_sheet_row_count, ods_total_string_length, ods_min_row_length, ods_max_numeric_sum,
            ods_numeric_ratio, ods_is_square, ods_numeric_column_count, ods_row_cell_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_line_count,
    abw_uppercase_ratio,
    abw_avg_word_length,
    abw_has_headings,
)
from ods.ods_parser import (
    ods_max_sheet_row_count,
    ods_total_string_length,
    ods_min_row_length,
    ods_max_numeric_sum,
    ods_numeric_ratio,
    ods_is_square,
    ods_numeric_column_count,
    ods_row_cell_variance,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _abw_file():
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if "two-paragraphs" in f.name:
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_abw_line_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_line_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_line_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_uppercase_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_uppercase_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_uppercase_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_word_length_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_word_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_word_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_headings_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_has_headings(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_headings", "has_headings": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_headings"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_max_sheet_row_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_max_sheet_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_max_sheet_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_total_string_length_returns_int(tmp_path):
    path = _ods_file()
    result = ods_total_string_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_total_string_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_min_row_length_returns_int(tmp_path):
    path = _ods_file()
    result = ods_min_row_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_min_row_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_max_numeric_sum_returns_float(tmp_path):
    path = _ods_file()
    result = ods_max_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "ods", "function": "ods_max_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ods_numeric_ratio_returns_float(tmp_path):
    path = _ods_file()
    result = ods_numeric_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ods", "function": "ods_numeric_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ods_is_square_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_square(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_square", "is_square": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_square"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_numeric_column_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_numeric_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_numeric_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_row_cell_variance_returns_float(tmp_path):
    path = _ods_file()
    result = ods_row_cell_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_row_cell_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None

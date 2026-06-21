"""
Dogfood pipeline: QOI remaining + TSV remaining + SYLK remaining +
                  NDJSON remaining + FODP remaining -> NDJSON export.
Covers QOI: qoi_blue_channel_sum, qoi_pixel_brightness_range, qoi_red_channel_sum, qoi_warm_pixel_ratio
Covers TSV: tsv_has_only_one_row, tsv_numeric_range
Covers SYLK: sylk_max_value, sylk_min_value
Covers NDJSON: ndjson_has_all_same_keys, ndjson_numeric_range
Covers FODP: fodp_blank_slide_count, fodp_slide_word_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    qoi_blue_channel_sum,
    qoi_pixel_brightness_range,
    qoi_red_channel_sum,
    qoi_warm_pixel_ratio,
)
from tsv.tsv_parser import tsv_has_only_one_row, tsv_numeric_range
from sylk.sylk_parser import sylk_max_value, sylk_min_value
from ndjson.ndjson_codec import (
    ndjson_has_all_same_keys,
    ndjson_numeric_range,
    write_ndjson,
    load_ndjson,
)
from fodp.fodp_codec import fodp_blank_slide_count, fodp_slide_word_variance

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name and "binary" not in f.name]
    return str(files[0])


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def test_qoi_blue_channel_sum_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_blue_channel_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_blue_channel_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_pixel_brightness_range_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_pixel_brightness_range(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_pixel_brightness_range", "range": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_red_channel_sum_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_red_channel_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_red_channel_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_warm_pixel_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_warm_pixel_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "qoi", "function": "qoi_warm_pixel_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_has_only_one_row_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_has_only_one_row(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_has_only_one_row", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_numeric_range_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_numeric_range(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_numeric_range", "range": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_value_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_max_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "sylk_max_value", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_sylk_min_value_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_min_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "sylk_min_value", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ndjson_has_all_same_keys_returns_bool(tmp_path):
    ndjson_path = tmp_path / "test.ndjson"
    records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    write_ndjson(records, str(ndjson_path))

    result = ndjson_has_all_same_keys(str(ndjson_path))
    assert isinstance(result, bool)

    record = {"format": "ndjson", "function": "ndjson_has_all_same_keys", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ndjson_numeric_range_returns_float(tmp_path):
    ndjson_path = tmp_path / "test.ndjson"
    records = [{"x": 1.0, "y": 5.0}, {"x": 2.0, "y": 10.0}]
    write_ndjson(records, str(ndjson_path))

    result = ndjson_numeric_range(str(ndjson_path))
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_numeric_range", "range": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_blank_slide_count_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_blank_slide_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_blank_slide_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_word_variance_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_slide_word_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_slide_word_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None

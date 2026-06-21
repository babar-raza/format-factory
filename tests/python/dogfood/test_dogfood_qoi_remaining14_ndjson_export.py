"""
Dogfood pipeline: QOI remaining -> NDJSON export.
Covers QOI: qoi_blue_variance, qoi_center_pixel_brightness, qoi_channel_range_sum,
            qoi_edge_brightness, qoi_entropy, qoi_green_variance, qoi_is_rgb_only,
            qoi_pixel_brightness_mean, qoi_red_green_diff, qoi_red_variance,
            qoi_top_half_brightness, qoi_total_channel_sum
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    qoi_blue_variance,
    qoi_center_pixel_brightness,
    qoi_channel_range_sum,
    qoi_edge_brightness,
    qoi_entropy,
    qoi_green_variance,
    qoi_is_rgb_only,
    qoi_pixel_brightness_mean,
    qoi_red_green_diff,
    qoi_red_variance,
    qoi_top_half_brightness,
    qoi_total_channel_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def test_qoi_blue_variance_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_blue_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_blue_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_center_pixel_brightness_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_center_pixel_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_center_pixel_brightness", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_channel_range_sum_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_channel_range_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_channel_range_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_edge_brightness_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_edge_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_edge_brightness", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_entropy_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_entropy(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_entropy", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_green_variance_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_green_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_green_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_rgb_only_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_is_rgb_only(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_rgb_only", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_qoi_pixel_brightness_mean_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_pixel_brightness_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_pixel_brightness_mean", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_red_green_diff_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_red_green_diff(path)
    assert isinstance(result, (int, float))

    record = {"format": "qoi", "function": "qoi_red_green_diff", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_qoi_red_variance_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_red_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_red_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_top_half_brightness_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_top_half_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_top_half_brightness", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_total_channel_sum_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_total_channel_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_total_channel_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None

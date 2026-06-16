"""
Dogfood pipeline: QOI remaining 2 analytics → NDJSON export.
Covers: get_capabilities, qoi_average_brightness, qoi_avg_rgb, qoi_avg_rgb_value,
        qoi_blue_channel_average, qoi_blue_dominant
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    get_capabilities,
    qoi_average_brightness,
    qoi_avg_rgb,
    qoi_avg_rgb_value,
    qoi_blue_channel_average,
    qoi_blue_dominant,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def test_qoi_get_capabilities_returns_dict(tmp_path):
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert caps.get("format") == "qoi"
    record = {"format": "qoi", "function": "get_capabilities", "gate": caps.get("gate")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format"] == "qoi"
    assert json.dumps(loaded[0]) is not None


def test_qoi_average_brightness_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_average_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "qoi", "function": "qoi_average_brightness", "brightness": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["brightness"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_avg_rgb_returns_tuple(tmp_path):
    path = _qoi_file()
    result = qoi_avg_rgb(path)
    assert isinstance(result, tuple)
    assert len(result) == 3
    record = {"format": "qoi", "function": "qoi_avg_rgb", "r": result[0], "g": result[1], "b": result[2]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["r"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_avg_rgb_value_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_avg_rgb_value(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "qoi", "function": "qoi_avg_rgb_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_blue_channel_average_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_blue_channel_average(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "qoi", "function": "qoi_blue_channel_average", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_blue_dominant_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_blue_dominant(path)
    assert isinstance(result, bool)
    record = {"format": "qoi", "function": "qoi_blue_dominant", "is_dominant": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_dominant"], bool)
    assert json.dumps(loaded[0]) is not None

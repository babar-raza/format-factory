"""
Dogfood pipeline: PPM mutation + QOI remaining + XCF remaining → NDJSON export.
Covers PPM: flip_horizontal, invert, ppm_column_count
Covers QOI: qoi_is_tall, qoi_channel_entropy
Covers XCF: xcf_column_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import flip_horizontal as ppm_flip, invert as ppm_invert, ppm_column_count
from qoi.qoi_parser import qoi_is_tall, qoi_channel_entropy
from xcf.xcf_parser import xcf_column_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _valid_ppm():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _valid_qoi():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def _valid_xcf():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_ppm_flip_horizontal_returns_dict(tmp_path):
    path = _valid_ppm()
    dest = str(tmp_path / "flipped.ppm")
    result = ppm_flip(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "ppm", "function": "flip_horizontal", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_ppm_invert_returns_dict(tmp_path):
    path = _valid_ppm()
    dest = str(tmp_path / "inverted.ppm")
    result = ppm_invert(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "ppm", "function": "invert", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_ppm_column_count_returns_int(tmp_path):
    path = _valid_ppm()
    result = ppm_column_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "ppm", "function": "ppm_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_tall_returns_bool(tmp_path):
    path = _valid_qoi()
    result = qoi_is_tall(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_tall", "is_tall": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_tall"], bool)
    assert json.dumps(loaded[0]) is not None


def test_qoi_channel_entropy_returns_float(tmp_path):
    path = _valid_qoi()
    result = qoi_channel_entropy(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "qoi", "function": "qoi_channel_entropy", "entropy": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["entropy"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_column_count_returns_int(tmp_path):
    path = _valid_xcf()
    result = xcf_column_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "xcf", "function": "xcf_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None

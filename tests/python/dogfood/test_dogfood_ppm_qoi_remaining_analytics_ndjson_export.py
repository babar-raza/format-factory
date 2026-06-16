"""
Dogfood pipeline: PPM remaining analytics + QOI remaining analytics → NDJSON export.
Covers: average_color, get_dimensions, is_grayscale, get_capabilities (ppm),
        qoi_area, qoi_aspect_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import average_color, get_dimensions, is_grayscale, get_capabilities
from qoi.qoi_parser import qoi_area, qoi_aspect_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def test_average_color_returns_tuple(tmp_path):
    path = _ppm_file()
    result = average_color(path)
    assert isinstance(result, tuple)
    assert len(result) == 3
    assert all(isinstance(v, (int, float)) for v in result)

    record = {"format": "ppm", "function": "average_color", "r": result[0], "g": result[1], "b": result[2]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["r"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_get_dimensions_returns_tuple(tmp_path):
    path = _ppm_file()
    result = get_dimensions(path)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert result[0] >= 1 and result[1] >= 1

    record = {"format": "ppm", "function": "get_dimensions", "width": result[0], "height": result[1]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_is_grayscale_returns_bool(tmp_path):
    path = _ppm_file()
    result = is_grayscale(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "is_grayscale", "is_grayscale": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_grayscale"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_get_capabilities_returns_dict(tmp_path):
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert caps.get("format") == "ppm"
    assert isinstance(caps.get("supported"), list)

    record = {"format": "ppm", "function": "get_capabilities", "gate": caps.get("gate")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format"] == "ppm"
    assert json.dumps(loaded[0]) is not None


def test_qoi_area_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_area(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "qoi", "function": "qoi_area", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_qoi_aspect_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_aspect_ratio(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "qoi", "function": "qoi_aspect_ratio", "aspect_ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["aspect_ratio"] > 0.0
    assert json.dumps(loaded[0]) is not None

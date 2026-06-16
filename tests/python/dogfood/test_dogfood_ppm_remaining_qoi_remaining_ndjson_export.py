"""
Dogfood pipeline: PPM remaining + QOI remaining → NDJSON export.
Covers PPM: crop, flip_vertical, ppm_min_dimension, ppm_is_tall, ppm_pixel_density
Covers QOI: qoi_is_monochrome
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import crop as ppm_crop, flip_vertical, ppm_min_dimension, ppm_is_tall, ppm_pixel_density
from qoi.qoi_parser import qoi_is_monochrome
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _valid_ppm():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _valid_qoi():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def test_ppm_crop_returns_dict(tmp_path):
    path = _valid_ppm()
    dest = str(tmp_path / "cropped.ppm")
    result = ppm_crop(path, dest, 0, 0, 1, 1)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "ppm", "function": "crop", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_ppm_flip_vertical_returns_dict(tmp_path):
    path = _valid_ppm()
    dest = str(tmp_path / "flipped_v.ppm")
    result = flip_vertical(path, dest)
    assert isinstance(result, dict)
    assert result.get("ok") is True

    record = {"format": "ppm", "function": "flip_vertical", "ok": result.get("ok")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert json.dumps(loaded[0]) is not None


def test_ppm_min_dimension_returns_int(tmp_path):
    path = _valid_ppm()
    result = ppm_min_dimension(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "ppm", "function": "ppm_min_dimension", "min_dim": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["min_dim"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_ppm_is_tall_returns_bool(tmp_path):
    path = _valid_ppm()
    result = ppm_is_tall(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "ppm_is_tall", "is_tall": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_tall"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_pixel_density_returns_float(tmp_path):
    path = _valid_ppm()
    result = ppm_pixel_density(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ppm", "function": "ppm_pixel_density", "density": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_monochrome_returns_bool(tmp_path):
    path = _valid_qoi()
    result = qoi_is_monochrome(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_monochrome", "is_monochrome": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_monochrome"], bool)
    assert json.dumps(loaded[0]) is not None

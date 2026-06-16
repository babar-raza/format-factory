"""
Dogfood pipeline: PPM parser remaining + PBM parser remaining → NDJSON export.
Covers: ppm_aspect_ratio, ppm_avg_brightness, pixel_count, parse_ppm (ppm),
        get_capabilities, image_pixel_stats (pbm)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_aspect_ratio, ppm_avg_brightness, pixel_count, parse_ppm
from pbm.pbm_parser import get_capabilities, image_pixel_stats
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def test_ppm_aspect_ratio_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_aspect_ratio(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "ppm", "function": "ppm_aspect_ratio", "ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_avg_brightness_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_avg_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "ppm", "function": "ppm_avg_brightness", "brightness": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["brightness"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_pixel_count_returns_int(tmp_path):
    path = _ppm_file()
    result = pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_parse_ppm_returns_dict(tmp_path):
    path = _ppm_file()
    result = parse_ppm(path)
    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert "width" in result
    assert "height" in result

    record = {"format": "ppm", "function": "parse_ppm", "width": result["width"], "height": result["height"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_pbm_get_capabilities_returns_dict(tmp_path):
    result = get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result

    record = {"format": "pbm", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "pbm"
    assert json.dumps(loaded[0]) is not None


def test_pbm_image_pixel_stats_returns_dict(tmp_path):
    path = _pbm_file()
    result = image_pixel_stats(path)
    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert "total_pixels" in result
    assert result["total_pixels"] >= 0

    record = {
        "format": "pbm",
        "function": "image_pixel_stats",
        "total_pixels": result["total_pixels"],
        "black_count": result["black_count"],
    }
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total_pixels"] >= 0
    assert json.dumps(loaded[0]) is not None

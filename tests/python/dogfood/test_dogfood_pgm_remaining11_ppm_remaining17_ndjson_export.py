"""
Dogfood pipeline: PGM remaining + PPM batch -> NDJSON export.
Covers PGM: pgm_edge_pixel_mean, pgm_pixel_count, pgm_pixel_entropy,
            pgm_pixel_median, pgm_row_brightness_sum
Covers PPM: ppm_blue_mean_value, ppm_blue_variance, ppm_center_brightness,
            ppm_entropy, ppm_green_mean_value, ppm_green_variance, ppm_has_pure_red_pixel
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_edge_pixel_mean,
    pgm_pixel_count,
    pgm_pixel_entropy,
    pgm_pixel_median,
    pgm_row_brightness_sum,
)
from ppm.ppm_parser import (
    ppm_blue_mean_value,
    ppm_blue_variance,
    ppm_center_brightness,
    ppm_entropy,
    ppm_green_mean_value,
    ppm_green_variance,
    ppm_has_pure_red_pixel,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


# --- PGM ---

def test_pgm_edge_pixel_mean_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_edge_pixel_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_edge_pixel_mean", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_entropy_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_entropy(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_entropy", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_median_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_median(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_median", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_row_brightness_sum_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_row_brightness_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_row_brightness_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- PPM ---

def test_ppm_blue_mean_value_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_blue_mean_value(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_blue_mean_value", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_blue_variance_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_blue_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_blue_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_center_brightness_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_center_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_center_brightness", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_entropy_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_entropy(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_entropy", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_green_mean_value_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_green_mean_value(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_green_mean_value", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_green_variance_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_green_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_green_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_has_pure_red_pixel_returns_bool(tmp_path):
    path = _ppm_file()
    result = ppm_has_pure_red_pixel(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "ppm_has_pure_red_pixel", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None

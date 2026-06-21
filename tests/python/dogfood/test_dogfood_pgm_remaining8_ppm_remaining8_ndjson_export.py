"""
Dogfood pipeline: PGM remaining + PPM remaining -> NDJSON export.
Covers PGM: pgm_full_white_pixel_count, pgm_height, pgm_pixel_density_ratio,
            pgm_pixel_value_variance, pgm_top_row_mean, pgm_width
Covers PPM: ppm_blue_dominance_ratio, ppm_channel_entropy, ppm_height,
            ppm_max_red_value, ppm_min_brightness, ppm_total_blue_sum
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_full_white_pixel_count,
    pgm_height,
    pgm_pixel_density_ratio,
    pgm_pixel_value_variance,
    pgm_top_row_mean,
    pgm_width,
)
from ppm.ppm_parser import (
    ppm_blue_dominance_ratio,
    ppm_channel_entropy,
    ppm_height,
    ppm_max_red_value,
    ppm_min_brightness,
    ppm_total_blue_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


# --- PGM ---

def test_pgm_full_white_pixel_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_full_white_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_full_white_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_height_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_height(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "pgm", "function": "pgm_height", "height": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["height"] > 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_density_ratio_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_density_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_density_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_value_variance_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_value_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_value_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_top_row_mean_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_top_row_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_top_row_mean", "mean": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_width_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_width(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "pgm", "function": "pgm_width", "width": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None


# --- PPM ---

def test_ppm_blue_dominance_ratio_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_blue_dominance_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ppm", "function": "ppm_blue_dominance_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_channel_entropy_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_channel_entropy(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_channel_entropy", "entropy": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["entropy"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_height_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_height(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "ppm", "function": "ppm_height", "height": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["height"] > 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_max_red_value_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_max_red_value(path)
    assert isinstance(result, int)
    assert 0 <= result <= 255

    record = {"format": "ppm", "function": "ppm_max_red_value", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0 <= loaded[0]["value"] <= 255
    assert json.dumps(loaded[0]) is not None


def test_ppm_min_brightness_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_min_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_min_brightness", "brightness": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["brightness"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_total_blue_sum_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_total_blue_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_total_blue_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None

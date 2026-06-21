"""
Dogfood pipeline: PGM remaining + PPM remaining + QOI start -> NDJSON export.
Covers PGM: pgm_top_half_avg, pgm_width_exceeds_height
Covers PPM: ppm_hue_diversity, ppm_is_multi_row, ppm_luminance_mean, ppm_max_green_value,
            ppm_non_black_pixel_count, ppm_pixel_count_total, ppm_red_mean_value,
            ppm_red_variance, ppm_top_half_brightness
Covers QOI: qoi_alpha_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_top_half_avg,
    pgm_width_exceeds_height,
)
from ppm.ppm_parser import (
    ppm_hue_diversity,
    ppm_is_multi_row,
    ppm_luminance_mean,
    ppm_max_green_value,
    ppm_non_black_pixel_count,
    ppm_pixel_count_total,
    ppm_red_mean_value,
    ppm_red_variance,
    ppm_top_half_brightness,
)
from qoi.qoi_parser import (
    qoi_alpha_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


# --- PGM ---

def test_pgm_top_half_avg_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_top_half_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_top_half_avg", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_width_exceeds_height_returns_bool(tmp_path):
    path = _pgm_file()
    result = pgm_width_exceeds_height(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_width_exceeds_height", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- PPM ---

def test_ppm_hue_diversity_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_hue_diversity(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_hue_diversity", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_is_multi_row_returns_bool(tmp_path):
    path = _ppm_file()
    result = ppm_is_multi_row(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "ppm_is_multi_row", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_luminance_mean_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_luminance_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_luminance_mean", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_max_green_value_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_max_green_value(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_max_green_value", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_non_black_pixel_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_non_black_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_non_black_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_pixel_count_total_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_pixel_count_total(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_pixel_count_total", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_red_mean_value_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_red_mean_value(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_red_mean_value", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_red_variance_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_red_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_red_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_top_half_brightness_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_top_half_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_top_half_brightness", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- QOI ---

def test_qoi_alpha_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_alpha_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "qoi", "function": "qoi_alpha_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None

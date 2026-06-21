"""
Dogfood pipeline: PPM remaining analytics + DIF remaining analytics → NDJSON export.
Covers PPM: ppm_cool_pixel_count, ppm_dark_pixel_ratio, ppm_distinct_pixel_count,
            ppm_luminance_sum, ppm_max_channel_avg, ppm_max_pixel_brightness
Covers DIF: dif_avg_cell_length_variance, dif_avg_row_cell_count, dif_cells_per_tuple,
            dif_column_fill_ratio, dif_is_wider_than_tall, dif_max_column_sum
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    ppm_cool_pixel_count,
    ppm_dark_pixel_ratio,
    ppm_distinct_pixel_count,
    ppm_luminance_sum,
    ppm_max_channel_avg,
    ppm_max_pixel_brightness,
)
from dif.dif_parser import (
    dif_avg_cell_length_variance,
    dif_avg_row_cell_count,
    dif_cells_per_tuple,
    dif_column_fill_ratio,
    dif_is_wider_than_tall,
    dif_max_column_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_ppm_cool_pixel_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_cool_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_cool_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_dark_pixel_ratio_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_dark_pixel_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ppm", "function": "ppm_dark_pixel_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_distinct_pixel_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_distinct_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_distinct_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_luminance_sum_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_luminance_sum(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_luminance_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_max_channel_avg_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_max_channel_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_max_channel_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_max_pixel_brightness_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_max_pixel_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_max_pixel_brightness", "brightness": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["brightness"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_avg_cell_length_variance_returns_float(tmp_path):
    path = _dif_file()
    result = dif_avg_cell_length_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_avg_cell_length_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_avg_row_cell_count_returns_float(tmp_path):
    path = _dif_file()
    result = dif_avg_row_cell_count(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_avg_row_cell_count", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_cells_per_tuple_returns_float(tmp_path):
    path = _dif_file()
    result = dif_cells_per_tuple(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_cells_per_tuple", "cells": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cells"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_column_fill_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_column_fill_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_column_fill_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_is_wider_than_tall_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_is_wider_than_tall(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_is_wider_than_tall", "is_wider": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_wider"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_max_column_sum_returns_float(tmp_path):
    path = _dif_file()
    result = dif_max_column_sum(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_max_column_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None

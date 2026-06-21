"""
Dogfood pipeline: PGM remaining + PPM remaining + Gnumeric remaining -> NDJSON export.
Covers PGM: pgm_column_mean, pgm_has_only_extremes, pgm_highlight_count, pgm_is_single_pixel
Covers PPM: ppm_avg_red_channel, ppm_is_single_pixel, ppm_warm_pixel_ratio
Covers Gnumeric: gnumeric_avg_sheet_cell_count, gnumeric_distinct_string_count,
                 gnumeric_file_size_bytes, gnumeric_max_sheet_cell_count, gnumeric_min_sheet_cell_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_column_mean,
    pgm_has_only_extremes,
    pgm_highlight_count,
    pgm_is_single_pixel,
)
from ppm.ppm_parser import (
    ppm_avg_red_channel,
    ppm_is_single_pixel,
    ppm_warm_pixel_ratio,
)
from gnumeric.gnumeric_codec import (
    gnumeric_avg_sheet_cell_count,
    gnumeric_distinct_string_count,
    gnumeric_file_size_bytes,
    gnumeric_max_sheet_cell_count,
    gnumeric_min_sheet_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def test_pgm_column_mean_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_column_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_column_mean", "mean": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_has_only_extremes_returns_bool(tmp_path):
    path = _pgm_file()
    result = pgm_has_only_extremes(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_has_only_extremes", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pgm_highlight_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_highlight_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_highlight_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_is_single_pixel_returns_bool(tmp_path):
    path = _pgm_file()
    result = pgm_is_single_pixel(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_is_single_pixel", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_avg_red_channel_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_avg_red_channel(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_avg_red_channel", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_is_single_pixel_returns_bool(tmp_path):
    path = _ppm_file()
    result = ppm_is_single_pixel(path)
    assert isinstance(result, bool)

    record = {"format": "ppm", "function": "ppm_is_single_pixel", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ppm_warm_pixel_ratio_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_warm_pixel_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ppm", "function": "ppm_warm_pixel_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_sheet_cell_count_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_avg_sheet_cell_count(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_avg_sheet_cell_count", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_distinct_string_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_distinct_string_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_distinct_string_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_file_size_bytes_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_file_size_bytes(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_max_sheet_cell_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_max_sheet_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_max_sheet_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_min_sheet_cell_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_min_sheet_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_min_sheet_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

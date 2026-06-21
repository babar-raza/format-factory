"""
Dogfood pipeline: PBM remaining + PGM remaining + PPM remaining + Gnumeric remaining -> NDJSON export.
Covers PBM: pbm_black_column_count, pbm_interior_black_count, pbm_max_row_white_count, pbm_row_density_avg
Covers PGM: pgm_above_average_count, pgm_pixel_quartile_count, pgm_row_mean, pgm_total_pixel_sum
Covers PPM: ppm_cold_pixel_ratio, ppm_red_green_diff
Covers Gnumeric: gnumeric_cells_in_first_column, gnumeric_has_only_one_column
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_black_column_count,
    pbm_interior_black_count,
    pbm_max_row_white_count,
    pbm_row_density_avg,
)
from pgm.pgm_parser import (
    pgm_above_average_count,
    pgm_pixel_quartile_count,
    pgm_row_mean,
    pgm_total_pixel_sum,
)
from ppm.ppm_parser import ppm_cold_pixel_ratio, ppm_red_green_diff
from gnumeric.gnumeric_codec import gnumeric_cells_in_first_column, gnumeric_has_only_one_column
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def test_pbm_black_column_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_black_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_black_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_interior_black_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_interior_black_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_interior_black_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_max_row_white_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_max_row_white_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_max_row_white_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_row_density_avg_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_row_density_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_row_density_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_above_average_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_above_average_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_above_average_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_quartile_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_quartile_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_quartile_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_row_mean_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_row_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_row_mean", "mean": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_total_pixel_sum_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_total_pixel_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_total_pixel_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_cold_pixel_ratio_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_cold_pixel_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ppm", "function": "ppm_cold_pixel_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_red_green_diff_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_red_green_diff(path)
    assert isinstance(result, (int, float))

    record = {"format": "ppm", "function": "ppm_red_green_diff", "diff": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["diff"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_cells_in_first_column_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cells_in_first_column(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cells_in_first_column", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_has_only_one_column_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_has_only_one_column(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_has_only_one_column", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None

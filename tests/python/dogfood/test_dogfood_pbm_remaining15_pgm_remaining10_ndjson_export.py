"""
Dogfood pipeline: PBM remaining + PGM batch -> NDJSON export.
Covers PBM: pbm_horizontal_symmetry, pbm_is_multi_row, pbm_longest_run, pbm_pixel_sum,
            pbm_row_transition_count, pbm_run_length_avg, pbm_top_half_density, pbm_white_per_row
Covers PGM: pgm_bottom_half_avg, pgm_col_brightness_variance, pgm_column_mean_max, pgm_mid_pixel_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_horizontal_symmetry,
    pbm_is_multi_row,
    pbm_longest_run,
    pbm_pixel_sum,
    pbm_row_transition_count,
    pbm_run_length_avg,
    pbm_top_half_density,
    pbm_white_per_row,
)
from pgm.pgm_parser import (
    pgm_bottom_half_avg,
    pgm_col_brightness_variance,
    pgm_column_mean_max,
    pgm_mid_pixel_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


# --- PBM ---

def test_pbm_horizontal_symmetry_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_horizontal_symmetry(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "pbm_horizontal_symmetry", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["value"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_multi_row_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_multi_row(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_multi_row", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_longest_run_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_longest_run(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_longest_run", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_pixel_sum_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_pixel_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_pixel_sum", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_row_transition_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_row_transition_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_row_transition_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_run_length_avg_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_run_length_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_run_length_avg", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_top_half_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_top_half_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "pbm_top_half_density", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_white_per_row_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_white_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_white_per_row", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- PGM ---

def test_pgm_bottom_half_avg_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_bottom_half_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_bottom_half_avg", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_col_brightness_variance_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_col_brightness_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_col_brightness_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_column_mean_max_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_column_mean_max(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_column_mean_max", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_mid_pixel_ratio_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_mid_pixel_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pgm", "function": "pgm_mid_pixel_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None

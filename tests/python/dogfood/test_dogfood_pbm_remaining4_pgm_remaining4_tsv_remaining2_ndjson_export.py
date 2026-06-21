"""
Dogfood pipeline: PBM remaining + PGM remaining + TSV remaining → NDJSON export.
Covers PBM: pbm_row_count, pbm_total_pixels, pbm_transition_count,
            pbm_white_density, pbm_white_pixel_count, pbm_white_row_count
Covers PGM: pgm_mode_pixel_value, pgm_nonzero_pixel_count, pgm_pixel_sum_normalized,
            pgm_pixel_value_range, pgm_row_brightness_variance
Covers TSV: tsv_max_field_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_row_count,
    pbm_total_pixels,
    pbm_transition_count,
    pbm_white_density,
    pbm_white_pixel_count,
    pbm_white_row_count,
)
from pgm.pgm_parser import (
    pgm_mode_pixel_value,
    pgm_nonzero_pixel_count,
    pgm_pixel_sum_normalized,
    pgm_pixel_value_range,
    pgm_row_brightness_variance,
)
from tsv.tsv_parser import tsv_max_field_length
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _pbm_file():
    return str(_PBM_DIR / "2x2-checker.pbm")


def _pgm_file():
    return str(_PGM_DIR / "2x2-gradient.pgm")


def _tsv_file():
    return str(_TSV_DIR / "minimal-2x2.tsv")


def test_pbm_row_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_total_pixels_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_total_pixels(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_total_pixels", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_transition_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_transition_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_transition_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_white_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_white_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "pbm_white_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_white_pixel_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_white_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_white_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_white_row_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_white_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_white_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_mode_pixel_value_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_mode_pixel_value(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_mode_pixel_value", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_nonzero_pixel_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_nonzero_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_nonzero_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_sum_normalized_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_sum_normalized(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pgm", "function": "pgm_pixel_sum_normalized", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["value"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pgm_pixel_value_range_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_pixel_value_range(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_pixel_value_range", "range": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_row_brightness_variance_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_row_brightness_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_row_brightness_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_max_field_length_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_max_field_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_max_field_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None

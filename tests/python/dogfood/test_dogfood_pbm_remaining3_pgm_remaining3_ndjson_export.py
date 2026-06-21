"""
Dogfood pipeline: PBM remaining analytics + PGM remaining analytics → NDJSON export.
Covers PBM: pbm_aspect_ratio, pbm_corner_black_count, pbm_diagonal_black_count,
            pbm_is_square, pbm_is_wider_than_tall, pbm_row_black_variance
Covers PGM: pgm_brightness_variance, pgm_entropy, pgm_is_uniform,
            pgm_median_brightness, pgm_midtone_pixel_count, pgm_min_brightness
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_aspect_ratio,
    pbm_corner_black_count,
    pbm_diagonal_black_count,
    pbm_is_square,
    pbm_is_wider_than_tall,
    pbm_row_black_variance,
)
from pgm.pgm_parser import (
    pgm_brightness_variance,
    pgm_entropy,
    pgm_is_uniform,
    pgm_median_brightness,
    pgm_midtone_pixel_count,
    pgm_min_brightness,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def _pgm_file():
    return str(_PGM_DIR / "2x2-gradient.pgm")


def test_pbm_aspect_ratio_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_aspect_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_aspect_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_corner_black_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_corner_black_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_corner_black_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_diagonal_black_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_diagonal_black_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_diagonal_black_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_square_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_square(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_square", "is_square": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_square"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_wider_than_tall_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_wider_than_tall(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_wider_than_tall", "is_wider": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_wider"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_row_black_variance_returns_float(tmp_path):
    path = str(_PBM_DIR / "2x2-checker.pbm")
    result = pbm_row_black_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_row_black_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_brightness_variance_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_brightness_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_brightness_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_entropy_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_entropy(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_entropy", "entropy": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["entropy"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_is_uniform_returns_bool(tmp_path):
    path = _pgm_file()
    result = pgm_is_uniform(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_is_uniform", "is_uniform": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_uniform"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pgm_median_brightness_returns_float(tmp_path):
    path = _pgm_file()
    result = pgm_median_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_median_brightness", "median": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["median"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_midtone_pixel_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_midtone_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_midtone_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pgm_min_brightness_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_min_brightness(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "pgm_min_brightness", "brightness": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["brightness"] >= 0
    assert json.dumps(loaded[0]) is not None

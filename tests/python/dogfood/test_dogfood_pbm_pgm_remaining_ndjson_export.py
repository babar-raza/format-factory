"""
Dogfood pipeline: PBM remaining + PGM remaining → NDJSON export.
Covers PBM: count_black, count_white, pbm_column_count
Covers PGM: count_above_threshold, min_max_gray, pgm_megapixels
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import count_black, count_white, pbm_column_count
from pgm.pgm_parser import count_above_threshold, min_max_gray, pgm_megapixels
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _checker_pbm():
    return str(next(f for f in sorted(_PBM_DIR.glob("*.pbm")) if "checker" in f.name or "2x2" in f.name))


def _gradient_pgm():
    return str(next(f for f in sorted(_PGM_DIR.glob("*.pgm")) if "gradient" in f.name or "2x2" in f.name))


def test_count_black_returns_int(tmp_path):
    path = _checker_pbm()
    result = count_black(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "pbm", "function": "count_black", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_count_white_returns_int(tmp_path):
    path = _checker_pbm()
    result = count_white(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "pbm", "function": "count_white", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_pbm_column_count_returns_int(tmp_path):
    path = _checker_pbm()
    result = pbm_column_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "pbm", "function": "pbm_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_count_above_threshold_returns_int(tmp_path):
    path = _gradient_pgm()
    result = count_above_threshold(path, 100)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pgm", "function": "count_above_threshold", "threshold": 100, "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_min_max_gray_returns_tuple(tmp_path):
    path = _gradient_pgm()
    result = min_max_gray(path)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert result[0] <= result[1]

    record = {"format": "pgm", "function": "min_max_gray", "min": result[0], "max": result[1]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["min"] <= loaded[0]["max"]
    assert json.dumps(loaded[0]) is not None


def test_pgm_megapixels_returns_float(tmp_path):
    path = _gradient_pgm()
    result = pgm_megapixels(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "pgm", "function": "pgm_megapixels", "megapixels": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["megapixels"] > 0.0
    assert json.dumps(loaded[0]) is not None

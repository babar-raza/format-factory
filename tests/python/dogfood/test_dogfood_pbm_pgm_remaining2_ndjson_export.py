"""
Dogfood pipeline: PBM remaining 2 + PGM remaining 2 → NDJSON export.
Covers: pbm_dimension_ratio, pbm_megapixels, pbm_is_tall, pbm_is_wide,
        pgm_column_count, pgm_is_wide
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_dimension_ratio, pbm_megapixels, pbm_is_tall, pbm_is_wide
from pgm.pgm_parser import pgm_column_count, pgm_is_wide
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def test_pbm_dimension_ratio_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_dimension_ratio(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "pbm", "function": "pbm_dimension_ratio", "ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_megapixels_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_megapixels(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "pbm", "function": "pbm_megapixels", "megapixels": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["megapixels"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_tall_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_tall(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_tall", "is_tall": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_tall"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pbm_is_wide_returns_bool(tmp_path):
    path = _pbm_file()
    result = pbm_is_wide(path)
    assert isinstance(result, bool)

    record = {"format": "pbm", "function": "pbm_is_wide", "is_wide": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_wide"], bool)
    assert json.dumps(loaded[0]) is not None


def test_pgm_column_count_returns_int(tmp_path):
    path = _pgm_file()
    result = pgm_column_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "pgm", "function": "pgm_column_count", "column_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["column_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_pgm_is_wide_returns_bool(tmp_path):
    path = _pgm_file()
    result = pgm_is_wide(path)
    assert isinstance(result, bool)

    record = {"format": "pgm", "function": "pgm_is_wide", "is_wide": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_wide"], bool)
    assert json.dumps(loaded[0]) is not None

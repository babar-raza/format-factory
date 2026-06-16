"""
Dogfood pipeline: DIF path-based + PBM remaining + PGM remaining → NDJSON export.
Covers: dif_all_numeric, dif_avg_cell_length, aspect_ratio (pbm), black_pixel_ratio,
        average_gray (pgm), grayscale_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_all_numeric, dif_avg_cell_length
from pbm.pbm_parser import aspect_ratio, black_pixel_ratio
from pgm.pgm_parser import average_gray, grayscale_variance
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def _pgm_file():
    return str(next(iter(sorted(_PGM_DIR.glob("*.pgm")))))


def test_dif_all_numeric_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_all_numeric(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_all_numeric", "all_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_avg_cell_length_returns_float(tmp_path):
    path = _dif_file()
    result = dif_avg_cell_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "dif", "function": "dif_avg_cell_length", "avg_length": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_length"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_aspect_ratio_returns_float(tmp_path):
    path = _pbm_file()
    result = aspect_ratio(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "pbm", "function": "aspect_ratio", "ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_black_pixel_ratio_returns_float(tmp_path):
    path = _pbm_file()
    result = black_pixel_ratio(path)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "black_pixel_ratio", "ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pgm_average_gray_returns_float(tmp_path):
    path = _pgm_file()
    result = average_gray(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "pgm", "function": "average_gray", "avg_gray": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_gray"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_pgm_grayscale_variance_returns_float(tmp_path):
    path = _pgm_file()
    result = grayscale_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "pgm", "function": "grayscale_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None

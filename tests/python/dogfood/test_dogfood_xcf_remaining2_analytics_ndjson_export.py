"""
Dogfood pipeline: XCF remaining 2 analytics → NDJSON export.
Covers: probe_xcf, xcf_average_dimension, xcf_compression_ratio, xcf_diagonal,
        xcf_dimension_ratio, xcf_file_size
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    probe_xcf,
    xcf_average_dimension,
    xcf_compression_ratio,
    xcf_diagonal,
    xcf_dimension_ratio,
    xcf_file_size,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_xcf_probe_returns_dict(tmp_path):
    path = _xcf_file()
    result = probe_xcf(path)
    assert isinstance(result, dict)
    assert result.get("valid_header") is True
    record = {"format": "xcf", "function": "probe_xcf", "valid": result.get("valid_header")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_xcf_average_dimension_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_average_dimension(path)
    assert isinstance(result, (int, float))
    assert result >= 1.0
    record = {"format": "xcf", "function": "xcf_average_dimension", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 1.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_compression_ratio_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_compression_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "xcf", "function": "xcf_compression_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_diagonal_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_diagonal(path)
    assert isinstance(result, (int, float))
    assert result >= 1.0
    record = {"format": "xcf", "function": "xcf_diagonal", "diagonal": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["diagonal"] >= 1.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_dimension_ratio_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_dimension_ratio(path)
    assert isinstance(result, (int, float))
    assert result > 0.0
    record = {"format": "xcf", "function": "xcf_dimension_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_file_size_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_file_size(path)
    assert isinstance(result, int)
    assert result >= 1
    record = {"format": "xcf", "function": "xcf_file_size", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 1
    assert json.dumps(loaded[0]) is not None

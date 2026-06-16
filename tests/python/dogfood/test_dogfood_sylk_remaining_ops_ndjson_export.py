"""
Dogfood pipeline: SYLK remaining ops → NDJSON export.
Covers: probe_sylk, sylk_to_html, sylk_column_variance, sylk_is_empty,
        sylk_has_empty_rows, sylk_avg_numeric_cell_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    probe_sylk,
    sylk_to_html,
    sylk_column_variance,
    sylk_is_empty,
    sylk_has_empty_rows,
    sylk_avg_numeric_cell_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _minimal_sylk():
    return str(next(f for f in sorted(_SYLK_DIR.glob("*.slk")) if "minimal" in f.name or "2x2" in f.name))


def test_probe_sylk_returns_dict(tmp_path):
    path = _minimal_sylk()
    result = probe_sylk(path)
    assert isinstance(result, dict)
    assert result.get("valid_header") is True

    record = {"format": "sylk", "function": "probe_sylk", "valid": result.get("valid_header")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_sylk_to_html_returns_str(tmp_path):
    path = _minimal_sylk()
    result = sylk_to_html(path)
    assert isinstance(result, str)
    assert "<table>" in result.lower() or "<tr>" in result.lower()

    record = {"format": "sylk", "function": "sylk_to_html", "length": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] > 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_column_variance_returns_float(tmp_path):
    path = _minimal_sylk()
    result = sylk_column_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "sylk", "function": "sylk_column_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_sylk_is_empty_returns_bool(tmp_path):
    path = _minimal_sylk()
    result = sylk_is_empty(path)
    assert isinstance(result, bool)
    assert result is False

    record = {"format": "sylk", "function": "sylk_is_empty", "is_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_empty"] is False
    assert json.dumps(loaded[0]) is not None


def test_sylk_has_empty_rows_returns_bool(tmp_path):
    path = _minimal_sylk()
    result = sylk_has_empty_rows(path)
    assert isinstance(result, bool)

    record = {"format": "sylk", "function": "sylk_has_empty_rows", "has_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_empty"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_avg_numeric_cell_length_returns_float(tmp_path):
    path = _minimal_sylk()
    result = sylk_avg_numeric_cell_length(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "sylk", "function": "sylk_avg_numeric_cell_length", "avg": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None

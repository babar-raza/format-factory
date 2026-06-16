"""
Dogfood pipeline: FODG remaining + Gnumeric remaining + DIF remaining → NDJSON export.
Covers FODG: export_page_to_json, fodg_is_multi_page
Covers Gnumeric: gnumeric_column_variance, gnumeric_is_rectangular
Covers DIF: dif_numeric_mean, dif_is_empty
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import load as load_fodg, export_page_to_json, fodg_is_multi_page
from gnumeric.gnumeric_codec import gnumeric_column_variance, gnumeric_is_rectangular
from dif.dif_parser import dif_numeric_mean, dif_is_empty
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
_GN_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _shapes_fodg():
    return str(next(f for f in sorted(_FODG_DIR.glob("*.fodg")) if "shapes" in f.name))


def _minimal_gnumeric():
    return str(next(f for f in sorted(_GN_DIR.glob("*.gnumeric")) if "minimal" in f.name))


def _numeric_dif():
    return str(next(f for f in sorted(_DIF_DIR.glob("*.dif")) if "numeric" in f.name))


def test_export_page_to_json_returns_str(tmp_path):
    path = _shapes_fodg()
    model = load_fodg(path)
    result = export_page_to_json(model, 0)
    assert isinstance(result, str)
    assert len(result) > 0
    parsed = json.loads(result)
    assert isinstance(parsed, dict)

    record = {"format": "fodg", "function": "export_page_to_json", "length": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] > 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_is_multi_page_returns_bool(tmp_path):
    path = _shapes_fodg()
    result = fodg_is_multi_page(path)
    assert isinstance(result, bool)
    assert result is False  # shapes-basic has 1 page

    record = {"format": "fodg", "function": "fodg_is_multi_page", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_multi"] is False
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_column_variance_returns_float(tmp_path):
    path = _minimal_gnumeric()
    result = gnumeric_column_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "gnumeric", "function": "gnumeric_column_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_is_rectangular_returns_bool(tmp_path):
    path = _minimal_gnumeric()
    result = gnumeric_is_rectangular(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_is_rectangular", "is_rectangular": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_rectangular"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_mean_returns_float(tmp_path):
    path = _numeric_dif()
    result = dif_numeric_mean(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "dif", "function": "dif_numeric_mean", "mean": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_dif_is_empty_returns_bool(tmp_path):
    path = _numeric_dif()
    result = dif_is_empty(path)
    assert isinstance(result, bool)
    assert result is False

    record = {"format": "dif", "function": "dif_is_empty", "is_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_empty"] is False
    assert json.dumps(loaded[0]) is not None

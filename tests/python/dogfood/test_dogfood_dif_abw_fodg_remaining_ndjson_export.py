"""
Dogfood pipeline: DIF remaining + ABW remaining + FODG remaining → NDJSON export.
Covers DIF: dif_col_count_variance, dif_unique_value_count
Covers ABW: abw_is_multi_paragraph, abw_heading_density
Covers FODG: fodg_shape_count_variance, fodg_is_text_only
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_col_count_variance, dif_unique_value_count
from abw.abw_codec import abw_is_multi_paragraph, abw_heading_density
from fodg.fodg_codec import fodg_shape_count_variance, fodg_is_text_only
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _numeric_dif():
    return str(next(f for f in sorted(_DIF_DIR.glob("*.dif")) if "numeric" in f.name))


def _two_para_abw():
    return str(next(f for f in sorted(_ABW_DIR.glob("*.abw")) if "two" in f.name or "paragraph" in f.name))


def _shapes_fodg():
    return str(next(f for f in sorted(_FODG_DIR.glob("*.fodg")) if "shapes" in f.name))


def test_dif_col_count_variance_returns_float(tmp_path):
    path = _numeric_dif()
    result = dif_col_count_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "dif", "function": "dif_col_count_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_dif_unique_value_count_returns_int(tmp_path):
    path = _numeric_dif()
    result = dif_unique_value_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "dif", "function": "dif_unique_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_abw_is_multi_paragraph_returns_bool(tmp_path):
    path = _two_para_abw()
    result = abw_is_multi_paragraph(path)
    assert isinstance(result, bool)
    assert result is True  # two-paragraphs.abw has 2 paragraphs

    record = {"format": "abw", "function": "abw_is_multi_paragraph", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_multi"] is True
    assert json.dumps(loaded[0]) is not None


def test_abw_heading_density_returns_float(tmp_path):
    path = _two_para_abw()
    result = abw_heading_density(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "abw", "function": "abw_heading_density", "density": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodg_shape_count_variance_returns_float(tmp_path):
    path = _shapes_fodg()
    result = fodg_shape_count_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "fodg", "function": "fodg_shape_count_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodg_is_text_only_returns_bool(tmp_path):
    path = _shapes_fodg()
    result = fodg_is_text_only(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_is_text_only", "is_text_only": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_text_only"], bool)
    assert json.dumps(loaded[0]) is not None

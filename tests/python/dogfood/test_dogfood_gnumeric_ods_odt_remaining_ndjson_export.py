"""
Dogfood pipeline: Gnumeric remaining + ODS remaining + ODT remaining → NDJSON export.
Covers Gnumeric: gnumeric_min_column_count, gnumeric_avg_column_count
Covers ODS: ods_column_value_variance, ods_row_value_variance
Covers ODT: odt_avg_chars_per_paragraph, odt_paragraph_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_min_column_count, gnumeric_avg_column_count
from ods.ods_parser import ods_column_value_variance, ods_row_value_variance
from odt.odt_parser import odt_avg_chars_per_paragraph, odt_paragraph_variance
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GN_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _minimal_gnumeric():
    return str(next(f for f in sorted(_GN_DIR.glob("*.gnumeric")) if "minimal" in f.name))


def _minimal_ods():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _minimal_odt():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def test_gnumeric_min_column_count_returns_int(tmp_path):
    path = _minimal_gnumeric()
    result = gnumeric_min_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_min_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_column_count_returns_float(tmp_path):
    path = _minimal_gnumeric()
    result = gnumeric_avg_column_count(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "gnumeric", "function": "gnumeric_avg_column_count", "avg": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_column_value_variance_returns_float(tmp_path):
    path = _minimal_ods()
    result = ods_column_value_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_column_value_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_row_value_variance_returns_float(tmp_path):
    path = _minimal_ods()
    result = ods_row_value_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_row_value_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_avg_chars_per_paragraph_returns_float(tmp_path):
    path = _minimal_odt()
    result = odt_avg_chars_per_paragraph(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_avg_chars_per_paragraph", "avg": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_paragraph_variance_returns_float(tmp_path):
    path = _minimal_odt()
    result = odt_paragraph_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_paragraph_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None

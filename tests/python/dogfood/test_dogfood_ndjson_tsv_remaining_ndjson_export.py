"""
Dogfood pipeline: NDJSON remaining + TSV remaining → NDJSON export.
Covers NDJSON: ndjson_avg_field_name_length, ndjson_record_size_variance
Covers TSV: probe_tsv, tsv_row_length_variance, tsv_column_type_counts, tsv_string_density
"""
from __future__ import annotations
import json
import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    ndjson_avg_field_name_length,
    ndjson_record_size_variance,
)
from tsv.tsv_parser import (
    probe_tsv,
    tsv_row_length_variance,
    tsv_column_type_counts,
    tsv_string_density,
)

_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _multi_tsv():
    return str(_TSV_DIR / "multi-column.tsv")


def _make_ndjson(tmp_path):
    path = str(tmp_path / "sample.ndjson")
    records = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "score": 95},
    ]
    write_ndjson(records, path)
    return path


def test_ndjson_avg_field_name_length_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_avg_field_name_length(path)
    assert isinstance(result, float)
    assert result >= 1.0

    record = {"format": "ndjson", "function": "ndjson_avg_field_name_length", "avg_length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_length"] >= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_record_size_variance_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_record_size_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ndjson", "function": "ndjson_record_size_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_probe_tsv_returns_dict(tmp_path):
    path = _multi_tsv()
    result = probe_tsv(path)
    assert isinstance(result, dict)
    assert result.get("exists") is True
    assert result.get("delimiter") == "\t"

    record = {"format": "tsv", "function": "probe_tsv", "column_count": result.get("column_count", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["column_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_tsv_row_length_variance_returns_float(tmp_path):
    path = _multi_tsv()
    result = tsv_row_length_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "tsv", "function": "tsv_row_length_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_column_type_counts_returns_dict(tmp_path):
    path = _multi_tsv()
    result = tsv_column_type_counts(path)
    assert isinstance(result, dict)
    assert len(result) > 0

    record = {"format": "tsv", "function": "tsv_column_type_counts",
              "numeric": result.get("numeric", 0), "string": result.get("string", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["numeric"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_string_density_returns_float(tmp_path):
    path = _multi_tsv()
    result = tsv_string_density(path)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_string_density", "density": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None

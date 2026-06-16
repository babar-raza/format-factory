"""
Dogfood pipeline: TSV remaining analytics → NDJSON export.
Covers: get_capabilities, tsv_min_field_count, tsv_nonempty_row_ratio,
        tsv_numeric_sum, tsv_avg_numeric_value, count_distinct_values
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    get_capabilities,
    tsv_min_field_count,
    tsv_nonempty_row_ratio,
    tsv_numeric_sum,
    tsv_avg_numeric_value,
    count_distinct_values,
    parse_tsv_strict,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _tsv_file():
    for f in sorted(_TSV_DIR.glob("*.tsv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_TSV_DIR.glob("*.tsv")))))


def test_tsv_get_capabilities_returns_dict(tmp_path):
    result = get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result
    assert result["format"] == "tsv"

    record = {"format": "tsv", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "tsv"
    assert json.dumps(loaded[0]) is not None


def test_tsv_min_field_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_min_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_min_field_count", "min_fields": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["min_fields"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_nonempty_row_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_nonempty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_nonempty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_numeric_sum_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "tsv", "function": "tsv_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_tsv_avg_numeric_value_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_avg_numeric_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "tsv", "function": "tsv_avg_numeric_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_tsv_count_distinct_values_returns_int(tmp_path):
    path = _tsv_file()
    parsed = parse_tsv_strict(path)
    headers = parsed.get("headers", [])
    if not headers:
        pytest.skip("No headers in TSV file")
    col = headers[0]
    result = count_distinct_values(path, col)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "count_distinct_values", "col": col, "distinct": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["distinct"] >= 0
    assert json.dumps(loaded[0]) is not None

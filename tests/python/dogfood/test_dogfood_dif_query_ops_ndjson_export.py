"""
Dogfood pipeline: DIF query ops → NDJSON export.
Covers: get_row_values, get_column_values, get_vector_count,
        count_distinct_values, export_to_html, sum_row
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    get_row_values,
    get_column_values,
    get_vector_count,
    count_distinct_values,
    export_to_html,
    sum_row,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


def _numeric_dif():
    return str(next(f for f in _valid_dif_files() if "numeric" in f.name))


def _minimal_dif():
    return str(next(f for f in _valid_dif_files() if "minimal" in f.name))


def test_get_row_values_returns_list(tmp_path):
    path = _numeric_dif()
    row = get_row_values(path, 0)
    assert isinstance(row, list)
    assert len(row) > 0
    # numeric-row.dif row 0 has numeric values
    assert all(isinstance(v, (int, float)) for v in row)

    record = {"format": "dif", "function": "get_row_values", "row_index": 0, "count": len(row)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == len(row)
    assert json.dumps(loaded[0]) is not None


def test_get_column_values_returns_list(tmp_path):
    path = _numeric_dif()
    col = get_column_values(path, 0)
    assert isinstance(col, list)
    assert len(col) > 0

    record = {"format": "dif", "function": "get_column_values", "col_index": 0, "count": len(col)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == len(col)
    assert json.dumps(loaded[0]) is not None


def test_get_vector_count(tmp_path):
    path = _numeric_dif()
    count = get_vector_count(path)
    assert isinstance(count, int)
    assert count > 0

    record = {"format": "dif", "function": "get_vector_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_count_distinct_values(tmp_path):
    path = _numeric_dif()
    distinct = count_distinct_values(path, 0)
    assert isinstance(distinct, int)
    assert distinct >= 1

    record = {"format": "dif", "function": "count_distinct_values", "col": 0, "distinct": distinct}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["distinct"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_export_to_html_returns_string(tmp_path):
    path = _minimal_dif()
    html = export_to_html(path)
    assert isinstance(html, str)
    assert len(html) > 0
    assert "<" in html  # HTML has tags

    record = {"format": "dif", "function": "export_to_html", "html_length": len(html)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["html_length"] > 0
    assert json.dumps(loaded[0]) is not None


def test_sum_row_returns_float(tmp_path):
    path = _numeric_dif()
    total = sum_row(path, 0)
    assert isinstance(total, float)
    # numeric-row.dif row 0 has [1.0, 2.0, 3.0] => sum = 6.0
    assert abs(total - 6.0) < 1e-6

    record = {"format": "dif", "function": "sum_row", "row": 0, "sum": total}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["sum"] - 6.0) < 1e-6
    assert json.dumps(loaded[0]) is not None

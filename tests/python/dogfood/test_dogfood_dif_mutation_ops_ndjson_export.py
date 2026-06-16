"""
Dogfood pipeline: DIF mutation ops → NDJSON export.
Covers: set_cell_value, delete_row, add_row, sum_column, average_column, get_row_as_dict
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

from dif.dif_parser import (
    parse_dif_strict,
    set_cell_value,
    delete_row,
    add_row,
    sum_column,
    average_column,
    get_row_as_dict,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _numeric_dif():
    return str(next(f for f in sorted(_DIF_DIR.glob("*.dif")) if "numeric" in f.name))


def test_set_cell_value_returns_dict(tmp_path):
    path = _numeric_dif()
    dest = str(tmp_path / "modified.dif")
    result = set_cell_value(path, dest, 0, 0, 999.0, "numeric")
    assert isinstance(result, dict)
    assert os.path.exists(dest)

    record = {"format": "dif", "function": "set_cell_value", "row": 0, "col": 0, "value": 999.0}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] == 999.0
    assert json.dumps(loaded[0]) is not None


def test_delete_row_returns_dict(tmp_path):
    path = _numeric_dif()
    doc = parse_dif_strict(path)
    original_rows = doc.tuples
    result = delete_row(doc, 0)
    assert isinstance(result, dict)
    # Row count decreases
    assert result.get("row_count", 0) == original_rows - 1 or len(result.get("rows", [])) == original_rows - 1

    record = {"format": "dif", "function": "delete_row", "rows_before": original_rows}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["rows_before"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_add_row_returns_dict(tmp_path):
    path = _numeric_dif()
    doc = parse_dif_strict(path)
    original_rows = doc.tuples
    result = add_row(doc, [100.0, 200.0, 300.0])
    assert isinstance(result, dict)
    new_rows = result.get("row_index", 0)
    assert result.get("success") is True
    assert new_rows > 0

    record = {"format": "dif", "function": "add_row", "rows_before": original_rows, "row_index": new_rows}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_index"] > 0
    assert json.dumps(loaded[0]) is not None


def test_sum_column_returns_float(tmp_path):
    path = _numeric_dif()
    total = sum_column(path, 0)
    assert isinstance(total, float)

    record = {"format": "dif", "function": "sum_column", "col": 0, "sum": total}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], float)
    assert json.dumps(loaded[0]) is not None


def test_average_column_returns_float(tmp_path):
    path = _numeric_dif()
    avg = average_column(path, 0)
    assert isinstance(avg, float)

    record = {"format": "dif", "function": "average_column", "col": 0, "avg": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], float)
    assert json.dumps(loaded[0]) is not None


def test_get_row_as_dict_returns_dict(tmp_path):
    path = _numeric_dif()
    doc = parse_dif_strict(path)
    row_dict = get_row_as_dict(doc, 0)
    assert isinstance(row_dict, dict)
    assert len(row_dict) > 0
    # All values should be numeric
    assert all(isinstance(v, (int, float)) for v in row_dict.values())

    # Convert dict keys to strings for JSON serialization
    record = {"format": "dif", "function": "get_row_as_dict", "row": 0, "col_count": len(row_dict)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["col_count"] > 0
    assert json.dumps(loaded[0]) is not None

"""
Dogfood pipeline: SYLK final ops → NDJSON export.
Covers: get_cell_count, get_all_values, add_row, delete_row,
        set_cell_value, get_row_values
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    get_cell_count,
    get_all_values,
    add_row,
    delete_row,
    set_cell_value,
    get_row_values,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _minimal_slk():
    return str(next(f for f in sorted(_SYLK_DIR.glob("*.slk")) if "minimal" in f.name))


def _numeric_slk():
    return str(next(f for f in sorted(_SYLK_DIR.glob("*.slk")) if "numeric" in f.name))


def test_get_cell_count(tmp_path):
    path = _minimal_slk()
    count = get_cell_count(path)
    assert isinstance(count, int)
    assert count > 0  # minimal-2x2.slk has 4 cells

    record = {"format": "sylk", "function": "get_cell_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_get_all_values(tmp_path):
    path = _minimal_slk()
    values = get_all_values(path)
    assert isinstance(values, list)
    assert len(values) > 0
    assert "Name" in values or "Alpha" in values

    record = {"format": "sylk", "function": "get_all_values", "count": len(values)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_add_row_creates_file(tmp_path):
    path = _minimal_slk()
    dest = str(tmp_path / "out.slk")
    result = add_row(path, dest, [100, 200])
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert result.get("row_index", 0) > 0
    import os
    assert os.path.exists(dest)

    record = {"format": "sylk", "function": "add_row", "row_index": result["row_index"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_index"] > 0
    assert json.dumps(loaded[0]) is not None


def test_delete_row_creates_file(tmp_path):
    path = _minimal_slk()
    dest = str(tmp_path / "out.slk")
    result = delete_row(path, dest, 1)
    assert isinstance(result, dict)
    assert result.get("success") is True
    import os
    assert os.path.exists(dest)

    record = {"format": "sylk", "function": "delete_row", "success": result["success"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["success"] is True
    assert json.dumps(loaded[0]) is not None


def test_set_cell_value_returns_dict(tmp_path):
    path = _minimal_slk()
    dest = str(tmp_path / "out.slk")
    result = set_cell_value(path, dest, 1, 1, "NewName", "string")
    assert isinstance(result, dict)
    assert result.get("ok") is True
    assert result.get("new_value") == "NewName"

    record = {"format": "sylk", "function": "set_cell_value", "ok": result["ok"], "new_value": result["new_value"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ok"] is True
    assert loaded[0]["new_value"] == "NewName"
    assert json.dumps(loaded[0]) is not None


def test_get_row_values(tmp_path):
    path = _minimal_slk()
    # SYLK rows are 1-indexed
    row = get_row_values(path, 1)
    assert isinstance(row, list)
    assert len(row) == 2  # minimal-2x2 row 1 has [Name, Value]
    assert "Name" in row

    record = {"format": "sylk", "function": "get_row_values", "row": 1, "values": row}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "Name" in loaded[0]["values"]
    assert json.dumps(loaded[0]) is not None

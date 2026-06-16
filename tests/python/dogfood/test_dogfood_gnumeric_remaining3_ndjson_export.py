"""
Dogfood pipeline: Gnumeric remaining model/path functions → NDJSON export.
Covers: get_sheet_metadata, get_sheet_names, get_row_count, get_column_count,
        get_row, get_column
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    get_sheet_metadata,
    get_sheet_names,
    get_row_count,
    get_column_count,
    get_row,
    get_column,
    load,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _gnumeric_file():
    # Prefer a non-empty file
    for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
        meta = get_sheet_metadata(str(f))
        if any(m["cell_count"] > 0 for m in meta):
            return str(f)
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def test_gnumeric_get_sheet_metadata_returns_list(tmp_path):
    path = _gnumeric_file()
    result = get_sheet_metadata(path)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert "name" in result[0]

    record = {"format": "gnumeric", "function": "get_sheet_metadata", "sheet_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_sheet_names_returns_list(tmp_path):
    path = _gnumeric_file()
    result = get_sheet_names(path)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert isinstance(result[0], str)

    record = {"format": "gnumeric", "function": "get_sheet_names", "first_name": result[0]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["first_name"], str)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_row_count_returns_int(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = get_row_count(model, 0)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "get_row_count", "row_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_column_count_returns_int(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = get_column_count(model, 0)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "get_column_count", "col_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["col_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_row_returns_list(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = get_row(model, 0, 0)
    assert isinstance(result, list)

    record = {"format": "gnumeric", "function": "get_row", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_column_returns_list(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = get_column(model, 0, 0)
    assert isinstance(result, list)

    record = {"format": "gnumeric", "function": "get_column", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None

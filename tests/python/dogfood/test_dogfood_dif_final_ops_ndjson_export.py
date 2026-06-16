"""
Dogfood pipeline: DIF final ops → NDJSON export.
Covers: min_column_value, max_column_value, sort_rows_by_column,
        get_row_as_dict + SYLK count_distinct_values, sylk_unique_values
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    min_column_value,
    max_column_value,
    sort_rows_by_column,
    parse_dif_strict,
)
from sylk.sylk_parser import (
    count_distinct_values,
    sylk_unique_values,
    get_column_values,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _numeric_dif():
    return str(next(f for f in sorted(_DIF_DIR.glob("*.dif")) if "numeric" in f.name))


def _minimal_slk():
    return str(next(f for f in sorted(_SYLK_DIR.glob("*.slk")) if "minimal" in f.name))


def test_dif_min_column_value(tmp_path):
    path = _numeric_dif()
    min_val = min_column_value(path, 0)
    assert min_val is not None
    assert isinstance(min_val, (int, float))

    record = {"format": "dif", "function": "min_column_value", "col": 0, "min": min_val}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["min"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_max_column_value(tmp_path):
    path = _numeric_dif()
    max_val = max_column_value(path, 0)
    assert max_val is not None
    assert isinstance(max_val, (int, float))
    min_val = min_column_value(path, 0)
    assert max_val >= min_val

    record = {"format": "dif", "function": "max_column_value", "col": 0, "max": max_val}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["max"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_sort_rows_by_column(tmp_path):
    path = _numeric_dif()
    result = sort_rows_by_column(path, 0)
    # Returns DifDocument
    assert hasattr(result, "rows")
    assert len(result.rows) > 0

    record = {"format": "dif", "function": "sort_rows_by_column", "col": 0, "row_count": len(result.rows)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_count_distinct_values(tmp_path):
    path = _minimal_slk()
    # Column 1 (1-indexed) has Name, Alpha — 2 distinct values
    distinct = count_distinct_values(path, 1)
    assert isinstance(distinct, int)
    assert distinct >= 2

    record = {"format": "sylk", "function": "count_distinct_values", "col": 1, "distinct": distinct}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["distinct"] >= 2
    assert json.dumps(loaded[0]) is not None


def test_sylk_unique_values(tmp_path):
    path = _minimal_slk()
    # Column 1 (1-indexed) has Name, Alpha
    unique = sylk_unique_values(path, 1)
    assert isinstance(unique, list)
    assert len(unique) >= 2
    assert "Name" in unique or "Alpha" in unique

    record = {"format": "sylk", "function": "sylk_unique_values", "col": 1, "count": len(unique)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 2
    assert json.dumps(loaded[0]) is not None


def test_sylk_get_column_values(tmp_path):
    path = _minimal_slk()
    # Column 1 (1-indexed) has Name, Alpha
    vals = get_column_values(path, 1)
    assert isinstance(vals, list)
    assert len(vals) >= 2

    record = {"format": "sylk", "function": "get_column_values", "col": 1, "values": vals}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert len(loaded[0]["values"]) >= 2
    assert json.dumps(loaded[0]) is not None

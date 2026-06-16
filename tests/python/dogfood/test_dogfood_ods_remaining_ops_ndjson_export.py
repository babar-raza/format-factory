"""
Dogfood pipeline: ODS remaining ops → NDJSON export.
Covers: get_capabilities, probe_ods, ods_is_single_row, ods_avg_row_length,
        ods_nonempty_cell_count, ods_cell_value_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    get_capabilities,
    probe_ods,
    ods_is_single_row,
    ods_avg_row_length,
    ods_nonempty_cell_count,
    ods_cell_value_variance,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_get_capabilities_returns_dict(tmp_path):
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert caps.get("format") == "ods"
    assert isinstance(caps.get("supported"), list)

    record = {"format": "ods", "function": "get_capabilities", "gate": caps.get("gate")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format"] == "ods"
    assert json.dumps(loaded[0]) is not None


def test_probe_ods_returns_dict(tmp_path):
    path = _valid_ods()
    result = probe_ods(path)
    assert isinstance(result, dict)
    assert result.get("valid_container") is True

    record = {"format": "ods", "function": "probe_ods", "valid": result.get("valid_container")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_ods_is_single_row_returns_bool(tmp_path):
    path = _valid_ods()
    result = ods_is_single_row(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_single_row", "is_single_row": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single_row"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_row_length_returns_float(tmp_path):
    path = _valid_ods()
    result = ods_avg_row_length(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_avg_row_length", "avg_row_length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_row_length"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_nonempty_cell_count_returns_int(tmp_path):
    path = _valid_ods()
    result = ods_nonempty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_nonempty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_cell_value_variance_returns_float(tmp_path):
    path = _valid_ods()
    result = ods_cell_value_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_cell_value_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None

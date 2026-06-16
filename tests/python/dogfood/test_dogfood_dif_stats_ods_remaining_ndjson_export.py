"""
Dogfood pipeline: DIF stats remaining + ODS remaining → NDJSON export.
Covers: dif_string_value_list, dif_numeric_range,
        get_capabilities (ods), get_all_values, get_cell_count, filter_rows_by_value
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import parse_dif
from dif.dif_stats import dif_string_value_list, dif_numeric_range
from ods.ods_parser import get_capabilities, get_all_values, get_cell_count, filter_rows_by_value
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_dif_string_value_list_returns_list(tmp_path):
    path = _dif_file()
    doc = parse_dif(path)
    result = dif_string_value_list(doc)
    assert isinstance(result, list)
    record = {"format": "dif", "function": "dif_string_value_list", "string_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["string_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_range_returns_dict(tmp_path):
    path = _dif_file()
    doc = parse_dif(path)
    result = dif_numeric_range(doc)
    assert isinstance(result, dict)
    assert "numeric_count" in result
    record = {"format": "dif", "function": "dif_numeric_range", "numeric_count": result.get("numeric_count", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["numeric_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_get_capabilities_returns_dict(tmp_path):
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert caps.get("format") == "ods"
    record = {"format": "ods", "function": "get_capabilities", "gate": caps.get("gate")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format"] == "ods"
    assert json.dumps(loaded[0]) is not None


def test_ods_get_all_values_returns_list(tmp_path):
    path = _ods_file()
    result = get_all_values(path)
    assert isinstance(result, list)
    assert len(result) >= 1
    record = {"format": "ods", "function": "get_all_values", "value_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_ods_get_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = get_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "ods", "function": "get_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_filter_rows_by_value_returns_list(tmp_path):
    path = _ods_file()
    all_vals = get_all_values(path)
    str_val = next((v for v in all_vals if isinstance(v, str)), None)
    if str_val is None:
        pytest.skip("No string values in ODS file")
    result = filter_rows_by_value(path, 0, str_val)
    assert isinstance(result, list)
    record = {"format": "ods", "function": "filter_rows_by_value", "match_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["match_count"] >= 0
    assert json.dumps(loaded[0]) is not None

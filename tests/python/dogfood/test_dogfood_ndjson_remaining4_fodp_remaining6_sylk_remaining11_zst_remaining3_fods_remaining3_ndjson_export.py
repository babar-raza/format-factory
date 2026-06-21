"""
Dogfood pipeline: NDJSON remaining + FODP remaining + SYLK remaining + ZST remaining + FODS remaining -> NDJSON export.
Covers NDJSON: ndjson_bool_ratio, ndjson_numeric_ratio
Covers FODP: fodp_notes_length_sum, fodp_total_shape_area
Covers SYLK: sylk_distinct_value_count, sylk_max_value_length, sylk_total_value_sum
Covers ZST: zst_file_info, zst_frame_header_descriptor, zst_is_minimal_frame
Covers FODS: fods_avg_cell_value_length, fods_total_string_cells
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_bool_ratio, ndjson_numeric_ratio, write_ndjson, load_ndjson
from fodp.fodp_codec import fodp_notes_length_sum, fodp_total_shape_area
from sylk.sylk_parser import sylk_distinct_value_count, sylk_max_value_length, sylk_total_value_sum
from zst.zst_codec import zst_file_info, zst_frame_header_descriptor, zst_is_minimal_frame
from fods import parse_fods
from fods.neutral_model import fods_avg_cell_value_length, fods_total_string_cells

_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _zst_file():
    return str(next(iter(sorted(_ZST_DIR.glob("*.zst")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


# --- NDJSON ---

def test_ndjson_bool_ratio_returns_float(tmp_path):
    ndjson_src = tmp_path / "src.ndjson"
    write_ndjson([{"a": True, "b": False, "c": 42}], str(ndjson_src))
    result = ndjson_bool_ratio(str(ndjson_src))
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_bool_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_numeric_ratio_returns_float(tmp_path):
    ndjson_src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1, "b": 2.5, "c": "text"}], str(ndjson_src))
    result = ndjson_numeric_ratio(str(ndjson_src))
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_numeric_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- FODP ---

def test_fodp_notes_length_sum_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_notes_length_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_notes_length_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_total_shape_area_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_total_shape_area(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_total_shape_area", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- SYLK ---

def test_sylk_distinct_value_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_distinct_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_distinct_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_value_length_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_max_value_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_max_value_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_total_value_sum_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_total_value_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "sylk_total_value_sum", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


# --- ZST ---

def test_zst_file_info_returns_dict(tmp_path):
    path = _zst_file()
    result = zst_file_info(path)
    assert isinstance(result, dict)

    record = {"format": "zst", "function": "zst_file_info", "keys": list(result.keys())}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["keys"], list)
    assert json.dumps(loaded[0]) is not None


def test_zst_frame_header_descriptor_returns_int(tmp_path):
    path = _zst_file()
    result = zst_frame_header_descriptor(path)
    assert isinstance(result, int)

    record = {"format": "zst", "function": "zst_frame_header_descriptor", "descriptor": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_zst_is_minimal_frame_returns_bool(tmp_path):
    path = _zst_file()
    result = zst_is_minimal_frame(path)
    assert isinstance(result, bool)

    record = {"format": "zst", "function": "zst_is_minimal_frame", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- FODS ---

def test_fods_total_string_cells_returns_int(tmp_path):
    path = _fods_file()
    import os
    workbook = parse_fods(os.path.abspath(path))
    result = fods_total_string_cells(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_total_string_cells", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_cell_value_length_returns_float(tmp_path):
    path = _fods_file()
    import os
    workbook = parse_fods(os.path.abspath(path))
    result = fods_avg_cell_value_length(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_avg_cell_value_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None

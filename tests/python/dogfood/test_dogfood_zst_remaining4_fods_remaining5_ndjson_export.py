"""
Dogfood pipeline: ZST remaining + FODS remaining -> NDJSON export.
Covers ZST: zst_avg_compression_per_byte, zst_bytes_saved, zst_frame_count_ratio,
            zst_header_size, zst_is_smaller_than_1kb, zst_magic_valid,
            zst_overhead_bytes, zst_ratio_vs_uncompressed, zst_size_exceeds_100k
Covers FODS: fods_file_size_bytes, fods_has_formula_cells, fods_numeric_ratio
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    zst_avg_compression_per_byte,
    zst_bytes_saved,
    zst_frame_count_ratio,
    zst_header_size,
    zst_is_smaller_than_1kb,
    zst_magic_valid,
    zst_overhead_bytes,
    zst_ratio_vs_uncompressed,
    zst_size_exceeds_100k,
)
from fods import parse_fods
from fods.neutral_model import (
    fods_file_size_bytes,
    fods_has_formula_cells,
    fods_numeric_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _zst_file():
    return str(next(iter(sorted(_ZST_DIR.glob("*.zst")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


# --- ZST ---

def test_zst_avg_compression_per_byte_returns_float(tmp_path):
    path = _zst_file()
    result = zst_avg_compression_per_byte(path)
    assert isinstance(result, (int, float))

    record = {"format": "zst", "function": "zst_avg_compression_per_byte", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_zst_bytes_saved_returns_int(tmp_path):
    path = _zst_file()
    result = zst_bytes_saved(path)
    assert isinstance(result, int)

    record = {"format": "zst", "function": "zst_bytes_saved", "bytes": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_zst_frame_count_ratio_returns_float(tmp_path):
    path = _zst_file()
    result = zst_frame_count_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "zst", "function": "zst_frame_count_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_zst_header_size_returns_int(tmp_path):
    path = _zst_file()
    result = zst_header_size(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "zst", "function": "zst_header_size", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_zst_is_smaller_than_1kb_returns_bool(tmp_path):
    path = _zst_file()
    result = zst_is_smaller_than_1kb(path)
    assert isinstance(result, bool)

    record = {"format": "zst", "function": "zst_is_smaller_than_1kb", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_zst_magic_valid_returns_bool(tmp_path):
    path = _zst_file()
    result = zst_magic_valid(path)
    assert isinstance(result, bool)

    record = {"format": "zst", "function": "zst_magic_valid", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_zst_overhead_bytes_returns_int(tmp_path):
    path = _zst_file()
    result = zst_overhead_bytes(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "zst", "function": "zst_overhead_bytes", "bytes": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["bytes"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_zst_ratio_vs_uncompressed_returns_float(tmp_path):
    path = _zst_file()
    result = zst_ratio_vs_uncompressed(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "zst", "function": "zst_ratio_vs_uncompressed", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_zst_size_exceeds_100k_returns_bool(tmp_path):
    path = _zst_file()
    result = zst_size_exceeds_100k(path)
    assert isinstance(result, bool)

    record = {"format": "zst", "function": "zst_size_exceeds_100k", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- FODS ---

def test_fods_file_size_bytes_returns_int(tmp_path):
    path = _fods_file()
    result = fods_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "fods", "function": "fods_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None


def test_fods_has_formula_cells_returns_bool(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_has_formula_cells(workbook)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_has_formula_cells", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_numeric_ratio_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_numeric_ratio(workbook)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_numeric_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None

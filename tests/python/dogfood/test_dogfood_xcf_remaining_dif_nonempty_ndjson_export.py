"""
Dogfood pipeline: XCF remaining analytics + DIF nonempty → NDJSON export.
Covers: xcf_aspect_ratio, xcf_average_layer_size, xcf_canvas_area, xcf_canvas_size_bytes,
        get_capabilities (xcf), count_nonempty_cells (dif)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_aspect_ratio, xcf_average_layer_size, xcf_canvas_area, xcf_canvas_size_bytes, get_capabilities
from dif.dif_parser import count_nonempty_cells
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_xcf_aspect_ratio_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_aspect_ratio(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "xcf", "function": "xcf_aspect_ratio", "aspect_ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["aspect_ratio"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_average_layer_size_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_average_layer_size(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "xcf", "function": "xcf_average_layer_size", "avg_layer_size": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_layer_size"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_canvas_area_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_canvas_area(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "xcf", "function": "xcf_canvas_area", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_xcf_canvas_size_bytes_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_canvas_size_bytes(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "xcf", "function": "xcf_canvas_size_bytes", "size_bytes": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size_bytes"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_xcf_get_capabilities_returns_dict(tmp_path):
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert caps.get("format") == "xcf"
    assert isinstance(caps.get("supported"), list)

    record = {"format": "xcf", "function": "get_capabilities", "gate": caps.get("gate")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format"] == "xcf"
    assert json.dumps(loaded[0]) is not None


def test_dif_count_nonempty_cells_returns_int(tmp_path):
    path = _dif_file()
    result = count_nonempty_cells(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "count_nonempty_cells", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

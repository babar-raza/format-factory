"""
Dogfood pipeline: FODT neutral remaining + Gnumeric model-based → NDJSON export.
Covers: document_footnote_count, document_change_tracking_summary, document_block_type_count,
        count_nonempty_cells (gnumeric), average_column (gnumeric), average_row (gnumeric)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_footnote_count, document_change_tracking_summary, document_block_type_count
from fodt.parser import parse_fodt
from gnumeric.gnumeric_codec import count_nonempty_cells, average_column, average_row, load
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _gnumeric_file():
    for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
        if "minimal" in f.name or "multi" in f.name:
            return str(f)
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def test_fodt_document_footnote_count_returns_dict(tmp_path):
    path = _fodt_file()
    model = parse_fodt(path)
    result = document_footnote_count(model)
    assert isinstance(result, dict)
    assert "total" in result
    assert result["total"] >= 0

    record = {"format": "fodt", "function": "document_footnote_count", "total": result["total"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_document_change_tracking_returns_dict(tmp_path):
    path = _fodt_file()
    model = parse_fodt(path)
    result = document_change_tracking_summary(model)
    assert isinstance(result, dict)
    assert "tracked_change_count" in result
    assert result["tracked_change_count"] >= 0

    record = {"format": "fodt", "function": "document_change_tracking_summary", "change_count": result["tracked_change_count"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["change_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_document_block_type_count_returns_dict(tmp_path):
    path = _fodt_file()
    model = parse_fodt(path)
    result = document_block_type_count(model)
    assert isinstance(result, dict)
    assert len(result) >= 1

    record = {"format": "fodt", "function": "document_block_type_count", "type_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["type_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_count_nonempty_cells_returns_int(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = count_nonempty_cells(model, 0)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "count_nonempty_cells", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_average_column_returns_float(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = average_column(model, 0, 0)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "average_column", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_average_row_returns_float(tmp_path):
    path = _gnumeric_file()
    model = load(path)
    result = average_row(model, 0, 0)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "average_row", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None

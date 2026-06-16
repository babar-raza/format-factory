"""
Dogfood pipeline: FODS remaining + FODT remaining → NDJSON export.
Covers: fods_formula_count, fods_avg_cells_per_sheet, fods_is_multi_sheet,
        fods_min_row_count, document_table_row_count, fodt_table_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods
from fods.neutral_model import (
    fods_formula_count,
    fods_avg_cells_per_sheet,
    fods_is_multi_sheet,
    fods_min_row_count,
)
from fodt.neutral_model import document_table_row_count, fodt_table_count
from fodt import parse_fodt
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


def test_fods_formula_count(tmp_path):
    path = str(_valid_fods_files()[0])
    model = parse_fods(path)
    count = fods_formula_count(model)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "fods", "function": "fods_formula_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_cells_per_sheet(tmp_path):
    path = str(_valid_fods_files()[0])
    model = parse_fods(path)
    avg = fods_avg_cells_per_sheet(model)
    assert isinstance(avg, float)
    assert avg >= 0.0

    record = {"format": "fods", "function": "fods_avg_cells_per_sheet", "avg": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fods_is_multi_sheet(tmp_path):
    path = str(_valid_fods_files()[0])
    model = parse_fods(path)
    result = fods_is_multi_sheet(model)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_is_multi_sheet", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_min_row_count(tmp_path):
    path = str(_valid_fods_files()[0])
    model = parse_fods(path)
    count = fods_min_row_count(model)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "fods", "function": "fods_min_row_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_document_table_row_count(tmp_path):
    path = str(_valid_fodt_files()[0])
    model = parse_fodt(path)
    count = document_table_row_count(model, 0)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "fodt", "function": "document_table_row_count", "table": 0, "row_count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_table_count(tmp_path):
    path = str(_valid_fodt_files()[0])
    count = fodt_table_count(path)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "fodt", "function": "fodt_table_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None

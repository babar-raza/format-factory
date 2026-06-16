"""
Dogfood pipeline: FODP final + FODS validate + FODG remaining → NDJSON export.
Covers: get_page_metadata, fodp_avg_shapes_per_slide (FODP),
        validate_workbook (FODS), validate_document (FODT),
        get_page_text, duplicate_page (FODG)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import get_page_metadata, fodp_avg_shapes_per_slide
from fods import parse_fods
from fods.neutral_model import validate_workbook
from fodt.neutral_model import validate_document
from fodt import parse_fodt
from fodg.fodg_codec import load as load_fodg, get_page_text, duplicate_page
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodp_files():
    return sorted(_FODP_DIR.glob("*.fodp"))


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


def _valid_fodt_files():
    return sorted(_FODT_DIR.glob("*.fodt"))


def _shapes_fodg():
    return str(next(f for f in sorted(_FODG_DIR.glob("*.fodg")) if "shapes" in f.name))


def test_fodp_get_page_metadata(tmp_path):
    path = str(_valid_fodp_files()[0])
    metadata = get_page_metadata(path)
    assert isinstance(metadata, list)
    assert len(metadata) > 0
    assert "name" in metadata[0]

    record = {"format": "fodp", "function": "get_page_metadata", "slide_count": len(metadata), "first_name": metadata[0]["name"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["slide_count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_avg_shapes_per_slide(tmp_path):
    path = str(_valid_fodp_files()[0])
    avg = fodp_avg_shapes_per_slide(path)
    assert isinstance(avg, float)
    assert avg >= 0.0

    record = {"format": "fodp", "function": "fodp_avg_shapes_per_slide", "avg": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fods_validate_workbook(tmp_path):
    path = str(_valid_fods_files()[0])
    model = parse_fods(path)
    result = validate_workbook(model)
    # validate_workbook returns list[str] of issues
    assert isinstance(result, list)

    record = {"format": "fods", "function": "validate_workbook", "issue_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["issue_count"], int)
    assert json.dumps(loaded[0]) is not None


def test_fodt_validate_document(tmp_path):
    path = str(_valid_fodt_files()[0])
    model = parse_fodt(path)
    result = validate_document(model)
    # validate_document returns list[str] of issues
    assert isinstance(result, list)

    record = {"format": "fodt", "function": "validate_document", "issue_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["issue_count"], int)
    assert json.dumps(loaded[0]) is not None


def test_fodg_get_page_text(tmp_path):
    model = load_fodg(_shapes_fodg())
    texts = get_page_text(model, 0)
    assert isinstance(texts, list)
    # shapes-basic.fodg has shapes with text
    assert len(texts) > 0

    record = {"format": "fodg", "function": "get_page_text", "page": 0, "text_count": len(texts)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["text_count"] > 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_duplicate_page(tmp_path):
    model = load_fodg(_shapes_fodg())
    original_count = len(model.get("pages", []))
    updated = duplicate_page(model, 0)
    assert isinstance(updated, dict)
    assert len(updated["pages"]) == original_count + 1

    record = {"format": "fodg", "function": "duplicate_page", "pages_before": original_count, "pages_after": len(updated["pages"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["pages_after"] == loaded[0]["pages_before"] + 1
    assert json.dumps(loaded[0]) is not None

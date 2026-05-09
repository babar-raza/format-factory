"""
test_neutral_model.py -- Unit tests for fodt neutral_model module.

Covers: make_warning, build_document, validate_document (IR-FODT-015).
Gate 5 neutral model: 7 entities (Document, Block, List, ListItem, Table, TableRow, TableCell).
"""
from pathlib import Path

import pytest

from fodt import parse_fodt
from fodt.constants import FORMAT_ID, SPEC_VERSION
from fodt.neutral_model import build_document, make_warning, validate_document

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fodt"


def _sample(name):
    return str(SAMPLES / name)


# ---------------------------------------------------------------------------
# make_warning
# ---------------------------------------------------------------------------

def test_make_warning_required_fields():
    w = make_warning("TEST_CODE", "test message")
    assert w["code"] == "TEST_CODE"
    assert w["message"] == "test message"


def test_make_warning_no_source_by_default():
    w = make_warning("X", "y")
    assert "source" not in w


def test_make_warning_with_source():
    w = make_warning("X", "y", source="block:3")
    assert w["source"] == "block:3"


# ---------------------------------------------------------------------------
# build_document
# ---------------------------------------------------------------------------

def test_build_document_format_id():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    assert doc["format_id"] == FORMAT_ID


def test_build_document_spec_version():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    assert doc["spec_version"] == SPEC_VERSION


def test_build_document_empty_blocks():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    assert doc["blocks"] == []


def test_build_document_empty_lists():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    assert doc["lists"] == []


def test_build_document_empty_tables():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    assert doc["tables"] == []


def test_build_document_unsupported_sorted():
    doc = build_document("1.3", None, [], [], [], [], ["text-field", "macros", "embedded-frame"], [])
    assert doc["unsupported_features"] == sorted(["text-field", "macros", "embedded-frame"])


# ---------------------------------------------------------------------------
# validate_document violations
# ---------------------------------------------------------------------------

def test_validate_document_valid_minimal():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    violations = validate_document(doc)
    assert violations == []


def test_validate_document_missing_format_id():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    del doc["format_id"]
    violations = validate_document(doc)
    assert any("format_id" in v for v in violations)


def test_validate_document_wrong_format_id():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    doc["format_id"] = "fods"
    violations = validate_document(doc)
    assert any("format_id" in v for v in violations)


def test_validate_document_missing_blocks():
    doc = build_document("1.3", None, [], [], [], [], [], [])
    del doc["blocks"]
    violations = validate_document(doc)
    assert any("blocks" in v for v in violations)


def test_validate_document_block_missing_type():
    doc = build_document("1.3", None, [{"text": "hello"}], [], [], [], [], [])
    violations = validate_document(doc)
    assert any("type" in v for v in violations)


def test_validate_document_block_wrong_type():
    doc = build_document("1.3", None, [{"type": "span", "text": "x"}], [], [], [], [], [])
    violations = validate_document(doc)
    assert any("type" in v for v in violations)


def test_validate_document_heading_missing_level():
    block = {"type": "heading", "text": "H1", "heading_level": None}
    doc = build_document("1.3", None, [block], [], [], [], [], [])
    violations = validate_document(doc)
    assert any("heading_level" in v for v in violations)


def test_validate_document_heading_level_in_range():
    block = {"type": "heading", "text": "H2", "heading_level": 2}
    doc = build_document("1.3", None, [block], [], [], [], [], [])
    violations = validate_document(doc)
    assert violations == []


def test_validate_document_list_missing_items():
    doc = build_document("1.3", None, [], [{}], [], [], [], [])
    violations = validate_document(doc)
    assert any("items" in v for v in violations)


def test_validate_document_list_item_missing_level():
    doc = build_document("1.3", None, [], [{"items": [{"text": "x"}]}], [], [], [], [])
    violations = validate_document(doc)
    assert any("level" in v for v in violations)


def test_validate_document_table_missing_rows():
    doc = build_document("1.3", None, [], [], [{"name": None}], [], [], [])
    violations = validate_document(doc)
    assert any("rows" in v for v in violations)


# ---------------------------------------------------------------------------
# Integration: parse_fodt output passes validate_document
# ---------------------------------------------------------------------------

def test_parse_result_passes_neutral_model_validation():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert "error" not in result
    violations = validate_document(result)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == [], f"Unexpected violations: {neutral_violations}"


def test_headings_sample_passes_validation():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    assert "error" not in result
    violations = validate_document(result)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == []


def test_list_sample_passes_validation():
    result = parse_fodt(_sample("list-basic.fodt"))
    assert "error" not in result
    violations = validate_document(result)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == []


def test_table_sample_passes_validation():
    result = parse_fodt(_sample("table-basic.fodt"))
    assert "error" not in result
    violations = validate_document(result)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == []

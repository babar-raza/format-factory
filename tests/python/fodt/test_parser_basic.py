"""
test_parser_basic.py -- Basic functional tests for parse_fodt().

Covers: IR-FODT-001 (root/mimetype), IR-FODT-005 (paragraphs/headings),
        IR-FODT-006 (lists), IR-FODT-007 (tables), IR-FODT-010 (heading level).
Uses Gate 3 samples: 4 FODT files in samples/by-format/fodt/.
"""
from pathlib import Path

import pytest

from fodt import parse_fodt
from fodt.constants import FORMAT_ID, SPEC_VERSION

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fodt"


def _sample(name):
    return str(SAMPLES / name)


# ---------------------------------------------------------------------------
# Document-level fields (IR-FODT-001)
# ---------------------------------------------------------------------------

def test_format_id():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert result.get("format_id") == FORMAT_ID


def test_spec_version():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert result.get("spec_version") == SPEC_VERSION


def test_mimetype_present():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert "mimetype" in result


def test_no_error_on_minimal():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert "error" not in result


def test_blocks_is_list():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert isinstance(result.get("blocks"), list)


def test_lists_is_list():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert isinstance(result.get("lists"), list)


def test_tables_is_list():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert isinstance(result.get("tables"), list)


# ---------------------------------------------------------------------------
# Paragraphs and headings (IR-FODT-005)
# ---------------------------------------------------------------------------

def test_paragraphs_extracted():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    assert "error" not in result
    paragraphs = [b for b in result["blocks"] if b["type"] == "paragraph"]
    assert len(paragraphs) >= 1


def test_headings_extracted():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    assert "error" not in result
    headings = [b for b in result["blocks"] if b["type"] == "heading"]
    assert len(headings) >= 1


# ---------------------------------------------------------------------------
# Heading outline level (IR-FODT-010)
# ---------------------------------------------------------------------------

def test_heading_level_is_int():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    headings = [b for b in result["blocks"] if b["type"] == "heading"]
    for h in headings:
        assert isinstance(h["heading_level"], int), (
            f"Expected int, got {type(h['heading_level'])}"
        )


def test_heading_level_in_range():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    headings = [b for b in result["blocks"] if b["type"] == "heading"]
    for h in headings:
        assert 1 <= h["heading_level"] <= 6, (
            f"Heading level out of range: {h['heading_level']}"
        )


def test_paragraph_heading_level_is_none():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    paragraphs = [b for b in result["blocks"] if b["type"] == "paragraph"]
    for p in paragraphs:
        assert p["heading_level"] is None


# ---------------------------------------------------------------------------
# Lists (IR-FODT-006)
# ---------------------------------------------------------------------------

def test_lists_extracted():
    result = parse_fodt(_sample("list-basic.fodt"))
    assert "error" not in result
    assert len(result["lists"]) >= 1


def test_list_items_present():
    result = parse_fodt(_sample("list-basic.fodt"))
    for lst in result["lists"]:
        assert "items" in lst
        assert isinstance(lst["items"], list)


def test_list_items_have_text_and_level():
    result = parse_fodt(_sample("list-basic.fodt"))
    for lst in result["lists"]:
        for item in lst["items"]:
            assert "text" in item
            assert "level" in item
            assert isinstance(item["level"], int)
            assert item["level"] >= 1


# ---------------------------------------------------------------------------
# Tables (IR-FODT-007)
# ---------------------------------------------------------------------------

def test_tables_extracted():
    result = parse_fodt(_sample("table-basic.fodt"))
    assert "error" not in result
    assert len(result["tables"]) >= 1


def test_table_rows_present():
    result = parse_fodt(_sample("table-basic.fodt"))
    for table in result["tables"]:
        assert "rows" in table
        assert isinstance(table["rows"], list)


def test_table_cells_have_text():
    result = parse_fodt(_sample("table-basic.fodt"))
    for table in result["tables"]:
        for row in table["rows"]:
            assert "cells" in row
            for cell in row["cells"]:
                assert "text" in cell
                assert isinstance(cell["text"], str)


# ---------------------------------------------------------------------------
# Unsupported features and warnings fields present
# ---------------------------------------------------------------------------

def test_unsupported_features_is_list():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert isinstance(result.get("unsupported_features"), list)


def test_unsupported_features_is_sorted():
    result = parse_fodt(_sample("minimal-document.fodt"))
    uf = result.get("unsupported_features", [])
    assert uf == sorted(uf)


def test_warnings_is_list():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert isinstance(result.get("warnings"), list)


def test_parse_errors_is_list():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert isinstance(result.get("parse_errors"), list)

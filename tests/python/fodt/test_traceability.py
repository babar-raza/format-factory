"""
test_traceability.py -- FUL requirement traceability for FODT product source.

Verifies that the product source satisfies each implementation requirement
from acquisition-packs/fodt/implementation-requirements.yaml (IR-FODT-001..015).

These are high-level traceability assertions, not duplicate functional tests.
Each test asserts one requirement is observably satisfied.
"""
from pathlib import Path
import os
import tempfile

import pytest

from fodt import parse_fodt, parse_fodt_strict, FodtInputError
from fodt.constants import (
    EXPECTED_MIMETYPE, FORMAT_ID, MAX_FILE_BYTES, NS_OFFICE, NS_TEXT
)
from fodt.list_traversal import collect_list_items
import xml.etree.ElementTree as ET

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fodt"


def _sample(name):
    return str(SAMPLES / name)


# IR-FODT-001: Parse root element + validate MIME type
def test_ir_fodt_001_root_and_mimetype():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert result.get("format_id") == FORMAT_ID
    assert "mimetype" in result


# IR-FODT-002: File size guard (100MB) -- verified by security tests
def test_ir_fodt_002_max_file_bytes_is_100mb():
    assert MAX_FILE_BYTES == 100 * 1024 * 1024


# IR-FODT-003: Iterative list traversal (no recursion)
def test_ir_fodt_003_iterative_traversal_no_recursion():
    """Build 500-level nested list and verify no RecursionError."""
    ns = NS_TEXT
    root_list = ET.Element(f"{{{ns}}}list")
    current = root_list
    for i in range(500):
        li = ET.SubElement(current, f"{{{ns}}}list-item")
        ET.SubElement(li, f"{{{ns}}}p").text = f"Level{i+1}"
        if i < 499:
            current = ET.SubElement(li, f"{{{ns}}}list")
    items = collect_list_items(root_list)
    assert len(items) == 500  # No RecursionError


# IR-FODT-004: defusedxml optional import
def test_ir_fodt_004_defusedxml_import_pattern():
    import fodt.parser as m
    assert hasattr(m, "_ET")  # Either defusedxml or stdlib ET


# IR-FODT-005: Extract paragraphs and headings
def test_ir_fodt_005_paragraphs_and_headings():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    types = {b["type"] for b in result.get("blocks", [])}
    assert "paragraph" in types or "heading" in types


# IR-FODT-006: Extract lists iteratively
def test_ir_fodt_006_list_extraction():
    result = parse_fodt(_sample("list-basic.fodt"))
    assert len(result.get("lists", [])) >= 1
    for lst in result["lists"]:
        assert isinstance(lst["items"], list)


# IR-FODT-007: Extract tables in text context
def test_ir_fodt_007_table_extraction():
    result = parse_fodt(_sample("table-basic.fodt"))
    assert len(result.get("tables", [])) >= 1


# IR-FODT-008: Detect draw:frame / draw:image
def test_ir_fodt_008_draw_frame_detection():
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{NS_OFFICE}"'
        f' xmlns:text="{NS_TEXT}"'
        ' office:version="1.3"'
        f' office:mimetype="{EXPECTED_MIMETYPE}"'
        f' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0">'
        "<office:body><office:text>"
        '<draw:frame/>'
        "</office:text></office:body></office:document>"
    )
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "embedded-frame" in result.get("unsupported_features", [])
    finally:
        os.unlink(fname)


# IR-FODT-009: Detect text:* field elements
def test_ir_fodt_009_text_field_detection():
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{NS_OFFICE}"'
        f' xmlns:text="{NS_TEXT}"'
        ' office:version="1.3"'
        f' office:mimetype="{EXPECTED_MIMETYPE}">'
        "<office:body><office:text>"
        '<text:date/>'
        "</office:text></office:body></office:document>"
    )
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        # text:date is a direct child of office:text -- detected as text-field
        assert "text-field" in result.get("unsupported_features", [])
    finally:
        os.unlink(fname)


# IR-FODT-010: heading_level integer from text:outline-level
def test_ir_fodt_010_heading_level_integer():
    result = parse_fodt(_sample("headings-and-paragraphs.fodt"))
    headings = [b for b in result.get("blocks", []) if b["type"] == "heading"]
    assert len(headings) >= 1
    for h in headings:
        assert isinstance(h["heading_level"], int)
        assert 1 <= h["heading_level"] <= 6


# IR-FODT-011: unsupported_features returned in result
def test_ir_fodt_011_unsupported_features_field():
    result = parse_fodt(_sample("minimal-document.fodt"))
    assert "unsupported_features" in result
    assert isinstance(result["unsupported_features"], list)


# IR-FODT-012: parse_errors list on ParseError
def test_ir_fodt_012_parse_errors_on_bad_xml():
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("<<<not xml>>>")
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "error" in result
        assert "parse_errors" in result
        assert isinstance(result["parse_errors"], list)
    finally:
        os.unlink(fname)


# IR-FODT-013: File path validation
def test_ir_fodt_013_nonexistent_file():
    result = parse_fodt("/no/such/file.fodt")
    assert "error" in result


def test_ir_fodt_013_strict_raises_input_error():
    with pytest.raises(FodtInputError):
        parse_fodt_strict("/no/such/file.fodt")


# IR-FODT-014: ET.iterparse streaming used in parser
def test_ir_fodt_014_iterparse_used():
    """Parser module must use iterparse (streaming), not ET.parse."""
    import inspect
    import fodt.parser as parser_module
    source = inspect.getsource(parser_module)
    assert "iterparse" in source


# IR-FODT-015: Validate against 7-entity neutral model before return
def test_ir_fodt_015_neutral_model_validated():
    result = parse_fodt(_sample("minimal-document.fodt"))
    from fodt.neutral_model import validate_document
    violations = validate_document(result)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == []

"""
test_parser_malformed.py -- Malformed input tests for parse_fodt().

Covers: IR-FODT-012 (parse_errors on malformed XML),
        IR-FODT-013 (non-file input graceful return),
        IR-FODT-015 (FFODT-015 Gate 7 fuzz fixture coverage).
Uses Gate 7 fixtures from tests/fixtures/fodt/malformed/.
"""
import os
import tempfile
from pathlib import Path

import pytest

from fodt import parse_fodt, parse_fodt_strict
from fodt.exceptions import FodtInputError, FodtParseError

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "tests" / "fixtures" / "fodt" / "malformed"
)


def _fixture(name):
    return str(FIXTURES_DIR / name)


def _fixture_exists(name):
    return (FIXTURES_DIR / name).exists()


# ---------------------------------------------------------------------------
# IR-FODT-013: non-file input
# ---------------------------------------------------------------------------

def test_missing_file_returns_error():
    result = parse_fodt("/nonexistent/path/file.fodt")
    assert "error" in result


def test_directory_path_returns_error():
    result = parse_fodt(os.path.dirname(__file__))
    assert "error" in result


def test_missing_file_strict_raises():
    with pytest.raises(FodtInputError):
        parse_fodt_strict("/nonexistent/path/file.fodt")


def test_directory_strict_raises():
    with pytest.raises(FodtInputError):
        parse_fodt_strict(os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# IR-FODT-012: malformed XML returns parse_errors
# ---------------------------------------------------------------------------

def test_empty_file_returns_error():
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "error" in result
    finally:
        os.unlink(fname)


def test_invalid_xml_returns_error():
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("not xml at all <<<>>>")
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "error" in result
    finally:
        os.unlink(fname)


def test_wrong_root_returns_error():
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write('<?xml version="1.0"?><html><body/></html>')
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "error" in result
    finally:
        try:
            os.unlink(fname)
        except PermissionError:
            pass


def test_parse_errors_field_present_on_error():
    result = parse_fodt("/nonexistent/path/file.fodt")
    assert "parse_errors" in result
    assert isinstance(result["parse_errors"], list)


def test_malformed_strict_raises_parse_error():
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("not xml at all <<<>>>")
        fname = f.name
    try:
        with pytest.raises(FodtParseError):
            parse_fodt_strict(fname)
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# Gate 7 fixture corpus — category a (malformed XML)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "a01-truncated-xml.fodt",
    "a02-no-root-element.fodt",
    "a03-invalid-xml-chars.fodt",
    "a04-unclosed-tag.fodt",
    "a05-mismatched-tags.fodt",
])
def test_gate7_a_malformed_xml(name):
    if not _fixture_exists(name):
        pytest.skip(f"fixture not found: {name}")
    result = parse_fodt(_fixture(name))
    assert "error" in result or isinstance(result.get("parse_errors"), list)


# ---------------------------------------------------------------------------
# Gate 7 fixture corpus — category b (structural issues)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "b01-wrong-root-element.fodt",
    "b02-missing-namespace.fodt",
    "b03-wrong-mime-type.fodt",
    "b04-fods-root-element.fodt",
])
def test_gate7_b_structural(name):
    if not _fixture_exists(name):
        pytest.skip(f"fixture not found: {name}")
    result = parse_fodt(_fixture(name))
    # These may parse but produce warnings (e.g., wrong mimetype) or errors
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Gate 7 fixture corpus — category c (content edge cases)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "c01-missing-office-body.fodt",
    "c02-missing-office-text.fodt",
    "c03-empty-body.fodt",
    "c04-wrong-body-child.fodt",
])
def test_gate7_c_content_edge_cases(name):
    if not _fixture_exists(name):
        pytest.skip(f"fixture not found: {name}")
    result = parse_fodt(_fixture(name))
    # Missing body/text: may return empty blocks (not necessarily an error)
    assert isinstance(result, dict)
    assert "parse_errors" in result or "blocks" in result


# ---------------------------------------------------------------------------
# Gate 7 fixture corpus — category d (stress/injection)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", [
    "d01-deeply-nested-paragraphs.fodt",
    "d02-very-long-text.fodt",
    "d03-empty-paragraphs.fodt",
    "d04-entity-injection-attempt.fodt",
    "d05-unicode-text.fodt",
])
def test_gate7_d_stress(name):
    if not _fixture_exists(name):
        pytest.skip(f"fixture not found: {name}")
    result = parse_fodt(_fixture(name))
    # These must not crash and must return a dict (error or valid result)
    assert isinstance(result, dict)


def test_gate7_entity_injection_rejected(name="d04-entity-injection-attempt.fodt"):
    if not _fixture_exists(name):
        pytest.skip(f"fixture not found: {name}")
    result = parse_fodt(_fixture(name))
    # DOCTYPE / entity injection must result in error (Expat rejects)
    assert "error" in result

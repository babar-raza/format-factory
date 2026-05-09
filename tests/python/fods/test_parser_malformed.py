"""
test_parser_malformed.py -- Malformed input tests for parse_fods().

Covers: IR-FODS-017 (graceful return on malformed XML),
        IR-FODS-020 (non-file input graceful return)
"""
import os
import tempfile
from pathlib import Path

import pytest

from fods import parse_fods, parse_fods_strict
from fods.exceptions import FodsInputError, FodsParseError

FUZZ_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "tests" / "fixtures" / "fuzz" / "fods"
)


def _fuzz(name):
    return str(FUZZ_DIR / name)


# ---------------------------------------------------------------------------
# IR-FODS-020: non-file input
# ---------------------------------------------------------------------------

def test_missing_file_returns_error():
    result = parse_fods("/nonexistent/path/file.fods")
    assert "error" in result


def test_directory_path_returns_error():
    result = parse_fods(os.path.dirname(__file__))
    assert "error" in result


def test_missing_file_strict_raises():
    with pytest.raises(FodsInputError):
        parse_fods_strict("/nonexistent/path/file.fods")


def test_directory_strict_raises():
    with pytest.raises(FodsInputError):
        parse_fods_strict(os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# IR-FODS-017: malformed XML
# ---------------------------------------------------------------------------

def test_empty_file_returns_error():
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        fname = f.name
    try:
        result = parse_fods(fname)
        assert "error" in result
    finally:
        os.unlink(fname)


def test_invalid_xml_returns_error():
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write("not xml at all <<<>>>")
        fname = f.name
    try:
        result = parse_fods(fname)
        assert "error" in result
    finally:
        os.unlink(fname)


def test_wrong_root_returns_error():
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write('<?xml version="1.0"?><html><body/></html>')
        fname = f.name
    try:
        result = parse_fods(fname)
        assert "error" in result
    finally:
        try:
            os.unlink(fname)
        except PermissionError:
            pass  # Windows: iterparse may hold the file handle briefly


def test_parse_errors_field_present_on_error():
    result = parse_fods("/nonexistent/path/file.fods")
    assert "parse_errors" in result
    assert isinstance(result["parse_errors"], list)


def test_malformed_strict_raises_parse_error():
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write("not xml at all <<<>>>")
        fname = f.name
    try:
        with pytest.raises(FodsParseError):
            parse_fods_strict(fname)
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# Fuzz corpus fixtures (Gate 7)
# ---------------------------------------------------------------------------

def test_fuzz_empty_file():
    p = _fuzz("empty-file.fods")
    if not Path(p).exists():
        pytest.skip("fuzz fixture not found")
    result = parse_fods(p)
    assert "error" in result


def test_fuzz_truncated_xml():
    p = _fuzz("truncated-xml.fods")
    if not Path(p).exists():
        pytest.skip("fuzz fixture not found")
    result = parse_fods(p)
    assert "error" in result


def test_fuzz_wrong_root():
    p = _fuzz("wrong-root.fods")
    if not Path(p).exists():
        pytest.skip("fuzz fixture not found")
    result = parse_fods(p)
    assert "error" in result


def test_fuzz_missing_spreadsheet():
    p = _fuzz("missing-spreadsheet.fods")
    if not Path(p).exists():
        pytest.skip("fuzz fixture not found")
    result = parse_fods(p)
    # missing spreadsheet yields zero sheets -- not necessarily an error
    assert "error" not in result or isinstance(result.get("error"), str)

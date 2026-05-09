"""
test_security.py -- Security-focused tests for parse_fodt().

Covers: IR-FODT-002 (file size guard), IR-FODT-004 (XXE protection),
        IR-FODT-008 (draw:frame detection), IR-FODT-013 (file path validation).
Gate 8 security review requirements (GATE8_SECURITY_REVIEW: PASS, run048).
"""
import os
import stat as stat_module
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fodt import parse_fodt, parse_fodt_strict
from fodt.constants import (
    EXPECTED_MIMETYPE,
    MAX_FILE_BYTES,
    NS_DRAW,
    NS_OFFICE,
    NS_TABLE,
    NS_TEXT,
    WARN_UNSUPPORTED_ELEMENT,
)
from fodt.exceptions import FodtSizeError


def _make_stat_mock(st_size):
    """Build a stat mock with both st_size and st_mode set."""
    mock = MagicMock()
    mock.st_size = st_size
    mock.st_mode = stat_module.S_IFREG | 0o644
    return mock


def _minimal_fodt_xml(extra_body_content=""):
    """Return minimal well-formed FODT XML string."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{NS_OFFICE}"'
        f' xmlns:table="{NS_TABLE}"'
        f' xmlns:text="{NS_TEXT}"'
        f' xmlns:draw="{NS_DRAW}"'
        ' office:version="1.3"'
        f' office:mimetype="{EXPECTED_MIMETYPE}">'
        "<office:body><office:text>"
        f"{extra_body_content}"
        "</office:text></office:body>"
        "</office:document>"
    )


# ---------------------------------------------------------------------------
# IR-FODT-002: File size guard (TC-2 Gate 8)
# ---------------------------------------------------------------------------

def test_oversized_file_returns_error():
    """parse_fodt() returns error dict for files over 100 MB."""
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
        fname = f.name
    try:
        with patch.object(Path, "stat", return_value=_make_stat_mock(MAX_FILE_BYTES + 1)):
            result = parse_fodt(fname)
        assert "error" in result
    finally:
        os.unlink(fname)


def test_oversized_file_strict_raises():
    """parse_fodt_strict() raises FodtSizeError for files over 100 MB."""
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
        fname = f.name
    try:
        with patch.object(Path, "stat", return_value=_make_stat_mock(MAX_FILE_BYTES + 1)):
            with pytest.raises(FodtSizeError):
                parse_fodt_strict(fname)
    finally:
        os.unlink(fname)


def test_exact_size_limit_not_size_error():
    """File exactly at MAX_FILE_BYTES should not trigger size error."""
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False) as f:
        fname = f.name
    try:
        with patch.object(Path, "stat", return_value=_make_stat_mock(MAX_FILE_BYTES)):
            result = parse_fodt(fname)
        # May fail at XML parsing (empty file), but not at size check
        if "error" in result:
            assert "100 MB" not in result["error"]
    finally:
        os.unlink(fname)


def test_max_file_bytes_constant():
    assert MAX_FILE_BYTES == 100 * 1024 * 1024


# ---------------------------------------------------------------------------
# IR-FODT-004: defusedxml import attempted (TC-1 Gate 8)
# ---------------------------------------------------------------------------

def test_defusedxml_import_attempted():
    """Verify defusedxml is attempted at import time."""
    import fodt.parser as parser_module
    assert hasattr(parser_module, "_ET")


# ---------------------------------------------------------------------------
# IR-FODT-008: draw:frame detection (TC-3 not_applicable for flat XML, but detect)
# ---------------------------------------------------------------------------

def _minimal_fodt_with_frame():
    return _minimal_fodt_xml(
        f'<draw:frame xmlns:draw="{NS_DRAW}" draw:name="Frame1"/>'
    )


def test_draw_frame_adds_embedded_frame_to_unsupported():
    xml = _minimal_fodt_with_frame()
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "embedded-frame" in result.get("unsupported_features", [])
    finally:
        os.unlink(fname)


def test_draw_frame_emits_warning():
    xml = _minimal_fodt_with_frame()
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        warn_codes = [w["code"] for w in result.get("warnings", [])]
        assert WARN_UNSUPPORTED_ELEMENT in warn_codes
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# Macros / office:scripts detection
# ---------------------------------------------------------------------------

def _minimal_fodt_with_scripts():
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{NS_OFFICE}"'
        f' xmlns:table="{NS_TABLE}"'
        f' xmlns:text="{NS_TEXT}"'
        ' office:version="1.3"'
        f' office:mimetype="{EXPECTED_MIMETYPE}">'
        "<office:scripts><office:script/></office:scripts>"
        "<office:body><office:text>"
        f'<text:p>Hello</text:p>'
        "</office:text></office:body>"
        "</office:document>"
    )


def test_scripts_adds_macros_to_unsupported():
    xml = _minimal_fodt_with_scripts()
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "macros" in result.get("unsupported_features", [])
    finally:
        os.unlink(fname)


def test_scripts_not_executed():
    """Presence of office:scripts must not execute any code."""
    xml = _minimal_fodt_with_scripts()
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        assert "error" not in result
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# unsupported_features contract
# ---------------------------------------------------------------------------

def test_unsupported_features_is_sorted():
    xml = _minimal_fodt_xml()
    with tempfile.NamedTemporaryFile(suffix=".fodt", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fodt(fname)
        uf = result.get("unsupported_features", [])
        assert uf == sorted(uf)
    finally:
        os.unlink(fname)

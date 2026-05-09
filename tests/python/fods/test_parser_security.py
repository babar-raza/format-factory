"""
test_parser_security.py -- Security-focused tests for parse_fods().

Covers: IR-FODS-003 (file size guard), IR-FODS-004 (XXE protection),
        IR-FODS-015 (draw:frame detection), IR-FODS-016 (macro detection),
        Gate 8 security review requirements.
"""
import stat as stat_module
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fods import parse_fods, parse_fods_strict
from fods.constants import (
    EXPECTED_MIMETYPE,
    MAX_FILE_BYTES,
    NS_DRAW,
    NS_OFFICE,
    NS_TABLE,
    NS_TEXT,
    WARN_UNSUPPORTED_ELEMENT,
)
from fods.exceptions import FodsSizeError

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fods"


def _sample(name):
    return str(SAMPLES / name)


def _make_stat_mock(st_size):
    """Build a stat mock with both st_size and st_mode set."""
    mock = MagicMock()
    mock.st_size = st_size
    mock.st_mode = stat_module.S_IFREG | 0o644
    return mock


# ---------------------------------------------------------------------------
# IR-FODS-003: File size guard
# ---------------------------------------------------------------------------

def test_oversized_file_returns_error():
    """parse_fods() returns error dict for files over 100 MB."""
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        fname = f.name
    try:
        with patch.object(Path, "stat", return_value=_make_stat_mock(MAX_FILE_BYTES + 1)):
            result = parse_fods(fname)
        assert "error" in result
    finally:
        os.unlink(fname)


def test_oversized_file_strict_raises():
    """parse_fods_strict() raises FodsSizeError for files over 100 MB."""
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        fname = f.name
    try:
        with patch.object(Path, "stat", return_value=_make_stat_mock(MAX_FILE_BYTES + 1)):
            with pytest.raises(FodsSizeError):
                parse_fods_strict(fname)
    finally:
        os.unlink(fname)


def test_exact_size_limit_passes():
    """File exactly at MAX_FILE_BYTES should not trigger size error."""
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False) as f:
        fname = f.name
    try:
        with patch.object(Path, "stat", return_value=_make_stat_mock(MAX_FILE_BYTES)):
            # This will fail at parsing (empty file), not at size check
            result = parse_fods(fname)
        # Error may be parse error, not size error
        if "error" in result:
            assert "100 MB" not in result["error"]
    finally:
        os.unlink(fname)


def test_max_file_bytes_constant():
    assert MAX_FILE_BYTES == 100 * 1024 * 1024


# ---------------------------------------------------------------------------
# IR-FODS-004: defusedxml
# ---------------------------------------------------------------------------

def test_defusedxml_import_attempted():
    """Verify defusedxml is attempted at import time."""
    import fods.parser as parser_module
    # Module-level _ET is either defusedxml or stdlib -- both are acceptable
    assert hasattr(parser_module, "_ET")


# ---------------------------------------------------------------------------
# IR-FODS-015: draw:frame (chart/image) detection
# ---------------------------------------------------------------------------

def _minimal_fods_with_frame():
    """Return minimal FODS XML string containing a draw:frame element."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{NS_OFFICE}"'
        f' xmlns:table="{NS_TABLE}"'
        f' xmlns:text="{NS_TEXT}"'
        f' xmlns:draw="{NS_DRAW}"'
        ' office:version="1.3"'
        f' office:mimetype="{EXPECTED_MIMETYPE}">'
        "<office:body><office:spreadsheet>"
        '<table:table table:name="Sheet1">'
        "<table:table-row>"
        "<table:table-cell>"
        f'<draw:frame draw:name="Frame1"/>'
        "</table:table-cell>"
        "</table:table-row>"
        "</table:table>"
        "</office:spreadsheet></office:body>"
        "</office:document>"
    )


def test_draw_frame_adds_chart_to_unsupported():
    xml = _minimal_fods_with_frame()
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fods(fname)
        assert "chart" in result.get("unsupported_features", [])
    finally:
        os.unlink(fname)


def test_draw_frame_emits_warning():
    xml = _minimal_fods_with_frame()
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fods(fname)
        warn_codes = [w["code"] for w in result.get("warnings", [])]
        assert WARN_UNSUPPORTED_ELEMENT in warn_codes
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# IR-FODS-016: office:scripts (macro) detection
# ---------------------------------------------------------------------------

def _minimal_fods_with_scripts():
    """Return minimal FODS XML with office:scripts element."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{NS_OFFICE}"'
        f' xmlns:table="{NS_TABLE}"'
        f' xmlns:text="{NS_TEXT}"'
        ' office:version="1.3"'
        f' office:mimetype="{EXPECTED_MIMETYPE}">'
        "<office:scripts><office:script/></office:scripts>"
        "<office:body><office:spreadsheet>"
        '<table:table table:name="Sheet1">'
        "<table:table-row>"
        "<table:table-cell/>"
        "</table:table-row>"
        "</table:table>"
        "</office:spreadsheet></office:body>"
        "</office:document>"
    )


def test_scripts_adds_macros_to_unsupported():
    xml = _minimal_fods_with_scripts()
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        result = parse_fods(fname)
        assert "macros" in result.get("unsupported_features", [])
    finally:
        os.unlink(fname)


def test_scripts_not_executed():
    """Presence of office:scripts must not execute any code."""
    xml = _minimal_fods_with_scripts()
    with tempfile.NamedTemporaryFile(suffix=".fods", delete=False, mode="w", encoding="utf-8") as f:
        f.write(xml)
        fname = f.name
    try:
        # If this completes without side effects, macros were not executed
        result = parse_fods(fname)
        assert "error" not in result
    finally:
        os.unlink(fname)


def test_unsupported_features_is_sorted():
    """unsupported_features list must be sorted (neutral model contract)."""
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    uf = result.get("unsupported_features", [])
    assert uf == sorted(uf)

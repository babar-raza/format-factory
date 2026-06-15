"""
test_tc_5369be63_fodg_probe.py -- Probe FODG test coverage for TC-5369BE63.

Taskcard: TC-5369BE63
Gap: GAP-FODG-FOSS-PROBE_FODG-001 (missing_test_coverage)
Sprint: product-probe-gap-closure-20260614-001
Required test types: file_based_input, string_input, empty_input,
                     return_type_check, error_handling
Minimum tests: 10
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import probe_fodg

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"
_SHAPES = _SAMPLES / "shapes-basic.fodg"
_EMPTY_PAGE = _SAMPLES / "empty-page.fodg"


# ---------------------------------------------------------------------------
# file_based_input (Path objects)
# ---------------------------------------------------------------------------

class TestFodgProbeFileBasedInput:
    def test_probe_minimal_drawing_true(self):
        result = probe_fodg(_MINIMAL)
        assert result is True

    def test_probe_shapes_basic_true(self):
        result = probe_fodg(_SHAPES)
        assert result is True

    def test_probe_empty_page_true(self):
        result = probe_fodg(_EMPTY_PAGE)
        assert result is True

    def test_probe_all_samples_true(self):
        for f in _SAMPLES.glob("*.fodg"):
            assert probe_fodg(f) is True, f"Expected True for {f.name}"


# ---------------------------------------------------------------------------
# string_input (string paths and raw XML strings)
# ---------------------------------------------------------------------------

class TestFodgProbeStringInput:
    def test_probe_string_path_returns_true(self):
        result = probe_fodg(str(_MINIMAL))
        assert result is True

    def test_probe_xml_string_with_mime_returns_true(self):
        xml = _MINIMAL.read_text(encoding="utf-8", errors="replace")
        # The XML string itself should contain the FODG MIME marker
        result = probe_fodg(xml)
        assert result is True

    def test_probe_non_fodg_xml_string_returns_false(self):
        result = probe_fodg("<root><child/></root>")
        assert result is False


# ---------------------------------------------------------------------------
# empty_input (empty bytes/strings, nonexistent paths)
# ---------------------------------------------------------------------------

class TestFodgProbeEmptyInput:
    def test_probe_empty_bytes_returns_false(self):
        result = probe_fodg(b"")
        assert result is False

    def test_probe_empty_string_returns_false(self):
        result = probe_fodg("")
        assert result is False

    def test_probe_nonexistent_path_returns_false(self, tmp_path):
        result = probe_fodg(tmp_path / "ghost.fodg")
        assert result is False


# ---------------------------------------------------------------------------
# return_type_check
# ---------------------------------------------------------------------------

class TestFodgProbeReturnType:
    def test_return_is_bool_for_valid_file(self):
        result = probe_fodg(_MINIMAL)
        assert isinstance(result, bool)

    def test_return_is_bool_for_invalid_bytes(self):
        result = probe_fodg(b"not a fodg")
        assert isinstance(result, bool)

    def test_return_is_bool_for_missing_file(self, tmp_path):
        result = probe_fodg(tmp_path / "no-file.fodg")
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# error_handling
# ---------------------------------------------------------------------------

class TestFodgProbeErrorHandling:
    def test_probe_never_raises_on_random_bytes(self):
        result = probe_fodg(b"\x00\xff\xfe\xfdrandom garbage bytes")
        assert isinstance(result, bool)

    def test_probe_never_raises_on_nonexistent_path(self, tmp_path):
        result = probe_fodg(tmp_path / "does-not-exist.fodg")
        assert result is False

    def test_probe_returns_false_for_non_fodg_content(self, tmp_path):
        f = tmp_path / "fake.fodg"
        f.write_bytes(b"PK\x03\x04 not a fodg archive")
        result = probe_fodg(f)
        assert result is False

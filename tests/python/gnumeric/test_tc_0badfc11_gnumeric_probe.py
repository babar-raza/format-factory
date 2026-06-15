"""
test_tc_0badfc11_gnumeric_probe.py -- Probe Gnumeric test coverage for TC-0BADFC11.

Taskcard: TC-0BADFC11
Gap: GAP-Gnumeric-FOSS-PROBE_GNUMER-001 (missing_test_coverage)
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

from src.python.gnumeric.gnumeric_codec import probe_gnumeric

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = _SAMPLES / "minimal-spreadsheet.gnumeric"
_MULTI = _SAMPLES / "multi-cell-basic.gnumeric"
_EMPTY_SHEET = _SAMPLES / "empty-sheet.gnumeric"


# ---------------------------------------------------------------------------
# file_based_input (Path objects)
# ---------------------------------------------------------------------------

class TestGnumericProbeFileBasedInput:
    def test_probe_minimal_spreadsheet_true(self):
        result = probe_gnumeric(_MINIMAL)
        assert result is True

    def test_probe_multi_cell_basic_true(self):
        result = probe_gnumeric(_MULTI)
        assert result is True

    def test_probe_empty_sheet_true(self):
        result = probe_gnumeric(_EMPTY_SHEET)
        assert result is True

    def test_probe_all_samples_true(self):
        for f in _SAMPLES.glob("*.gnumeric"):
            assert probe_gnumeric(f) is True, f"Expected True for {f.name}"


# ---------------------------------------------------------------------------
# string_input (string paths and raw bytes)
# ---------------------------------------------------------------------------

class TestGnumericProbeStringInput:
    def test_probe_string_path_returns_true(self):
        result = probe_gnumeric(str(_MINIMAL))
        assert result is True

    def test_probe_valid_bytes_returns_true(self):
        raw = _MINIMAL.read_bytes()
        result = probe_gnumeric(raw)
        assert result is True

    def test_probe_multi_cell_bytes_returns_true(self):
        raw = _MULTI.read_bytes()
        result = probe_gnumeric(raw)
        assert result is True


# ---------------------------------------------------------------------------
# empty_input
# ---------------------------------------------------------------------------

class TestGnumericProbeEmptyInput:
    def test_probe_empty_bytes_returns_false(self):
        result = probe_gnumeric(b"")
        assert result is False

    def test_probe_nonexistent_path_returns_false(self, tmp_path):
        result = probe_gnumeric(tmp_path / "ghost.gnumeric")
        assert result is False

    def test_probe_short_bytes_returns_false(self):
        # Less than 2 bytes: can't check gzip magic
        result = probe_gnumeric(b"\x1f")
        assert result is False


# ---------------------------------------------------------------------------
# return_type_check
# ---------------------------------------------------------------------------

class TestGnumericProbeReturnType:
    def test_return_is_bool_for_valid_file(self):
        result = probe_gnumeric(_MINIMAL)
        assert isinstance(result, bool)

    def test_return_is_bool_for_invalid_bytes(self):
        result = probe_gnumeric(b"not a gnumeric file")
        assert isinstance(result, bool)

    def test_return_is_bool_for_missing_file(self, tmp_path):
        result = probe_gnumeric(tmp_path / "no-file.gnumeric")
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# error_handling
# ---------------------------------------------------------------------------

class TestGnumericProbeErrorHandling:
    def test_probe_never_raises_on_random_bytes(self):
        result = probe_gnumeric(b"\x1f\x8b random garbage not real gzip")
        assert isinstance(result, bool)

    def test_probe_never_raises_on_nonexistent_path(self, tmp_path):
        result = probe_gnumeric(tmp_path / "does-not-exist.gnumeric")
        assert result is False

    def test_probe_returns_false_for_non_gnumeric_gzip(self, tmp_path):
        import gzip
        # Valid gzip but not Gnumeric XML
        f = tmp_path / "fake.gnumeric"
        f.write_bytes(gzip.compress(b"<html><body>not gnumeric</body></html>"))
        result = probe_gnumeric(f)
        assert result is False

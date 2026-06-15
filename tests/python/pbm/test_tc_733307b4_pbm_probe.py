"""
test_tc_733307b4_pbm_probe.py -- Probe PBM test coverage for TC-733307B4.

Taskcard: TC-733307B4
Gap: GAP-PBM-FOSS-PROBE_PBM-001 (missing_test_coverage)
Sprint: pbm-pgm-probe-gap-closure-20260614-001
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

from src.python.pbm.pbm_parser import probe_pbm

_VALID = _REPO / "samples" / "by-format" / "pbm" / "valid"
_INVALID = _REPO / "samples" / "by-format" / "pbm" / "invalid"
_1X1 = _VALID / "1x1-black.pbm"
_2X2 = _VALID / "2x2-checker.pbm"
_3X2 = _VALID / "3x2-pattern.pbm"
_WRONG_MAGIC = _INVALID / "wrong-magic.pbm"


# ---------------------------------------------------------------------------
# file_based_input (Path objects)
# ---------------------------------------------------------------------------

class TestPbmProbeFileBasedInput:
    def test_probe_1x1_black_valid_header(self):
        result = probe_pbm(_1X1)
        assert result["valid_header"] is True

    def test_probe_1x1_width_and_height(self):
        result = probe_pbm(_1X1)
        assert result["width"] == 1
        assert result["height"] == 1

    def test_probe_2x2_checker_valid(self):
        result = probe_pbm(_2X2)
        assert result["valid_header"] is True
        assert result["width"] == 2
        assert result["height"] == 2

    def test_probe_3x2_dimensions(self):
        result = probe_pbm(_3X2)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_probe_magic_is_p1(self):
        result = probe_pbm(_1X1)
        assert result["magic"] == "P1"

    def test_probe_invalid_magic_valid_header_false(self):
        result = probe_pbm(_WRONG_MAGIC)
        assert result["valid_header"] is False


# ---------------------------------------------------------------------------
# string_input (string file paths)
# ---------------------------------------------------------------------------

class TestPbmProbeStringInput:
    def test_probe_accepts_string_path(self):
        result = probe_pbm(str(_1X1))
        assert isinstance(result, dict)

    def test_probe_string_path_exists_true(self):
        result = probe_pbm(str(_2X2))
        assert result["exists"] is True

    def test_probe_string_path_valid_header(self):
        result = probe_pbm(str(_3X2))
        assert result["valid_header"] is True


# ---------------------------------------------------------------------------
# empty_input (nonexistent paths and empty files)
# ---------------------------------------------------------------------------

class TestPbmProbeEmptyInput:
    def test_probe_nonexistent_returns_dict(self, tmp_path):
        result = probe_pbm(tmp_path / "ghost.pbm")
        assert isinstance(result, dict)

    def test_probe_nonexistent_exists_false(self, tmp_path):
        result = probe_pbm(tmp_path / "ghost.pbm")
        assert result["exists"] is False

    def test_probe_empty_file_has_no_valid_header(self, tmp_path):
        f = tmp_path / "empty.pbm"
        f.write_bytes(b"")
        result = probe_pbm(f)
        assert result["exists"] is True
        # Empty file produces no valid header (no tokens)
        assert result.get("valid_header") is False or "valid_header" not in result


# ---------------------------------------------------------------------------
# return_type_check
# ---------------------------------------------------------------------------

class TestPbmProbeReturnType:
    def test_return_is_dict_for_valid_file(self):
        result = probe_pbm(_1X1)
        assert isinstance(result, dict)

    def test_return_has_exists_key(self):
        result = probe_pbm(_1X1)
        assert "exists" in result

    def test_return_has_path_key(self):
        result = probe_pbm(_1X1)
        assert "path" in result

    def test_return_has_valid_header_key_for_existing_file(self):
        result = probe_pbm(_1X1)
        assert "valid_header" in result

    def test_return_is_dict_for_missing_file(self, tmp_path):
        result = probe_pbm(tmp_path / "no-file.pbm")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# error_handling
# ---------------------------------------------------------------------------

class TestPbmProbeErrorHandling:
    def test_probe_never_raises_on_nonexistent_path(self, tmp_path):
        result = probe_pbm(tmp_path / "does-not-exist.pbm")
        assert isinstance(result, dict)

    def test_probe_wrong_magic_returns_dict_with_error(self):
        result = probe_pbm(_WRONG_MAGIC)
        assert isinstance(result, dict)
        assert "error" in result or result.get("valid_header") is False

    def test_probe_binary_garbage_does_not_raise(self, tmp_path):
        f = tmp_path / "junk.pbm"
        f.write_bytes(bytes(range(256)))
        result = probe_pbm(f)
        assert isinstance(result, dict)

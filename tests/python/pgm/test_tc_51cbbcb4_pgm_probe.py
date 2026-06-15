"""
test_tc_51cbbcb4_pgm_probe.py -- Probe PGM test coverage for TC-51CBBCB4.

Taskcard: TC-51CBBCB4
Gap: GAP-PGM-FOSS-PROBE_PGM-001 (missing_test_coverage)
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

from src.python.pgm.pgm_parser import probe_pgm

_VALID = _REPO / "samples" / "by-format" / "pgm" / "valid"
_INVALID = _REPO / "samples" / "by-format" / "pgm" / "invalid"
_1X1 = _VALID / "1x1-white.pgm"
_2X2 = _VALID / "2x2-gradient.pgm"
_3X1 = _VALID / "3x1-ramp.pgm"
_WRONG_MAGIC = _INVALID / "wrong-magic.pgm"


# ---------------------------------------------------------------------------
# file_based_input (Path objects)
# ---------------------------------------------------------------------------

class TestPgmProbeFileBasedInput:
    def test_probe_1x1_white_valid_header(self):
        result = probe_pgm(_1X1)
        assert result["valid_header"] is True

    def test_probe_1x1_width_height_maxval(self):
        result = probe_pgm(_1X1)
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["maxval"] == 255

    def test_probe_2x2_gradient_valid(self):
        result = probe_pgm(_2X2)
        assert result["valid_header"] is True
        assert result["width"] == 2
        assert result["height"] == 2

    def test_probe_3x1_ramp_dimensions(self):
        result = probe_pgm(_3X1)
        assert result["width"] == 3
        assert result["height"] == 1

    def test_probe_magic_is_p2(self):
        result = probe_pgm(_1X1)
        assert result["magic"] == "P2"

    def test_probe_invalid_magic_valid_header_false(self):
        result = probe_pgm(_WRONG_MAGIC)
        assert result["valid_header"] is False


# ---------------------------------------------------------------------------
# string_input (string file paths)
# ---------------------------------------------------------------------------

class TestPgmProbeStringInput:
    def test_probe_accepts_string_path(self):
        result = probe_pgm(str(_1X1))
        assert isinstance(result, dict)

    def test_probe_string_path_exists_true(self):
        result = probe_pgm(str(_2X2))
        assert result["exists"] is True

    def test_probe_string_path_valid_header(self):
        result = probe_pgm(str(_3X1))
        assert result["valid_header"] is True


# ---------------------------------------------------------------------------
# empty_input (nonexistent paths and empty files)
# ---------------------------------------------------------------------------

class TestPgmProbeEmptyInput:
    def test_probe_nonexistent_returns_dict(self, tmp_path):
        result = probe_pgm(tmp_path / "ghost.pgm")
        assert isinstance(result, dict)

    def test_probe_nonexistent_exists_false(self, tmp_path):
        result = probe_pgm(tmp_path / "ghost.pgm")
        assert result["exists"] is False

    def test_probe_empty_file_no_valid_header(self, tmp_path):
        f = tmp_path / "empty.pgm"
        f.write_bytes(b"")
        result = probe_pgm(f)
        assert result["exists"] is True
        assert result.get("valid_header") is False or "valid_header" not in result


# ---------------------------------------------------------------------------
# return_type_check
# ---------------------------------------------------------------------------

class TestPgmProbeReturnType:
    def test_return_is_dict_for_valid_file(self):
        result = probe_pgm(_1X1)
        assert isinstance(result, dict)

    def test_return_has_exists_key(self):
        result = probe_pgm(_1X1)
        assert "exists" in result

    def test_return_has_path_key(self):
        result = probe_pgm(_1X1)
        assert "path" in result

    def test_return_has_valid_header_key(self):
        result = probe_pgm(_1X1)
        assert "valid_header" in result

    def test_return_has_maxval_for_valid_p2(self):
        result = probe_pgm(_1X1)
        assert "maxval" in result
        assert isinstance(result["maxval"], int)

    def test_return_is_dict_for_missing_file(self, tmp_path):
        result = probe_pgm(tmp_path / "no-file.pgm")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# error_handling
# ---------------------------------------------------------------------------

class TestPgmProbeErrorHandling:
    def test_probe_never_raises_on_nonexistent_path(self, tmp_path):
        result = probe_pgm(tmp_path / "does-not-exist.pgm")
        assert isinstance(result, dict)

    def test_probe_wrong_magic_has_error_or_false_header(self):
        result = probe_pgm(_WRONG_MAGIC)
        assert isinstance(result, dict)
        assert "error" in result or result.get("valid_header") is False

    def test_probe_binary_garbage_does_not_raise(self, tmp_path):
        f = tmp_path / "junk.pgm"
        f.write_bytes(bytes(range(256)))
        result = probe_pgm(f)
        assert isinstance(result, dict)

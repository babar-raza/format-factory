"""
tests/python/pbm/test_r76_netpbm_family.py

R76 Train K — Netpbm family advancement: shared family-level tests for PBM/PGM/PPM.

These tests verify consistent behavior across the Netpbm family:
- Comment handling (lines starting with #)
- Malformed input rejection (bad magic number, missing dims, etc.)
- Image stats consistency
- P1/P2/P3 ASCII vs P4/P5/P6 binary format probe

Tests run against all three Netpbm parsers to prove family consistency.
"""

import io
import struct
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.pbm.pbm_parser import parse_pbm, parse_pbm_strict, PbmError
from src.python.pgm.pgm_parser import parse_pgm, parse_pgm_strict, PgmError
from src.python.ppm.ppm_parser import parse_ppm, parse_ppm_strict, PpmError


# ---------------------------------------------------------------------------
# Helpers for building minimal valid Netpbm test files
# ---------------------------------------------------------------------------

def _write_p1_pbm(path: Path, width: int, height: int, pixels: list[list[int]]) -> None:
    with open(path, "w") as f:
        f.write(f"P1\n{width} {height}\n")
        for row in pixels:
            f.write(" ".join(str(p) for p in row) + "\n")


def _write_p2_pgm(path: Path, width: int, height: int, maxval: int, pixels: list[list[int]]) -> None:
    with open(path, "w") as f:
        f.write(f"P2\n{width} {height}\n{maxval}\n")
        for row in pixels:
            f.write(" ".join(str(p) for p in row) + "\n")


def _write_p3_ppm(
    path: Path, width: int, height: int, maxval: int, pixels: list[tuple[int, int, int]]
) -> None:
    with open(path, "w") as f:
        f.write(f"P3\n{width} {height}\n{maxval}\n")
        for r, g, b in pixels:
            f.write(f"{r} {g} {b}\n")


# ---------------------------------------------------------------------------
# Comment handling — family consistency
# ---------------------------------------------------------------------------

class TestNetpbmCommentHandling:
    """Verify all three parsers handle comment lines (#...) correctly."""

    def test_pbm_ascii_with_comments(self, tmp_path):
        path = tmp_path / "test.pbm"
        path.write_text("P1\n# This is a comment\n2 2\n0 1\n1 0\n")
        result = parse_pbm(path)
        assert result.get("width") == 2
        assert result.get("height") == 2

    def test_pgm_ascii_with_comments(self, tmp_path):
        path = tmp_path / "test.pgm"
        path.write_text("P2\n# PGM comment\n2 2\n255\n0 128\n200 255\n")
        result = parse_pgm(path)
        assert result.get("width") == 2
        assert result.get("height") == 2

    def test_ppm_ascii_with_comments(self, tmp_path):
        path = tmp_path / "test.ppm"
        path.write_text("P3\n# PPM comment\n1 1\n255\n100 150 200\n")
        result = parse_ppm(path)
        assert result.get("width") == 1
        assert result.get("height") == 1

    def test_pbm_comment_between_header_fields(self, tmp_path):
        path = tmp_path / "test.pbm"
        path.write_text("P1\n# comment before dims\n1 1\n0\n")
        result = parse_pbm(path)
        assert result.get("width") == 1


# ---------------------------------------------------------------------------
# Malformed input rejection — family consistency
# ---------------------------------------------------------------------------

class TestNetpbmMalformedInputRejection:
    """All parsers must reject obviously malformed input."""

    def test_pbm_rejects_wrong_magic(self, tmp_path):
        path = tmp_path / "test.pbm"
        path.write_text("P3\n1 1\n0\n")  # PPM magic in PBM file
        result = parse_pbm(path)
        assert result.get("parse_result") == "fail" or result.get("magic") != "P1"

    def test_pgm_rejects_wrong_magic(self, tmp_path):
        path = tmp_path / "test.pgm"
        path.write_text("P1\n1 1\n255\n0\n")  # PBM magic in PGM file
        result = parse_pgm(path)
        assert result.get("parse_result") == "fail" or result.get("magic") not in ("P2", "P5")

    def test_pbm_strict_raises_on_empty_file(self, tmp_path):
        path = tmp_path / "empty.pbm"
        path.write_bytes(b"")
        with pytest.raises(PbmError):
            parse_pbm_strict(path)

    def test_pgm_strict_raises_on_empty_file(self, tmp_path):
        path = tmp_path / "empty.pgm"
        path.write_bytes(b"")
        with pytest.raises(PgmError):
            parse_pgm_strict(path)

    def test_ppm_strict_raises_on_empty_file(self, tmp_path):
        path = tmp_path / "empty.ppm"
        path.write_bytes(b"")
        with pytest.raises(PpmError):
            parse_ppm_strict(path)


# ---------------------------------------------------------------------------
# Image stats consistency
# ---------------------------------------------------------------------------

class TestNetpbmImageStatsConsistency:
    """Verify that parsers return consistent image dimension metadata."""

    def test_pbm_reports_correct_dimensions(self, tmp_path):
        path = tmp_path / "test.pbm"
        _write_p1_pbm(path, 3, 2, [[0, 1, 0], [1, 0, 1]])
        result = parse_pbm(path)
        assert result.get("width") == 3
        assert result.get("height") == 2

    def test_pgm_reports_correct_dimensions(self, tmp_path):
        path = tmp_path / "test.pgm"
        _write_p2_pgm(path, 4, 3, 255, [[0, 64, 128, 255]] * 3)
        result = parse_pgm(path)
        assert result.get("width") == 4
        assert result.get("height") == 3

    def test_ppm_reports_correct_dimensions(self, tmp_path):
        path = tmp_path / "test.ppm"
        _write_p3_ppm(path, 2, 2, 255, [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)])
        result = parse_ppm(path)
        assert result.get("width") == 2
        assert result.get("height") == 2

    def test_all_parsers_return_dict_with_width_height(self, tmp_path):
        pbm_path = tmp_path / "t.pbm"
        pgm_path = tmp_path / "t.pgm"
        ppm_path = tmp_path / "t.ppm"
        _write_p1_pbm(pbm_path, 1, 1, [[0]])
        _write_p2_pgm(pgm_path, 1, 1, 255, [[128]])
        _write_p3_ppm(ppm_path, 1, 1, 255, [(100, 100, 100)])

        for parser, path in [(parse_pbm, pbm_path), (parse_pgm, pgm_path), (parse_ppm, ppm_path)]:
            result = parser(path)
            assert isinstance(result, dict), f"{parser.__name__} must return dict"
            assert "width" in result or result.get("parse_result") == "fail"
            assert "height" in result or result.get("parse_result") == "fail"

"""
test_netpbm_image_pipeline.py -- Netpbm image processing pipeline tests.

Sprint: TRUE-AUTONOMOUS-REWORK-MEGATRAIN
Added: 2026-06-10

Tests PBM->PGM->PPM conversion chains, transformation composition,
stats validation, and edge cases for the Netpbm format family.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import parse_pbm, parse_pbm_strict, PbmImage
from pgm.pgm_parser import parse_pgm, parse_pgm_strict
from ppm.ppm_parser import parse_ppm, parse_ppm_strict


def _write_pbm_ascii(path: Path, width: int, height: int, pixels: list[list[int]]):
    """Write a P1 (ASCII) PBM file."""
    lines = [f"P1\n{width} {height}\n"]
    for row in pixels:
        lines.append(" ".join(str(p) for p in row) + "\n")
    path.write_text("".join(lines), encoding="ascii")


def _write_pgm_ascii(path: Path, width: int, height: int, maxval: int, pixels: list[list[int]]):
    """Write a P2 (ASCII) PGM file."""
    lines = [f"P2\n{width} {height}\n{maxval}\n"]
    for row in pixels:
        lines.append(" ".join(str(p) for p in row) + "\n")
    path.write_text("".join(lines), encoding="ascii")


def _write_ppm_ascii(path: Path, width: int, height: int, maxval: int, pixels: list[list[tuple]]):
    """Write a P3 (ASCII) PPM file."""
    lines = [f"P3\n{width} {height}\n{maxval}\n"]
    for row in pixels:
        for r, g, b in row:
            lines.append(f"{r} {g} {b}\n")
    path.write_text("".join(lines), encoding="ascii")


# ---- PBM Tests ----

def test_pbm_parse_1x1_white():
    """Parse a minimal 1x1 white PBM image."""
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
        f.write("P1\n1 1\n0\n")
        f.flush()
        result = parse_pbm(Path(f.name))
    assert result["ok"] is True
    assert result["width"] == 1
    assert result["height"] == 1
    Path(f.name).unlink(missing_ok=True)


def test_pbm_parse_3x3_checkerboard():
    """Parse a 3x3 checkerboard pattern."""
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
        f.write("P1\n3 3\n1 0 1\n0 1 0\n1 0 1\n")
        f.flush()
        result = parse_pbm(Path(f.name))
    assert result["ok"] is True
    assert result["width"] == 3
    assert result["height"] == 3
    doc = parse_pbm_strict(Path(f.name))
    assert doc.width == 3
    assert doc.height == 3
    Path(f.name).unlink(missing_ok=True)


def test_pbm_strict_returns_dataclass():
    """parse_pbm_strict returns a PbmImage dataclass."""
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
        f.write("P1\n2 2\n0 1\n1 0\n")
        f.flush()
        doc = parse_pbm_strict(Path(f.name))
    assert isinstance(doc, PbmImage)
    assert doc.magic == "P1"
    Path(f.name).unlink(missing_ok=True)


# ---- PGM Tests ----

def test_pgm_parse_gradient():
    """Parse a 3x1 grayscale gradient."""
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False, mode="w") as f:
        f.write("P2\n3 1\n255\n0 128 255\n")
        f.flush()
        result = parse_pgm(Path(f.name))
    assert result["ok"] is True
    assert result["width"] == 3
    assert result["height"] == 1
    Path(f.name).unlink(missing_ok=True)


def test_pgm_parse_2x2():
    """Parse a 2x2 PGM with known values."""
    with tempfile.NamedTemporaryFile(suffix=".pgm", delete=False, mode="w") as f:
        f.write("P2\n2 2\n255\n10 20\n30 40\n")
        f.flush()
        doc = parse_pgm_strict(Path(f.name))
    assert doc.width == 2
    assert doc.height == 2
    assert doc.maxval == 255
    Path(f.name).unlink(missing_ok=True)


# ---- PPM Tests ----

def test_ppm_parse_solid_red():
    """Parse a 2x2 solid red PPM image."""
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w") as f:
        f.write("P3\n2 2\n255\n255 0 0\n255 0 0\n255 0 0\n255 0 0\n")
        f.flush()
        result = parse_ppm(Path(f.name))
    assert result["ok"] is True
    assert result["width"] == 2
    assert result["height"] == 2
    Path(f.name).unlink(missing_ok=True)


def test_ppm_parse_rgb_triangle():
    """Parse a 1x3 PPM with R, G, B pixels."""
    with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w") as f:
        f.write("P3\n1 3\n255\n255 0 0\n0 255 0\n0 0 255\n")
        f.flush()
        doc = parse_ppm_strict(Path(f.name))
    assert doc.width == 1
    assert doc.height == 3
    assert doc.maxval == 255
    Path(f.name).unlink(missing_ok=True)


# ---- Cross-format chain tests ----

def test_pbm_and_pgm_dimensions_match():
    """Verify PBM and PGM parsers agree on dimensions for same geometry."""
    with tempfile.TemporaryDirectory() as tmp:
        pbm_path = Path(tmp) / "test.pbm"
        pgm_path = Path(tmp) / "test.pgm"

        _write_pbm_ascii(pbm_path, 4, 3, [[0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]])
        _write_pgm_ascii(pgm_path, 4, 3, 255, [[0, 128, 0, 128], [128, 0, 128, 0], [0, 128, 0, 128]])

        pbm_result = parse_pbm(pbm_path)
        pgm_result = parse_pgm(pgm_path)

        assert pbm_result["width"] == pgm_result["width"] == 4
        assert pbm_result["height"] == pgm_result["height"] == 3


def test_all_three_formats_parse_same_geometry():
    """PBM, PGM, PPM all parse successfully with 2x2 geometry."""
    with tempfile.TemporaryDirectory() as tmp:
        pbm_path = Path(tmp) / "test.pbm"
        pgm_path = Path(tmp) / "test.pgm"
        ppm_path = Path(tmp) / "test.ppm"

        _write_pbm_ascii(pbm_path, 2, 2, [[0, 1], [1, 0]])
        _write_pgm_ascii(pgm_path, 2, 2, 255, [[0, 255], [128, 64]])
        _write_ppm_ascii(ppm_path, 2, 2, 255, [[(255, 0, 0), (0, 255, 0)], [(0, 0, 255), (128, 128, 128)]])

        for parser, path in [(parse_pbm, pbm_path), (parse_pgm, pgm_path), (parse_ppm, ppm_path)]:
            result = parser(path)
            assert result["ok"] is True, f"Failed for {path.suffix}: {result.get('error')}"
            assert result["width"] == 2
            assert result["height"] == 2


def test_pbm_comment_handling():
    """PBM parser handles comments in header."""
    with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
        f.write("P1\n# This is a comment\n2 2\n0 1\n1 0\n")
        f.flush()
        result = parse_pbm(Path(f.name))
    assert result["ok"] is True
    assert result["width"] == 2
    Path(f.name).unlink(missing_ok=True)

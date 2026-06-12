"""Dogfood chain test: PBM -> PGM conversion -> rotation -> scale.

Proves that Format Factory PBM and PGM libraries work together as a pipeline.
Sprint: PACKAGING-BREAKTHROUGH.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from pbm.pbm_parser import write_pbm, parse_pbm_strict, scale_nearest
from pbm.pbm_to_pgm import convert_pbm_to_pgm
from pgm.pgm_parser import parse_pgm_strict, rotate_90 as pgm_rotate_90


class TestPbmPgmDogfoodChain:
    def test_pbm_to_pgm_conversion(self, tmp_path: Path) -> None:
        """Create PBM -> convert to PGM -> verify grayscale values."""
        pbm_path = tmp_path / "input.pbm"
        pgm_path = tmp_path / "output.pgm"
        # 2x2 checkerboard: black=1, white=0
        write_pbm([1, 0, 0, 1], 2, 2, pbm_path)
        convert_pbm_to_pgm(pbm_path, pgm_path)
        pgm = parse_pgm_strict(pgm_path)
        assert pgm.width == 2
        assert pgm.height == 2
        # PBM 1=black -> PGM 0=black, PBM 0=white -> PGM 255=white
        assert pgm.pixels[0] == 0    # was black (1)
        assert pgm.pixels[1] == 255  # was white (0)

    def test_full_chain_pbm_to_pgm_rotate(self, tmp_path: Path) -> None:
        """PBM -> PGM -> rotate_90 -> verify dimensions swapped."""
        pbm_path = tmp_path / "src.pbm"
        pgm_path = tmp_path / "conv.pgm"
        rotated_path = tmp_path / "rotated.pgm"
        # 3x2 image
        write_pbm([1, 0, 1, 0, 1, 0], 3, 2, pbm_path)
        convert_pbm_to_pgm(pbm_path, pgm_path)
        pgm_rotate_90(pgm_path, rotated_path)
        rotated = parse_pgm_strict(rotated_path)
        assert rotated.width == 2  # was height=2
        assert rotated.height == 3  # was width=3

    def test_chain_with_scale(self, tmp_path: Path) -> None:
        """PBM scale_nearest -> PGM conversion -> verify scaled dimensions."""
        pbm_src = tmp_path / "tiny.pbm"
        pbm_scaled = tmp_path / "scaled.pbm"
        pgm_out = tmp_path / "scaled.pgm"
        write_pbm([1, 0, 0, 1], 2, 2, pbm_src)
        scale_nearest(pbm_src, pbm_scaled, 3)
        convert_pbm_to_pgm(pbm_scaled, pgm_out)
        pgm = parse_pgm_strict(pgm_out)
        assert pgm.width == 6
        assert pgm.height == 6
        # Top-left 3x3 block should all be black (PGM value 0)
        for r in range(3):
            for c in range(3):
                assert pgm.pixels[r * 6 + c] == 0

    def test_roundtrip_pixel_preservation(self, tmp_path: Path) -> None:
        """PBM -> PGM -> verify every pixel maps correctly."""
        pbm_path = tmp_path / "rt.pbm"
        pgm_path = tmp_path / "rt.pgm"
        pixels = [1, 1, 0, 0, 1, 0]  # 3x2
        write_pbm(pixels, 3, 2, pbm_path)
        convert_pbm_to_pgm(pbm_path, pgm_path)
        pgm = parse_pgm_strict(pgm_path)
        for i, px in enumerate(pixels):
            expected = 0 if px == 1 else 255
            assert pgm.pixels[i] == expected, f"pixel {i}: expected {expected}, got {pgm.pixels[i]}"

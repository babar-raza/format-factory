"""Tests for PBM scale_nearest API — Sprint PACKAGING-BREAKTHROUGH."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from pbm.pbm_parser import (
    parse_pbm_strict,
    scale_nearest,
    write_pbm,
    PbmError,
)


def _make_pbm(tmp_path: Path, pixels: list[int], w: int, h: int) -> Path:
    p = tmp_path / "input.pbm"
    write_pbm(pixels, w, h, p)
    return p


class TestScaleNearest:
    def test_scale_2x_dimensions(self, tmp_path: Path) -> None:
        src = _make_pbm(tmp_path, [1, 0, 0, 1], 2, 2)
        dest = tmp_path / "out.pbm"
        result = scale_nearest(src, dest, 2)
        assert result["ok"] is True
        assert result["width"] == 4
        assert result["height"] == 4
        assert result["pixel_count"] == 16

    def test_scale_2x_pixel_values(self, tmp_path: Path) -> None:
        # [1, 0]
        # [0, 1]
        src = _make_pbm(tmp_path, [1, 0, 0, 1], 2, 2)
        dest = tmp_path / "out.pbm"
        scale_nearest(src, dest, 2)
        img = parse_pbm_strict(dest)
        # Row 0: 1,1,0,0  Row 1: 1,1,0,0  Row 2: 0,0,1,1  Row 3: 0,0,1,1
        assert img.pixels[0] == 1
        assert img.pixels[1] == 1
        assert img.pixels[2] == 0
        assert img.pixels[3] == 0
        assert img.pixels[8] == 0
        assert img.pixels[9] == 0
        assert img.pixels[10] == 1
        assert img.pixels[11] == 1

    def test_scale_1x_identity(self, tmp_path: Path) -> None:
        pixels = [1, 0, 0, 1]
        src = _make_pbm(tmp_path, pixels, 2, 2)
        dest = tmp_path / "out.pbm"
        scale_nearest(src, dest, 1)
        img = parse_pbm_strict(dest)
        assert img.width == 2
        assert img.height == 2
        assert img.pixels == pixels

    def test_scale_3x(self, tmp_path: Path) -> None:
        src = _make_pbm(tmp_path, [1], 1, 1)
        dest = tmp_path / "out.pbm"
        result = scale_nearest(src, dest, 3)
        assert result["width"] == 3
        assert result["height"] == 3
        img = parse_pbm_strict(dest)
        assert all(p == 1 for p in img.pixels)

    def test_scale_rectangular(self, tmp_path: Path) -> None:
        # 3x1 image: [1, 0, 1]
        src = _make_pbm(tmp_path, [1, 0, 1], 3, 1)
        dest = tmp_path / "out.pbm"
        result = scale_nearest(src, dest, 2)
        assert result["width"] == 6
        assert result["height"] == 2
        img = parse_pbm_strict(dest)
        # Row 0: 1,1,0,0,1,1  Row 1: 1,1,0,0,1,1
        assert img.pixels == [1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1]

    def test_scale_invalid_factor_zero(self, tmp_path: Path) -> None:
        src = _make_pbm(tmp_path, [1], 1, 1)
        dest = tmp_path / "out.pbm"
        with pytest.raises(ValueError, match="factor must be >= 1"):
            scale_nearest(src, dest, 0)

    def test_scale_invalid_factor_negative(self, tmp_path: Path) -> None:
        src = _make_pbm(tmp_path, [1], 1, 1)
        dest = tmp_path / "out.pbm"
        with pytest.raises(ValueError, match="factor must be >= 1"):
            scale_nearest(src, dest, -2)

    def test_scale_invalid_file(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.pbm"
        bad.write_text("not a pbm file")
        dest = tmp_path / "out.pbm"
        with pytest.raises(PbmError):
            scale_nearest(bad, dest, 2)

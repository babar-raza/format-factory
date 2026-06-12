"""
tests/python/pbm/test_r166_pbm_aspect_ratio.py

Tests for PBM aspect_ratio function.

Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
Queue: broad-accel-q-007
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import aspect_ratio, write_pbm


def _make_pbm(tmp_path: Path, width: int, height: int) -> Path:
    """Helper: write a minimal PBM file of given dimensions."""
    pixels = [0] * (width * height)
    path = tmp_path / f"test_{width}x{height}.pbm"
    write_pbm(pixels, width, height, path)
    return path


class TestAspectRatio:
    def test_square_image(self, tmp_path: Path) -> None:
        path = _make_pbm(tmp_path, 4, 4)
        ratio = aspect_ratio(path)
        assert abs(ratio - 1.0) < 1e-6

    def test_landscape_image(self, tmp_path: Path) -> None:
        path = _make_pbm(tmp_path, 8, 4)
        ratio = aspect_ratio(path)
        assert abs(ratio - 2.0) < 1e-6

    def test_portrait_image(self, tmp_path: Path) -> None:
        path = _make_pbm(tmp_path, 2, 4)
        ratio = aspect_ratio(path)
        assert abs(ratio - 0.5) < 1e-6

    def test_returns_float(self, tmp_path: Path) -> None:
        path = _make_pbm(tmp_path, 3, 2)
        result = aspect_ratio(path)
        assert isinstance(result, float)

    def test_aspect_ratio_1x1(self, tmp_path: Path) -> None:
        path = _make_pbm(tmp_path, 1, 1)
        assert abs(aspect_ratio(path) - 1.0) < 1e-6

    def test_wide_image(self, tmp_path: Path) -> None:
        path = _make_pbm(tmp_path, 10, 2)
        assert abs(aspect_ratio(path) - 5.0) < 1e-6

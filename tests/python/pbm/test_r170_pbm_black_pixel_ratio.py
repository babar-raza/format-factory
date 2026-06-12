"""Tests for PBM black_pixel_ratio function (rnext37)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import black_pixel_ratio, write_pbm, PbmError


def _make_pbm(pixels: list[list[int]]) -> str:
    height = len(pixels)
    width = len(pixels[0]) if pixels else 0
    flat = [px for row in pixels for px in row]
    tmp = tempfile.NamedTemporaryFile(suffix=".pbm", delete=False)
    tmp.close()
    write_pbm(flat, width, height, tmp.name)
    return tmp.name


class TestBlackPixelRatio:
    def test_all_black(self):
        path = _make_pbm([[1, 1], [1, 1]])
        try:
            assert black_pixel_ratio(path) == 1.0
        finally:
            os.unlink(path)

    def test_all_white(self):
        path = _make_pbm([[0, 0], [0, 0]])
        try:
            assert black_pixel_ratio(path) == 0.0
        finally:
            os.unlink(path)

    def test_half_black(self):
        path = _make_pbm([[1, 0], [0, 1]])
        try:
            assert black_pixel_ratio(path) == 0.5
        finally:
            os.unlink(path)

    def test_one_row(self):
        path = _make_pbm([[1, 0, 0, 0]])
        try:
            assert black_pixel_ratio(path) == 0.25
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        with pytest.raises(Exception):
            black_pixel_ratio("/nonexistent/file.pbm")

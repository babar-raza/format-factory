"""Tests for xcf_is_indexed — check if XCF image uses indexed color mode."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_is_indexed, xcf_is_rgb, xcf_is_grayscale

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfIsIndexed:
    def test_returns_bool(self):
        files = list(SAMPLES.glob("*.xcf")) if SAMPLES.exists() else []
        if not files:
            pytest.skip("No XCF samples")
        result = xcf_is_indexed(files[0])
        assert isinstance(result, bool)

    def test_rgb_is_not_indexed(self):
        files = list(SAMPLES.glob("*.xcf")) if SAMPLES.exists() else []
        if not files:
            pytest.skip("No XCF samples")
        for f in files:
            if xcf_is_rgb(f):
                assert xcf_is_indexed(f) is False
                return
        pytest.skip("No RGB XCF samples found")

    def test_grayscale_is_not_indexed(self):
        files = list(SAMPLES.glob("*.xcf")) if SAMPLES.exists() else []
        if not files:
            pytest.skip("No XCF samples")
        for f in files:
            if xcf_is_grayscale(f):
                assert xcf_is_indexed(f) is False
                return
        pytest.skip("No grayscale XCF samples found")

    def test_mutually_exclusive_with_rgb_and_grayscale(self):
        files = list(SAMPLES.glob("*.xcf")) if SAMPLES.exists() else []
        if not files:
            pytest.skip("No XCF samples")
        for f in files:
            modes = [xcf_is_rgb(f), xcf_is_grayscale(f), xcf_is_indexed(f)]
            assert sum(modes) == 1, f"Exactly one mode should be True for {f.name}"

    def test_importable_from_init(self):
        from src.python.xcf import xcf_is_indexed as fn
        assert callable(fn)

    def test_in_all_list(self):
        from src.python.xcf import __all__
        assert "xcf_is_indexed" in __all__

    def test_completes_type_trio(self):
        from src.python.xcf import __all__
        assert "xcf_is_rgb" in __all__
        assert "xcf_is_grayscale" in __all__
        assert "xcf_is_indexed" in __all__

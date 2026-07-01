"""R565: PPM additional properties — is_high_depth, is_tiny, megapixels.

Tests for PpmDocument depth and dimension properties added in R565.
Spec refs: FACT-PPM-001 (ppm:image).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.models import PpmDocument

SAMPLES = Path("samples/by-format/ppm/valid")


def _make_doc(width=1, height=1, maxval=255):
    """Build a minimal PpmDocument."""
    parsed = types.SimpleNamespace(
        width=width, height=height, maxval=maxval,
        magic="P6", pixels=[(0, 0, 0)] * (width * height), path="test.ppm",
        is_binary=True,
    )
    return PpmDocument(parsed)


class TestIsHighDepth:
    def test_maxval_255_not_high_depth(self):
        doc = _make_doc(maxval=255)
        assert doc.is_high_depth is False

    def test_maxval_256_is_high_depth(self):
        doc = _make_doc(maxval=256)
        assert doc.is_high_depth is True

    def test_maxval_65535_is_high_depth(self):
        doc = _make_doc(maxval=65535)
        assert doc.is_high_depth is True

    def test_maxval_100_not_high_depth(self):
        doc = _make_doc(maxval=100)
        assert doc.is_high_depth is False

    def test_is_high_depth_type(self):
        doc = _make_doc()
        assert isinstance(doc.is_high_depth, bool)


class TestIsTiny:
    def test_1x1_is_tiny(self):
        doc = _make_doc(width=1, height=1)
        assert doc.is_tiny is True

    def test_64x64_is_tiny(self):
        doc = _make_doc(width=64, height=64)
        assert doc.is_tiny is True

    def test_65x65_not_tiny(self):
        doc = _make_doc(width=65, height=65)
        assert doc.is_tiny is False

    def test_1x65_not_tiny(self):
        doc = _make_doc(width=1, height=65)
        assert doc.is_tiny is False

    def test_is_tiny_type(self):
        doc = _make_doc()
        assert isinstance(doc.is_tiny, bool)


class TestMegapixels:
    def test_1x1_megapixels(self):
        doc = _make_doc(width=1, height=1)
        assert doc.megapixels == pytest.approx(1e-6)

    def test_1000x1000_is_one_megapixel(self):
        doc = _make_doc(width=1000, height=1000)
        assert doc.megapixels == pytest.approx(1.0)

    def test_megapixels_type(self):
        doc = _make_doc()
        assert isinstance(doc.megapixels, float)

    def test_megapixels_consistent_with_pixel_count(self):
        doc = _make_doc(width=640, height=480)
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000.0)


class TestPropertyConsistency:
    def test_tiny_and_standard_depth(self):
        doc = _make_doc(width=4, height=4, maxval=255)
        assert doc.is_tiny is True
        assert doc.is_high_depth is False

    def test_from_file(self):
        doc = PpmDocument.from_file(SAMPLES / "2x2-rgbw.ppm")
        assert isinstance(doc.is_high_depth, bool)
        assert isinstance(doc.is_tiny, bool)
        assert isinstance(doc.megapixels, float)
        assert doc.is_tiny is True  # 2x2 is tiny
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000.0)

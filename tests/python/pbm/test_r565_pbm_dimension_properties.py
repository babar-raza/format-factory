"""R565: PBM additional dimension properties — is_tiny, is_large_image, megapixels.

Tests for PbmDocument additional properties added in R565.
Spec refs: SAL-PBM-00001 (pbm:image).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.models import PbmDocument

SAMPLES = Path("samples/by-format/pbm/valid")


def _make_doc(width=1, height=1):
    """Build a minimal PbmDocument."""
    parsed = types.SimpleNamespace(
        width=width, height=height, magic="P4",
        pixels=[0] * (width * height), path="test.pbm",
        is_binary=True,
    )
    return PbmDocument(parsed)


class TestIsTiny:
    def test_1x1_is_tiny(self):
        doc = _make_doc(width=1, height=1)
        assert doc.is_tiny is True

    def test_64x64_is_tiny(self):
        doc = _make_doc(width=64, height=64)
        assert doc.is_tiny is True

    def test_65x64_not_tiny(self):
        doc = _make_doc(width=65, height=64)
        assert doc.is_tiny is False

    def test_64x65_not_tiny(self):
        doc = _make_doc(width=64, height=65)
        assert doc.is_tiny is False

    def test_1000x1000_not_tiny(self):
        doc = _make_doc(width=1000, height=1000)
        assert doc.is_tiny is False

    def test_is_tiny_type(self):
        doc = _make_doc(width=10, height=10)
        assert isinstance(doc.is_tiny, bool)


class TestIsLargeImage:
    def test_small_image_not_large(self):
        doc = _make_doc(width=100, height=100)
        assert doc.is_large_image is False

    def test_exactly_1mp_is_large(self):
        doc = _make_doc(width=1000, height=1000)
        assert doc.is_large_image is True

    def test_999x1000_not_large(self):
        doc = _make_doc(width=999, height=1000)
        assert doc.is_large_image is False

    def test_1920x1080_is_large(self):
        doc = _make_doc(width=1920, height=1080)
        assert doc.is_large_image is True

    def test_is_large_image_type(self):
        doc = _make_doc(width=1000, height=1000)
        assert isinstance(doc.is_large_image, bool)


class TestMegapixels:
    def test_1x1_zero_megapixels(self):
        doc = _make_doc(width=1, height=1)
        assert doc.megapixels == pytest.approx(0.000001)

    def test_1000x1000_one_megapixel(self):
        doc = _make_doc(width=1000, height=1000)
        assert doc.megapixels == pytest.approx(1.0)

    def test_100x100(self):
        doc = _make_doc(width=100, height=100)
        assert doc.megapixels == pytest.approx(0.01)

    def test_megapixels_type(self):
        doc = _make_doc(width=10, height=10)
        assert isinstance(doc.megapixels, float)

    def test_megapixels_consistent_with_pixel_count(self):
        doc = _make_doc(width=500, height=400)
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000.0)


class TestPropertyConsistency:
    def test_tiny_not_large(self):
        doc = _make_doc(width=10, height=10)
        assert doc.is_tiny is True
        assert doc.is_large_image is False

    def test_large_not_tiny(self):
        doc = _make_doc(width=1500, height=1000)
        assert doc.is_tiny is False
        assert doc.is_large_image is True

    def test_from_file(self):
        doc = PbmDocument.from_file(SAMPLES / "2x2-checker.pbm")
        assert isinstance(doc.is_tiny, bool)
        assert isinstance(doc.is_large_image, bool)
        assert isinstance(doc.megapixels, float)
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000.0)

"""R565: PGM additional properties — is_high_depth, is_tiny, megapixels.

Tests for PgmDocument depth and dimension properties added in R565.
Spec refs: FACT-PGM-001 (pgm:image).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.models import PgmDocument

SAMPLES = Path("samples/by-format/pgm/valid")


def _make_doc(width=1, height=1, maxval=255):
    """Build a minimal PgmDocument."""
    parsed = types.SimpleNamespace(
        width=width, height=height, maxval=maxval,
        magic="P5", pixels=[0] * (width * height), path="test.pgm",
        is_binary=True,
    )
    return PgmDocument(parsed)


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

    def test_maxval_1_not_high_depth(self):
        doc = _make_doc(maxval=1)
        assert doc.is_high_depth is False

    def test_is_high_depth_type(self):
        doc = _make_doc(maxval=255)
        assert isinstance(doc.is_high_depth, bool)


class TestIsTiny:
    def test_1x1_is_tiny(self):
        doc = _make_doc(width=1, height=1)
        assert doc.is_tiny is True

    def test_64x64_is_tiny(self):
        doc = _make_doc(width=64, height=64)
        assert doc.is_tiny is True

    def test_65x1_not_tiny(self):
        doc = _make_doc(width=65, height=1)
        assert doc.is_tiny is False

    def test_100x100_not_tiny(self):
        doc = _make_doc(width=100, height=100)
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
        doc = _make_doc(width=400, height=300)
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000.0)


class TestPropertyConsistency:
    def test_standard_8bit_not_high_depth(self):
        doc = _make_doc(maxval=255)
        assert not doc.is_high_depth

    def test_16bit_is_high_depth(self):
        doc = _make_doc(maxval=65535)
        assert doc.is_high_depth

    def test_from_file(self):
        doc = PgmDocument.from_file(SAMPLES / "2x2-gradient.pgm")
        assert isinstance(doc.is_high_depth, bool)
        assert isinstance(doc.is_tiny, bool)
        assert isinstance(doc.megapixels, float)
        assert doc.is_tiny is True  # 2x2 is tiny
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000.0)

"""R1223: QOI image size classification properties — is_tiny, is_large_image, megapixels.

Tests for QoiDocument size properties added in R1223.
Spec refs: SAL-QOI-00001 (qoi:image header width/height).
"""

from __future__ import annotations

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.models import QoiDocument

SAMPLES = Path("samples/by-format/qoi/valid")


def _make_doc(width: int = 1, height: int = 1, channels: int = 3, colorspace: int = 0) -> QoiDocument:
    """Build a minimal QoiDocument from stub data."""
    parsed = types.SimpleNamespace(
        width=width, height=height, channels=channels,
        colorspace=colorspace, pixels=[], path="test.qoi",
    )
    return QoiDocument(parsed)


class TestIsTiny:
    def test_1x1_is_tiny(self):
        doc = _make_doc(1, 1)
        assert doc.is_tiny is True

    def test_32x32_is_tiny(self):
        """32x32 = 1024 pixels — boundary: strictly less than 1024, so 31x33=1023 is tiny."""
        doc = _make_doc(31, 33)
        assert doc.is_tiny is True

    def test_32x32_exact_not_tiny(self):
        """32x32 = 1024 pixels — not tiny (boundary is < 1024)."""
        doc = _make_doc(32, 32)
        assert doc.is_tiny is False

    def test_100x100_not_tiny(self):
        doc = _make_doc(100, 100)
        assert doc.is_tiny is False

    def test_is_tiny_returns_bool(self):
        doc = _make_doc(1, 1)
        assert isinstance(doc.is_tiny, bool)

    def test_is_tiny_from_file_1x1(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert doc.is_tiny is True

    def test_is_tiny_from_file_2x2(self):
        doc = QoiDocument.from_file(SAMPLES / "2x2-black.qoi")
        assert doc.is_tiny is True

    def test_is_tiny_from_file_4x1(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.is_tiny is True


class TestIsLargeImage:
    def test_1x1_not_large(self):
        doc = _make_doc(1, 1)
        assert doc.is_large_image is False

    def test_2000x2000_not_large(self):
        """2000x2000 = 4,000,000 pixels — boundary: strictly greater than 4M."""
        doc = _make_doc(2000, 2000)
        assert doc.is_large_image is False

    def test_2001x2000_is_large(self):
        """2001x2000 = 4,002,000 pixels — above 4M threshold."""
        doc = _make_doc(2001, 2000)
        assert doc.is_large_image is True

    def test_4001x1000_is_large(self):
        """4001x1000 = 4,001,000 pixels — above 4M threshold."""
        doc = _make_doc(4001, 1000)
        assert doc.is_large_image is True

    def test_is_large_returns_bool(self):
        doc = _make_doc(1, 1)
        assert isinstance(doc.is_large_image, bool)

    def test_sample_files_not_large(self):
        for fname in ("1x1-red.qoi", "2x2-black.qoi", "4x1-gradient.qoi"):
            doc = QoiDocument.from_file(SAMPLES / fname)
            assert doc.is_large_image is False


class TestMegapixels:
    def test_1x1_megapixels(self):
        doc = _make_doc(1, 1)
        assert doc.megapixels == pytest.approx(0.000001)

    def test_1000x1000_megapixels(self):
        doc = _make_doc(1000, 1000)
        assert doc.megapixels == pytest.approx(1.0)

    def test_2000x2000_megapixels(self):
        doc = _make_doc(2000, 2000)
        assert doc.megapixels == pytest.approx(4.0)

    def test_returns_float(self):
        doc = _make_doc(10, 10)
        assert isinstance(doc.megapixels, float)

    def test_megapixels_nonnegative(self):
        doc = _make_doc(1, 1)
        assert doc.megapixels >= 0.0

    def test_megapixels_from_file_1x1(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert doc.megapixels == pytest.approx(1e-6)

    def test_megapixels_from_file_4x1(self):
        doc = QoiDocument.from_file(SAMPLES / "4x1-gradient.qoi")
        assert doc.megapixels == pytest.approx(4e-6)

    def test_megapixels_consistent_with_pixel_count(self):
        doc = _make_doc(500, 800)
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000)

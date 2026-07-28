"""R565: QOI channel and colorspace properties — is_rgb, is_srgb, is_linear.

Tests for QoiDocument channel and colorspace properties added in R565.
Spec refs: SAL-QOI-00001 (qoi:image).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.models import QoiDocument

SAMPLES = Path("samples/by-format/qoi/valid")


def _make_doc(width=1, height=1, channels=3, colorspace=0):
    """Build a minimal QoiDocument."""
    parsed = types.SimpleNamespace(
        width=width, height=height, channels=channels,
        colorspace=colorspace, pixels=[], path="test.qoi",
    )
    return QoiDocument(parsed)


class TestIsRgb:
    def test_3_channels_is_rgb(self):
        doc = _make_doc(channels=3)
        assert doc.is_rgb is True

    def test_4_channels_not_rgb(self):
        doc = _make_doc(channels=4)
        assert doc.is_rgb is False

    def test_is_rgb_type(self):
        doc = _make_doc(channels=3)
        assert isinstance(doc.is_rgb, bool)

    def test_is_rgb_inverse_of_has_alpha(self):
        doc3 = _make_doc(channels=3)
        doc4 = _make_doc(channels=4)
        assert doc3.is_rgb is True
        assert doc3.has_alpha is False
        assert doc4.is_rgb is False
        assert doc4.has_alpha is True


class TestIsSrgb:
    def test_colorspace_0_is_srgb(self):
        doc = _make_doc(colorspace=0)
        assert doc.is_srgb is True

    def test_colorspace_1_not_srgb(self):
        doc = _make_doc(colorspace=1)
        assert doc.is_srgb is False

    def test_is_srgb_type(self):
        doc = _make_doc(colorspace=0)
        assert isinstance(doc.is_srgb, bool)

    def test_srgb_and_linear_exclusive(self):
        doc0 = _make_doc(colorspace=0)
        doc1 = _make_doc(colorspace=1)
        assert doc0.is_srgb is True
        assert doc0.is_linear is False
        assert doc1.is_srgb is False
        assert doc1.is_linear is True


class TestIsLinear:
    def test_colorspace_1_is_linear(self):
        doc = _make_doc(colorspace=1)
        assert doc.is_linear is True

    def test_colorspace_0_not_linear(self):
        doc = _make_doc(colorspace=0)
        assert doc.is_linear is False

    def test_is_linear_type(self):
        doc = _make_doc(colorspace=1)
        assert isinstance(doc.is_linear, bool)


class TestChannelColorspaceConsistency:
    def test_rgb_srgb_typical_image(self):
        doc = _make_doc(channels=3, colorspace=0)
        assert doc.is_rgb is True
        assert doc.is_srgb is True
        assert not doc.has_alpha
        assert not doc.is_linear

    def test_rgba_linear_hdr_image(self):
        doc = _make_doc(channels=4, colorspace=1)
        assert doc.is_rgb is False
        assert doc.has_alpha is True
        assert doc.is_linear is True
        assert not doc.is_srgb

    def test_from_file(self):
        doc = QoiDocument.from_file(SAMPLES / "1x1-red.qoi")
        assert isinstance(doc.is_rgb, bool)
        assert isinstance(doc.is_srgb, bool)
        assert isinstance(doc.is_linear, bool)
        # sRGB and linear are mutually exclusive
        assert not (doc.is_srgb and doc.is_linear)

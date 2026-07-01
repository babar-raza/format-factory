"""R560: XCF is_multilayer domain model property.

Tests for XcfDocument.is_multilayer added in R560.
Spec refs: FACT-XCF-001.
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.models import XcfDocument

SAMPLES = Path("samples/by-format/xcf/valid")


def _make_xcf(width=100, height=100, num_layers=1, image_type=0, version="xcf v011"):
    """Build a minimal parsed XCF object."""
    return types.SimpleNamespace(
        width=width,
        height=height,
        num_layers=num_layers,
        image_type=image_type,
        version=version,
        path="test.xcf",
        layer_names=None,
    )


class TestIsMultilayer:
    def test_single_layer_not_multilayer(self):
        doc = XcfDocument(_make_xcf(num_layers=1))
        assert doc.is_multilayer is False

    def test_two_layers_is_multilayer(self):
        doc = XcfDocument(_make_xcf(num_layers=2))
        assert doc.is_multilayer is True

    def test_three_layers_is_multilayer(self):
        doc = XcfDocument(_make_xcf(num_layers=3))
        assert doc.is_multilayer is True

    def test_is_multilayer_type(self):
        doc = XcfDocument(_make_xcf(num_layers=1))
        assert isinstance(doc.is_multilayer, bool)

    def test_multilayer_consistent_with_layer_count(self):
        for n in range(5):
            doc = XcfDocument(_make_xcf(num_layers=n))
            assert doc.is_multilayer == (n > 1)


class TestGeometryProperties:
    def test_aspect_ratio_square(self):
        doc = XcfDocument(_make_xcf(width=100, height=100))
        assert doc.aspect_ratio == pytest.approx(1.0)

    def test_aspect_ratio_landscape(self):
        doc = XcfDocument(_make_xcf(width=200, height=100))
        assert doc.aspect_ratio == pytest.approx(2.0)

    def test_is_square_true(self):
        doc = XcfDocument(_make_xcf(width=64, height=64))
        assert doc.is_square is True

    def test_is_square_false(self):
        doc = XcfDocument(_make_xcf(width=200, height=100))
        assert doc.is_square is False

    def test_is_landscape_true(self):
        doc = XcfDocument(_make_xcf(width=300, height=100))
        assert doc.is_landscape is True

    def test_is_portrait_true(self):
        doc = XcfDocument(_make_xcf(width=100, height=300))
        assert doc.is_portrait is True

    def test_is_portrait_type(self):
        doc = XcfDocument(_make_xcf(width=100, height=300))
        assert isinstance(doc.is_portrait, bool)


class TestGeometryConsistency:
    def test_square_mutual_exclusion(self):
        doc = XcfDocument(_make_xcf(width=100, height=100))
        assert doc.is_square
        assert not doc.is_landscape
        assert not doc.is_portrait

    def test_landscape_mutual_exclusion(self):
        doc = XcfDocument(_make_xcf(width=200, height=100))
        assert doc.is_landscape
        assert not doc.is_square
        assert not doc.is_portrait

    def test_portrait_mutual_exclusion(self):
        doc = XcfDocument(_make_xcf(width=100, height=200))
        assert doc.is_portrait
        assert not doc.is_square
        assert not doc.is_landscape

    def test_aspect_ratio_consistent_with_landscape(self):
        doc = XcfDocument(_make_xcf(width=300, height=100))
        assert doc.is_landscape == (doc.aspect_ratio > 1.0)

    def test_from_file_returns_document(self):
        doc = XcfDocument.from_file(SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(doc, XcfDocument)
        assert isinstance(doc.is_multilayer, bool)
        assert isinstance(doc.is_square, bool)

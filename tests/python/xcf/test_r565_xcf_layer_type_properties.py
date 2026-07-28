"""R565: XCF additional layer and type properties — is_flat, has_layers, is_rgb_type.

Tests for XcfDocument layer and image type properties added in R565.
Spec refs: SAL-XCF-00001 (xcf:image).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.models import XcfDocument

SAMPLES = Path("samples/by-format/xcf/valid")


def _make_doc(width=100, height=100, layer_count=1, image_type=0, version="file"):
    """Build a minimal XcfDocument."""
    parsed = types.SimpleNamespace(
        width=width, height=height, num_layers=layer_count,
        version=version, image_type=image_type,
        layer_names=[f"Layer {i}" for i in range(layer_count)],
        path="test.xcf",
    )
    return XcfDocument(parsed)


class TestIsFlat:
    def test_no_layers_is_flat(self):
        doc = _make_doc(layer_count=0)
        assert doc.is_flat is True

    def test_one_layer_is_flat(self):
        doc = _make_doc(layer_count=1)
        assert doc.is_flat is True

    def test_two_layers_not_flat(self):
        doc = _make_doc(layer_count=2)
        assert doc.is_flat is False

    def test_many_layers_not_flat(self):
        doc = _make_doc(layer_count=5)
        assert doc.is_flat is False

    def test_is_flat_type(self):
        doc = _make_doc(layer_count=1)
        assert isinstance(doc.is_flat, bool)

    def test_is_flat_inverse_of_is_multilayer(self):
        doc1 = _make_doc(layer_count=1)
        doc2 = _make_doc(layer_count=2)
        assert doc1.is_flat is True
        assert doc1.is_multilayer is False
        assert doc2.is_flat is False
        assert doc2.is_multilayer is True


class TestHasLayers:
    def test_zero_layers_no_layers(self):
        doc = _make_doc(layer_count=0)
        assert doc.has_layers is False

    def test_one_layer_has_layers(self):
        doc = _make_doc(layer_count=1)
        assert doc.has_layers is True

    def test_many_layers_has_layers(self):
        doc = _make_doc(layer_count=10)
        assert doc.has_layers is True

    def test_has_layers_type(self):
        doc = _make_doc(layer_count=1)
        assert isinstance(doc.has_layers, bool)


class TestIsRgbType:
    def test_image_type_0_is_rgb(self):
        doc = _make_doc(image_type=0)
        assert doc.is_rgb_type is True

    def test_image_type_1_not_rgb(self):
        doc = _make_doc(image_type=1)
        assert doc.is_rgb_type is False

    def test_image_type_2_not_rgb(self):
        doc = _make_doc(image_type=2)
        assert doc.is_rgb_type is False

    def test_is_rgb_type_type(self):
        doc = _make_doc(image_type=0)
        assert isinstance(doc.is_rgb_type, bool)


class TestLayerTypeConsistency:
    def test_flat_has_layers_exclusive_for_zero(self):
        doc = _make_doc(layer_count=0)
        assert doc.is_flat is True
        assert doc.has_layers is False

    def test_one_layer_flat_and_has_layers(self):
        doc = _make_doc(layer_count=1)
        assert doc.is_flat is True
        assert doc.has_layers is True

    def test_multilayer_not_flat_has_layers(self):
        doc = _make_doc(layer_count=3)
        assert doc.is_flat is False
        assert doc.has_layers is True
        assert doc.is_multilayer is True

    def test_from_file(self):
        doc = XcfDocument.from_file(SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(doc.is_flat, bool)
        assert isinstance(doc.has_layers, bool)
        assert isinstance(doc.is_rgb_type, bool)
        assert doc.is_rgb_type is True  # 1x1-red-rgb.xcf is RGB

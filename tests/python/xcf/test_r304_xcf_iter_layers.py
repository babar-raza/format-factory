"""
tests/python/xcf/test_r304_xcf_iter_layers.py

Sprint: ff-sprint-s304-xcf-layer-iterator-20260626
Authority: GIMP XCF file format — layer record

Tests for xcf_iter_layers() in xcf_layer_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_MINIMAL = _VALID_DIR / "1x1-red-rgb.xcf"
_RGBA = _VALID_DIR / "1x1-rgba-blue.xcf"


class TestXcfIterLayersImport:
    def test_importable_from_xcf_layer_iterator(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        assert callable(xcf_iter_layers)

    def test_importable_from_package(self):
        import xcf
        assert hasattr(xcf, "xcf_iter_layers")


class TestXcfIterLayersOutput:
    def test_returns_iterator(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        result = xcf_iter_layers(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_layers(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        layers = list(xcf_iter_layers(str(_MINIMAL)))
        assert len(layers) >= 1

    def test_layer_type_is_spec_layer(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        from xcf.spec.layer.layer import Layer
        layers = list(xcf_iter_layers(str(_MINIMAL)))
        assert all(isinstance(l, Layer) for l in layers)

    def test_layer_has_spec_qname(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        layers = list(xcf_iter_layers(str(_MINIMAL)))
        assert all(hasattr(l, "spec_qname") for l in layers)

    def test_layer_qname_value(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        layers = list(xcf_iter_layers(str(_MINIMAL)))
        assert all(l.spec_qname == "xcf:layer" for l in layers)

    def test_layer_has_name(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        layers = list(xcf_iter_layers(str(_MINIMAL)))
        for l in layers:
            assert isinstance(l.name, str)

    def test_layer_has_dimensions(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        layers = list(xcf_iter_layers(str(_MINIMAL)))
        for l in layers:
            assert isinstance(l.width, int) and l.width >= 0
            assert isinstance(l.height, int) and l.height >= 0

    def test_consistent(self):
        from xcf.xcf_layer_iterator import xcf_iter_layers
        r1 = [l.name for l in xcf_iter_layers(str(_MINIMAL))]
        r2 = [l.name for l in xcf_iter_layers(str(_MINIMAL))]
        assert r1 == r2

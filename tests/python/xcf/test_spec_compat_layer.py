"""Behavioral tests for XCF spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.xcf.Compat import XcfHeader, XcfLayer
from src.python.xcf.spec.layer.header import Header as SpecHeader
from src.python.xcf.spec.layer.layer import Layer as SpecLayer


_SAMPLE_HEADER = {"version": "file", "width": 800, "height": 600, "color_mode": 0, "layer_count": 3}
_SAMPLE_LAYER = {"name": "Background", "width": 800, "height": 600, "type": 0, "visible": True}


class TestXcfHeaderMetadata:
    def test_spec_qname(self):
        assert XcfHeader.spec_qname == "xcf:header"

    def test_spec_fact_ref(self):
        assert XcfHeader.spec_fact_ref == "FACT-XCF-001"

    def test_magic_constant(self):
        assert XcfHeader.MAGIC == b"gimp xcf "

    def test_namespace_uri_present(self):
        assert XcfHeader.namespace_uri


class TestXcfHeaderBehavior:
    def test_instantiation(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_version_property(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert h.version == "file"

    def test_width_property(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert h.width == 800

    def test_height_property(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert h.height == 600

    def test_layer_count(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert h.layer_count == 3

    def test_to_dict(self):
        h = XcfHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = XcfHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestXcfLayerBehavior:
    def test_instantiation(self):
        l = XcfLayer(_SAMPLE_LAYER)
        assert l is not None

    def test_spec_qname(self):
        assert XcfLayer.spec_qname == "xcf:layer"

    def test_name_property(self):
        l = XcfLayer(_SAMPLE_LAYER)
        assert l.name == "Background"

    def test_visible_property(self):
        l = XcfLayer(_SAMPLE_LAYER)
        assert l.visible is True

    def test_inherits_spec_class(self):
        l = XcfLayer(_SAMPLE_LAYER)
        assert isinstance(l, SpecLayer)

    def test_repr_nonempty(self):
        l = XcfLayer(_SAMPLE_LAYER)
        assert repr(l)

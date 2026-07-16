"""Behavioral tests for PPM spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.ppm.Compat import PpmHeader, PpmPixmap
from src.python.ppm.spec.pixmap.header import Header as SpecHeader
from src.python.ppm.spec.pixmap.pixmap import Pixmap as SpecPixmap


_SAMPLE_HEADER = {"magic": "P3", "width": 4, "height": 4, "maxval": 255}
_SAMPLE_PIXMAP = {"width": 4, "height": 4, "pixel_count": 16}


class TestPpmHeaderMetadata:
    def test_spec_qname(self):
        assert PpmHeader.spec_qname == "ppm:header"

    def test_spec_fact_ref(self):
        assert PpmHeader.spec_fact_ref == "SAL-PPM-00001"

    def test_namespace_uri_present(self):
        assert PpmHeader.namespace_uri


class TestPpmHeaderBehavior:
    def test_instantiation(self):
        h = PpmHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_magic_property(self):
        h = PpmHeader(_SAMPLE_HEADER)
        assert h.magic == "P3"

    def test_width_property(self):
        h = PpmHeader(_SAMPLE_HEADER)
        assert h.width == 4

    def test_maxval(self):
        h = PpmHeader(_SAMPLE_HEADER)
        assert h.maxval == 255

    def test_to_dict(self):
        h = PpmHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = PpmHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = PpmHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestPpmPixmapBehavior:
    def test_instantiation(self):
        p = PpmPixmap(_SAMPLE_PIXMAP)
        assert p is not None

    def test_spec_qname(self):
        assert PpmPixmap.spec_qname == "ppm:pixmap"

    def test_pixel_count(self):
        p = PpmPixmap(_SAMPLE_PIXMAP)
        assert p.pixel_count == 16

    def test_inherits_spec_class(self):
        p = PpmPixmap(_SAMPLE_PIXMAP)
        assert isinstance(p, SpecPixmap)

    def test_repr_nonempty(self):
        p = PpmPixmap(_SAMPLE_PIXMAP)
        assert repr(p)

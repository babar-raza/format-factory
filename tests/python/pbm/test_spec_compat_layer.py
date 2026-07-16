"""Behavioral tests for PBM spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.pbm.Compat import PbmHeader, PbmBitmap
from src.python.pbm.spec.bitmap.header import Header as SpecHeader
from src.python.pbm.spec.bitmap.bitmap import Bitmap as SpecBitmap


_SAMPLE_HEADER = {"magic": "P1", "width": 10, "height": 5, "is_binary": False}
_SAMPLE_BITMAP = {"width": 10, "height": 5, "pixel_count": 50}


class TestPbmHeaderMetadata:
    def test_spec_qname(self):
        assert PbmHeader.spec_qname == "pbm:header"

    def test_spec_fact_ref(self):
        assert PbmHeader.spec_fact_ref == "SAL-PBM-00001"

    def test_namespace_uri_present(self):
        assert PbmHeader.namespace_uri


class TestPbmHeaderBehavior:
    def test_instantiation(self):
        h = PbmHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_magic_property(self):
        h = PbmHeader(_SAMPLE_HEADER)
        assert h.magic == "P1"

    def test_width_property(self):
        h = PbmHeader(_SAMPLE_HEADER)
        assert h.width == 10

    def test_height_property(self):
        h = PbmHeader(_SAMPLE_HEADER)
        assert h.height == 5

    def test_to_dict(self):
        h = PbmHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = PbmHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = PbmHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestPbmBitmapBehavior:
    def test_instantiation(self):
        b = PbmBitmap(_SAMPLE_BITMAP)
        assert b is not None

    def test_spec_qname(self):
        assert PbmBitmap.spec_qname == "pbm:bitmap"

    def test_spec_fact_ref(self):
        assert PbmBitmap.spec_fact_ref == "SAL-PBM-00002"

    def test_pixel_count(self):
        b = PbmBitmap(_SAMPLE_BITMAP)
        assert b.pixel_count == 50

    def test_inherits_spec_class(self):
        b = PbmBitmap(_SAMPLE_BITMAP)
        assert isinstance(b, SpecBitmap)

    def test_repr_nonempty(self):
        b = PbmBitmap(_SAMPLE_BITMAP)
        assert repr(b)

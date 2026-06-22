"""Behavioral tests for PGM spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.pgm.Compat import PgmHeader, PgmGraymap
from src.python.pgm.spec.graymap.header import Header as SpecHeader
from src.python.pgm.spec.graymap.graymap import Graymap as SpecGraymap


_SAMPLE_HEADER = {"magic": "P2", "width": 8, "height": 8, "maxval": 255}
_SAMPLE_GRAYMAP = {"width": 8, "height": 8, "pixel_count": 64}


class TestPgmHeaderMetadata:
    def test_spec_qname(self):
        assert PgmHeader.spec_qname == "pgm:header"

    def test_spec_fact_ref(self):
        assert PgmHeader.spec_fact_ref == "FACT-PGM-001"

    def test_namespace_uri_present(self):
        assert PgmHeader.namespace_uri


class TestPgmHeaderBehavior:
    def test_instantiation(self):
        h = PgmHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_magic_property(self):
        h = PgmHeader(_SAMPLE_HEADER)
        assert h.magic == "P2"

    def test_width_property(self):
        h = PgmHeader(_SAMPLE_HEADER)
        assert h.width == 8

    def test_maxval(self):
        h = PgmHeader(_SAMPLE_HEADER)
        assert h.maxval == 255

    def test_to_dict(self):
        h = PgmHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = PgmHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = PgmHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestPgmGraymapBehavior:
    def test_instantiation(self):
        g = PgmGraymap(_SAMPLE_GRAYMAP)
        assert g is not None

    def test_spec_qname(self):
        assert PgmGraymap.spec_qname == "pgm:graymap"

    def test_pixel_count(self):
        g = PgmGraymap(_SAMPLE_GRAYMAP)
        assert g.pixel_count == 64

    def test_inherits_spec_class(self):
        g = PgmGraymap(_SAMPLE_GRAYMAP)
        assert isinstance(g, SpecGraymap)

    def test_repr_nonempty(self):
        g = PgmGraymap(_SAMPLE_GRAYMAP)
        assert repr(g)

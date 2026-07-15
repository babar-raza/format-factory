"""Tests for xliff.spec stub classes and xliff.Compat facade classes.

L2 (facade/behavior) classes: TestSpecStubs, TestSpecStubClassAttrs,
TestCompatFacades.
L3 (malformed/boundary) class: TestCompatEdgeCases.
"""

from __future__ import annotations

from pathlib import Path

from xliff.Compat import XliffFile, XliffSegment, XliffUnit
from xliff.spec.file.file import File
from xliff.spec.file.segment import Segment
from xliff.spec.file.unit import Unit
from xliff.xliff_codec import load_xliff

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"
VALID_DIR = SAMPLES / "valid"

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"


class TestSpecStubs:
    def test_file_stub_wraps_dict(self):
        f = File({"id": "f1", "units": [{"id": "u1", "segments": []}]})
        assert f.id == "f1"
        assert f.unit_count == 1

    def test_unit_stub_segment_count(self):
        u = Unit({"id": "u1", "segments": [{"source": "A"}, {"source": "B"}]})
        assert u.segment_count == 2

    def test_segment_stub_is_translated_true(self):
        seg = Segment({"source": "Hi", "target": "Hola"})
        assert seg.is_translated is True

    def test_segment_stub_is_translated_false(self):
        seg = Segment({"source": "Hi", "target": ""})
        assert seg.is_translated is False

    def test_segment_stub_to_dict_roundtrips(self):
        data = {"source": "Hi", "target": "Hola", "state": "translated"}
        seg = Segment(data)
        assert seg.to_dict() == data

    def test_file_stub_repr(self):
        f = File({"id": "f1", "units": []})
        assert "f1" in repr(f)


class TestSpecStubClassAttrs:
    def test_file_spec_qname(self):
        assert File.spec_qname == "xliff:file"
        assert File.spec_fact_ref == "FACT-XLIFF-001"

    def test_unit_spec_qname(self):
        assert Unit.spec_qname == "xliff:unit"
        assert Unit.spec_fact_ref == "FACT-XLIFF-002"

    def test_segment_spec_qname(self):
        assert Segment.spec_qname == "xliff:segment"
        assert Segment.spec_fact_ref == "FACT-XLIFF-002"


class TestCompatFacades:
    def test_xliff_file_subclasses_spec_file(self):
        assert issubclass(XliffFile, File)

    def test_xliff_unit_subclasses_spec_unit(self):
        assert issubclass(XliffUnit, Unit)

    def test_xliff_segment_subclasses_spec_segment(self):
        assert issubclass(XliffSegment, Segment)

    def test_xliff_file_spec_qname_matches_registry(self):
        assert XliffFile.spec_qname == "xliff:file"
        assert XliffFile.spec_fact_ref == "FACT-XLIFF-001"
        assert XliffFile.namespace_uri == XLIFF_NS

    def test_xliff_unit_spec_qname_matches_registry(self):
        assert XliffUnit.spec_qname == "xliff:unit"
        assert XliffUnit.spec_fact_ref == "FACT-XLIFF-002"
        assert XliffUnit.namespace_uri == XLIFF_NS

    def test_xliff_segment_spec_qname_matches_registry(self):
        assert XliffSegment.spec_qname == "xliff:segment"
        assert XliffSegment.spec_fact_ref == "FACT-XLIFF-002"
        assert XliffSegment.namespace_uri == XLIFF_NS

    def test_xliff_facade_wraps_real_loaded_data(self):
        model = load_xliff(VALID_DIR / "multi-unit.xliff")
        facade = XliffFile(model["files"][0])
        assert facade.unit_count == 3

    def test_xliff_segment_facade_translated_state(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        seg_data = model["files"][0]["units"][0]["segments"][0]
        facade = XliffSegment(seg_data)
        assert facade.is_translated is True
        assert facade.source == "Hello"


class TestCompatEdgeCases:
    def test_file_stub_empty_dict_defaults(self):
        f = File({})
        assert f.id == ""
        assert f.units == []
        assert f.unit_count == 0

    def test_unit_stub_empty_dict_defaults(self):
        u = Unit({})
        assert u.id == ""
        assert u.segments == []
        assert u.segment_count == 0

    def test_segment_stub_empty_dict_defaults(self):
        seg = Segment({})
        assert seg.source == ""
        assert seg.target == ""
        assert seg.state == ""
        assert seg.is_translated is False

    def test_facade_with_malformed_data_missing_units_key(self):
        facade = XliffFile({"id": "orphan"})
        assert facade.unit_count == 0
        assert facade.units == []

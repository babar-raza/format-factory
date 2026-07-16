"""XLIFF gap-ledger coverage — explicit tests for every gap-listed capability.

Targets: roundtrip, probe_xliff, get_file_count, get_unit_count, iter_file_units,
load_xliff, write_xliff, xliff_installed_workflow, XliffDocument,
XliffError, XliffParseError, XliffWriteError, InlineElement,
parse_inline_content, serialize_inline_content,
xliff_average_source_length, xliff_translated_segment_count,
xliff_untranslated_segment_count.
"""
from __future__ import annotations

import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xliff import (
    XliffDocument,
    load_xliff,
    write_xliff,
    roundtrip,
)
from xliff.exceptions import XliffError, XliffParseError, XliffWriteError
from xliff.xliff_codec import (
    get_file_count,
    get_unit_count,
    iter_file_units,
    probe_xliff,
    xliff_installed_workflow,
)
from xliff.xliff_inline_model import InlineElement
from xliff.xliff_inline import parse_inline_content, serialize_inline_content
from xliff.xliff_analytics import (
    xliff_average_source_length,
    xliff_translated_segment_count,
    xliff_untranslated_segment_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "xliff" / "valid"


class TestProbeXliff:
    def test_probe_valid_minimal(self):
        result = probe_xliff(SAMPLES / "minimal.xliff")
        assert result is True or (isinstance(result, dict) and result.get("valid"))

    def test_probe_invalid_data(self):
        result = probe_xliff(b"not xliff data")
        assert result is False or (isinstance(result, dict) and not result.get("valid"))

    def test_probe_bytes_source(self):
        data = (SAMPLES / "minimal.xliff").read_bytes()
        result = probe_xliff(data)
        assert result is True or (isinstance(result, dict) and result.get("valid"))


class TestLoadXliff:
    def test_load_returns_dict(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        assert isinstance(model, dict)

    def test_load_has_source_language(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        assert "source_language" in model

    def test_load_has_files(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        assert "files" in model
        assert len(model["files"]) > 0

    def test_load_from_bytes(self):
        data = (SAMPLES / "minimal.xliff").read_bytes()
        model = load_xliff(data)
        assert isinstance(model, dict)


class TestWriteXliff:
    def test_write_returns_string(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        result = write_xliff(model)
        assert isinstance(result, str)
        assert "xliff" in result.lower()

    def test_write_to_file(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as f:
            tmp = Path(f.name)
        try:
            write_xliff(model, tmp)
            assert tmp.exists()
            content = tmp.read_text(encoding="utf-8")
            assert "xliff" in content.lower()
        finally:
            tmp.unlink(missing_ok=True)

    def test_roundtrip_identity(self):
        with tempfile.NamedTemporaryFile(suffix=".xliff", delete=False) as f:
            tmp = Path(f.name)
        try:
            result = roundtrip(SAMPLES / "minimal.xliff", tmp)
            assert isinstance(result, dict)
            orig = load_xliff(SAMPLES / "minimal.xliff")
            assert result["source_language"] == orig["source_language"]
        finally:
            tmp.unlink(missing_ok=True)


class TestGetCounts:
    def test_get_unit_count(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        count = get_unit_count(model)
        assert isinstance(count, int)
        assert count >= 1

    def test_get_unit_count_multi(self):
        model = load_xliff(SAMPLES / "multi-unit.xliff")
        count = get_unit_count(model)
        assert count >= 2

    def test_get_file_count(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        count = get_file_count(model)
        assert isinstance(count, int)
        assert count >= 1

    def test_iter_file_units(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        for f in model["files"]:
            units = list(iter_file_units(f))
            assert len(units) >= 1
            assert all(isinstance(u, dict) for u in units)


class TestXliffDocument:
    def test_from_file(self):
        doc = XliffDocument.from_file(str(SAMPLES / "minimal.xliff"))
        assert doc is not None

    def test_raw_property(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        doc = XliffDocument(model)
        assert doc.raw is model

    def test_source_language(self):
        doc = XliffDocument(load_xliff(SAMPLES / "minimal.xliff"))
        assert doc.source_language is not None

    def test_to_dict(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        doc = XliffDocument(model)
        d = doc.to_dict()
        assert isinstance(d, dict)


class TestErrorClasses:
    def test_xliff_error_is_exception(self):
        assert issubclass(XliffError, Exception)

    def test_parse_error_inherits(self):
        assert issubclass(XliffParseError, XliffError)

    def test_write_error_inherits(self):
        assert issubclass(XliffWriteError, XliffError)

    def test_parse_error_message(self):
        err = XliffParseError("bad xml")
        assert str(err) == "bad xml"

    def test_write_error_message(self):
        err = XliffWriteError("write failed")
        assert str(err) == "write failed"

    def test_catchable_as_base(self):
        with pytest.raises(XliffError):
            raise XliffParseError("test")


class TestInlineElement:
    def test_create(self):
        elem = InlineElement(tag="ph", attributes={"id": "1"})
        assert elem.tag == "ph"

    def test_content(self):
        elem = InlineElement(tag="pc", attributes={"id": "1"}, content=["hello"])
        assert "hello" in elem.content

    def test_nested(self):
        inner = InlineElement(tag="ph", attributes={"id": "1"})
        outer = InlineElement(tag="pc", attributes={"id": "2"}, content=["text ", inner])
        assert len(outer.content) == 2


class TestInlineParseSerialization:
    NS = "urn:oasis:names:tc:xliff:document:2.0"

    def test_parse_plain_text(self):
        xml_str = f'<source xmlns="{self.NS}">Hello world</source>'
        elem = ET.fromstring(xml_str)
        content = parse_inline_content(elem)
        assert any(isinstance(c, str) and "Hello" in c for c in content)

    def test_serialize_plain_text(self):
        parent = ET.Element("source")
        serialize_inline_content(parent, ["Hello world"], self.NS)
        assert parent.text == "Hello world" or "Hello" in ET.tostring(parent, encoding="unicode")


class TestAnalytics:
    def test_translated_count_minimal(self):
        count = xliff_translated_segment_count(SAMPLES / "minimal.xliff")
        assert isinstance(count, int)
        assert count >= 0

    def test_untranslated_count_minimal(self):
        count = xliff_untranslated_segment_count(SAMPLES / "minimal.xliff")
        assert isinstance(count, int)
        assert count >= 0

    def test_average_source_length(self):
        avg = xliff_average_source_length(SAMPLES / "minimal.xliff")
        assert isinstance(avg, (int, float))
        assert avg >= 0

    def test_translated_plus_untranslated_matches_total(self):
        model = load_xliff(SAMPLES / "minimal.xliff")
        total_segs = 0
        for f in model["files"]:
            for u in iter_file_units(f):
                total_segs += len(u.get("segments", []))
        trans = xliff_translated_segment_count(SAMPLES / "minimal.xliff")
        untrans = xliff_untranslated_segment_count(SAMPLES / "minimal.xliff")
        assert trans + untrans == total_segs


class TestInstalledWorkflow:
    def test_returns_dict(self):
        result = xliff_installed_workflow(SAMPLES / "minimal.xliff")
        assert isinstance(result, dict)

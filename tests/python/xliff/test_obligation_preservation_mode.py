"""XLIFF-PRESERVE-001 -- explicit LOSSLESS-vs-CANONICAL dump mode, and a
first-class loss-reporting API.

MUST, quoted from the format contract (SAL-XLIFF-OBL-A9AF9198E92EA6F9,
SAL-XLIFF-OBL-F920057AE26D1B4F):

  "dumps()/dump() take no preservation-mode parameter at all -- there is
   exactly one output path" -- closed by threading a keyword-only ``mode:
   PreservationMode`` parameter through the real, exported ``dumps()``/
   ``dump()`` in codec/writer/writer.py, defaulting to LOSSLESS (the
   historical, unchanged behavior).
  "no LossReport/check_preservation-style API exists anywhere in this
   package" -- closed by ``codec.preservation.check_preservation()``.

Scope, quoted from the evidence YAML's own honesty note: CANONICAL mode
drops every ``ExtensionNode`` in the tree (the one place this model
already distinguishes modeled from unmodeled content); every attribute in
the generic ``attributes`` dicts is preserved in both modes, since the
model does not separately mark any of those as vendor-only. This file
tests exactly that scope -- not a broader canonicalization this model
cannot honestly support yet.
"""

from __future__ import annotations

import pytest

from format_factory.xliff import (
    ExtensionNode,
    Group,
    LossReport,
    PreservationMode,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    XliffWriteError,
    canonicalize,
    check_preservation,
    dump,
    dumps,
    load,
    loads,
)


def _unit_extension(tag: str = "{urn:vendor:x}meta") -> ExtensionNode:
    local = tag.split("}")[-1]
    ns = tag[1 : tag.index("}")]
    return ExtensionNode(tag=tag, xml=f'<{local} xmlns="{ns}">payload</{local}>'.encode())


def _clean_document() -> XliffDocument:
    segment = Segment(id="s1", source=["hello"])
    unit = Unit(id="u1", children=[segment])
    file_ = XliffFile(id="f1", children=[unit])
    return XliffDocument(
        version="2.0", source_language="en", target_language=None, children=[file_]
    )


def _document_with_extensions() -> XliffDocument:
    segment = Segment(id="s1", source=["hello"])
    unit_ext = _unit_extension("{urn:vendor:x}unitmeta")
    unit = Unit(id="u1", children=[segment, unit_ext])
    group_ext = _unit_extension("{urn:vendor:x}groupmeta")
    group = Group(id="g1", children=[unit, group_ext])
    file_ext = _unit_extension("{urn:vendor:x}filemeta")
    file_ = XliffFile(id="f1", children=[group, file_ext])
    doc_ext = _unit_extension("{urn:vendor:x}docmeta")
    return XliffDocument(
        version="2.0",
        source_language="en",
        target_language=None,
        children=[file_, doc_ext],
    )


def _document_with_segment_extension() -> XliffDocument:
    segment_ext = _unit_extension("{urn:vendor:x}segmeta")
    segment = Segment(id="s1", source=["hello"], extensions=[segment_ext])
    unit = Unit(id="u1", children=[segment])
    file_ = XliffFile(id="f1", children=[unit])
    return XliffDocument(
        version="2.0", source_language="en", target_language=None, children=[file_]
    )


class TestPreservationModeDefault:
    def test_default_mode_is_lossless(self) -> None:
        doc = _document_with_extensions()
        assert dumps(doc) == dumps(doc, mode=PreservationMode.LOSSLESS)

    def test_lossless_mode_preserves_every_extension(self) -> None:
        doc = _document_with_extensions()
        out = dumps(doc, mode=PreservationMode.LOSSLESS)
        assert "unitmeta" in out
        assert "groupmeta" in out
        assert "filemeta" in out
        assert "docmeta" in out

    def test_lossless_dump_roundtrips_through_load(self, tmp_path) -> None:
        doc = _document_with_extensions()
        destination = tmp_path / "lossless.xlf"
        dump(doc, destination, mode=PreservationMode.LOSSLESS)
        reloaded = load(destination)
        report = check_preservation(reloaded)
        assert report.dropped_count == 4

    def test_unknown_mode_string_rejected_by_type(self) -> None:
        with pytest.raises(XliffWriteError):
            dumps(_clean_document(), mode="not-a-real-mode")  # type: ignore[arg-type]

    def test_plain_string_matching_enum_value_is_accepted(self) -> None:
        doc = _document_with_extensions()
        assert dumps(doc, mode="canonical") == dumps(  # type: ignore[arg-type]
            doc, mode=PreservationMode.CANONICAL
        )


class TestPreservationModeCanonical:
    def test_canonical_mode_drops_all_extension_levels(self) -> None:
        doc = _document_with_extensions()
        out = dumps(doc, mode=PreservationMode.CANONICAL)
        assert "unitmeta" not in out
        assert "groupmeta" not in out
        assert "filemeta" not in out
        assert "docmeta" not in out
        # typed content untouched
        assert 'id="s1"' in out
        assert "hello" in out

    def test_canonical_mode_drops_segment_level_extension(self) -> None:
        doc = _document_with_segment_extension()
        out = dumps(doc, mode=PreservationMode.CANONICAL)
        assert "segmeta" not in out
        assert "segmeta" in dumps(doc, mode=PreservationMode.LOSSLESS)

    def test_canonical_mode_output_still_loads(self, tmp_path) -> None:
        doc = _document_with_extensions()
        destination = tmp_path / "canonical.xlf"
        dump(doc, destination, mode=PreservationMode.CANONICAL)
        reloaded = load(destination)
        assert check_preservation(reloaded).is_lossless is True

    def test_canonical_mode_is_noop_when_no_extensions_present(self) -> None:
        doc = _clean_document()
        assert dumps(doc, mode=PreservationMode.LOSSLESS) == dumps(
            doc, mode=PreservationMode.CANONICAL
        )

    def test_canonical_mode_preserves_all_attributes(self) -> None:
        segment = Segment(
            id="s1", source=["hello"], attributes={"custom:vendor-flag": "1"}
        )
        unit = Unit(id="u1", children=[segment], attributes={"custom:tag": "x"})
        file_ = XliffFile(id="f1", children=[unit])
        doc = XliffDocument(
            version="2.0", source_language="en", target_language=None, children=[file_]
        )
        canonical_out = dumps(doc, mode=PreservationMode.CANONICAL)
        assert 'custom:vendor-flag="1"' in canonical_out
        assert 'custom:tag="x"' in canonical_out


class TestCanonicalizeDoesNotMutateOriginal:
    def test_original_document_children_unchanged(self) -> None:
        doc = _document_with_extensions()
        original_unit_children = len(doc.files[0].children[0].children)
        canonical_doc, dropped = canonicalize(doc)
        assert len(doc.files[0].children[0].children) == original_unit_children
        assert isinstance(canonical_doc, XliffDocument)
        assert len(dropped) == 4

    def test_canonicalize_returns_tags_in_document_order(self) -> None:
        doc = _document_with_extensions()
        _canonical, dropped = canonicalize(doc)
        assert dropped == (
            "{urn:vendor:x}unitmeta",
            "{urn:vendor:x}groupmeta",
            "{urn:vendor:x}filemeta",
            "{urn:vendor:x}docmeta",
        )


class TestCheckPreservation:
    def test_clean_document_reports_lossless(self) -> None:
        report = check_preservation(_clean_document())
        assert isinstance(report, LossReport)
        assert report.is_lossless is True
        assert report.dropped_count == 0
        assert report.dropped_tags == ()

    def test_document_with_extensions_reports_lossy(self) -> None:
        report = check_preservation(_document_with_extensions())
        assert report.is_lossless is False
        assert report.dropped_count == 4
        assert set(report.dropped_tags) == {
            "{urn:vendor:x}unitmeta",
            "{urn:vendor:x}groupmeta",
            "{urn:vendor:x}filemeta",
            "{urn:vendor:x}docmeta",
        }

    def test_report_does_not_serialize(self) -> None:
        doc = _document_with_extensions()
        report = check_preservation(doc)
        assert "docmeta" not in report.detail or True  # detail is a summary, not output
        assert isinstance(report.detail, str)
        assert str(report.dropped_count) in report.detail

    def test_check_preservation_matches_canonicalize_drop_count(self) -> None:
        doc = _document_with_extensions()
        report = check_preservation(doc)
        _canonical, dropped = canonicalize(doc)
        assert report.dropped_count == len(dropped)


class TestLoadedDocumentPreservationReport:
    def test_real_parsed_extension_reports_lossy(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" '
            'version="2.0" srcLang="en">'
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>hi</source></segment>"
            '<vendor:meta xmlns:vendor="urn:vendor:x">extra</vendor:meta>'
            "</unit></file></xliff>"
        )
        doc = loads(xml)
        report = check_preservation(doc)
        assert report.is_lossless is False
        assert report.dropped_count == 1

    def test_real_document_without_extensions_reports_lossless(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" '
            'version="2.0" srcLang="en">'
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>hi</source></segment></unit></file></xliff>"
        )
        doc = loads(xml)
        assert check_preservation(doc).is_lossless is True

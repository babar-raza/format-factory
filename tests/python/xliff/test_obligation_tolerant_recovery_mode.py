"""XLIFF-LIFECYCLE-001 -- a genuine tolerant/recovery read mode.

MUST, quoted from the format contract (SAL-XLIFF-OBL-0C477B7B6441FE75):

  "Support a strict read mode that rejects malformed input with
   diagnostics and a tolerant read mode that recovers where the format
   permits, with recovery actions reported."

Before this slice, ``mode="preservation"`` was accepted by loads()/load()
but had no distinct effect versus ``mode="strict"`` -- both raised
identically on every malformed input, and no ``recovery_actions`` field
existed anywhere to report what was recovered.

This file proves each of the four recoverable defect sites in the reader
now behaves differently under strict vs. preservation mode: strict still
refuses with the same pre-existing diagnostic message, preservation
recovers with a conservative default and records a human-readable action.
Genuinely unrecoverable defects (malformed XML syntax, a non-XLIFF root)
stay hard failures under both modes -- there is no tree to recover from,
matching the same discipline already applied to nrrd's own security-
sensitive raise sites.
"""

from __future__ import annotations

import pytest

from format_factory.xliff import XliffParseError, loads


def _wrap(body: str, *, version: str = "2.1", src_lang: str | None = "en") -> str:
    attrs = f'version="{version}"'
    if src_lang is not None:
        attrs += f' srcLang="{src_lang}"'
    return (
        f'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" {attrs}>'
        f"{body}</xliff>"
    )


class TestDuplicateSource:
    def test_strict_mode_refuses_duplicate_source(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source><source>b</source>"
            "</segment></unit></file>"
        )
        with pytest.raises(XliffParseError, match="duplicate source"):
            loads(xml, mode="strict")

    def test_preservation_mode_recovers_duplicate_source(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source><source>b</source>"
            "</segment></unit></file>"
        )
        doc = loads(xml, mode="preservation")
        segment = doc.files[0].children[0].children[0]
        assert segment.source == ["a"]
        assert len(doc.recovery_actions) == 1
        assert "duplicate <source>" in doc.recovery_actions[0]
        assert "s1" in doc.recovery_actions[0]


class TestDuplicateTarget:
    def test_strict_mode_refuses_duplicate_target(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source><target>x</target><target>y</target>"
            "</segment></unit></file>"
        )
        with pytest.raises(XliffParseError, match="duplicate target"):
            loads(xml, mode="strict")

    def test_preservation_mode_recovers_duplicate_target(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source><target>x</target><target>y</target>"
            "</segment></unit></file>"
        )
        doc = loads(xml, mode="preservation")
        segment = doc.files[0].children[0].children[0]
        assert segment.target == ["x"]
        assert len(doc.recovery_actions) == 1
        assert "duplicate <target>" in doc.recovery_actions[0]


class TestMissingSource:
    def test_strict_mode_refuses_missing_source(self) -> None:
        xml = _wrap('<file id="f1"><unit id="u1"><segment id="s1"/></unit></file>')
        with pytest.raises(XliffParseError, match="missing source"):
            loads(xml, mode="strict")

    def test_preservation_mode_recovers_missing_source(self) -> None:
        xml = _wrap('<file id="f1"><unit id="u1"><segment id="s1"/></unit></file>')
        doc = loads(xml, mode="preservation")
        segment = doc.files[0].children[0].children[0]
        assert segment.source == []
        assert len(doc.recovery_actions) == 1
        assert "missing required <source>" in doc.recovery_actions[0]

    def test_missing_source_recovers_inside_an_ignorable_too(self) -> None:
        xml = _wrap('<file id="f1"><unit id="u1"><ignorable id="i1"/></unit></file>')
        doc = loads(xml, mode="preservation")
        ignorable = doc.files[0].children[0].children[0]
        assert ignorable.source == []
        assert "ignorable" in doc.recovery_actions[0]


class TestInvalidNotePriority:
    def test_strict_mode_refuses_non_integer_priority(self) -> None:
        xml = _wrap(
            '<file id="f1"><notes><note id="n1" priority="abc">hi</note></notes>'
            '<unit id="u1"><segment id="s1"><source>a</source></segment></unit>'
            "</file>"
        )
        with pytest.raises(XliffParseError, match="priority must be an integer"):
            loads(xml, mode="strict")

    def test_preservation_mode_recovers_non_integer_priority(self) -> None:
        xml = _wrap(
            '<file id="f1"><notes><note id="n1" priority="abc">hi</note></notes>'
            '<unit id="u1"><segment id="s1"><source>a</source></segment></unit>'
            "</file>"
        )
        doc = loads(xml, mode="preservation")
        note = doc.files[0].notes[0]
        assert note.priority is None
        assert len(doc.recovery_actions) == 1
        assert "non-integer priority" in doc.recovery_actions[0]
        assert "n1" in doc.recovery_actions[0]


class TestMissingSrcLang:
    def test_strict_mode_refuses_missing_src_lang(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source></segment></unit></file>",
            src_lang=None,
        )
        with pytest.raises(XliffParseError, match="missing srcLang"):
            loads(xml, mode="strict")

    def test_preservation_mode_recovers_missing_src_lang(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source></segment></unit></file>",
            src_lang=None,
        )
        doc = loads(xml, mode="preservation")
        assert doc.source_language == ""
        assert "missing srcLang" in doc.recovery_actions[0]


class TestUnsupportedVersion:
    def test_strict_mode_refuses_unsupported_version(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source></segment></unit></file>",
            version="9.9",
        )
        with pytest.raises(XliffParseError, match="stable profile supports"):
            loads(xml, mode="strict")

    def test_preservation_mode_recovers_unsupported_version(self) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source></segment></unit></file>",
            version="9.9",
        )
        doc = loads(xml, mode="preservation")
        assert doc.version == "9.9"
        assert "unsupported version" in doc.recovery_actions[0]


class TestMultipleRecoveriesAccumulate:
    def test_several_independent_defects_all_recover_in_one_pass(self) -> None:
        xml = _wrap(
            '<file id="f1"><notes><note id="n1" priority="x">hi</note></notes>'
            '<unit id="u1">'
            '<segment id="s1"><source>a</source><source>b</source></segment>'
            '<segment id="s2"/>'
            "</unit></file>",
            src_lang=None,
        )
        doc = loads(xml, mode="preservation")
        assert len(doc.recovery_actions) == 4
        joined = " | ".join(doc.recovery_actions)
        assert "missing srcLang" in joined
        assert "non-integer priority" in joined
        assert "duplicate <source>" in joined
        assert "missing required <source>" in joined


class TestUnrecoverableDefectsStayHardFailuresInBothModes:
    def test_malformed_xml_syntax_is_never_recoverable(self) -> None:
        xml = "<xliff><unclosed>"
        with pytest.raises(XliffParseError, match="invalid XML"):
            loads(xml, mode="strict")
        with pytest.raises(XliffParseError, match="invalid XML"):
            loads(xml, mode="preservation")

    def test_non_xliff_root_is_never_recoverable(self) -> None:
        xml = "<not-xliff/>"
        with pytest.raises(XliffParseError, match="not an XLIFF"):
            loads(xml, mode="strict")
        with pytest.raises(XliffParseError, match="not an XLIFF"):
            loads(xml, mode="preservation")


class TestCleanDocumentUnaffected:
    def test_a_well_formed_document_has_no_recovery_actions_under_either_mode(
        self,
    ) -> None:
        xml = _wrap(
            '<file id="f1"><unit id="u1"><segment id="s1">'
            "<source>a</source></segment></unit></file>"
        )
        strict_doc = loads(xml, mode="strict")
        preservation_doc = loads(xml, mode="preservation")
        assert strict_doc.recovery_actions == []
        assert preservation_doc.recovery_actions == []

    def test_a_document_built_directly_in_memory_has_no_recovery_actions(self) -> None:
        from format_factory.xliff import Segment, Unit, XliffDocument, XliffFile

        segment = Segment(id="s1", source=["hello"])
        unit = Unit(id="u1", children=[segment])
        file_ = XliffFile(id="f1", children=[unit])
        doc = XliffDocument(
            version="2.1", source_language="en", target_language=None, children=[file_]
        )
        assert doc.recovery_actions == []

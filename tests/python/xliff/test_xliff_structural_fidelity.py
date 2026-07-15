"""Tests for the 2026-07-15 real-defect fixes to the xliff codec:

  - FACT-XLIFF-101: structural inline markup (pc/sc/ec/ph/mrk) preservation
    (`xliff.xliff_inline.InlineElement`, `parse_inline_content`,
    `serialize_inline_content`) replacing the prior flatten-to-plain-text
    behavior that destroyed placeholder boundaries on every round trip.
  - FACT-XLIFF-102: `segment/@state` write-back (previously read but
    silently dropped by `write_xliff`).
  - FACT-XLIFF-103: notes/note preservation (file/group/unit).
  - FACT-XLIFF-104: group element hierarchy preservation (id, notes, nested
    groups/units) instead of a blind ``.//unit`` findall that hoisted
    grouped units into the file's flat unit list.

L2 (behavior) classes: TestInlineElementModel, TestInlineMarkupRoundtrip,
TestStateWriteBack, TestNotesPreservation, TestGroupHierarchy.
L3 (edge/boundary) class: TestStructuralEdgeCases.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from xliff.models import XliffDocument
from xliff.xliff_codec import get_unit_count, iter_file_units, load_xliff, write_xliff
from xliff.xliff_inline import (
    InlineElement,
    flatten_inline_content,
    parse_inline_content,
    serialize_inline_content,
)

import xml.etree.ElementTree as ET

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"
VALID_DIR = SAMPLES / "valid"

NS = "urn:oasis:names:tc:xliff:document:2.0"


def _xliff_bytes(file_inner_xml: str) -> bytes:
    """Wrap raw XLIFF 2.0 <file> inner XML in a minimal document envelope."""
    return (
        '<?xml version="1.0"?>'
        f'<xliff xmlns="{NS}" version="2.0" srcLang="en" trgLang="de">'
        f"{file_inner_xml}"
        "</xliff>"
    ).encode("utf-8")


class TestInlineElementModel:
    """Direct unit tests for the InlineElement class and parse/serialize functions."""

    def test_inline_element_basic_fields(self):
        elem = InlineElement(tag="pc", attributes={"id": "pc1"}, content=["here"], tail=" world")
        assert elem.tag == "pc"
        assert elem.id == "pc1"
        assert elem.content == ["here"]
        assert elem.tail == " world"

    def test_inline_element_data_ref_prefers_dataRef(self):
        elem = InlineElement(tag="ph", attributes={"id": "1", "dataRef": "d1"})
        assert elem.data_ref == "d1"

    def test_inline_element_data_ref_falls_back_to_dataRefStart(self):
        elem = InlineElement(tag="pc", attributes={"id": "1", "dataRefStart": "d1", "dataRefEnd": "d2"})
        assert elem.data_ref == "d1"

    def test_inline_element_data_ref_none_when_absent(self):
        elem = InlineElement(tag="mrk", attributes={"id": "m1"})
        assert elem.data_ref is None

    def test_inline_element_plain_text_flattens_nested_content(self):
        inner = InlineElement(tag="ph", attributes={"id": "ph1"}, content=[], tail="")
        outer = InlineElement(tag="pc", attributes={"id": "pc1"}, content=["before ", inner, " after"])
        assert outer.plain_text() == "before  after"

    def test_inline_element_to_dict_and_from_dict_roundtrip(self):
        original = InlineElement(
            tag="pc",
            attributes={"id": "pc1", "dataRefStart": "d1"},
            content=["hello ", InlineElement(tag="ph", attributes={"id": "ph1", "dataRef": "d2"})],
            tail=" tail-text",
        )
        as_dict = original.to_dict()
        restored = InlineElement.from_dict(as_dict)
        assert restored == original
        assert restored.tail == " tail-text"
        assert restored.content[1].id == "ph1"

    def test_inline_element_equality(self):
        a = InlineElement(tag="ph", attributes={"id": "1"})
        b = InlineElement(tag="ph", attributes={"id": "1"})
        c = InlineElement(tag="ph", attributes={"id": "2"})
        assert a == b
        assert a != c
        assert a != "not an InlineElement"

    def test_inline_element_repr_contains_tag_and_id(self):
        elem = InlineElement(tag="mrk", attributes={"id": "m1"})
        r = repr(elem)
        assert "mrk" in r
        assert "m1" in r

    def test_flatten_inline_content_empty_list(self):
        assert flatten_inline_content([]) == ""


class TestInlineMarkupRoundtrip:
    """Integration tests: real XML -> parse_inline_content -> serialize_inline_content -> real XML."""

    def test_with_inline_codes_sample_pc_survives_full_roundtrip(self):
        """load -> write -> reload the real with-inline-codes.xliff sample:
        the <pc id="pc1"> element must still be present as structured data,
        not flattened away, after a full round trip."""
        model = load_xliff(VALID_DIR / "with-inline-codes.xliff")
        seg = model["files"][0]["units"][0]["segments"][0]
        assert seg["source"] == "Click here to continue"
        assert seg["target"] == "Klicken Sie hier um fortzufahren"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "roundtrip.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)

        reseg = reloaded["files"][0]["units"][0]["segments"][0]
        assert reseg["source"] == "Click here to continue"
        assert reseg["target"] == "Klicken Sie hier um fortzufahren"

        source_pc = [n for n in reseg["source_content"] if isinstance(n, dict)]
        target_pc = [n for n in reseg["target_content"] if isinstance(n, dict)]
        assert len(source_pc) == 1
        assert len(target_pc) == 1
        assert source_pc[0]["tag"] == "pc"
        assert source_pc[0]["attributes"]["id"] == "pc1"
        assert source_pc[0]["content"] == ["here"]
        assert target_pc[0]["tag"] == "pc"
        assert target_pc[0]["attributes"]["id"] == "pc1"
        assert target_pc[0]["content"] == ["hier"]

    def test_synthetic_sc_ec_ph_mrk_roundtrip(self):
        """Construct a synthetic XLIFF exercising sc/ec/ph/mrk (not just pc)
        and prove each inline element type + its id/dataRef survives a
        parse -> serialize -> reparse round trip."""
        xml = _xliff_bytes(
            '<file id="f1"><unit id="u1"><segment>'
            '<source>Start <sc id="s1" dataRef="d1"/>bold text'
            '<ec startRef="s1"/> end. <ph id="p1" dataRef="d2"/> '
            '<mrk id="m1" type="term">glossary term</mrk> done.</source>'
            "<target>Zielsprache</target>"
            "</segment></unit></file>"
        )
        model = load_xliff(xml)
        seg = model["files"][0]["units"][0]["segments"][0]
        nodes = [n for n in seg["source_content"] if isinstance(n, dict)]
        tags = [n["tag"] for n in nodes]
        assert tags == ["sc", "ec", "ph", "mrk"]

        sc_node, ec_node, ph_node, mrk_node = nodes
        assert sc_node["attributes"]["id"] == "s1"
        assert sc_node["attributes"]["dataRef"] == "d1"
        assert sc_node["tail"] == "bold text"
        assert ec_node["attributes"]["startRef"] == "s1"
        assert ec_node["tail"] == " end. "
        assert ph_node["attributes"]["id"] == "p1"
        assert ph_node["attributes"]["dataRef"] == "d2"
        assert mrk_node["attributes"]["id"] == "m1"
        assert mrk_node["attributes"]["type"] == "term"
        assert mrk_node["content"] == ["glossary term"]

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "synthetic.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)

        reseg = reloaded["files"][0]["units"][0]["segments"][0]
        renotes = [n for n in reseg["source_content"] if isinstance(n, dict)]
        assert [n["tag"] for n in renotes] == ["sc", "ec", "ph", "mrk"]
        assert renotes[0]["attributes"]["dataRef"] == "d1"
        assert renotes[1]["attributes"]["startRef"] == "s1"
        assert renotes[2]["attributes"]["dataRef"] == "d2"
        assert renotes[3]["content"] == ["glossary term"]
        assert reseg["source"] == seg["source"]

    def test_parse_inline_content_direct_on_element_tree(self):
        """Unit-level (not full-document) test of parse_inline_content against
        a hand-built ElementTree element."""
        xml = f'<source xmlns="{NS}">Click <pc id="pc1">here</pc> now</source>'
        elem = ET.fromstring(xml)
        nodes = parse_inline_content(elem)
        assert nodes[0] == "Click "
        assert isinstance(nodes[1], InlineElement)
        assert nodes[1].tag == "pc"
        assert nodes[1].id == "pc1"
        assert nodes[1].content == ["here"]
        assert nodes[1].tail == " now"

    def test_serialize_inline_content_direct_produces_expected_xml(self):
        """Unit-level test of serialize_inline_content building an element
        from a hand-built structured content list (inverse direction)."""
        nodes = [
            "Click ",
            InlineElement(tag="pc", attributes={"id": "pc1"}, content=["here"], tail=" now"),
        ]
        parent = ET.Element(f"{{{NS}}}source")
        serialize_inline_content(parent, nodes, NS)
        assert parent.text == "Click "
        assert len(parent) == 1
        assert parent[0].get("id") == "pc1"
        assert parent[0].text == "here"
        assert parent[0].tail == " now"

    def test_plain_source_without_inline_codes_still_flat_string(self):
        """Segments with no inline markup keep behaving exactly as before:
        `source`/`target` are the plain string, `source_content`/
        `target_content` are a single-text-node structured list."""
        model = load_xliff(VALID_DIR / "minimal.xliff")
        seg = model["files"][0]["units"][0]["segments"][0]
        assert seg["source"] == "Hello"
        assert seg["source_content"] == ["Hello"]


class TestStateWriteBack:
    """FACT-XLIFF-102: segment/@state must be written back, not dropped."""

    def test_state_translated_survives_roundtrip(self):
        xml = _xliff_bytes(
            '<file id="f1"><unit id="u1">'
            '<segment state="translated"><source>Hi</source><target>Salut</target></segment>'
            "</unit></file>"
        )
        model = load_xliff(xml)
        assert model["files"][0]["units"][0]["segments"][0]["state"] == "translated"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "state.xliff"
            write_xliff(model, dest)
            content = dest.read_text(encoding="utf-8")
            assert 'state="translated"' in content
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["units"][0]["segments"][0]["state"] == "translated"

    def test_state_mutated_to_reviewed_is_written(self):
        xml = _xliff_bytes(
            '<file id="f1"><unit id="u1">'
            '<segment state="translated"><source>Hi</source><target>Salut</target></segment>'
            "</unit></file>"
        )
        model = load_xliff(xml)
        model["files"][0]["units"][0]["segments"][0]["state"] = "reviewed"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "state_mutated.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["units"][0]["segments"][0]["state"] == "reviewed"

    def test_state_absent_is_not_synthesized(self):
        """A segment with no @state attribute should not gain a spurious
        state="" attribute in the written output."""
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert model["files"][0]["units"][0]["segments"][0]["state"] == ""

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "no_state.xliff"
            write_xliff(model, dest)
            content = dest.read_text(encoding="utf-8")
            assert "state=" not in content


class TestNotesPreservation:
    """FACT-XLIFF-103: notes/note elements on file/group/unit must survive."""

    def test_unit_note_preserved_on_roundtrip(self):
        xml = _xliff_bytes(
            '<file id="f1"><unit id="u1">'
            '<notes><note id="n1" category="general">Check this term</note></notes>'
            "<segment><source>Hi</source><target>Salut</target></segment>"
            "</unit></file>"
        )
        model = load_xliff(xml)
        notes = model["files"][0]["units"][0]["notes"]
        assert len(notes) == 1
        assert notes[0]["id"] == "n1"
        assert notes[0]["category"] == "general"
        assert notes[0]["text"] == "Check this term"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "notes.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            renotes = reloaded["files"][0]["units"][0]["notes"]
            assert renotes == notes

    def test_file_note_preserved(self):
        xml = _xliff_bytes(
            '<file id="f1"><notes><note id="fn1">File-level note</note></notes>'
            '<unit id="u1"><segment><source>Hi</source></segment></unit></file>'
        )
        model = load_xliff(xml)
        assert model["files"][0]["notes"][0]["text"] == "File-level note"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "file_notes.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
            assert reloaded["files"][0]["notes"][0]["text"] == "File-level note"

    def test_no_notes_element_when_absent(self):
        model = load_xliff(VALID_DIR / "minimal.xliff")
        assert model["files"][0]["units"][0]["notes"] == []
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "no_notes.xliff"
            write_xliff(model, dest)
            content = dest.read_text(encoding="utf-8")
            assert "<notes>" not in content


class TestGroupHierarchy:
    """FACT-XLIFF-104: group element wrappers must be preserved, not flattened."""

    def test_group_with_two_units_and_note_preserved(self):
        xml = _xliff_bytes(
            '<file id="f1">'
            '<group id="g1"><notes><note id="gn1">Group note</note></notes>'
            '<unit id="u1"><segment><source>One</source><target>Un</target></segment></unit>'
            '<unit id="u2"><segment><source>Two</source><target>Deux</target></segment></unit>'
            "</group>"
            "</file>"
        )
        model = load_xliff(xml)
        file_data = model["files"][0]

        # NOT flattened into the file's top-level unit list.
        assert file_data["units"] == []
        assert len(file_data["groups"]) == 1

        group = file_data["groups"][0]
        assert group["id"] == "g1"
        assert group["notes"][0]["text"] == "Group note"
        assert len(group["units"]) == 2
        assert group["units"][0]["id"] == "u1"
        assert group["units"][1]["id"] == "u2"
        assert group["units"][0]["segments"][0]["source"] == "One"
        assert group["units"][1]["segments"][0]["source"] == "Two"

        # get_unit_count / iter_file_units still see grouped units.
        assert get_unit_count(model) == 2
        assert [u["id"] for u in iter_file_units(file_data)] == ["u1", "u2"]

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "group.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)

        rfile = reloaded["files"][0]
        assert rfile["units"] == []
        assert len(rfile["groups"]) == 1
        rgroup = rfile["groups"][0]
        assert rgroup["id"] == "g1"
        assert rgroup["notes"][0]["text"] == "Group note"
        assert len(rgroup["units"]) == 2
        assert rgroup["units"][0]["segments"][0]["target"] == "Un"
        assert rgroup["units"][1]["segments"][0]["target"] == "Deux"
        assert get_unit_count(reloaded) == 2

    def test_nested_groups_preserved(self):
        xml = _xliff_bytes(
            '<file id="f1">'
            '<group id="outer">'
            '<group id="inner"><unit id="u1"><segment><source>Deep</source></segment></unit></group>'
            "</group>"
            "</file>"
        )
        model = load_xliff(xml)
        outer = model["files"][0]["groups"][0]
        assert outer["id"] == "outer"
        assert len(outer["groups"]) == 1
        inner = outer["groups"][0]
        assert inner["id"] == "inner"
        assert inner["units"][0]["segments"][0]["source"] == "Deep"
        assert get_unit_count(model) == 1

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "nested.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)
        reloaded_outer = reloaded["files"][0]["groups"][0]
        assert reloaded_outer["groups"][0]["id"] == "inner"
        assert reloaded_outer["groups"][0]["units"][0]["segments"][0]["source"] == "Deep"

    def test_file_with_groups_and_top_level_units_both_counted(self):
        xml = _xliff_bytes(
            '<file id="f1">'
            '<unit id="top1"><segment><source>Top</source></segment></unit>'
            '<group id="g1"><unit id="u1"><segment><source>Grouped</source></segment></unit></group>'
            "</file>"
        )
        model = load_xliff(xml)
        file_data = model["files"][0]
        assert len(file_data["units"]) == 1
        assert file_data["units"][0]["id"] == "top1"
        assert get_unit_count(model) == 2

    def test_xliff_document_units_property_includes_grouped_units(self):
        xml = _xliff_bytes(
            '<file id="f1">'
            '<group id="g1">'
            '<unit id="u1"><segment><source>One</source></segment></unit>'
            '<unit id="u2"><segment><source>Two</source></segment></unit>'
            "</group></file>"
        )
        doc = XliffDocument(load_xliff(xml))
        assert doc.unit_count == 2
        assert [u["id"] for u in doc.units] == ["u1", "u2"]


class TestStructuralEdgeCases:
    def test_empty_group_no_units_no_notes(self):
        xml = _xliff_bytes('<file id="f1"><group id="empty"/></file>')
        model = load_xliff(xml)
        group = model["files"][0]["groups"][0]
        assert group["id"] == "empty"
        assert group["units"] == []
        assert group["notes"] == []
        assert get_unit_count(model) == 0

    def test_mutating_plain_target_after_load_discards_stale_structure(self):
        """A caller that mutates the plain `target` string directly (the
        existing, supported convenience — see test_xliff_mutation.py) gets
        exactly that new plain text written back, even for a segment that
        originally had inline markup — no corruption from stale structure."""
        model = load_xliff(VALID_DIR / "with-inline-codes.xliff")
        model["files"][0]["units"][0]["segments"][0]["target"] = "Plain replacement"

        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated_inline.xliff"
            write_xliff(model, dest)
            reloaded = load_xliff(dest)

        seg = reloaded["files"][0]["units"][0]["segments"][0]
        assert seg["target"] == "Plain replacement"
        # No stray <pc> survives in the mutated field.
        assert all(isinstance(n, str) for n in seg["target_content"])

    def test_from_dict_missing_content_key_defaults_empty(self):
        elem = InlineElement.from_dict({"tag": "ph", "attributes": {"id": "1"}})
        assert elem.content == []
        assert elem.tail == ""

    def test_pc_with_no_id_attribute(self):
        xml = _xliff_bytes(
            '<file id="f1"><unit id="u1"><segment><source>'
            "<pc>no id here</pc></source></segment></unit></file>"
        )
        model = load_xliff(xml)
        seg = model["files"][0]["units"][0]["segments"][0]
        node = seg["source_content"][0]
        assert node["tag"] == "pc"
        assert node["attributes"] == {}
        assert seg["source"] == "no id here"

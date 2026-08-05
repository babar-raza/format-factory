"""XLIFF-NOTE-001 against the shipped namespace.

SAL-XLIFF-00014, -00015, -00027 (MUST): note groups, priorities, categories,
and annotation spans -- including overlapping start/end markers -- are
represented and survive edits.

Written directly against format_factory.xliff, not ported from the shadow
xliff.* package that dominates this test directory (GAP-018).
"""

from __future__ import annotations

from format_factory.xliff import Group, InlineElement, Note, Unit, dumps, loads

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"
HEADER = f'<?xml version="1.0" encoding="UTF-8"?>\n<xliff xmlns="{XLIFF_NS}" version="2.0" srcLang="en">\n'
FOOTER = "</xliff>\n"


# ── Notes: priority, category, appliesTo ────────────────────────────────────


def test_note_priority_and_category_are_represented() -> None:
    """"notes elements carry note children with optional priority and
    category attributes." """
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1">'
        + '<notes><note id="n1" priority="2" category="general">Translator note</note></notes>'
        + "<segment><source>hi</source></segment>"
        + "</unit></file>"
        + FOOTER
    )
    document = loads(xml)
    unit = document.files[0].children[0]

    assert unit.notes == [
        Note(text="Translator note", id="n1", category="general", priority=2)
    ]


def test_note_applies_to_is_represented() -> None:
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1">'
        + '<notes><note id="n1" appliesTo="target">target-only note</note></notes>'
        + "<segment><source>hi</source></segment>"
        + "</unit></file>"
        + FOOTER
    )
    document = loads(xml)
    unit = document.files[0].children[0]

    assert unit.notes[0].applies_to == "target"


def test_multiple_notes_on_one_unit_all_survive() -> None:
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1">'
        + "<notes>"
        + '<note id="n1" priority="1">first</note>'
        + '<note id="n2" priority="5">second</note>'
        + '<note id="n3">third</note>'
        + "</notes>"
        + "<segment><source>hi</source></segment>"
        + "</unit></file>"
        + FOOTER
    )
    document = loads(xml)
    unit = document.files[0].children[0]

    assert [note.text for note in unit.notes] == ["first", "second", "third"]
    assert [note.priority for note in unit.notes] == [1, 5, None]


# ── Notes attach at file, group, and unit level ─────────────────────────────


def test_notes_attach_at_file_group_and_unit_level() -> None:
    """"attached to files groups or units" -- not unit-only."""
    xml = (
        HEADER
        + '<file id="f1">'
        + '<notes><note id="fn1">file note</note></notes>'
        + '<group id="g1">'
        + '<notes><note id="gn1">group note</note></notes>'
        + '<unit id="u1">'
        + '<notes><note id="un1">unit note</note></notes>'
        + "<segment><source>hi</source></segment>"
        + "</unit>"
        + "</group>"
        + "</file>"
        + FOOTER
    )
    document = loads(xml)
    file = document.files[0]
    group = next(child for child in file.children if isinstance(child, Group))
    unit = next(child for child in group.children if isinstance(child, Unit))

    assert file.notes[0].text == "file note"
    assert group.notes[0].text == "group note"
    assert unit.notes[0].text == "unit note"


def test_notes_at_every_level_round_trip() -> None:
    xml = (
        HEADER
        + '<file id="f1">'
        + '<notes><note id="fn1" priority="3">file note</note></notes>'
        + '<group id="g1">'
        + '<notes><note id="gn1" category="qa">group note</note></notes>'
        + '<unit id="u1">'
        + '<notes><note id="un1" appliesTo="source">unit note</note></notes>'
        + "<segment><source>hi</source></segment>"
        + "</unit>"
        + "</group>"
        + "</file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    file = reparsed.files[0]
    group = next(child for child in file.children if isinstance(child, Group))
    unit = next(child for child in group.children if isinstance(child, Unit))
    assert file.notes[0] == Note(text="file note", id="fn1", priority=3)
    assert group.notes[0] == Note(text="group note", id="gn1", category="qa")
    assert unit.notes[0] == Note(text="unit note", id="un1", applies_to="source")


# ── Annotation spans: mrk (wrapping) ─────────────────────────────────────────


def test_mrk_annotation_wraps_a_span() -> None:
    """"mrk elements annotate inline spans." """
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1"><segment>'
        + '<source>The <mrk id="m1" type="comment" ref="#n1">quick fox</mrk> jumps</source>'
        + "</segment></unit></file>"
        + FOOTER
    )
    document = loads(xml)
    segment = document.files[0].children[0].segments[0]

    mrk = next(node for node in segment.source if isinstance(node, InlineElement))
    assert mrk.tag == "mrk"
    assert mrk.attributes["type"] == "comment"
    assert mrk.attributes["ref"] == "#n1"
    assert mrk.plain_text() == "quick fox"


def test_mrk_annotation_round_trips() -> None:
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1"><segment>'
        + '<source>The <mrk id="m1" type="term">quick fox</mrk> jumps</source>'
        + "</segment></unit></file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    segment = reparsed.files[0].children[0].segments[0]
    mrk = next(node for node in segment.source if isinstance(node, InlineElement))
    assert mrk.tag == "mrk"
    assert mrk.attributes["id"] == "m1"
    assert mrk.attributes["type"] == "term"
    assert mrk.plain_text() == "quick fox"


# ── Annotation spans: sm/em (overlapping, non-nesting) ──────────────────────


def test_overlapping_span_uses_sm_and_em_markers_not_nesting() -> None:
    """"sm/em elements mark span boundaries where spans overlap element
    structure." An overlapping annotation cannot be a properly nested XML
    element pair -- sm marks the start point and em marks the corresponding
    end point via a ref/id pairing, both self-closing markers in a flat
    sequence rather than a wrapper."""
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1"><segment>'
        + '<source>The <sm id="s1" type="comment"/>quick brown fox<em startRef="s1"/> jumps</source>'
        + "</segment></unit></file>"
        + FOOTER
    )
    document = loads(xml)
    segment = document.files[0].children[0].segments[0]

    markers = [node for node in segment.source if isinstance(node, InlineElement)]
    assert [marker.tag for marker in markers] == ["sm", "em"]
    sm, em = markers
    assert sm.attributes["id"] == "s1"
    assert em.attributes["startRef"] == "s1"
    # Both are markers, not wrappers: neither owns the annotated text as
    # nested content -- the text lives in each marker's `tail`, in sequence.
    assert sm.content == []
    assert em.content == []


def test_sm_em_span_survives_overlap_with_another_inline_element() -> None:
    """The defining case for sm/em: an annotation whose boundary falls
    inside another inline element's span, which a properly nested mrk could
    not represent without splitting that element."""
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1"><segment>'
        + '<source>a <sm id="s1"/>b <pc id="c1">c d</pc> e<em startRef="s1"/> f</source>'
        + "</segment></unit></file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        segment = parsed.files[0].children[0].segments[0]
        tags_in_order = [
            node.tag for node in segment.source if isinstance(node, InlineElement)
        ]
        assert tags_in_order == ["sm", "pc", "em"]
        sm = next(node for node in segment.source if isinstance(node, InlineElement) and node.tag == "sm")
        em = next(node for node in segment.source if isinstance(node, InlineElement) and node.tag == "em")
        assert em.attributes["startRef"] == sm.attributes["id"]


def test_sm_em_round_trips_with_document_order_preserved() -> None:
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1"><segment>'
        + '<source>The <sm id="s1"/>quick brown fox<em startRef="s1"/> jumps</source>'
        + "</segment></unit></file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        segment = parsed.files[0].children[0].segments[0]
        rendered = "".join(
            node if isinstance(node, str) else (node.plain_text() + node.tail)
            for node in segment.source
        )
        assert rendered == "The quick brown fox jumps"


# ── Edits: annotations survive after a target is created from source ───────


def test_annotation_spans_survive_target_creation_from_source() -> None:
    """"...are represented and survive edits." """
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1"><segment>'
        + '<source>The <mrk id="m1" type="term">fox</mrk> jumps</source>'
        + "</segment></unit></file>"
        + FOOTER
    )
    document = loads(xml)
    segment = document.files[0].children[0].segments[0]

    segment.create_target_from_source(code_policy="copy")

    target_mrk = next(node for node in segment.target if isinstance(node, InlineElement))
    assert target_mrk.tag == "mrk"
    assert target_mrk.attributes["id"] == "m1"
    assert target_mrk.plain_text() == "fox"
    # Source and target must not share the same mutable node.
    source_mrk = next(node for node in segment.source if isinstance(node, InlineElement))
    assert target_mrk is not source_mrk

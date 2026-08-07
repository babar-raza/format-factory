"""XLIFF-MODEL-001 / XLIFF-PARSE-001 / XLIFF-VALIDATE-001 / XLIFF-INLINE-001
-- mrk's own ref attribute resolution (the last remaining "references must
resolve" gap after ec/sc pairing and dataRef were closed).

MUST (SAL-XLIFF-OBL-441E7C6F7C341B12 and cross-capability duplicates):
"(XLIFF core - identifier constraints) id attributes on file group unit
and inline elements must be unique within their specification-defined
scope and references must resolve."

Before this slice: no code path anywhere in validator.py or model/inline.py
read or resolved mrk's own ref attribute at all -- confirmed directly by
reading _validate_inline and _data_ref_diagnostics before writing anything.

Grounded directly in the pinned XLIFF 2.1 spec's own prose
(.local/format-contracts/acquired/xliff/src-xliff-001.bin, section
4.7.3.1.3 Comment Annotation): "The ref attribute MUST be present and
contain the URI of a <note> element within the same enclosing <unit>
element that holds the comment," with the spec's own worked example using
the fragment form ref="#n=n1" against a sibling <note id="n1">.

Deliberately narrow, matching this obligation's own established scope
discipline: only mrk[type="comment"] is checked. The spec's other
documented ref usage (type="term", e.g. ref="http://dbpedia.org/page/...")
points at an arbitrary external URI with no same-document resolution
requirement at all, and is correctly left unchecked -- checking it would
mean inventing a constraint the spec never states.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Note, Segment, Unit, XliffDocument, XliffFile, validate


def _document(notes: list[Note], source: list[object]) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(id="u", notes=notes, children=[Segment(id="s", source=source)])
                ],
            )
        ],
    )


def test_a_comment_ref_that_resolves_to_a_note_in_the_same_unit_is_not_flagged() -> None:
    document = _document(
        [Note(id="n1", text="check this")],
        [InlineElement("mrk", {"id": "m1", "type": "comment", "ref": "#n=n1"}, content=["x"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.mrk.comment.ref.unresolved" not in codes


def test_a_comment_ref_that_does_not_match_any_note_id_is_a_violation() -> None:
    document = _document(
        [Note(id="n1", text="check this")],
        [InlineElement("mrk", {"id": "m1", "type": "comment", "ref": "#n=nX"}, content=["x"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.mrk.comment.ref.unresolved" in codes


def test_a_comment_ref_with_no_notes_in_the_unit_at_all_is_a_violation() -> None:
    document = _document(
        [],
        [InlineElement("mrk", {"id": "m1", "type": "comment", "ref": "#n=n1"}, content=["x"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.mrk.comment.ref.unresolved" in codes


def test_a_term_type_mrk_with_an_external_uri_ref_is_never_checked() -> None:
    """type="term" ref values are arbitrary external URIs (the spec's own
    example points at a DBpedia page) -- no same-document resolution is
    required, and this check must not invent one."""
    document = _document(
        [],
        [
            InlineElement(
                "mrk",
                {"id": "m1", "type": "term", "ref": "http://dbpedia.org/page/Example"},
                content=["x"],
            )
        ],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.mrk.comment.ref.unresolved" not in codes


def test_a_comment_type_mrk_with_no_ref_attribute_at_all_is_not_checked_here() -> None:
    """Presence of ref on a comment annotation is a separate concern from
    this obligation's own "references must resolve" scope; this check only
    fires when a ref value is present but does not resolve."""
    document = _document(
        [],
        [InlineElement("mrk", {"id": "m1", "type": "comment"}, content=["x"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.mrk.comment.ref.unresolved" not in codes


def test_a_comment_ref_is_checked_independently_in_target_content() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language="fr",
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(
                        id="u",
                        notes=[Note(id="n1", text="check this")],
                        children=[
                            Segment(
                                id="s",
                                source=["hi"],
                                target=[
                                    InlineElement(
                                        "mrk",
                                        {"id": "m1", "type": "comment", "ref": "#n=nX"},
                                        content=["x"],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.mrk.comment.ref.unresolved" in codes

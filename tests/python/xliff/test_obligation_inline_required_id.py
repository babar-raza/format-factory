"""XLIFF-INLINE-001 / XLIFF-PARSE-001 -- inline code required id.

MUST (SAL-XLIFF-OBL-378A1E5A93B9F0E1 / SAL-XLIFF-OBL-3A70AA27631A594D,
identical rule_text): "(XLIFF core - inline elements) Standalone
placeholders use ph with a required id; paired containers use pc with a
required id; spanning pairs use sc with a required id and non-isolated ec
with a startRef to that id."

Before this slice: _validate_inline already checked duplicate ids and
ec/sc pairing, but nothing checked that ph/pc/sc actually carry an id at
all -- confirmed directly by reading the function before writing any test.
ec is deliberately excluded from this new check: it identifies its pairing
via startRef, not its own id, and the spec text does not require one on ec
itself (only that its startRef resolve, already covered by the separate
xliff.inline.ec.unpaired check).
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, Unit, XliffDocument, XliffFile, validate


def _document(source: list[object]) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[Unit(id="u", children=[Segment(id="s", source=source)])],
            )
        ],
    )


def test_a_ph_without_an_id_is_flagged() -> None:
    document = _document([InlineElement("ph", {}), "text"])

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "xliff.inline.id.required" for item in report.diagnostics)


def test_a_ph_with_an_id_is_not_flagged() -> None:
    document = _document([InlineElement("ph", {"id": "p1"}), "text"])

    report = validate(document)

    assert "xliff.inline.id.required" not in {item.code for item in report.diagnostics}


def test_a_pc_without_an_id_is_flagged() -> None:
    document = _document([InlineElement("pc", {}, content=["text"])])

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "xliff.inline.id.required" for item in report.diagnostics)


def test_an_sc_without_an_id_is_flagged() -> None:
    document = _document([InlineElement("sc", {"isolated": "yes"}), "text"])

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "xliff.inline.id.required" for item in report.diagnostics)


def test_an_ec_without_an_id_is_not_flagged_for_missing_id() -> None:
    """ec has no id requirement of its own -- only startRef, which the
    separate ec/sc pairing check already covers."""
    document = _document(
        [InlineElement("sc", {"id": "c1"}), "text", InlineElement("ec", {"startRef": "c1"})]
    )

    report = validate(document)

    assert "xliff.inline.id.required" not in {item.code for item in report.diagnostics}


def test_a_well_formed_document_with_every_inline_tag_carrying_an_id_is_clean() -> None:
    document = _document(
        [
            InlineElement("ph", {"id": "p1"}),
            InlineElement("pc", {"id": "c1"}, content=["text"]),
            InlineElement("sc", {"id": "c2"}),
            "more text",
            InlineElement("ec", {"startRef": "c2"}),
        ]
    )

    report = validate(document)

    assert "xliff.inline.id.required" not in {item.code for item in report.diagnostics}


def test_id_required_is_checked_independently_in_target_content() -> None:
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
                        children=[
                            Segment(
                                id="s",
                                source=["hi"],
                                target=[InlineElement("ph", {})],
                            )
                        ],
                    )
                ],
            )
        ],
    )

    report = validate(document)

    assert report.is_valid is False
    assert any(
        item.code == "xliff.inline.id.required" and "target" in item.message
        for item in report.diagnostics
    )

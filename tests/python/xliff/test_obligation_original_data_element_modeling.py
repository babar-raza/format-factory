"""XLIFF-PARSE-001 / XLIFF-INLINE-001 -- originalData/data element
modeling and dataRef resolution.

MUST (SAL-XLIFF-OBL-C6C67E6C253C9EAB / SAL-XLIFF-OBL-C632C43201760C05):
"(XLIFF core - original data) originalData elements carry native code data
referenced from inline codes via dataRef attributes."

Before this slice: no originalData/data element modeling existed at all --
`<originalData>` fell into the generic ExtensionNode fallback (preserved
as an opaque byte blob, but not typed, queryable, or validated), and
InlineElement.data_ref merely read a dataRef/dataRefStart/dataRefEnd/
startRef attribute value generically without resolving it to anything.

This slice adds a typed `DataElement` model (`<data>`'s content is modeled
the same way as source/target inline content -- text plus any `<cp>`
children round-trip generically as InlineElement, matching this package's
existing "unknown tags round-trip generically" precedent rather than
inventing dedicated `<cp>` modeling) plus `Unit.original_data`, wires the
reader/writer to round-trip it in the correct structural position (after
notes, before segments, per the XLIFF Core 4.2.2.1 unit content model),
and implements dataRef/dataRefStart/dataRefEnd resolution validation
grounded directly in the pinned XLIFF 2.1 schematron's own F15/F16S/F16T/
F17S/F17T patterns (inside
.local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/xliff_core_2.1.sch): every dataRef-family attribute must point to
a `<data>` id within the same unit, and a pc's dataRefStart/dataRefEnd
must be used as a pair.

While verifying this slice against the full pre-existing suite before
writing any new test, a genuinely pre-existing, non-conformant fixture was
found and fixed: test_production_namespace.py's SAMPLE constant had a
`<pc dataRefStart="d1" dataRefEnd="d2">` with no `<originalData>` element
anywhere in the document at all -- the ids never resolved to anything, a
document that was never actually spec-conformant. Fixed by adding a
matching `<originalData>` block, the same "correct the fixture, not the
validation" discipline already applied earlier this session (XLIFF Event
206, UBL Event 191).
"""

from __future__ import annotations

from format_factory.xliff import DataElement, InlineElement, Segment, Unit, XliffDocument, XliffFile, dumps, loads, validate


def _document(
    original_data: list[DataElement], source: list[object], *, target: list[object] | None = None
) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language="fr" if target is not None else None,
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(id="u", original_data=original_data, children=[Segment(id="s", source=source, target=target)])
                ],
            )
        ],
    )


def test_originaldata_round_trips_through_dumps_and_reload() -> None:
    xml = (
        b'<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.1" srcLang="en">'
        b'<file id="f"><unit id="u">'
        b'<originalData><data id="d1">&lt;br/&gt;</data></originalData>'
        b'<segment id="s"><source>x<ph id="1" dataRef="d1"/></source></segment>'
        b"</unit></file></xliff>"
    )

    document = loads(xml)
    unit = next(document.iter_units())

    assert len(unit.original_data) == 1
    assert unit.original_data[0].id == "d1"
    assert unit.original_data[0].content == ["<br/>"]

    reloaded = loads(dumps(document).encode())
    reloaded_unit = next(reloaded.iter_units())

    assert reloaded_unit.original_data[0].id == "d1"
    assert reloaded_unit.original_data[0].content == ["<br/>"]


def test_originaldata_is_written_before_segments() -> None:
    document = _document(
        [DataElement(id="d1", content=["<br/>"])],
        [InlineElement("ph", {"id": "1", "dataRef": "d1"})],
    )

    xml = dumps(document)

    assert xml.index("<originalData>") < xml.index("<segment")


def test_a_dataref_that_resolves_to_a_real_data_id_validates_cleanly() -> None:
    document = _document(
        [DataElement(id="d1", content=["<br/>"])],
        [InlineElement("ph", {"id": "1", "dataRef": "d1"})],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.dataRef.unresolved" not in codes


def test_a_dataref_that_does_not_match_any_data_id_is_a_violation() -> None:
    document = _document([], [InlineElement("ph", {"id": "1", "dataRef": "missing"})])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.dataRef.unresolved" in codes


def test_a_pc_with_a_resolved_datarefstart_and_datarefend_pair_validates_cleanly() -> None:
    document = _document(
        [DataElement(id="d1", content=["<b>"]), DataElement(id="d2", content=["</b>"])],
        [InlineElement("pc", {"id": "1", "dataRefStart": "d1", "dataRefEnd": "d2"}, ["text"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert not any(code.startswith("xliff.inline.dataRef") for code in codes)


def test_a_pc_with_only_datarefstart_and_no_datarefend_is_unpaired() -> None:
    document = _document(
        [DataElement(id="d1", content=["<b>"])],
        [InlineElement("pc", {"id": "1", "dataRefStart": "d1"}, ["text"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.dataRef.unpaired" in codes


def test_a_pc_with_only_datarefend_and_no_datarefstart_is_unpaired() -> None:
    document = _document(
        [DataElement(id="d2", content=["</b>"])],
        [InlineElement("pc", {"id": "1", "dataRefEnd": "d2"}, ["text"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.dataRef.unpaired" in codes


def test_a_pc_datarefend_that_does_not_match_any_data_id_is_a_violation() -> None:
    document = _document(
        [DataElement(id="d1", content=["<b>"])],
        [InlineElement("pc", {"id": "1", "dataRefStart": "d1", "dataRefEnd": "missing"}, ["text"])],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.dataRefEnd.unresolved" in codes


def test_no_dataref_usage_anywhere_validates_cleanly() -> None:
    document = _document([], ["plain text, no inline codes"])

    codes = {item.code for item in validate(document).diagnostics}

    assert not any(code.startswith("xliff.inline.dataRef") for code in codes)


def test_a_target_side_dataref_is_checked_independently_of_source() -> None:
    document = _document(
        [DataElement(id="d1", content=["<br/>"])],
        ["x"],
        target=[InlineElement("ph", {"id": "1", "dataRef": "missing"})],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.dataRef.unresolved" in codes

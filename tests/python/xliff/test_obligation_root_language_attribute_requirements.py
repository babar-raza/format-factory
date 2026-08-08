"""XLIFF-PARSE-001 / XLIFF-TEXT-001 -- root version/srcLang/trgLang
attribute requirements.

MUST (SAL-XLIFF-OBL-C96F6CB613A6F95D / SAL-XLIFF-OBL-2602F9167F95464B):
"(XLIFF core - version attribute) The version and srcLang attributes are
required on the xliff root. The trgLang attribute is optional in the XSD
but required by the core Schematron when target elements are present."

Before this slice: version-omitted and srcLang-omitted documents were
already correctly refused at parse time (reader.py raises XliffParseError
for both), but no shipped test exercised either omission -- only that the
values are read when present. trgLang had zero implementation: nothing in
validator.py referenced it at all.

This slice adds direct coverage for the two already-correct parse-time
refusals, and implements the trgLang half from scratch, grounded directly
in the pinned XLIFF 2.1 schematron's own F1 pattern (inside
.local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/xliff_core_2.1.sch): "The 'trgLang' attribute is required if and
only if the XLIFF Document contains 'target' elements that are children of
'segment' or 'ignorable'". The schematron rule itself only asserts one
direction (target present => trgLang required); it does not also assert
the reverse (trgLang present => target required), so this slice does not
invent that reverse check either, despite the obligation's own rule_text
using "if and only if" language -- the formal schematron is the more
precise, authoritative source and is what is implemented here.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, Unit, XliffDocument, XliffFile, loads, validate
from format_factory.xliff.errors import XliffParseError

_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _document(*, target: list[object] | None = None, trg_lang: str | None = None) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=trg_lang,
        children=[
            XliffFile(
                id="f",
                children=[Unit(id="u", children=[Segment(id="s", source=["x"], target=target)])],
            )
        ],
    )


def test_a_document_with_version_omitted_from_the_xml_is_refused_at_parse_time() -> None:
    xml = (
        f'<xliff xmlns="{_NS}" srcLang="en">'
        '<file id="f"><unit id="u"><segment id="s"><source>x</source></segment></unit></file>'
        "</xliff>"
    ).encode()

    try:
        loads(xml)
        raised = False
    except XliffParseError:
        raised = True

    assert raised


def test_a_document_with_srclang_omitted_from_the_xml_is_refused_at_parse_time() -> None:
    xml = (
        f'<xliff xmlns="{_NS}" version="2.1">'
        '<file id="f"><unit id="u"><segment id="s"><source>x</source></segment></unit></file>'
        "</xliff>"
    ).encode()

    try:
        loads(xml)
        raised = False
    except XliffParseError:
        raised = True

    assert raised


def test_a_document_with_version_and_srclang_present_parses_cleanly() -> None:
    xml = (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en">'
        '<file id="f"><unit id="u"><segment id="s"><source>x</source></segment></unit></file>'
        "</xliff>"
    ).encode()

    document = loads(xml)

    assert document.version == "2.1"
    assert document.source_language == "en"


def test_a_target_element_with_no_trglang_is_a_violation() -> None:
    document = _document(target=["translated"], trg_lang=None)

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.trgLang.required" in codes


def test_a_target_element_with_trglang_set_validates_cleanly() -> None:
    document = _document(target=["translated"], trg_lang="fr")

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.trgLang.required" not in codes


def test_no_target_element_anywhere_and_no_trglang_validates_cleanly() -> None:
    """trgLang is genuinely optional per the XSD when no target content
    exists -- an untranslated document must not be forced to declare one."""
    document = _document(target=None, trg_lang=None)

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.trgLang.required" not in codes


def test_trglang_set_with_no_target_element_anywhere_also_validates_cleanly() -> None:
    """The reverse direction the schematron's own F1 <sch:assert> test does
    NOT check (only its descriptive, non-normative <sch:title> uses "if and
    only if" language): declaring trgLang without any target content is not
    a violation either. Confirms this package does not silently invent the
    unasserted reverse rule -- trgLang is optional in the XSD in both
    directions, not a paired on/off switch."""
    document = _document(target=None, trg_lang="fr")

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.trgLang.required" not in codes


def test_an_empty_target_element_still_counts_as_present_and_requires_trglang() -> None:
    """An empty <target/> is still a real target element structurally --
    segment.target is [] (not None) only when the reader found one -- so
    the requirement still applies even with no inline content inside it."""
    document = _document(target=[], trg_lang=None)

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.trgLang.required" in codes


def test_a_target_in_one_unit_requires_trglang_even_if_other_units_are_untranslated() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(id="u1", children=[Segment(id="s1", source=["x"], target=None)]),
                    Unit(id="u2", children=[Segment(id="s2", source=["y"], target=["z"])]),
                ],
            )
        ],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.trgLang.required" in codes

"""XLIFF-PARSE-001 / XLIFF-MODULE-001 -- Glossary module cardinality
constraints.

MUST (SAL-XLIFF-OBL-3C4EB05F176E240D and its cross-capability duplicate
SAL-XLIFF-OBL-0F4BED4809335F28): "the 'one or more glossEntry /
zero-or-more translation / at most one definition' cardinality
constraints are not enforced or tested -- Glossary is preserved only as
opaque extension content." Confirmed genuinely true before this slice by
direct probing: glossary content round-trips (test_glossary_module_
round_trips in test_obligation_module_coverage.py), but validate() never
inspected it.

Grounded directly in the pinned XLIFF 2.1 specification text and schema
(.local/format-contracts/acquired/xliff/src-xliff-003.bin, Section 5.2
"Glossary Module" and its bundled glossary.xsd): glossary's own sequence
declares minOccurs="1" maxOccurs="unbounded" for glossEntry; glossEntry
declares minOccurs="1" maxOccurs="1" for term, minOccurs="0"
maxOccurs="unbounded" for translation, and minOccurs="0" maxOccurs="1"
for definition. The spec's own prose Constraints section separately
states two rules not visible in the XSD grammar alone: a glossEntry
element MUST contain a translation or a definition element to be valid,
and id values MUST be unique among all glossEntry and translation
elements within the same enclosing glossary element.

Deliberately narrow, mirroring this package's own established pattern
for the Metadata/Resource Data/Matches modules exactly (each a
_{module}_module_diagnostics function keyed on the module's own
namespace, walking the preserved extension XML with ElementTree): this
slice adds cardinality/constraint diagnostics only. It does not add a
typed Glossary/GlossEntry/Term/Translation/Definition object model --
content continues to round-trip as opaque ExtensionNode XML, unchanged
from before this slice.
"""

from __future__ import annotations

from format_factory.xliff import ExtensionNode, XliffDocument, XliffFile, validate

_GLS_NS = "urn:oasis:names:tc:xliff:glossary:2.0"
_GLOSSARY_TAG = f"{{{_GLS_NS}}}glossary"


def _document(glossary_xml: bytes) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[ExtensionNode(tag=_GLOSSARY_TAG, xml=glossary_xml)],
            )
        ],
    )


def _codes(document: XliffDocument) -> set[str]:
    return {item.code for item in validate(document).diagnostics if "glossary" in item.code}


def test_a_well_formed_glossary_entry_validates_cleanly() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>widget</gls:term>'
        "<gls:translation>gadget</gls:translation></gls:glossEntry>"
        "</gls:glossary>"
    ).encode()

    assert _codes(_document(xml)) == set()


def test_a_glossentry_with_only_a_definition_validates_cleanly() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>widget</gls:term>'
        "<gls:definition>a small mechanical device</gls:definition></gls:glossEntry>"
        "</gls:glossary>"
    ).encode()

    assert _codes(_document(xml)) == set()


def test_an_empty_glossary_is_a_violation() -> None:
    xml = f'<gls:glossary xmlns:gls="{_GLS_NS}"/>'.encode()

    assert _codes(_document(xml)) == {"xliff.module.glossary.glossentry.required"}


def test_a_glossentry_missing_term_is_a_violation() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:definition>d</gls:definition></gls:glossEntry>'
        "</gls:glossary>"
    ).encode()

    assert "xliff.module.glossary.term.required" in _codes(_document(xml))


def test_a_glossentry_with_two_terms_is_a_violation() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>a</gls:term><gls:term>b</gls:term>'
        "<gls:definition>d</gls:definition></gls:glossEntry>"
        "</gls:glossary>"
    ).encode()

    assert "xliff.module.glossary.term.required" in _codes(_document(xml))


def test_a_glossentry_with_two_definitions_is_a_violation() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>a</gls:term>'
        "<gls:definition>d1</gls:definition><gls:definition>d2</gls:definition>"
        "</gls:glossEntry></gls:glossary>"
    ).encode()

    assert "xliff.module.glossary.definition.multiple" in _codes(_document(xml))


def test_a_glossentry_with_neither_translation_nor_definition_is_a_violation() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>widget</gls:term></gls:glossEntry>'
        "</gls:glossary>"
    ).encode()

    assert "xliff.module.glossary.translation_or_definition.required" in _codes(_document(xml))


def test_multiple_translations_with_no_definition_validates_cleanly() -> None:
    """"Zero, one or more translation elements" -- multiple translations
    alone (no definition) satisfy the translation-or-definition rule."""
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>widget</gls:term>'
        "<gls:translation>gadget</gls:translation>"
        "<gls:translation>gizmo</gls:translation></gls:glossEntry>"
        "</gls:glossary>"
    ).encode()

    assert _codes(_document(xml)) == set()


def test_a_duplicate_id_between_two_glossentries_is_a_violation() -> None:
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="dup"><gls:term>a</gls:term>'
        "<gls:definition>d</gls:definition></gls:glossEntry>"
        '<gls:glossEntry id="dup"><gls:term>b</gls:term>'
        "<gls:definition>d</gls:definition></gls:glossEntry>"
        "</gls:glossary>"
    ).encode()

    assert "xliff.module.glossary.id.duplicate" in _codes(_document(xml))


def test_a_duplicate_id_between_a_glossentry_and_a_translation_is_a_violation() -> None:
    """"The values of id attributes MUST be unique among all glossEntry
    AND translation elements" -- the uniqueness scope spans both element
    kinds, not just glossEntry-to-glossEntry."""
    xml = (
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="dup"><gls:term>a</gls:term>'
        "<gls:definition>d</gls:definition></gls:glossEntry>"
        '<gls:glossEntry><gls:term>b</gls:term>'
        '<gls:translation id="dup">x</gls:translation></gls:glossEntry>'
        "</gls:glossary>"
    ).encode()

    assert "xliff.module.glossary.id.duplicate" in _codes(_document(xml))


def test_a_non_glossary_extension_is_unaffected() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    ExtensionNode(
                        tag="{urn:example:other}thing",
                        xml=b'<other xmlns="urn:example:other"/>',
                    )
                ],
            )
        ],
    )

    assert _codes(document) == set()

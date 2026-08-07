"""XLIFF-PARSE-001 against the shipped namespace.

MUST (SAL-XLIFF-OBL-D2BB0F0D8018D601): "(XLIFF core - whitespace and
language) The xliff root declares xml:space with default value default,
and source and target permit optional xml:lang and xml:space attributes."

Before this slice: source/target permitting optional xml:lang/xml:space
as generic passthrough attributes was already proven, but the root's own
"default value default" clause was untested and not actually modeled --
the reader never synthesized a default xml:space on the root; if absent
from the source XML, it was simply absent from XliffDocument.attributes
rather than defaulted, per the pinned spec's own text: "When used in
<xliff>: The value default" (section 4.3.2.2, distinct from the broader
per-element inheritance chain that rule -- not modeled here, since this
obligation's own rule_text is scoped to only the root's default, not the
full file/group/unit/source/target/data inheritance rule).

This file proves the new XliffDocument.xml_space property: "default" when
absent (the spec-mandated root default), the explicit value when present,
and that the raw attributes dict still separately distinguishes absent
from an explicitly-written "default" for any caller that needs that
finer distinction (XLIFF-PRESERVE-001's own absent-vs-explicit concern).
"""

from __future__ import annotations

from format_factory.xliff import loads

_NS = "urn:oasis:names:tc:xliff:document:2.0"
_XML_NS = "http://www.w3.org/XML/1998/namespace"


def _document(xml_space_attr: str = "") -> bytes:
    xmlns_xml = f' xmlns:xml="{_XML_NS}"' if xml_space_attr else ""
    return (
        f'<xliff xmlns="{_NS}"{xmlns_xml} version="2.1" srcLang="en"{xml_space_attr}>'
        '<file id="f1"><unit id="u1"><segment id="s1"><source>hi</source></segment></unit></file>'
        "</xliff>"
    ).encode()


def test_an_absent_xml_space_attribute_defaults_to_default() -> None:
    document = loads(_document())

    assert document.xml_space == "default"


def test_an_explicit_preserve_is_reported_verbatim() -> None:
    document = loads(_document(' xml:space="preserve"'))

    assert document.xml_space == "preserve"


def test_an_explicit_default_is_reported_verbatim_too() -> None:
    document = loads(_document(' xml:space="default"'))

    assert document.xml_space == "default"


def test_absent_and_explicit_default_are_still_distinguishable_via_raw_attributes() -> None:
    """xml_space itself cannot distinguish "absent" from "explicitly
    default" (both correctly report "default", the spec-mandated value in
    either case) -- but the underlying raw attributes dict still can, for
    a caller with XLIFF-PRESERVE-001's finer absent-vs-explicit concern."""
    absent = loads(_document())
    explicit = loads(_document(' xml:space="default"'))

    assert "{http://www.w3.org/XML/1998/namespace}space" not in absent.attributes
    assert explicit.attributes["{http://www.w3.org/XML/1998/namespace}space"] == "default"

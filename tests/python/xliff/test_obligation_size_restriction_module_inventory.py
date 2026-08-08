"""XLIFF-MODEL-001 / XLIFF-PARSE-001 / XLIFF-MODULE-001 -- the Size and
Length Restriction module's own structural inventory: namespace, its
profiles/normalization/data elements, and its sizeRestriction/
storageRestriction attributes.

MUST (SAL-XLIFF-OBL-05547046CBCB57F7 and its cross-capability duplicates
SAL-XLIFF-OBL-57668EDF714BE172, SAL-XLIFF-OBL-EEA9C58A385F7C96): "The
Size and Length Restriction module uses namespace urn:oasis:names:tc:
xliff:sizerestriction:2.0 and defines profiles, normalization, data, and
restriction attributes including sizeRestriction and storageRestriction."

This is a structural inventory claim about the module's own schema shape
-- distinct from and narrower than "typed sizeRestriction/storageRestriction
attribute VALUE parsing" (the "[minsize,]maxsize" format), which each of
these obligations' own missing_behavior correctly still leaves unbuilt as
a separate, profile-scoped, whole-tree-resolution-dependent capability
(see test_obligation_size_restriction_module_sizeinfo_conflict.py's own
docstring). Neither this obligation's rule_text nor its required_tests
("Nested-structure fixtures verify order, inheritance, and ID preservation
after round trip") asks for value parsing -- both ask for the module's
namespace/elements/attributes to exist and for content using them to
round-trip losslessly, both of which this package's existing generic
XmlNode preservation layer (used by every other module this session:
Glossary, Validation, Matches, ITS, ITS Mapping) already provides.

Grounded directly in the bundled official schema (validation/schemas/
size_restriction.xsd, extracted at FF6-EVENT-000272 from the pinned
src-xlf-002.bin ZIP) -- not assumed from the rule_text's own prose alone.
"""

from __future__ import annotations

from format_factory.xliff import dumps, loads
from format_factory.xliff.validation.schema_validator import _load_full_schema

_SLR_NS = "urn:oasis:names:tc:xliff:sizerestriction:2.0"


def test_the_bundled_schema_declares_the_slr_namespace() -> None:
    schema = _load_full_schema()

    assert _SLR_NS in schema.maps.namespaces


def test_the_bundled_schema_defines_profiles_normalization_and_data_elements() -> None:
    schema = _load_full_schema()

    element_names = {
        name.rsplit("}", 1)[-1]
        for name in schema.maps.elements
        if name.startswith(f"{{{_SLR_NS}}}")
    }

    assert {"profiles", "normalization", "data"}.issubset(element_names)


def test_the_bundled_schema_defines_sizerestriction_and_storagerestriction_attributes() -> None:
    schema = _load_full_schema()

    attribute_names = {
        name.rsplit("}", 1)[-1]
        for name in schema.maps.attributes
        if name.startswith(f"{{{_SLR_NS}}}")
    }

    assert {"sizeRestriction", "storageRestriction"}.issubset(attribute_names)


def _document_using_the_full_module_inventory() -> bytes:
    return (
        '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" '
        f'xmlns:slr="{_SLR_NS}" version="2.1" srcLang="en">'
        "<file id=\"f\">"
        '<slr:profiles generalProfile="xliff:codepoints" storageProfile="xliff:utf8">'
        '<slr:normalization general="nfc" storage="nfd"/>'
        "</slr:profiles>"
        '<unit id="u" slr:sizeRestriction="10" slr:storageRestriction="20,utf8">'
        "<segment><source>Hi</source></segment>"
        "</unit></file></xliff>"
    ).encode()


def test_profiles_normalization_and_restriction_attributes_round_trip_losslessly() -> None:
    """Content using every element/attribute this module defines survives
    a real load->dumps cycle -- the same generic XmlNode preservation
    already proven for every other standard module this session, applied
    here directly rather than assumed to transfer."""
    document = loads(_document_using_the_full_module_inventory())
    redumped = loads(dumps(document))

    assert redumped == document


def test_sizerestriction_and_storagerestriction_survive_round_trip_with_their_raw_values_unchanged() -> None:
    document = loads(_document_using_the_full_module_inventory())
    # children[0] is the standalone slr:profiles extension element; the unit follows it.
    unit = document.children[0].children[1]

    size_key = f"{{{_SLR_NS}}}sizeRestriction"
    storage_key = f"{{{_SLR_NS}}}storageRestriction"
    assert unit.attributes[size_key] == "10"
    assert unit.attributes[storage_key] == "20,utf8"

    redumped = loads(dumps(document))
    redumped_unit = redumped.children[0].children[1]
    assert redumped_unit.attributes[size_key] == "10"
    assert redumped_unit.attributes[storage_key] == "20,utf8"

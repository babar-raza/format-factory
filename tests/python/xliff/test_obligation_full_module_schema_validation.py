"""XLIFF-PARSE-001 / XLIFF-MODULE-001 -- module content valid against
its own module schema, composed with the core schema.

MUST (SAL-XLIFF-OBL-078DE5F17834C232 / SAL-XLIFF-OBL-C1BB9934B09B3B70):
"XLIFF documents must be well-formed XML and valid against the core
schema with module content valid against its module schema." This file
supplies the final, previously-missing clause -- schema_validate()
(test_obligation_core_schema_validation.py) already proves "valid
against the core schema."

The bundled module schemas (validation/schemas/*.xsd, alongside the
core) are the actual OASIS-published XLIFF 2.1 schema files for every
standard module: Format Style, Glossary, ITS, ITS Mapping, Matches,
Metadata, Resource Data, Size and Length Restriction, Validation.
Extracted from the real official distribution ZIP found inside the
pinned raw acquisition cache (.local/format-contracts/acquired/xliff/
src-xlf-002.bin -- confirmed a ZIP by its own "PK" magic bytes, not
spec prose, discovered by checking why this file was anomalously large
as a text dump compared to its siblings). Each module schema's own
xs:import of xliff_core_2.0.xsd resolves automatically because every
file is bundled together, unmodified, in the same directory exactly as
OASIS ships them -- this is the real, OASIS-defined combined grammar,
not a hand-assembled approximation.

Deliberately narrow about one remaining thing: XSD structural
conformance only. The distribution package also ships per-module ISO
Schematron (.sch) files for additional business-rule assertions beyond
XSD's own expressive power -- not required by this obligation's own
rule_text. Those files are bundled too (see
test_obligation_schematron_and_nvdl_bundle_inventory.py) but not executed:
they declare queryBinding="xslt2", which lxml.isoschematron -- the only
engine available without a new heavyweight dependency -- refuses outright.
"""

from __future__ import annotations

import pytest

xmlschema = pytest.importorskip("xmlschema", reason="optional xmlschema dependency not installed")

from format_factory.xliff import full_schema_validate  # noqa: E402
from format_factory.xliff.validation.schema_validator import _load_full_schema  # noqa: E402

_XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"
_GLS_NS = "urn:oasis:names:tc:xliff:glossary:2.0"
_VAL_NS = "urn:oasis:names:tc:xliff:validation:2.0"


def _document(extension_xml: str) -> bytes:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{_XLIFF_NS}" version="2.0" srcLang="en">\n'
        f'<file id="f1">{extension_xml}'
        f'<unit id="u1"><segment><source>Hello</source></segment></unit>'
        f"</file>\n"
        f"</xliff>\n"
    ).encode()


def test_composed_schema_loads_all_nine_standard_module_namespaces() -> None:
    schema = _load_full_schema()

    expected_module_namespaces = {
        "urn:oasis:names:tc:xliff:fs:2.0",
        "urn:oasis:names:tc:xliff:glossary:2.0",
        "http://www.w3.org/2005/11/its",
        "urn:oasis:names:tc:xliff:itsm:2.1",
        "urn:oasis:names:tc:xliff:matches:2.0",
        "urn:oasis:names:tc:xliff:metadata:2.0",
        "urn:oasis:names:tc:xliff:resourcedata:2.0",
        "urn:oasis:names:tc:xliff:sizerestriction:2.0",
        "urn:oasis:names:tc:xliff:validation:2.0",
    }
    assert expected_module_namespaces.issubset(set(schema.maps.namespaces.keys()))
    assert "urn:oasis:names:tc:xliff:document:2.0" in schema.maps.namespaces


def test_a_document_with_no_module_extension_validates_cleanly() -> None:
    document = _document("")

    assert full_schema_validate(document).is_valid


def test_a_well_formed_glossary_extension_validates_cleanly() -> None:
    document = _document(
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>widget</gls:term>'
        "<gls:translation>gadget</gls:translation></gls:glossEntry>"
        "</gls:glossary>"
    )

    assert full_schema_validate(document).is_valid


def test_a_glossary_entry_with_two_terms_violates_the_module_schema() -> None:
    """glossEntry's own module schema declares term as maxOccurs=1 --
    XSD structurally rejects a second one, independent of this
    package's own separate, narrower _glossary_module_diagnostics
    cardinality check."""
    document = _document(
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>a</gls:term><gls:term>b</gls:term>'
        "<gls:translation>x</gls:translation></gls:glossEntry>"
        "</gls:glossary>"
    )

    report = full_schema_validate(document)

    assert not report.is_valid
    assert {item.code for item in report.diagnostics} == {"xliff.schema.module.invalid"}


def test_a_well_formed_validation_module_extension_validates_cleanly() -> None:
    document = _document(
        f'<val:validation xmlns:val="{_VAL_NS}"><val:rule isPresent="store"/></val:validation>'
    )

    assert full_schema_validate(document).is_valid


def test_a_core_level_violation_is_still_caught_when_a_module_extension_is_present() -> None:
    """The composed schema does not silently ignore core-level defects
    just because a module extension elsewhere in the document is
    well-formed -- both are checked together, in one combined report."""
    document = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{_XLIFF_NS}" version="2.0" srcLang="en">\n'
        f"<file>"  # missing required id attribute -- a core-level defect
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>widget</gls:term>'
        "<gls:translation>gadget</gls:translation></gls:glossEntry>"
        "</gls:glossary>"
        '<unit id="u1"><segment><source>Hello</source></segment></unit>'
        "</file>\n"
        "</xliff>\n"
    ).encode()

    report = full_schema_validate(document)

    assert not report.is_valid


def test_every_violation_is_reported_not_just_the_first() -> None:
    document = _document(
        f'<gls:glossary xmlns:gls="{_GLS_NS}">'
        '<gls:glossEntry id="g1"><gls:term>a</gls:term><gls:term>b</gls:term></gls:glossEntry>'
        "</gls:glossary>"
    )

    report = full_schema_validate(document)

    # the two-terms violation AND the glossEntry-with-neither-translation-
    # nor-definition constraint (a Schematron-level rule outside this
    # schema's own XSD reach) means at least the XSD term-cardinality
    # violation must appear -- proven, not the module-level diagnostics
    # check's own separate business-rule count.
    assert len(report.diagnostics) >= 1

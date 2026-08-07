"""XLIFF-MODULE-001 against the shipped namespace.

SAL-XLIFF facts 00021 through 00026 plus the ITS and Resource Data normative
rules (MUST): declare per-module coverage (modeled/preservation-only/
unsupported) for every optional module of the target version, and preserve
unknown module content losslessly -- never drop module data silently.

Written directly against format_factory.xliff. Per the mission's own rule,
this is NOT a port of any shadow-package test: every other file in this
directory imports the deprecated top-level ``xliff`` package, which is why
none of them may supply this obligation's selector.
"""

from __future__ import annotations

import pytest

from format_factory.xliff import (
    STANDARD_MODULES,
    ModuleCoverage,
    ModuleInfo,
    dumps,
    is_production_complete,
    loads,
    module_coverage_manifest,
)

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"

HEADER = (
    f'<?xml version="1.0" encoding="UTF-8"?>\n'
    f'<xliff xmlns="{XLIFF_NS}" version="2.0" srcLang="en">\n'
)
FOOTER = "</xliff>\n"


def _document(file_body: str) -> str:
    return (
        HEADER
        + f'<file id="f1">{file_body}'
        + '<unit id="u1"><segment><source>hi</source></segment></unit>'
        + "</file>"
        + FOOTER
    )


# ── Manifest structure: every module named in the contract is declared ─────


EXPECTED_MODULE_NAMES = {
    "Translation Candidates",
    "Glossary",
    "Format Style",
    "Metadata",
    "Resource Data",
    "Size and Length Restriction",
    "Validation",
    "ITS",
}


def test_all_eight_standard_modules_are_declared() -> None:
    """"The XLIFF 2.1 standard package defines the Translation Candidates,
    Glossary, Format Style, Metadata, Resource Data, Size and Length
    Restriction, Validation, and ITS modules in their own namespaces." """
    manifest = module_coverage_manifest()
    assert set(manifest) == EXPECTED_MODULE_NAMES


def test_manifest_is_keyed_by_module_name_and_returns_module_info() -> None:
    manifest = module_coverage_manifest()
    for name, info in manifest.items():
        assert isinstance(info, ModuleInfo)
        assert info.name == name


@pytest.mark.parametrize(
    ("name", "namespace"),
    [
        ("Translation Candidates", "urn:oasis:names:tc:xliff:matches:2.0"),
        ("Glossary", "urn:oasis:names:tc:xliff:glossary:2.0"),
        ("Format Style", "urn:oasis:names:tc:xliff:fs:2.0"),
        ("Metadata", "urn:oasis:names:tc:xliff:metadata:2.0"),
        ("Size and Length Restriction", "urn:oasis:names:tc:xliff:sizerestriction:2.0"),
        ("Validation", "urn:oasis:names:tc:xliff:validation:2.0"),
        ("ITS", "http://www.w3.org/2005/11/its"),
    ],
)
def test_confirmed_module_namespaces_match_the_sal_facts(name: str, namespace: str) -> None:
    module = module_coverage_manifest()[name]
    assert module.namespace == namespace
    assert module.namespace_confirmed is True


def test_resource_data_namespace_is_explicitly_unconfirmed_not_invented() -> None:
    """Unlike the other six, no SAL fact states Resource Data's namespace URI.
    Reporting one anyway would be an invented fact; reporting none candidly
    says so rather than silently omitting the module from the manifest."""
    module = module_coverage_manifest()["Resource Data"]
    assert module.namespace is None
    assert module.namespace_confirmed is False
    assert module.coverage is ModuleCoverage.PRESERVATION_ONLY


def test_no_module_is_silently_absent_from_the_manifest() -> None:
    """"silent module downgrade is forbidden" -- every module has an explicit
    coverage value, never merely missing from the manifest."""
    for module in STANDARD_MODULES:
        assert module.coverage in ModuleCoverage


# ── Honesty control: no module may claim MODELED without a typed accessor ──


def test_no_module_is_falsely_reported_as_modeled() -> None:
    """GAP-022 control: model/document.py defines no Match, GlossEntry,
    MetaGroup, or other typed accessor for any of the eight modules today.
    Reporting MODELED without one would be exactly that overstatement."""
    import format_factory.xliff as xliff_package

    typed_accessor_names = {
        "Match",
        "GlossEntry",
        "MetaGroup",
        "SizeRestriction",
        "ValidationRule",
        "ResourceData",
        "FormatStyle",
        "ItsAnnotation",
    }
    exported = set(xliff_package.__all__)
    assert not (typed_accessor_names & exported)
    for module in STANDARD_MODULES:
        assert module.coverage is not ModuleCoverage.MODELED


def test_production_complete_is_false_while_any_module_is_preservation_only() -> None:
    """"production-complete status requires all modules modeled." """
    assert is_production_complete() is False


# ── Per-module round-trip fixtures: element-based modules ──────────────────


def _extension_of(document, index: int = 0):
    file = document.files[0]
    extensions = [child for child in file.children if not hasattr(child, "id")]
    return extensions[index]


def test_translation_candidates_module_round_trips() -> None:
    body = '<mtc:matches xmlns:mtc="urn:oasis:names:tc:xliff:matches:2.0">'
    body += (
        '<mtc:match ref="#u1/source-text">'
        "<source>candidate</source><target>candidate</target>"
        "</mtc:match>"
    )
    body += "</mtc:matches>"
    document = loads(_document(body))
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        extension = _extension_of(parsed)
        # The serialized prefix is a local alias ElementTree is free to rename
        # (ns0 vs mtc); what preservation actually promises is the namespace
        # URI, local names, attributes and text -- all present in the
        # clark-notation tag and the round-tripped bytes.
        assert extension.tag == "{urn:oasis:names:tc:xliff:matches:2.0}matches"
        assert b"match" in extension.xml
        assert b'ref="#u1/source-text"' in extension.xml
        assert b"candidate" in extension.xml


def test_glossary_module_round_trips() -> None:
    body = '<gls:glossary xmlns:gls="urn:oasis:names:tc:xliff:glossary:2.0">'
    body += '<gls:glossEntry id="g1"><gls:term>widget</gls:term></gls:glossEntry>'
    body += "</gls:glossary>"
    document = loads(_document(body))
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        extension = _extension_of(parsed)
        assert extension.tag == "{urn:oasis:names:tc:xliff:glossary:2.0}glossary"
        assert b"glossEntry" in extension.xml
        assert b'id="g1"' in extension.xml
        assert b"widget" in extension.xml


def test_metadata_module_round_trips() -> None:
    body = '<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0">'
    body += '<mda:metaGroup><mda:meta type="project-id">PRJ-42</mda:meta></mda:metaGroup>'
    body += "</mda:metadata>"
    document = loads(_document(body))
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        extension = _extension_of(parsed)
        assert extension.tag == "{urn:oasis:names:tc:xliff:metadata:2.0}metadata"
        assert b"metaGroup" in extension.xml
        assert b'type="project-id"' in extension.xml
        assert b"PRJ-42" in extension.xml


def test_size_and_length_restriction_module_round_trips() -> None:
    body = (
        '<slr:profiles xmlns:slr="urn:oasis:names:tc:xliff:sizerestriction:2.0" '
        'general="pixel"/>'
    )
    document = loads(_document(body))
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        extension = _extension_of(parsed)
        assert extension.tag == "{urn:oasis:names:tc:xliff:sizerestriction:2.0}profiles"
        assert b'general="pixel"' in extension.xml


def test_validation_module_round_trips() -> None:
    body = '<val:validation xmlns:val="urn:oasis:names:tc:xliff:validation:2.0">'
    body += '<val:rule occurs="1"/>'
    body += "</val:validation>"
    document = loads(_document(body))
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        extension = _extension_of(parsed)
        assert extension.tag == "{urn:oasis:names:tc:xliff:validation:2.0}validation"
        assert b"rule" in extension.xml
        assert b'occurs="1"' in extension.xml


def test_resource_data_module_round_trips_despite_unconfirmed_namespace() -> None:
    """Proves the mechanism is namespace-agnostic: preservation does not
    require this module's manifest entry to name a specific namespace."""
    body = (
        '<res:resourceData xmlns:res="urn:oasis:names:tc:xliff:resourcedata:2.0">'
        '<res:resourceItemRef id="img1"/>'
        "</res:resourceData>"
    )
    document = loads(_document(body))
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        extension = _extension_of(parsed)
        assert extension.tag == "{urn:oasis:names:tc:xliff:resourcedata:2.0}resourceData"
        assert b"resourceItemRef" in extension.xml
        assert b'id="img1"' in extension.xml


# ── Per-module round-trip fixtures: attribute-based modules ────────────────


def test_format_style_attributes_round_trip_on_a_unit() -> None:
    """"The Format Style module...defines fs and subFs attributes" -- these
    attach to existing core elements rather than introducing their own."""
    xml = (
        HEADER
        + '<file id="f1"><unit id="u1" xmlns:fs="urn:oasis:names:tc:xliff:fs:2.0" '
        + 'fs:fs="span" fs:subFs="bold">'
        + "<segment><source>hi</source></segment>"
        + "</unit></file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        unit = parsed.files[0].children[0]
        fs_keys = {key for key in unit.attributes if key.endswith("}fs") or key.endswith("}subFs")}
        assert len(fs_keys) == 2
        values = {unit.attributes[key] for key in fs_keys}
        assert values == {"span", "bold"}


def test_its_mapping_attributes_round_trip_on_a_unit() -> None:
    """"the XLIFF 2.1 mapping adds urn:oasis:names:tc:xliff:itsm:2.1
    attributes for domains and language."

    Unlike this file's shared HEADER (version="2.0"), this fixture declares
    version="2.1": the itsm:2.1 mapping is content-level 2.1-only per the
    specification's own Appendix C change summary, so XLIFF-WRITE-001's
    version-downgrade-loss check (test_obligation_version_downgrade_loss.py)
    correctly refuses to write it under a "version=2.0" declaration -- a
    fixture that actually carries this content must honestly declare 2.1
    to remain writable at all, which this test now does.
    """
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{XLIFF_NS}" version="2.1" srcLang="en">\n'
        + '<file id="f1"><unit id="u1" xmlns:itsm="urn:oasis:names:tc:xliff:itsm:2.1" '
        + 'itsm:domains="legal">'
        + "<segment><source>hi</source></segment>"
        + "</unit></file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        unit = parsed.files[0].children[0]
        domain_keys = [key for key in unit.attributes if key.endswith("}domains")]
        assert len(domain_keys) == 1
        assert unit.attributes[domain_keys[0]] == "legal"


def test_its_mapping_lang_attribute_round_trips_on_a_unit() -> None:
    """The rule_text's own prose names this attribute "language", but the
    pinned itsm.xsd schema declares it as itsm:lang (xs:attribute
    name="lang" type="xs:language") -- confirmed by reading the pinned
    schema directly rather than guessing an attribute name from the
    obligation's own English description. Previously untested from this
    specific angle, unlike the sibling itsm:domains attribute above."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{XLIFF_NS}" version="2.1" srcLang="en">\n'
        + '<file id="f1"><unit id="u1" xmlns:itsm="urn:oasis:names:tc:xliff:itsm:2.1" '
        + 'itsm:lang="fr">'
        + "<segment><source>hi</source></segment>"
        + "</unit></file>"
        + FOOTER
    )
    document = loads(xml)
    reparsed = loads(dumps(document))

    for parsed in (document, reparsed):
        unit = parsed.files[0].children[0]
        lang_keys = [key for key in unit.attributes if key.endswith("}lang")]
        assert len(lang_keys) == 1
        assert unit.attributes[lang_keys[0]] == "fr"


# ── Nothing is silently dropped: unit/segment structure survives alongside ──


def test_module_content_does_not_disturb_the_surrounding_unit() -> None:
    body = '<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0">'
    body += '<mda:metaGroup><mda:meta type="k">v</mda:meta></mda:metaGroup>'
    body += "</mda:metadata>"
    document = loads(_document(body))

    assert document.unit_count == 1
    unit = document.files[0].children[-1]
    assert unit.id == "u1"
    assert unit.segments[0].source == ["hi"]

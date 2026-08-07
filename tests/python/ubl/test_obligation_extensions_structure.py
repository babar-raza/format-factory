"""UBL-EXT-001 (and its cross-capability duplicates in UBL-REF-001,
UBL-DOCTYPES-001, UBL-MODEL-001, UBL-PARSE-001, UBL-VALIDATE-001) --
ext:UBLExtensions structural constraints.

MUST ("UBL extension model", 6-way cross-capability duplicate rule_text):
"ext:UBLExtensions is the first optional component in UBL document
sequences; each UBLExtension contains ExtensionContent, which permits one
foreign-namespaced apex element with lax validation."

Before this slice, validator.py had zero handling of ext:UBLExtensions at
all -- confirmed by grepping the file. The only existing test that looked
adjacent (test_unknown_extension_is_preserved_semantically in
test_production_namespace.py) places a foreign-namespaced element directly
as a root child, never actually constructing the real
ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent container structure
this obligation names -- so the specific structural constraints (sequence
position, UBLExtension-only children, exactly-one-ExtensionContent,
exactly-one-apex-element) had never been exercised, positively or
negatively, anywhere in the suite. Confirmed empirically before writing any
fix: constructing a document with ext:UBLExtensions NOT first, or with an
ExtensionContent carrying zero or two apex-element children, both passed
validate() with zero diagnostics.

Fixed by adding _extension_diagnostics() to validator.py, which checks
position (index 0 among root children, if present), that ext:UBLExtensions
only contains ext:UBLExtension children, that each ext:UBLExtension
contains exactly one ext:ExtensionContent, and that each ExtensionContent
contains exactly one child element. "Lax validation" for the apex
element's own content is satisfied by construction: nothing inspects
inside it beyond counting it as present, exactly once.
"""

from __future__ import annotations

from format_factory.ubl import ROOT_CLASSES, XmlNode, loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_EXT_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
_VENDOR_NS = "urn:example:vendor"
Invoice = ROOT_CLASSES["Invoice"]


def _version_node() -> XmlNode:
    return XmlNode.create(f"{{{_CBC}}}UBLVersionID", text="2.3")


def _id_node() -> XmlNode:
    return XmlNode.create(f"{{{_CBC}}}ID", text="INV-001")


def _extension_content(apex_children: tuple[XmlNode, ...]) -> XmlNode:
    return XmlNode.create(f"{{{_EXT_NS}}}ExtensionContent", children=apex_children)


def _apex() -> XmlNode:
    return XmlNode.create(f"{{{_VENDOR_NS}}}Payload", text="vendor payload")


def _extensions(*, content_children: tuple[XmlNode, ...] | None = None) -> XmlNode:
    if content_children is None:
        content_children = (_apex(),)
    return XmlNode.create(
        f"{{{_EXT_NS}}}UBLExtensions",
        children=(
            XmlNode.create(
                f"{{{_EXT_NS}}}UBLExtension",
                children=(_extension_content(content_children),),
            ),
        ),
    )


def test_extensions_first_in_sequence_is_valid() -> None:
    document = Invoice.build(children=(_extensions(), _version_node(), _id_node()))

    report = validate(document)

    assert report.is_valid


def test_extensions_not_first_in_sequence_is_rejected() -> None:
    document = Invoice.build(children=(_version_node(), _extensions(), _id_node()))

    report = validate(document)

    assert not report.is_valid
    assert "ubl.extensions.position" in {item.code for item in report.diagnostics}


def test_an_extension_content_with_zero_apex_elements_is_rejected() -> None:
    document = Invoice.build(
        children=(_extensions(content_children=()), _version_node(), _id_node())
    )

    report = validate(document)

    assert not report.is_valid
    assert "ubl.extension.content.apex" in {item.code for item in report.diagnostics}


def test_an_extension_content_with_two_apex_elements_is_rejected() -> None:
    document = Invoice.build(
        children=(
            _extensions(content_children=(_apex(), _apex())),
            _version_node(),
            _id_node(),
        )
    )

    report = validate(document)

    assert not report.is_valid
    assert "ubl.extension.content.apex" in {item.code for item in report.diagnostics}


def test_an_extension_carrying_two_extension_content_elements_is_rejected() -> None:
    malformed_extensions = XmlNode.create(
        f"{{{_EXT_NS}}}UBLExtensions",
        children=(
            XmlNode.create(
                f"{{{_EXT_NS}}}UBLExtension",
                children=(_extension_content((_apex(),)), _extension_content((_apex(),))),
            ),
        ),
    )
    document = Invoice.build(children=(malformed_extensions, _version_node(), _id_node()))

    report = validate(document)

    assert not report.is_valid
    assert "ubl.extension.content.cardinality" in {item.code for item in report.diagnostics}


def test_a_non_extension_child_of_ublextensions_is_rejected() -> None:
    malformed_extensions = XmlNode.create(
        f"{{{_EXT_NS}}}UBLExtensions", children=(_apex(),)
    )
    document = Invoice.build(children=(malformed_extensions, _version_node(), _id_node()))

    report = validate(document)

    assert not report.is_valid
    assert "ubl.extensions.child" in {item.code for item in report.diagnostics}


def test_a_document_with_no_extensions_container_is_unaffected() -> None:
    document = Invoice.build(children=(_version_node(), _id_node()))

    report = validate(document)

    assert report.is_valid


def test_a_conformant_extension_round_trips_through_dumps_and_loads() -> None:
    from format_factory.ubl import dumps

    document = Invoice.build(children=(_extensions(), _version_node(), _id_node()))

    reloaded = loads(dumps(document))

    report = validate(reloaded)
    assert report.is_valid

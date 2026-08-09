"""UBL-PARSE-001 / UBL-REF-001 / UBL-MODEL-001 / UBL-DOCTYPES-001 /
UBL-VALIDATE-001 -- namespace-spoofing detection.

MUST (SAL-UBL-OBL-0996E6D7B91D544F, "identifier constraints" cluster):
id/name-bearing elements must be resolved unambiguously, never by
best-effort local-name guessing across namespace boundaries.

Before this slice: model/typed.py's find()/find_all() (the navigation
primitives underlying amount_of, quantity_of, identifier_of, and every
aggregate-of function) matched children by local name only, confirmed
directly: a spoofed `{urn:evil:attacker:namespace}ID` child placed ahead
of the real `{urn:oasis:...:CommonBasicComponents-2}ID` child made
find() return the spoofed element's text, not the real one.

Rewriting find()/find_all() to check an expected namespace per call
would require auditing ~78 call sites across the whole typed-projection
layer -- a cross-cutting change with real blast radius, deliberately
left out of scope. Instead, validate() now detects the one structural
signature every such spoofing attempt must share: two or more
same-local-name children, in different namespaces, under one parent --
a shape no conformant UBL document produces. This makes validate() the
safety net: a spoofed sibling fails validation before any find()-derived
value is trusted downstream. find() itself remains unchanged and is
still naively vulnerable if a caller reads a value without validating
the document first -- that caveat is proven directly below, not hidden.

FF6-EVENT-000481 adds the complementary fix at the lookup site itself:
find_qname()/find_all_qname() (model/typed.py), matching BOTH namespace
and local name exactly (a full QName match), generalizing the pattern
document.py's own _first_child_text() already used internally for
UBLVersionID/CustomizationID/ProfileID rather than inventing a new
matching convention. This is purely additive -- none of the ~78 existing
find()/find_all() call sites are touched or migrated here, so there is
no regression risk to existing behavior; a caller wanting namespace
-precise resolution now has a real, tested primitive to migrate to, one
call site at a time, in future work. The 78-site migration itself
remains a separate, larger, disclosed task.
"""

from __future__ import annotations

from format_factory.ubl import XmlNode, validate
from format_factory.ubl.model.root_types import Invoice
from format_factory.ubl.model.typed import find, find_all_qname, find_qname

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_EXT_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
_EVIL = "urn:evil:attacker:namespace"


def test_find_itself_is_still_naively_vulnerable_a_known_documented_caveat() -> None:
    """Proven directly, not assumed: this is exactly why validate() must
    run before any find()-derived value is trusted."""
    spoofed = XmlNode.create(f"{{{_EVIL}}}ID", text="SPOOFED-VALUE")
    real = XmlNode.create(f"{{{_CBC}}}ID", text="INV-001")
    document = Invoice.build(children=(spoofed, real))

    assert find(document.root, "ID").text == "SPOOFED-VALUE"


def test_a_spoofed_sibling_from_an_unrelated_namespace_fails_validation() -> None:
    spoofed = XmlNode.create(f"{{{_EVIL}}}ID", text="SPOOFED-VALUE")
    real = XmlNode.create(f"{{{_CBC}}}ID", text="INV-001")
    document = Invoice.build(children=(spoofed, real))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.namespace.shadowed_element" for item in report.diagnostics)


def test_the_spoofing_order_does_not_matter_real_element_first_is_also_caught() -> None:
    real = XmlNode.create(f"{{{_CBC}}}ID", text="INV-001")
    spoofed = XmlNode.create(f"{{{_EVIL}}}ID", text="SPOOFED-VALUE")
    document = Invoice.build(children=(real, spoofed))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.namespace.shadowed_element" for item in report.diagnostics)


def test_the_diagnostic_names_the_shadowed_local_name_and_both_namespaces() -> None:
    spoofed = XmlNode.create(f"{{{_EVIL}}}ID", text="x")
    real = XmlNode.create(f"{{{_CBC}}}ID", text="y")
    document = Invoice.build(children=(spoofed, real))

    report = validate(document)

    shadow = next(
        item for item in report.diagnostics if item.code == "ubl.namespace.shadowed_element"
    )
    assert "'ID'" in shadow.message
    assert _EVIL in shadow.message
    assert _CBC in shadow.message


def test_a_document_with_no_namespace_collision_is_unaffected() -> None:
    """Control: this is the same shape as every existing fixture in this
    package's whole suite (878 tests, zero false positives) -- distinct
    local names never trigger the check."""
    document = Invoice.build(
        children=(
            XmlNode.create(f"{{{_CBC}}}ID", text="INV-001"),
            XmlNode.create(f"{{{_CBC}}}IssueDate", text="2024-01-01"),
        )
    )

    report = validate(document)

    assert not any(
        item.code == "ubl.namespace.shadowed_element" for item in report.diagnostics
    )


def test_nested_shadowing_deeper_in_the_tree_is_also_detected() -> None:
    """The check walks the whole tree, not only the document root."""
    spoofed_child = XmlNode.create(f"{{{_EVIL}}}Amount", text="999999")
    real_child = XmlNode.create(f"{{{_CBC}}}Amount", text="42")
    nested_parent = XmlNode.create(
        f"{{{_CBC}}}LegalMonetaryTotal", children=(spoofed_child, real_child)
    )
    document = Invoice.build(
        children=(XmlNode.create(f"{{{_CBC}}}ID", text="INV-001"), nested_parent)
    )

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.namespace.shadowed_element" for item in report.diagnostics)


def test_the_check_does_not_recurse_into_opaque_extension_content() -> None:
    """ext:ExtensionContent wraps arbitrary, opaque vendor content this
    package never queries via find()/find_all() by field name -- applying
    the shadowing check inside it would be a false-positive risk, not a
    real protection, so it is deliberately excluded."""
    vendor_a = XmlNode.create("{urn:vendor:a}Marker", text="a")
    vendor_b = XmlNode.create("{urn:vendor:b}Marker", text="b")
    extension_content = XmlNode.create(
        f"{{{_EXT_NS}}}ExtensionContent", children=(vendor_a, vendor_b)
    )
    extension = XmlNode.create(f"{{{_EXT_NS}}}UBLExtension", children=(extension_content,))
    extensions = XmlNode.create(f"{{{_EXT_NS}}}UBLExtensions", children=(extension,))
    document = Invoice.build(
        children=(extensions, XmlNode.create(f"{{{_CBC}}}ID", text="INV-001"))
    )

    report = validate(document)

    assert not any(
        item.code == "ubl.namespace.shadowed_element" for item in report.diagnostics
    )


# ── find_qname()/find_all_qname(): the namespace-precise lookup primitive ──


def test_find_qname_correctly_disambiguates_a_spoofed_sibling() -> None:
    """The exact scenario find() gets wrong (test_find_itself_is_still_
    naively_vulnerable_a_known_documented_caveat above), resolved
    correctly by the namespace-precise primitive instead."""
    spoofed = XmlNode.create(f"{{{_EVIL}}}ID", text="SPOOFED-VALUE")
    real = XmlNode.create(f"{{{_CBC}}}ID", text="INV-001")
    document = Invoice.build(children=(spoofed, real))

    assert find_qname(document.root, _CBC, "ID").text == "INV-001"
    assert find_qname(document.root, _EVIL, "ID").text == "SPOOFED-VALUE"


def test_find_qname_returns_none_for_a_namespace_with_no_matching_child() -> None:
    document = Invoice.build(children=(XmlNode.create(f"{{{_CBC}}}ID", text="INV-001"),))

    assert find_qname(document.root, _EVIL, "ID") is None


def test_find_qname_matches_finds_own_result_when_there_is_no_collision() -> None:
    """Not a behavior change for the common, unambiguous case -- both
    primitives agree when there is nothing to disambiguate."""
    document = Invoice.build(children=(XmlNode.create(f"{{{_CBC}}}ID", text="INV-001"),))

    assert find_qname(document.root, _CBC, "ID").text == find(document.root, "ID").text


def test_find_all_qname_excludes_a_same_local_name_sibling_from_another_namespace() -> None:
    spoofed = XmlNode.create(f"{{{_EVIL}}}Amount", text="999999")
    real = XmlNode.create(f"{{{_CBC}}}Amount", text="42")
    document = Invoice.build(children=(spoofed, real))

    matches = find_all_qname(document.root, _CBC, "Amount")

    assert [node.text for node in matches] == ["42"]


def test_find_all_qname_preserves_document_order_among_genuine_matches() -> None:
    first = XmlNode.create(f"{{{_CBC}}}Line", text="1")
    second = XmlNode.create(f"{{{_CBC}}}Line", text="2")
    third = XmlNode.create(f"{{{_CBC}}}Line", text="3")
    document = Invoice.build(children=(first, second, third))

    matches = find_all_qname(document.root, _CBC, "Line")

    assert [node.text for node in matches] == ["1", "2", "3"]

"""UBL-MODEL-001 / UBL-PARSE-001 -- the CBC/CAC namespace convention itself,
proven as a standalone architectural fact.

MUST (SAL-UBL-OBL-0AFE5C0F7BA8AC02 / SAL-UBL-OBL-2E913739AA1D3A6C, "UBL
common library - CBC namespace"): "Common basic components live in the
CommonBasicComponents-2 namespace conventionally prefixed cbc and represent
typed leaf values."

MUST (SAL-UBL-OBL-EDA03586C360349D / SAL-UBL-OBL-7B14DCF48B17C706, "UBL
common library - CAC namespace"): "Common aggregate components live in the
CommonAggregateComponents-2 namespace conventionally prefixed cac and
represent typed composite structures."

Before this slice, no single test asserted this convention as a standalone
fact -- it was only implicit in the pervasive use of cbc:/cac:-qualified
element names throughout every other test in the suite. The underlying
mechanism was already real and correct: model/document.py's
`_CBC_NAMESPACE` constant and codec/writer/writer.py's `ET.register_namespace`
calls for "cbc"/"cac" both bind the exact CommonBasicComponents-2 /
CommonAggregateComponents-2 URIs. This file proves it directly: a parsed
document resolves cbc-prefixed elements to the CBC URI and cac-prefixed
elements to the CAC URI; cbc elements are leaf values (no children, plain
text) while cac elements are composite structures (children, no direct
text); and a written document declares both namespace bindings with the
correct prefixes and URIs, surviving a full dumps()/loads() round trip.
"""

from __future__ import annotations

from format_factory.ubl import dumps, loads

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice(body: str) -> str:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{CBC}" xmlns:cac="{CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"{body}"
        f"</Invoice>"
    )


_LINE = (
    "<cac:InvoiceLine>"
    "<cbc:ID>1</cbc:ID>"
    '<cbc:InvoicedQuantity unitCode="KGM">2</cbc:InvoicedQuantity>'
    '<cbc:LineExtensionAmount currencyID="EUR">20.00</cbc:LineExtensionAmount>'
    "<cac:Item><cbc:Name>Coffee beans</cbc:Name></cac:Item>"
    "</cac:InvoiceLine>"
)
_MONETARY_TOTAL = (
    "<cac:LegalMonetaryTotal>"
    '<cbc:LineExtensionAmount currencyID="EUR">20.00</cbc:LineExtensionAmount>'
    '<cbc:PayableAmount currencyID="EUR">20.00</cbc:PayableAmount>'
    "</cac:LegalMonetaryTotal>"
)


def _document():
    return loads(_invoice(_LINE + _MONETARY_TOTAL).encode())


def test_a_cbc_prefixed_element_resolves_to_the_common_basic_components_uri() -> None:
    document = _document()

    id_element = next(child for child in document.root.children if child.qname.endswith("}ID"))

    assert id_element.qname == f"{{{CBC}}}ID"


def test_a_cac_prefixed_element_resolves_to_the_common_aggregate_components_uri() -> None:
    document = _document()

    invoice_line = next(
        child for child in document.root.children if child.qname.endswith("}InvoiceLine")
    )

    assert invoice_line.qname == f"{{{CAC}}}InvoiceLine"


def test_cbc_elements_are_leaf_values_with_no_children() -> None:
    """"represent typed leaf values" -- a cbc element carries text and has
    no child elements of its own."""
    document = _document()

    id_element = next(child for child in document.root.children if child.qname.endswith("}ID"))

    assert id_element.text.strip() == "INV-001"
    assert id_element.children == ()


def test_cac_elements_are_composite_structures_with_children() -> None:
    """"represent typed composite structures" -- a cac element carries
    child elements rather than direct text."""
    document = _document()

    invoice_line = next(
        child for child in document.root.children if child.qname.endswith("}InvoiceLine")
    )

    assert len(invoice_line.children) > 0
    assert invoice_line.text.strip() == ""


def test_writing_the_document_declares_both_namespace_bindings_with_the_correct_uris() -> None:
    document = _document()

    written = dumps(document)

    assert f'xmlns:cbc="{CBC}"'.encode() in written
    assert f'xmlns:cac="{CAC}"'.encode() in written


def test_the_namespace_convention_survives_a_full_round_trip() -> None:
    document = _document()

    reloaded = loads(dumps(document))

    id_element = next(child for child in reloaded.root.children if child.qname.endswith("}ID"))
    invoice_line = next(
        child for child in reloaded.root.children if child.qname.endswith("}InvoiceLine")
    )
    assert id_element.qname == f"{{{CBC}}}ID"
    assert invoice_line.qname == f"{{{CAC}}}InvoiceLine"

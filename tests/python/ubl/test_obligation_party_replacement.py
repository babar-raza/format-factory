"""UBL-EDIT-001 -- party-scoped update, narrowing further alongside
lines.py's own line-scoped narrowing.

MUST (SAL-UBL-OBL-237188D47391391E): "CRUD for core business components
with schema-order preservation; edits cannot produce elements the schema
forbids at that position." -- narrowed to updating an already-present
cac:Party inside an existing cac:AccountingSupplierParty or
cac:AccountingCustomerParty wrapper (see components.py's own module
docstring for the honest scope boundary: creating a brand-new wrapper
remains the still-unbuilt arbitrary-position insertion problem).
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblValidationError, load
from format_factory.ubl.components import replace_party
from format_factory.ubl.model import XmlNode

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_CBC_NS = f"{{{_CBC}}}"
_CAC_NS = f"{{{_CAC}}}"


def _invoice_bytes(*, supplier_uri: str = "http://x.com", include_customer: bool = True) -> bytes:
    customer = (
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        if include_customer
        else ""
    )
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        f'<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>{supplier_uri}</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        f"{customer}"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        "<cac:InvoiceLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        "</cac:InvoiceLine>"
        "</Invoice>"
    ).encode()


def _party_node(*, website: str) -> XmlNode:
    return XmlNode.create(
        f"{_CAC_NS}Party",
        children=(XmlNode.create(f"{_CBC_NS}WebsiteURI", text=website),),
    )


# -- Replacing an existing party succeeds and stays valid --------------


def test_replace_party_swaps_the_supplier_party() -> None:
    document = load(_invoice_bytes())
    new_party = _party_node(website="http://new-supplier.example")

    edited = replace_party(document, role="AccountingSupplierParty", new_party=new_party)

    (supplier,) = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}AccountingSupplierParty"
    ]
    (party,) = supplier.children
    assert party == new_party


def test_replace_party_swaps_the_customer_party() -> None:
    document = load(_invoice_bytes())
    new_party = _party_node(website="http://new-customer.example")

    edited = replace_party(document, role="AccountingCustomerParty", new_party=new_party)

    (customer,) = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}AccountingCustomerParty"
    ]
    (party,) = customer.children
    assert party == new_party


def test_replace_party_does_not_mutate_the_original_document() -> None:
    document = load(_invoice_bytes(supplier_uri="http://original.example"))

    replace_party(
        document, role="AccountingSupplierParty", new_party=_party_node(website="http://other.example")
    )

    (supplier,) = [
        child for child in document.root.children if child.qname == f"{_CAC_NS}AccountingSupplierParty"
    ]
    (party,) = supplier.children
    (uri,) = party.children
    assert uri.text == "http://original.example"


def test_replace_party_leaves_every_other_root_child_untouched() -> None:
    document = load(_invoice_bytes())

    edited = replace_party(
        document, role="AccountingCustomerParty", new_party=_party_node(website="http://new.example")
    )

    original_others = [
        child for child in document.root.children if child.qname != f"{_CAC_NS}AccountingCustomerParty"
    ]
    edited_others = [
        child for child in edited.root.children if child.qname != f"{_CAC_NS}AccountingCustomerParty"
    ]
    assert original_others == edited_others


# -- Refusing what this narrowed API does not support --------------------


def test_replace_party_refuses_an_unknown_role() -> None:
    document = load(_invoice_bytes())

    with pytest.raises(UblValidationError, match="role must be one of"):
        replace_party(
            document, role="AccountingDeliveryParty", new_party=_party_node(website="http://x.example")
        )


def test_replace_party_refuses_a_non_party_replacement_node() -> None:
    document = load(_invoice_bytes())
    not_a_party = XmlNode.create(f"{_CAC_NS}PaymentMeans")

    with pytest.raises(UblValidationError, match="cac:Party element"):
        replace_party(document, role="AccountingSupplierParty", new_party=not_a_party)


def test_replace_party_refuses_when_the_wrapper_does_not_exist() -> None:
    """Creating a brand-new wrapper is the still-unbuilt arbitrary-position
    insertion problem -- correctly refused, not silently created."""
    document = load(_invoice_bytes(include_customer=False))

    with pytest.raises(UblValidationError, match="no existing AccountingCustomerParty"):
        replace_party(
            document, role="AccountingCustomerParty", new_party=_party_node(website="http://new.example")
        )

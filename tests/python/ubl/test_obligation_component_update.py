"""UBL-EDIT-001 -- generic core-business-component update, further
narrowing alongside lines.py's own line-scoped narrowing and
components.py's own replace_party().

MUST (SAL-UBL-OBL-237188D47391391E): "CRUD for core business components
with schema-order preservation; edits cannot produce elements the schema
forbids at that position." -- narrowed to updating an already-present
occurrence of any repeating root-level component (cac:PaymentMeans,
cac:TaxTotal, cac:AllowanceCharge, ...), not just Party. Creating an
additional occurrence remains the still-unbuilt arbitrary-position
insertion problem (see components.py's own module docstring).
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblValidationError, load
from format_factory.ubl.components import update_component
from format_factory.ubl.model import XmlNode

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_CBC_NS = f"{{{_CBC}}}"
_CAC_NS = f"{{{_CAC}}}"


def _payment_means_xml(*, code: str) -> str:
    return f"<cac:PaymentMeans><cbc:PaymentMeansCode>{code}</cbc:PaymentMeansCode></cac:PaymentMeans>"


def _invoice_bytes(*, payment_means_codes: tuple[str, ...]) -> bytes:
    payment_means = "".join(_payment_means_xml(code=code) for code in payment_means_codes)
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        f"{payment_means}"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
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


def _payment_means_node(*, code: str) -> XmlNode:
    return XmlNode.create(
        f"{_CAC_NS}PaymentMeans",
        children=(XmlNode.create(f"{_CBC_NS}PaymentMeansCode", text=code),),
    )


# -- Updating an existing occurrence among a repeating component --------


def test_update_component_replaces_the_only_occurrence() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))
    new_node = _payment_means_node(code="30")

    edited = update_component(
        document, component_name="PaymentMeans", index=0, new_component=new_node
    )

    (payment_means,) = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    assert payment_means == new_node


def test_update_component_replaces_only_the_targeted_index_among_several() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10", "20", "42")))
    new_node = _payment_means_node(code="99")

    edited = update_component(
        document, component_name="PaymentMeans", index=1, new_component=new_node
    )

    payment_means = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    assert len(payment_means) == 3
    codes = [pm.children[0].text for pm in payment_means]
    assert codes == ["10", "99", "42"]


def test_update_component_does_not_mutate_the_original_document() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))

    update_component(
        document, component_name="PaymentMeans", index=0, new_component=_payment_means_node(code="30")
    )

    (payment_means,) = [
        child for child in document.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    assert payment_means.children[0].text == "10"


def test_update_component_leaves_every_other_root_child_untouched() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10", "20")))

    edited = update_component(
        document, component_name="PaymentMeans", index=0, new_component=_payment_means_node(code="99")
    )

    original_others = [
        child for child in document.root.children if child.qname != f"{_CAC_NS}PaymentMeans"
    ]
    edited_others = [
        child for child in edited.root.children if child.qname != f"{_CAC_NS}PaymentMeans"
    ]
    assert original_others == edited_others


# -- Refusing what this narrowed API does not support --------------------


def test_update_component_refuses_a_type_mismatched_replacement() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))
    wrong_type = XmlNode.create(f"{_CAC_NS}TaxTotal")

    with pytest.raises(UblValidationError, match="cac:PaymentMeans element"):
        update_component(document, component_name="PaymentMeans", index=0, new_component=wrong_type)


def test_update_component_refuses_an_out_of_range_index_when_none_exist() -> None:
    """Creating the first occurrence of a component a document has none of
    is the still-unbuilt arbitrary-position insertion problem."""
    document = load(_invoice_bytes(payment_means_codes=()))

    with pytest.raises(UblValidationError, match="out of range"):
        update_component(
            document, component_name="PaymentMeans", index=0, new_component=_payment_means_node(code="10")
        )


def test_update_component_refuses_an_out_of_range_index_beyond_existing_count() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10", "20")))

    with pytest.raises(UblValidationError, match="out of range"):
        update_component(
            document, component_name="PaymentMeans", index=2, new_component=_payment_means_node(code="30")
        )


def test_update_component_refuses_a_negative_index() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))

    with pytest.raises(UblValidationError, match="out of range"):
        update_component(
            document, component_name="PaymentMeans", index=-1, new_component=_payment_means_node(code="30")
        )

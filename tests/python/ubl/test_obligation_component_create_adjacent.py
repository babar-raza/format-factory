"""UBL-EDIT-001 -- Create for an additional occurrence of an
already-present component, narrowing the "Create" half of this
obligation's own remaining gap (Update was already closed by
replace_party()/update_component()).

MUST (SAL-UBL-OBL-237188D47391391E): "CRUD for core business components
with schema-order preservation; edits cannot produce elements the schema
forbids at that position." -- narrowed to inserting an ADDITIONAL
occurrence of a repeating component (cac:PaymentMeans, cac:TaxTotal,
cac:AllowanceCharge, ...) immediately after the last existing same-name
occurrence, which is always schema-position-correct per XSD sequence
semantics for repeating elements (see components.py's own module
docstring). Inserting the FIRST occurrence of a component type a
document has none of was, at the time this file was first written, the
still-unbuilt, genuinely harder half -- now closed unconditionally (no
optional dependency required, since FF6-UBL-EDIT-FIRST-OCCURRENCE-002)
by `test_obligation_component_first_occurrence_insertion.py`; this file
keeps only the additional-occurrence scope its own name describes.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblValidationError, load
from format_factory.ubl.components import add_component
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


# -- Adding an additional occurrence next to an existing sibling --------


def test_add_component_appends_after_the_only_existing_occurrence() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))
    new_node = _payment_means_node(code="30")

    edited = add_component(document, component_name="PaymentMeans", new_component=new_node)

    payment_means = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    assert len(payment_means) == 2
    codes = [pm.children[0].text for pm in payment_means]
    assert codes == ["10", "30"]


def test_add_component_appends_after_the_last_of_several_existing() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10", "20")))

    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node(code="42")
    )

    payment_means = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    codes = [pm.children[0].text for pm in payment_means]
    assert codes == ["10", "20", "42"]


def test_add_component_result_stays_schema_valid() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))

    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node(code="30")
    )

    from format_factory.ubl import validate

    assert validate(edited).is_valid


def test_add_component_does_not_mutate_the_original_document() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))

    add_component(document, component_name="PaymentMeans", new_component=_payment_means_node(code="30"))

    payment_means = [
        child for child in document.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    assert len(payment_means) == 1
    assert payment_means[0].children[0].text == "10"


def test_add_component_leaves_every_other_root_child_untouched() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))

    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node(code="30")
    )

    original_others = [
        child for child in document.root.children if child.qname != f"{_CAC_NS}PaymentMeans"
    ]
    edited_others = [
        child for child in edited.root.children if child.qname != f"{_CAC_NS}PaymentMeans"
    ]
    assert original_others == edited_others


def test_add_component_reorders_the_new_components_own_internal_fields() -> None:
    """PaymentMeans is in _ORDER_CHECKED_COMPONENTS
    (PaymentMeansCode/PaymentDueDate/PayeeFinancialAccount) -- a caller
    who constructs it with fields out of order still gets schema-valid
    output, the same benefit add_line already gives."""
    document = load(_invoice_bytes(payment_means_codes=("10",)))
    out_of_order = XmlNode.create(
        f"{_CAC_NS}PaymentMeans",
        children=(
            XmlNode.create(f"{_CBC_NS}PaymentDueDate", text="2026-02-01"),
            XmlNode.create(f"{_CBC_NS}PaymentMeansCode", text="42"),
        ),
    )

    edited = add_component(document, component_name="PaymentMeans", new_component=out_of_order)

    payment_means = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    new_one = payment_means[-1]
    field_names = [child.qname.rsplit("}", 1)[-1] for child in new_one.children]
    assert field_names == ["PaymentMeansCode", "PaymentDueDate"]


# -- Refusing what this narrowed API does not support --------------------


def test_add_component_refuses_a_type_mismatched_new_component() -> None:
    document = load(_invoice_bytes(payment_means_codes=("10",)))
    wrong_type = XmlNode.create(f"{_CAC_NS}TaxTotal")

    with pytest.raises(UblValidationError, match="cac:PaymentMeans element"):
        add_component(document, component_name="PaymentMeans", new_component=wrong_type)


def test_add_component_no_longer_unconditionally_refuses_a_first_occurrence() -> None:
    """Superseded by test_obligation_component_first_occurrence_insertion.py:
    inserting the FIRST occurrence of a type the document has none of is
    now supported unconditionally (real schema-position knowledge, not a
    guess, and no optional dependency required since
    FF6-UBL-EDIT-FIRST-OCCURRENCE-002). Kept here, narrowly, only to prove
    this file's own additional-occurrence scope note above is accurate --
    not a positive test of the new capability itself."""
    document = load(_invoice_bytes(payment_means_codes=()))

    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node(code="10")
    )

    payment_means = [
        child for child in edited.root.children if child.qname == f"{_CAC_NS}PaymentMeans"
    ]
    assert len(payment_means) == 1

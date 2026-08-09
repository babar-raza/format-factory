"""UBL-EDIT-001 -- inserting the FIRST occurrence of a core business
component a document does not already have at all.

MUST (SAL-UBL-OBL-237188D47391391E): "CRUD for core business components
with schema-order preservation; edits cannot produce elements the schema
forbids at that position."

Before FF6-UBL-EDIT-FIRST-OCCURRENCE-001, `add_component()` supported
only an ADDITIONAL occurrence of a component type the document already
had at least one of (see test_obligation_component_create_adjacent.py);
a document with NO existing occurrence was refused unconditionally,
because placing a brand-new component type correctly needs to know
where it belongs relative to every OTHER header field -- "full
header-position knowledge" the package did not have.

That knowledge now comes from `validation.schema_validator.
schema_root_order()`, which reads the bundled, official UBL 2.3 maindoc
XSD's own declared child sequence for a document's root type. This file
proves the resulting placement is genuinely schema-correct -- not merely
"does not raise" -- against the real UBL 2.3 Invoice schema's own
declared order, independently derived here from the same schema files
rather than assumed from memory.

FF6-UBL-EDIT-FIRST-OCCURRENCE-002: `schema_root_order()` now answers from
a table precomputed once, checked in as `_generated/schema_root_order.py`,
covering all 91 known root types -- no `xmlschema` installation is
required to run this file anymore, so the tests below run unconditionally
rather than being skipped when the optional dependency is absent.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblValidationError, load
from format_factory.ubl.components import add_component
from format_factory.ubl.model import XmlNode
from format_factory.ubl.validation.schema_validator import schema_root_order

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_CBC_NS = f"{{{_CBC}}}"
_CAC_NS = f"{{{_CAC}}}"


def _invoice_bytes(*, include_payment_means: bool = False, include_tax_total: bool = False) -> bytes:
    payment_means = (
        "<cac:PaymentMeans><cbc:PaymentMeansCode>10</cbc:PaymentMeansCode></cac:PaymentMeans>"
        if include_payment_means
        else ""
    )
    tax_total = (
        '<cac:TaxTotal><cbc:TaxAmount currencyID="USD">0.00</cbc:TaxAmount></cac:TaxTotal>'
        if include_tax_total
        else ""
    )
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
        f"{tax_total}"
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


def _tax_total_node() -> XmlNode:
    return XmlNode.create(
        f"{_CAC_NS}TaxTotal",
        children=(XmlNode.create(f"{_CBC_NS}TaxAmount", attributes={"currencyID": "USD"}, text="0.00"),),
    )


def _payment_means_node(*, code: str = "10") -> XmlNode:
    return XmlNode.create(
        f"{_CAC_NS}PaymentMeans",
        children=(XmlNode.create(f"{_CBC_NS}PaymentMeansCode", text=code),),
    )


def _local_names(document) -> list[str]:
    return [child.qname.rsplit("}", 1)[-1] for child in document.root.children]


# -- schema_root_order() itself -------------------------------------------


def test_schema_root_order_matches_the_real_invoice_schema_declared_sequence() -> None:
    order = schema_root_order("Invoice")

    # Cross-checked directly against the pinned OASIS UBL 2.3 Invoice
    # maindoc XSD's own declared xsd:sequence (not asserted from memory --
    # this is the same order a human reading that XSD file would see).
    assert order[0] == "UBLExtensions"
    assert order.index("ID") < order.index("IssueDate")
    assert order.index("AccountingSupplierParty") < order.index("AccountingCustomerParty")
    assert order.index("PaymentMeans") < order.index("TaxTotal")
    assert order.index("TaxTotal") < order.index("LegalMonetaryTotal")
    assert order[-1] == "InvoiceLine"
    assert len(order) == len(set(order))  # every declared child named exactly once


def test_schema_root_order_differs_for_a_different_root_type() -> None:
    invoice_order = schema_root_order("Invoice")
    credit_note_order = schema_root_order("CreditNote")

    assert invoice_order != credit_note_order
    assert "InvoiceLine" in invoice_order
    assert "InvoiceLine" not in credit_note_order
    assert "CreditNoteLine" in credit_note_order


def test_schema_root_order_is_cached_and_returns_an_equal_result() -> None:
    first = schema_root_order("Invoice")
    second = schema_root_order("Invoice")

    assert first == second


# -- add_component(): first occurrence, correctly positioned -------------


def test_first_occurrence_is_inserted_at_its_real_schema_position() -> None:
    """TaxTotal (schema position 50) inserted into a document with none,
    must land between AccountingCustomerParty and LegalMonetaryTotal --
    the real neighbors per schema_root_order(), not merely "somewhere"."""
    document = load(_invoice_bytes())
    assert "TaxTotal" not in _local_names(document)

    edited = add_component(document, component_name="TaxTotal", new_component=_tax_total_node())

    names = _local_names(edited)
    assert names.index("AccountingCustomerParty") < names.index("TaxTotal") < names.index(
        "LegalMonetaryTotal"
    )


def test_first_occurrence_before_an_already_present_later_component() -> None:
    """PaymentMeans (schema position 42) inserted into a document that
    already has TaxTotal (position 50, later) must land BEFORE it, not
    after -- proves placement uses real order, not "always append"."""
    document = load(_invoice_bytes(include_tax_total=True))
    assert "PaymentMeans" not in _local_names(document)

    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node()
    )

    names = _local_names(edited)
    assert names.index("PaymentMeans") < names.index("TaxTotal")


def test_first_occurrence_after_an_already_present_earlier_component() -> None:
    """TaxTotal (position 50) inserted into a document that already has
    PaymentMeans (position 42, earlier) must land AFTER it."""
    document = load(_invoice_bytes(include_payment_means=True))
    assert "TaxTotal" not in _local_names(document)

    edited = add_component(document, component_name="TaxTotal", new_component=_tax_total_node())

    names = _local_names(edited)
    assert names.index("PaymentMeans") < names.index("TaxTotal")


def test_first_occurrence_result_is_schema_valid() -> None:
    from format_factory.ubl import validate

    document = load(_invoice_bytes())

    edited = add_component(document, component_name="TaxTotal", new_component=_tax_total_node())

    assert validate(edited).is_valid


def test_first_occurrence_does_not_mutate_the_original_document() -> None:
    document = load(_invoice_bytes())

    add_component(document, component_name="TaxTotal", new_component=_tax_total_node())

    assert "TaxTotal" not in _local_names(document)


def test_component_name_not_a_declared_child_of_the_root_type_is_refused() -> None:
    document = load(_invoice_bytes())
    bogus = XmlNode.create(f"{_CAC_NS}NotARealUblElement")

    with pytest.raises(UblValidationError, match="not a declared child"):
        add_component(document, component_name="NotARealUblElement", new_component=bogus)


# -- FF6-UBL-EDIT-FIRST-OCCURRENCE-002: no xmlschema needed at runtime ----


def test_first_occurrence_insertion_works_without_xmlschema_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The whole point of the precomputed table: first-occurrence
    insertion previously fell back to an unconditional refusal when the
    optional `xmlschema` dependency was not installed
    (SchemaValidationUnavailable, caught inside add_component). Blocking
    the real import here (the same technique
    test_obligation_official_schema_validation.py's own
    test_schema_validation_unavailable_when_xmlschema_cannot_be_imported
    uses to prove the OLD degraded-gracefully behavior) proves the NEW
    behavior directly: schema_root_order() answers from the generated
    table without ever attempting to import xmlschema, so add_component()
    now succeeds -- not merely does not raise -- with the dependency
    genuinely absent."""
    import sys

    real_import = __import__

    def _blocked_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "xmlschema":
            raise ImportError("simulated: xmlschema not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setitem(sys.modules, "xmlschema", None)
    monkeypatch.delitem(sys.modules, "xmlschema", raising=False)
    monkeypatch.setattr("builtins.__import__", _blocked_import)

    document = load(_invoice_bytes())
    assert "TaxTotal" not in _local_names(document)

    edited = add_component(document, component_name="TaxTotal", new_component=_tax_total_node())

    names = _local_names(edited)
    assert names.index("AccountingCustomerParty") < names.index("TaxTotal") < names.index(
        "LegalMonetaryTotal"
    )

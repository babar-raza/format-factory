"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 / UBL-SIGN-001 -- element order validation.

MUST (SAL-UBL-OBL-3B43504E9C74003C and its cross-capability duplicates):
"(UBL naming and design rules - element order) Child elements inside UBL
aggregate components must appear in the order declared by the schema
sequence model for the document to be valid."

This is a genuine, spec-grounded slice: diagnoses a present, checked child
element that appears out of its declared relative order among the
already-modeled single-occurrence fields the cardinality cluster
(events 216-223) already checks -- cac:Party/cac:PostalAddress/
cac:Contact/cac:PaymentMeans/cac:PayeeFinancialAccount/cac:CreditNoteLine/
cac:Response/cac:DocumentReference/cac:InvoiceLine/cac:TaxSubtotal/
cac:TaxTotal/cac:LegalMonetaryTotal/cac:ExternalReference. Every
component's exact declared child order is read directly from the pinned
OASIS UBL 2.3 CommonAggregateComponents schema, filtered and order-
preserved PROGRAMMATICALLY (not transcribed by hand): a manual
transcription error on cac:LegalMonetaryTotal's own order was caught this
way -- cbc:PayableAmount is declared LAST in the schema (after
ChargeTotalAmount), not second (after LineExtensionAmount) as this
package's own pre-existing frozenset iteration order for the unrelated
cardinality check might suggest if read carelessly.

Deliberately narrow, matching the cardinality cluster's own established
scope discipline: covers only relative order among already-modeled
fields, not every child of every UBL complexType. Does not itself
re-check cardinality -- a genuinely duplicated field is handled
separately by the existing cardinality check.
"""

from __future__ import annotations

from format_factory.ubl import loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_with(body: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"{body}"
        f"</Invoice>"
    ).encode()


def test_a_party_with_postal_address_before_contact_validates_cleanly() -> None:
    """The schema declares PostalAddress before Contact within PartyType."""
    body = (
        "<cac:AccountingSupplierParty><cac:Party>"
        "<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>"
        "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
        "</cac:Party></cac:AccountingSupplierParty>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_a_party_with_contact_before_postal_address_is_an_order_violation() -> None:
    body = (
        "<cac:AccountingSupplierParty><cac:Party>"
        "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
        "<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>"
        "</cac:Party></cac:AccountingSupplierParty>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_a_postal_address_with_fields_in_declared_order_validates_cleanly() -> None:
    """The schema declares StreetName, then CityName, then PostalZone, then
    Country within AddressType (cac:PostalAddress's underlying type)."""
    body = (
        "<cac:AccountingSupplierParty><cac:Party><cac:PostalAddress>"
        "<cbc:StreetName>Main St</cbc:StreetName>"
        "<cbc:CityName>Springfield</cbc:CityName>"
        "<cbc:PostalZone>12345</cbc:PostalZone>"
        "<cac:Country><cbc:IdentificationCode>US</cbc:IdentificationCode></cac:Country>"
        "</cac:PostalAddress></cac:Party></cac:AccountingSupplierParty>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_a_postal_address_with_postal_zone_before_city_name_is_an_order_violation() -> None:
    body = (
        "<cac:AccountingSupplierParty><cac:Party><cac:PostalAddress>"
        "<cbc:PostalZone>12345</cbc:PostalZone>"
        "<cbc:CityName>Springfield</cbc:CityName>"
        "</cac:PostalAddress></cac:Party></cac:AccountingSupplierParty>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_a_legal_monetary_total_with_payable_amount_last_validates_cleanly() -> None:
    """The schema declares PayableAmount LAST within MonetaryTotalType
    (the real complexType behind cac:LegalMonetaryTotal), after
    LineExtensionAmount/TaxExclusiveAmount/TaxInclusiveAmount/
    AllowanceTotalAmount/ChargeTotalAmount -- confirmed programmatically
    against the pinned schema, catching a manual-transcription risk."""
    body = (
        "<cac:LegalMonetaryTotal>"
        "<cbc:LineExtensionAmount>100</cbc:LineExtensionAmount>"
        "<cbc:TaxExclusiveAmount>90</cbc:TaxExclusiveAmount>"
        "<cbc:TaxInclusiveAmount>95</cbc:TaxInclusiveAmount>"
        "<cbc:AllowanceTotalAmount>5</cbc:AllowanceTotalAmount>"
        "<cbc:ChargeTotalAmount>0</cbc:ChargeTotalAmount>"
        "<cbc:PayableAmount>95</cbc:PayableAmount>"
        "</cac:LegalMonetaryTotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_a_legal_monetary_total_with_payable_amount_before_tax_exclusive_amount_is_a_violation() -> None:
    body = (
        "<cac:LegalMonetaryTotal>"
        "<cbc:PayableAmount>95</cbc:PayableAmount>"
        "<cbc:TaxExclusiveAmount>90</cbc:TaxExclusiveAmount>"
        "</cac:LegalMonetaryTotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_unchecked_fields_interspersed_among_checked_fields_do_not_disturb_ordering() -> None:
    """Fields this package does not yet model as checkable (e.g.
    cbc:WebsiteURI, cac:PartyLegalEntity) may legitimately appear between
    checked fields without triggering a false violation -- only the
    relative order among the checked fields themselves is verified."""
    body = (
        "<cac:AccountingSupplierParty><cac:Party>"
        "<cbc:WebsiteURI>http://example.com</cbc:WebsiteURI>"
        "<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>"
        "<cac:PartyLegalEntity/>"
        "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
        "</cac:Party></cac:AccountingSupplierParty>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_an_invoice_line_with_id_before_invoiced_quantity_before_line_extension_amount_before_item_validates_cleanly() -> None:
    body = (
        "<cac:InvoiceLine>"
        "<cbc:ID>L1</cbc:ID>"
        "<cbc:InvoicedQuantity>1</cbc:InvoicedQuantity>"
        "<cbc:LineExtensionAmount>10</cbc:LineExtensionAmount>"
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        "</cac:InvoiceLine>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_an_invoice_line_with_item_before_id_is_an_order_violation() -> None:
    body = (
        "<cac:InvoiceLine>"
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        "<cbc:ID>L1</cbc:ID>"
        "</cac:InvoiceLine>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)

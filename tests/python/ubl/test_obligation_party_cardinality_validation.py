"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 -- cardinality validation, a first spec-grounded slice.

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates):
"UBL document schemas are W3C XML Schema definitions and conforming
documents must be valid against the maindoc schema of their declared
type." validator.py's own docstring states this chassis validation "is
deliberately not an XSD-conformance claim" and that "full schema and
cardinality validation remains a mandatory open obligation."

Before this slice: no cardinality checking existed anywhere -- a
document declaring 2 cac:PostalAddress elements under one cac:Party (or
2 cbc:StreetName elements under one cac:PostalAddress) validated
cleanly, with the model's own projector functions (postal_address_of,
etc.) silently using only the first match via find() and discarding the
rest.

This is a deliberately narrow FIRST slice of the larger "full schema and
cardinality validation" obligation, not a claim of completeness: it
covers exactly the minOccurs=0 maxOccurs=1 fields already modeled as
typed accessors on Party/PostalAddress/Contact (party.postal_address,
party.contact; postal_address.street_name/city_name/postal_zone/country;
contact.name/telephone/electronic_mail), grounded directly in the pinned
OASIS UBL 2.3 CommonAggregateComponents schema's own PartyType/
AddressType/ContactType complexType definitions
(xsd/common/UBL-CommonAggregateComponents-2.3.xsd, read from the pinned
release ZIP). Every other UBL complexType's cardinality remains
unchecked -- a genuinely larger, separate undertaking this slice does
not attempt or claim.
"""

from __future__ import annotations

from format_factory.ubl import XmlNode, loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_with_supplier_party(party_body: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AccountingSupplierParty><cac:Party>{party_body}</cac:Party>"
        f"</cac:AccountingSupplierParty>"
        f"</Invoice>"
    ).encode()


# ── cac:Party: PostalAddress and Contact are each 0..1 in the schema ───────


def test_a_party_with_a_single_postal_address_validates_cleanly() -> None:
    body = "<cac:PostalAddress><cbc:CityName>Springfield</cbc:CityName></cac:PostalAddress>"

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is True


def test_a_party_with_two_postal_addresses_is_a_cardinality_violation() -> None:
    body = (
        "<cac:PostalAddress><cbc:CityName>Springfield</cbc:CityName></cac:PostalAddress>"
        "<cac:PostalAddress><cbc:CityName>Shelbyville</cbc:CityName></cac:PostalAddress>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_party_with_two_contacts_is_a_cardinality_violation() -> None:
    body = (
        "<cac:Contact><cbc:Name>Alice</cbc:Name></cac:Contact>"
        "<cac:Contact><cbc:Name>Bob</cbc:Name></cac:Contact>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_the_diagnostic_message_names_the_component_field_and_schema_rule() -> None:
    body = (
        "<cac:PostalAddress><cbc:CityName>A</cbc:CityName></cac:PostalAddress>"
        "<cac:PostalAddress><cbc:CityName>B</cbc:CityName></cac:PostalAddress>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    violation = next(
        item for item in report.diagnostics if item.code == "ubl.cardinality.exceeded"
    )
    assert "cac:Party" in violation.message
    assert "'PostalAddress'" in violation.message
    assert "0..1" in violation.message


# ── cac:PostalAddress: several leaf fields are each 0..1 ───────────────────


def test_a_postal_address_with_a_single_street_name_validates_cleanly() -> None:
    body = "<cac:PostalAddress><cbc:StreetName>Main St</cbc:StreetName></cac:PostalAddress>"

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is True


def test_a_postal_address_with_two_street_names_is_a_cardinality_violation() -> None:
    body = (
        "<cac:PostalAddress>"
        "<cbc:StreetName>Main St</cbc:StreetName>"
        "<cbc:StreetName>Second St</cbc:StreetName>"
        "</cac:PostalAddress>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_postal_address_with_two_countries_is_a_cardinality_violation() -> None:
    body = (
        "<cac:PostalAddress>"
        "<cac:Country><cbc:IdentificationCode>US</cbc:IdentificationCode></cac:Country>"
        "<cac:Country><cbc:IdentificationCode>CA</cbc:IdentificationCode></cac:Country>"
        "</cac:PostalAddress>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


# ── cac:Contact: leaf fields are each 0..1 ──────────────────────────────────


def test_a_contact_with_two_telephone_numbers_is_a_cardinality_violation() -> None:
    body = (
        "<cac:Contact>"
        "<cbc:Telephone>555-1111</cbc:Telephone>"
        "<cbc:Telephone>555-2222</cbc:Telephone>"
        "</cac:Contact>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


# ── Repeatable (0..unbounded) fields must never be flagged ─────────────────


def test_multiple_party_tax_schemes_are_not_a_violation_they_are_repeatable() -> None:
    body = (
        "<cac:PartyTaxScheme><cbc:CompanyID>VAT1</cbc:CompanyID>"
        "<cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>"
        "<cac:PartyTaxScheme><cbc:CompanyID>VAT2</cbc:CompanyID>"
        "<cac:TaxScheme><cbc:ID>GST</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is True


def test_multiple_party_names_are_not_a_violation_they_are_repeatable() -> None:
    body = (
        "<cac:PartyName><cbc:Name>Acme Corp</cbc:Name></cac:PartyName>"
        "<cac:PartyName><cbc:Name>Acme Inc</cbc:Name></cac:PartyName>"
    )

    report = validate(loads(_invoice_with_supplier_party(body)))

    assert report.is_valid is True


def test_nested_at_a_customer_party_is_also_checked_not_only_supplier() -> None:
    """The check walks the whole tree, not only AccountingSupplierParty."""
    document = (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AccountingCustomerParty><cac:Party>"
        "<cac:PostalAddress><cbc:CityName>A</cbc:CityName></cac:PostalAddress>"
        "<cac:PostalAddress><cbc:CityName>B</cbc:CityName></cac:PostalAddress>"
        "</cac:Party></cac:AccountingCustomerParty>"
        f"</Invoice>"
    ).encode()

    report = validate(loads(document))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)

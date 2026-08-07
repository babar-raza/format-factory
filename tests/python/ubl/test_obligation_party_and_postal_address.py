"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-CALC-001 / UBL-EDIT-001 / UBL-REF-001
-- cac:Party and cac:PostalAddress, an 8-way cross-capability duplicate.

MUST ("UBL common library - Party", 5-way cross-capability duplicate
rule_text: SAL-UBL-OBL-75FA432A5A176927 / AE02391EE2696F99 /
C4BD36751BD0B3AB / C73836B17D8ECDBC / E016695D69C2BC7D): "cac:Party is an
aggregate component type carrying party identification, names, postal
addresses, tax schemes, and contacts as child elements."

MUST ("UBL common library - Address", 3-way cross-capability duplicate
rule_text: SAL-UBL-OBL-5D2ED9EBC9246EDA / 63B4E9D295EF12C0 /
CADCC40DD4CD3689): "cac:PostalAddress is an aggregate component type
composed of street, city, postal zone, and country sub-elements."

Before this slice: no Party or PostalAddress dataclass existed anywhere in
the model at all -- confirmed by grepping the package for "class Party"
and "class PostalAddress" (zero hits). Both are now modeled in a new
module (model/party.py), grounded directly in the pinned OASIS UBL 2.3
release package's own vendored XSD (xsd/common/UBL-CommonAggregateComponents
-2.3.xsd, read from the ZIP, not a SAL-fact paraphrase or memory) -- the
same technique that unblocked PaymentMeans.payee_financial_account earlier
this session. See model/party.py's own module docstring for the exact
scope boundary (leaf-level fields each element's own complexType declares;
deeper nested structures the contract does not separately name, like
cac:RegistrationAddress inside cac:PartyTaxScheme, are not modeled).
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    Code,
    Contact,
    Country,
    Identifier,
    Party,
    PartyIdentification,
    PartyName,
    PartyTaxScheme,
    PostalAddress,
    TaxScheme,
    UblValidationError,
    XmlNode,
    contact_of,
    country_of,
    dumps,
    find,
    loads,
    party_identification_of,
    party_name_of,
    party_of,
    party_tax_scheme_of,
    postal_address_of,
    tax_scheme_of,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _leaf(local: str, text: str) -> XmlNode:
    return XmlNode.create("{" + CBC + "}" + local, text=text)


def _cac(local: str, children: tuple[XmlNode, ...]) -> XmlNode:
    return XmlNode.create("{" + CAC + "}" + local, children=children)


# ── cac:Country ──────────────────────────────────────────────────────────


def test_country_projects_with_code_and_name() -> None:
    node = _cac(
        "Country",
        (_leaf("IdentificationCode", "US"), _leaf("Name", "United States")),
    )

    country = country_of(node)

    assert country == Country(identification_code=Code("US"), name="United States")


def test_country_of_returns_none_for_a_missing_node() -> None:
    assert country_of(None) is None


# ── cac:PostalAddress ────────────────────────────────────────────────────


def test_postal_address_projects_with_its_four_named_sub_elements() -> None:
    node = _cac(
        "PostalAddress",
        (
            _leaf("StreetName", "1 Main St"),
            _leaf("CityName", "Springfield"),
            _leaf("PostalZone", "12345"),
            _cac("Country", (_leaf("IdentificationCode", "US"),)),
        ),
    )

    address = postal_address_of(node)

    assert address == PostalAddress(
        street_name="1 Main St",
        city_name="Springfield",
        postal_zone="12345",
        country=Country(identification_code=Code("US")),
    )


def test_postal_address_fields_are_each_independently_optional() -> None:
    address = postal_address_of(_cac("PostalAddress", (_leaf("CityName", "Springfield"),)))

    assert address == PostalAddress(city_name="Springfield")


def test_postal_address_of_returns_none_for_a_missing_node() -> None:
    assert postal_address_of(None) is None


# ── cac:PartyIdentification / cac:PartyName ─────────────────────────────


def test_party_identification_projects_with_its_id() -> None:
    node = _cac("PartyIdentification", (_leaf("ID", "VAT-123"),))

    projected = party_identification_of(node)

    assert projected == PartyIdentification(id=Identifier("VAT-123"))


def test_party_identification_requires_an_id() -> None:
    with pytest.raises(UblValidationError):
        party_identification_of(_cac("PartyIdentification", ()))


def test_party_name_projects_with_its_name() -> None:
    node = _cac("PartyName", (_leaf("Name", "Acme Corp"),))

    assert party_name_of(node) == PartyName(name="Acme Corp")


def test_party_name_requires_a_name() -> None:
    with pytest.raises(UblValidationError):
        party_name_of(_cac("PartyName", ()))


# ── cac:Contact ──────────────────────────────────────────────────────────


def test_contact_projects_with_its_leaf_fields() -> None:
    node = _cac(
        "Contact",
        (_leaf("Name", "Jane Doe"), _leaf("ElectronicMail", "jane@acme.example")),
    )

    assert contact_of(node) == Contact(name="Jane Doe", electronic_mail="jane@acme.example")


def test_contact_of_returns_none_for_a_missing_node() -> None:
    assert contact_of(None) is None


# ── cac:TaxScheme / cac:PartyTaxScheme ───────────────────────────────────


def test_tax_scheme_projects_with_its_id() -> None:
    node = _cac("TaxScheme", (_leaf("ID", "VAT"),))

    assert tax_scheme_of(node) == TaxScheme(id=Identifier("VAT"))


def test_party_tax_scheme_requires_a_tax_scheme() -> None:
    with pytest.raises(UblValidationError):
        party_tax_scheme_of(_cac("PartyTaxScheme", (_leaf("RegistrationName", "Acme"),)))


def test_party_tax_scheme_projects_with_registration_name_and_scheme() -> None:
    node = _cac(
        "PartyTaxScheme",
        (
            _leaf("RegistrationName", "Acme Corp Ltd"),
            _cac("TaxScheme", (_leaf("ID", "VAT"),)),
        ),
    )

    projected = party_tax_scheme_of(node)

    assert projected.registration_name == "Acme Corp Ltd"
    assert projected.tax_scheme == TaxScheme(id=Identifier("VAT"))


# ── cac:Party (the full aggregate) ──────────────────────────────────────


def _full_party_node() -> XmlNode:
    return _cac(
        "Party",
        (
            _cac("PartyIdentification", (_leaf("ID", "VAT-123"),)),
            _cac("PartyName", (_leaf("Name", "Acme Corp"),)),
            _cac(
                "PostalAddress",
                (
                    _leaf("StreetName", "1 Main St"),
                    _leaf("CityName", "Springfield"),
                    _leaf("PostalZone", "12345"),
                    _cac("Country", (_leaf("IdentificationCode", "US"),)),
                ),
            ),
            _cac(
                "PartyTaxScheme",
                (
                    _leaf("RegistrationName", "Acme Corp Ltd"),
                    _cac("TaxScheme", (_leaf("ID", "VAT"),)),
                ),
            ),
            _cac(
                "Contact",
                (_leaf("Name", "Jane Doe"), _leaf("ElectronicMail", "jane@acme.example")),
            ),
        ),
    )


def test_party_projects_all_five_named_child_kinds() -> None:
    party = party_of(_full_party_node())

    assert party.party_identifications == (PartyIdentification(id=Identifier("VAT-123")),)
    assert party.party_names == (PartyName(name="Acme Corp"),)
    assert party.postal_address == PostalAddress(
        street_name="1 Main St",
        city_name="Springfield",
        postal_zone="12345",
        country=Country(identification_code=Code("US")),
    )
    assert party.party_tax_schemes[0].tax_scheme == TaxScheme(id=Identifier("VAT"))
    assert party.contact == Contact(name="Jane Doe", electronic_mail="jane@acme.example")


def test_an_empty_party_projects_with_all_absent_fields() -> None:
    party = party_of(_cac("Party", ()))

    assert party == Party()


def test_party_of_returns_none_for_a_missing_node() -> None:
    assert party_of(None) is None


def test_multiple_party_identifications_and_names_are_each_preserved() -> None:
    node = _cac(
        "Party",
        (
            _cac("PartyIdentification", (_leaf("ID", "A"),)),
            _cac("PartyIdentification", (_leaf("ID", "B"),)),
            _cac("PartyName", (_leaf("Name", "Legal Name"),)),
            _cac("PartyName", (_leaf("Name", "Trading Name"),)),
        ),
    )

    party = party_of(node)

    assert [p.id.value for p in party.party_identifications] == ["A", "B"]
    assert [n.name for n in party.party_names] == ["Legal Name", "Trading Name"]


# ── Through the real document pipeline ──────────────────────────────────


def _invoice_with_supplier_party(party_body: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{CBC}" xmlns:cac="{CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AccountingSupplierParty><cac:Party>{party_body}</cac:Party>"
        f"</cac:AccountingSupplierParty>"
        f"</Invoice>"
    ).encode()


def test_a_party_survives_a_real_document_round_trip() -> None:
    body = (
        "<cac:PartyName><cbc:Name>Acme Corp</cbc:Name></cac:PartyName>"
        "<cac:PostalAddress><cbc:CityName>Springfield</cbc:CityName></cac:PostalAddress>"
    )
    original = loads(_invoice_with_supplier_party(body))
    reloaded = loads(dumps(original))

    supplier = find(reloaded.root, "AccountingSupplierParty")
    party = party_of(find(supplier, "Party"))

    assert party.party_names == (PartyName(name="Acme Corp"),)
    assert party.postal_address == PostalAddress(city_name="Springfield")

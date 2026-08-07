"""cac:Party, cac:PostalAddress, and the aggregates they carry.

The contract names both explicitly:

  "cac:Party is an aggregate component type carrying party identification,
   names, postal addresses, tax schemes, and contacts as child elements"
  "cac:PostalAddress is an aggregate component type composed of street,
   city, postal zone, and country sub-elements"

Every field modeled here is grounded directly in the pinned OASIS UBL 2.3
release package's own vendored XSD (xsd/common/UBL-CommonAggregateComponents
-2.3.xsd, read from the ZIP itself, not a SAL-fact paraphrase or memory).
Scope is deliberately bounded to the leaf-level structure each element's
own complexType declares, matching this codebase's existing pattern for
comparable aggregates (e.g. `charges.FinancialAccount`): PostalAddress
models the 4 sub-elements the contract itself names (street, city, postal
zone, country) plus the `cac:Country` it references, out of the XSD type's
full ~28 optional fields; Party models its 5 named child-element kinds,
each as a thin leaf-level aggregate. Deeper nested structures the contract
does not separately name (e.g. `cac:RegistrationAddress` inside
`cac:PartyTaxScheme`, itself another PostalAddress) are not modeled, the
same honest-narrowing discipline already applied elsewhere in this package.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import UblValidationError
from .aggregates import _require
from .document import XmlNode
from .typed import code_of, find, find_all, identifier_of, local_name
from .values import Code, Identifier


def _text_or_none(node: XmlNode | None) -> str | None:
    return node.text.strip() if node is not None else None


@dataclass(frozen=True)
class Country:
    """`cac:Country` -- an ISO-coded country reference."""

    identification_code: Code | None = None
    name: str | None = None


@dataclass(frozen=True)
class PostalAddress:
    """`cac:PostalAddress` -- street, city, postal zone, and country."""

    street_name: str | None = None
    city_name: str | None = None
    postal_zone: str | None = None
    country: Country | None = None


@dataclass(frozen=True)
class PartyIdentification:
    """`cac:PartyIdentification` -- a single identifier for a party."""

    id: Identifier

    def __post_init__(self) -> None:
        _require(self.id, "cbc:ID", "cac:PartyIdentification")


@dataclass(frozen=True)
class PartyName:
    """`cac:PartyName` -- a single name a party is known by."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise UblValidationError("cac:PartyName requires a non-empty cbc:Name")


@dataclass(frozen=True)
class Contact:
    """`cac:Contact` -- a named point of contact for a party."""

    name: str | None = None
    telephone: str | None = None
    electronic_mail: str | None = None


@dataclass(frozen=True)
class TaxScheme:
    """`cac:TaxScheme` -- identifies a tax scheme (e.g. VAT)."""

    id: Identifier | None = None
    name: str | None = None
    tax_type_code: Code | None = None


@dataclass(frozen=True)
class PartyTaxScheme:
    """`cac:PartyTaxScheme` -- a party's registration under a tax scheme.
    `cac:RegistrationAddress` (itself another PostalAddress) is not modeled
    here -- see this module's own docstring for the scope rationale."""

    tax_scheme: TaxScheme
    registration_name: str | None = None
    company_id: str | None = None

    def __post_init__(self) -> None:
        _require(self.tax_scheme, "cac:TaxScheme", "cac:PartyTaxScheme")


@dataclass(frozen=True)
class Party:
    """`cac:Party` -- identification, names, postal addresses, tax
    schemes, and a contact."""

    party_identifications: tuple[PartyIdentification, ...] = ()
    party_names: tuple[PartyName, ...] = ()
    postal_address: PostalAddress | None = None
    party_tax_schemes: tuple[PartyTaxScheme, ...] = ()
    contact: Contact | None = None


def country_of(node: XmlNode | None) -> Country | None:
    if node is None:
        return None
    code = find(node, "IdentificationCode")
    return Country(
        identification_code=code_of(code) if code is not None else None,
        name=_text_or_none(find(node, "Name")),
    )


def postal_address_of(node: XmlNode | None) -> PostalAddress | None:
    if node is None:
        return None
    return PostalAddress(
        street_name=_text_or_none(find(node, "StreetName")),
        city_name=_text_or_none(find(node, "CityName")),
        postal_zone=_text_or_none(find(node, "PostalZone")),
        country=country_of(find(node, "Country")),
    )


def party_identification_of(node: XmlNode) -> PartyIdentification:
    identifier = find(node, "ID")
    if identifier is None:
        raise UblValidationError(
            f"<{local_name(node.qname)}> has no cbc:ID"
        )
    return PartyIdentification(id=identifier_of(identifier))


def party_name_of(node: XmlNode) -> PartyName:
    name = find(node, "Name")
    if name is None:
        raise UblValidationError(f"<{local_name(node.qname)}> has no cbc:Name")
    return PartyName(name=name.text.strip())


def contact_of(node: XmlNode | None) -> Contact | None:
    if node is None:
        return None
    return Contact(
        name=_text_or_none(find(node, "Name")),
        telephone=_text_or_none(find(node, "Telephone")),
        electronic_mail=_text_or_none(find(node, "ElectronicMail")),
    )


def tax_scheme_of(node: XmlNode | None) -> TaxScheme | None:
    if node is None:
        return None
    identifier = find(node, "ID")
    code = find(node, "TaxTypeCode")
    return TaxScheme(
        id=identifier_of(identifier) if identifier is not None else None,
        name=_text_or_none(find(node, "Name")),
        tax_type_code=code_of(code) if code is not None else None,
    )


def party_tax_scheme_of(node: XmlNode) -> PartyTaxScheme:
    scheme_node = find(node, "TaxScheme")
    scheme = tax_scheme_of(scheme_node)
    if scheme is None:
        raise UblValidationError(
            f"<{local_name(node.qname)}> has no cac:TaxScheme"
        )
    return PartyTaxScheme(
        tax_scheme=scheme,
        registration_name=_text_or_none(find(node, "RegistrationName")),
        company_id=_text_or_none(find(node, "CompanyID")),
    )


def party_of(node: XmlNode | None) -> Party | None:
    """Absent per `cac:Party`'s own optional cardinality wherever it is
    referenced (e.g. `cac:AccountingSupplierParty/cac:Party`)."""
    if node is None:
        return None
    return Party(
        party_identifications=tuple(
            party_identification_of(child) for child in find_all(node, "PartyIdentification")
        ),
        party_names=tuple(party_name_of(child) for child in find_all(node, "PartyName")),
        postal_address=postal_address_of(find(node, "PostalAddress")),
        party_tax_schemes=tuple(
            party_tax_scheme_of(child) for child in find_all(node, "PartyTaxScheme")
        ),
        contact=contact_of(find(node, "Contact")),
    )


__all__ = [
    "Contact",
    "Country",
    "Party",
    "PartyIdentification",
    "PartyName",
    "PartyTaxScheme",
    "PostalAddress",
    "TaxScheme",
    "contact_of",
    "country_of",
    "party_identification_of",
    "party_name_of",
    "party_of",
    "party_tax_scheme_of",
    "postal_address_of",
    "tax_scheme_of",
]

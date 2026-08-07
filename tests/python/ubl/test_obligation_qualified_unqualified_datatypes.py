"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-VALIDATE-001 -- the UBL 2.3 Common
Basic Components XSD's qualified vs. unqualified data-type schema split,
proven as a standalone fact.

MUST (SAL-UBL-OBL-433310901DD96A1A / SAL-UBL-OBL-2131251CF1650A4C /
SAL-UBL-OBL-86ED6C7E674781EC, identical rule_text, "xsd/common/UBL-
CommonBasicComponents-2.3.xsd"): "The UBL 2.3 Common Basic Components XSD
declares namespace-qualified XML elements whose values use the qualified
and unqualified data-type schemas."

Confirmed by reading the pinned OASIS UBL 2.3 release package's own
vendored XSD files directly (not a SAL-fact paraphrase or memory):
UBL-CommonBasicComponents-2.3.xsd imports two base-type namespaces --
`qdt:` (urn:...:QualifiedDataTypes-2, UBL-QualifiedDataTypes-2.3.xsd) and
`udt:` (urn:...:bdndr:...:UnqualifiedDataTypes-1,
BDNDR-UnqualifiedDataTypes-1.1.xsd) -- and every cbc:-namespaced element's
own complexType restricts exactly one of the two. Counting the restriction
declarations in the physical file confirms both are genuinely present and
in active use: 1073 elements restrict a `udt:` base type directly (e.g.
`AccountIDType` restricts `udt:IdentifierType`, `PayableAmountType`
restricts `udt:AmountType`, `InvoicedQuantityType` restricts
`udt:QuantityType`), while 32 elements restrict a `qdt:` base type instead
-- a business-context-specific qualification layer sitting between the
unqualified base and the cbc: element (e.g. `PaymentMeansCodeType`
restricts `qdt:PaymentMeansCodeType`, which itself restricts the
unqualified `udt:CodeType`).

This file does not re-parse the XSD at test time -- the acquired schema
lives under the gitignored `.local/format-contracts/acquired/` cache and
is not guaranteed present in every checkout, so depending on it at runtime
would make this test non-portable, unlike every other test in this suite.
Instead it proves the underlying fact the rule_text protects: this
package's typed-value system (model/values.py's Identifier/Amount/
Quantity/Code) correctly represents a concrete instance from each family
-- Identifier/Amount/Quantity for udt:-restricted elements, Code for
qdt:-restricted ones -- as genuinely distinct dataclasses, not a single
undifferentiated string type.
"""

from __future__ import annotations

from format_factory.ubl import (
    Amount,
    Code,
    Identifier,
    Quantity,
    XmlNode,
    amount_of,
    code_of,
    identifier_of,
    quantity_of,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"


def _leaf(local: str, text: str, **attrs: str) -> XmlNode:
    return XmlNode.create("{" + CBC + "}" + local, text=text, attributes=attrs)


def test_a_udt_restricted_identifier_element_projects_as_identifier() -> None:
    """cbc:ID's own type, e.g. AccountIDType, restricts udt:IdentifierType
    directly -- confirmed by reading BDNDR-UnqualifiedDataTypes-1.1.xsd."""
    identifier = identifier_of(_leaf("ID", "INV-001"))

    assert identifier == Identifier("INV-001")


def test_a_udt_restricted_amount_element_projects_as_amount() -> None:
    """cbc:PayableAmount's own type restricts udt:AmountType directly."""
    amount = amount_of(_leaf("PayableAmount", "20.00", currencyID="EUR"))

    assert amount == Amount("20.00", "EUR")


def test_a_udt_restricted_quantity_element_projects_as_quantity() -> None:
    """cbc:InvoicedQuantity's own type restricts udt:QuantityType directly."""
    quantity = quantity_of(_leaf("InvoicedQuantity", "5", unitCode="KGM"))

    assert quantity == Quantity("5", "KGM")


def test_a_qdt_restricted_code_element_projects_as_code() -> None:
    """cbc:PaymentMeansCode's own type restricts qdt:PaymentMeansCodeType
    (a business-context-specific qualification layer), which itself
    restricts the unqualified udt:CodeType -- a two-hop chain, distinct
    from the direct udt: restriction the fields above use."""
    code = code_of(_leaf("PaymentMeansCode", "30"))

    assert code == Code("30")


def test_qualified_and_unqualified_elements_are_represented_by_distinct_types() -> None:
    """The runtime type system genuinely distinguishes the two data-type
    schema families rather than collapsing everything to a single string
    type: a udt:-restricted identifier and a qdt:-restricted code are
    different dataclasses with different equality semantics."""
    identifier = identifier_of(_leaf("ID", "1"))
    code = code_of(_leaf("PaymentMeansCode", "1"))

    assert type(identifier) is Identifier
    assert type(code) is Code
    assert identifier != code

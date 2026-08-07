"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 -- cardinality validation, extended to InvoiceLine/
TaxSubtotal/TaxTotal/LegalMonetaryTotal.

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates):
"UBL document schemas are W3C XML Schema definitions and conforming
documents must be valid against the maindoc schema of their declared
type."

This extends the cardinality-validation slice (already proven for
cac:Party/cac:PostalAddress/cac:Contact/cac:PaymentMeans/
cac:PayeeFinancialAccount/cac:CreditNoteLine/cac:Response/
cac:DocumentReference) to model/aggregates.py's InvoiceLine, TaxSubtotal,
TaxTotal, and LegalMonetaryTotal -- the package's original, most-
established typed components. Every field's exact cardinality is read
directly from the pinned OASIS UBL 2.3 CommonAggregateComponents schema
(InvoiceLineType, TaxSubtotalType, TaxTotalType, and MonetaryTotalType --
the real complexType name behind cac:LegalMonetaryTotal, confirmed
directly rather than assumed from the element name -- read from the
pinned release ZIP).

TaxTotal.subtotals (cac:TaxSubtotal) is deliberately excluded from
TaxTotal's own check even though it is a modeled field: the schema
declares it minOccurs=0 maxOccurs=UNBOUNDED, matching the model's own
tuple[TaxSubtotal, ...] field exactly -- genuinely repeatable, proven
directly below, not a violation candidate.

model/aggregates.py's Item.identifiers/classification_codes are
deliberately NOT covered by this slice: ItemType's own schema has no
direct cbc:ID or cbc:CommodityClassification child at all, a genuinely
separate and unresolved question about whether those model fields
correspond to the real schema, out of scope for a cardinality-only tick.
"""

from __future__ import annotations

from format_factory.ubl import XmlNode, loads, validate

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


# ── cac:InvoiceLine: ID/InvoicedQuantity/LineExtensionAmount/Item are each
#    maxOccurs=1 in InvoiceLineType ─────────────────────────────────────────


def test_an_invoice_line_with_a_single_id_validates_cleanly() -> None:
    body = "<cac:InvoiceLine><cbc:ID>L1</cbc:ID></cac:InvoiceLine>"

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_an_invoice_line_with_two_ids_is_a_cardinality_violation() -> None:
    body = "<cac:InvoiceLine><cbc:ID>L1</cbc:ID><cbc:ID>L2</cbc:ID></cac:InvoiceLine>"

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_an_invoice_line_with_two_line_extension_amounts_is_a_cardinality_violation() -> None:
    body = (
        "<cac:InvoiceLine><cbc:ID>L1</cbc:ID>"
        "<cbc:LineExtensionAmount>10</cbc:LineExtensionAmount>"
        "<cbc:LineExtensionAmount>20</cbc:LineExtensionAmount>"
        "</cac:InvoiceLine>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


# ── cac:TaxSubtotal: TaxableAmount/TaxAmount/TaxCategory are each
#    maxOccurs=1 in TaxSubtotalType ─────────────────────────────────────────


def test_a_tax_subtotal_with_two_tax_categories_is_a_cardinality_violation() -> None:
    body = (
        "<cac:TaxSubtotal>"
        "<cbc:TaxAmount>5</cbc:TaxAmount>"
        "<cac:TaxCategory><cbc:ID>S</cbc:ID></cac:TaxCategory>"
        "<cac:TaxCategory><cbc:ID>Z</cbc:ID></cac:TaxCategory>"
        "</cac:TaxSubtotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_tax_subtotal_with_one_of_each_field_validates_cleanly() -> None:
    body = (
        "<cac:TaxSubtotal>"
        "<cbc:TaxableAmount>100</cbc:TaxableAmount>"
        "<cbc:TaxAmount>5</cbc:TaxAmount>"
        "<cac:TaxCategory><cbc:ID>S</cbc:ID></cac:TaxCategory>"
        "</cac:TaxSubtotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


# ── cac:TaxTotal: TaxAmount is maxOccurs=1; TaxSubtotal is repeatable ──────


def test_a_tax_total_with_two_tax_amounts_is_a_cardinality_violation() -> None:
    body = "<cac:TaxTotal><cbc:TaxAmount>10</cbc:TaxAmount><cbc:TaxAmount>20</cbc:TaxAmount></cac:TaxTotal>"

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_tax_total_with_multiple_tax_subtotals_is_not_a_violation_the_schema_declares_them_repeatable() -> None:
    """cac:TaxSubtotal is minOccurs=0 maxOccurs=UNBOUNDED in TaxTotalType --
    genuinely different from cbc:TaxAmount's maxOccurs=1, proven directly
    rather than assumed uniform, and matches the model's own
    tuple[TaxSubtotal, ...] field."""
    body = (
        "<cac:TaxTotal><cbc:TaxAmount>15</cbc:TaxAmount>"
        "<cac:TaxSubtotal><cbc:TaxAmount>5</cbc:TaxAmount></cac:TaxSubtotal>"
        "<cac:TaxSubtotal><cbc:TaxAmount>10</cbc:TaxAmount></cac:TaxSubtotal>"
        "</cac:TaxTotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


# ── cac:LegalMonetaryTotal: all 6 checked fields are maxOccurs=1 in
#    MonetaryTotalType (the real complexType behind this element name) ─────


def test_a_legal_monetary_total_with_one_of_each_field_validates_cleanly() -> None:
    body = (
        "<cac:LegalMonetaryTotal>"
        "<cbc:LineExtensionAmount>100</cbc:LineExtensionAmount>"
        "<cbc:PayableAmount>100</cbc:PayableAmount>"
        "</cac:LegalMonetaryTotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is True


def test_a_legal_monetary_total_with_two_payable_amounts_is_a_cardinality_violation() -> None:
    body = (
        "<cac:LegalMonetaryTotal>"
        "<cbc:LineExtensionAmount>100</cbc:LineExtensionAmount>"
        "<cbc:PayableAmount>100</cbc:PayableAmount>"
        "<cbc:PayableAmount>200</cbc:PayableAmount>"
        "</cac:LegalMonetaryTotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_legal_monetary_total_with_two_tax_exclusive_amounts_is_a_cardinality_violation() -> None:
    body = (
        "<cac:LegalMonetaryTotal>"
        "<cbc:LineExtensionAmount>100</cbc:LineExtensionAmount>"
        "<cbc:PayableAmount>100</cbc:PayableAmount>"
        "<cbc:TaxExclusiveAmount>90</cbc:TaxExclusiveAmount>"
        "<cbc:TaxExclusiveAmount>95</cbc:TaxExclusiveAmount>"
        "</cac:LegalMonetaryTotal>"
    )

    report = validate(loads(_invoice_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)

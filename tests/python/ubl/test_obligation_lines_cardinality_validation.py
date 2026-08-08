"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 -- cardinality validation, extended to CreditNoteLine/
Response/DocumentReference.

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates):
"UBL document schemas are W3C XML Schema definitions and conforming
documents must be valid against the maindoc schema of their declared
type."

This extends the cardinality-validation slice (already proven for
cac:Party/cac:PostalAddress/cac:Contact/cac:PaymentMeans/
cac:PayeeFinancialAccount) to cac:CreditNoteLine, cac:Response, and
cac:DocumentReference -- model/lines.py's other already-typed aggregate
components. Every field's exact cardinality is read directly from the
pinned OASIS UBL 2.3 CommonAggregateComponents schema
(CreditNoteLineType, ResponseType, DocumentReferenceType complexTypes,
read from the pinned release ZIP).

ResponseType.Description is deliberately excluded even though it is a
modeled field: the schema declares it minOccurs=0 maxOccurs=UNBOUNDED
(genuinely repeatable), unlike ResponseCode, which is maxOccurs=1 --
proven directly below, not merely assumed, the same discipline already
applied to PaymentMeans.PaymentID in the prior slice.
"""

from __future__ import annotations

from format_factory.ubl import XmlNode, loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _credit_note_with(body: str) -> bytes:
    return (
        f'<CreditNote xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>CN-001</cbc:ID>"
        f"{body}"
        f"</CreditNote>"
    ).encode()


# ── cac:CreditNoteLine: ID/CreditedQuantity/LineExtensionAmount/Item are
#    each maxOccurs=1 in the schema ─────────────────────────────────────────


def test_a_credit_note_line_with_a_single_id_validates_cleanly() -> None:
    body = "<cac:CreditNoteLine><cbc:ID>L1</cbc:ID></cac:CreditNoteLine>"

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is True


def test_a_credit_note_line_with_two_ids_is_a_cardinality_violation() -> None:
    body = "<cac:CreditNoteLine><cbc:ID>L1</cbc:ID><cbc:ID>L2</cbc:ID></cac:CreditNoteLine>"

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_credit_note_line_missing_its_id_is_a_missing_mandatory_field_violation() -> None:
    """ID is minOccurs="1" in CreditNoteLineType (FF6-EVENT-000339) -- unlike
    CreditedQuantity/LineExtensionAmount/Item, all minOccurs="0" there,
    confirmed directly and NOT assumed symmetric with InvoiceLineType,
    where LineExtensionAmount/Item are mandatory instead."""
    body = "<cac:CreditNoteLine><cbc:CreditedQuantity>1</cbc:CreditedQuantity></cac:CreditNoteLine>"

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is False
    assert any(
        item.code == "ubl.cardinality.missing" and "'ID'" in item.message
        for item in report.diagnostics
    )


def test_a_credit_note_line_missing_its_optional_line_extension_amount_is_not_a_violation() -> None:
    """LineExtensionAmount is minOccurs="0" in CreditNoteLineType --
    confirmed directly, not assumed -- unlike InvoiceLine's own
    otherwise-identically-named field, which IS mandatory."""
    body = "<cac:CreditNoteLine><cbc:ID>L1</cbc:ID></cac:CreditNoteLine>"

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is True


def test_a_credit_note_line_with_two_credited_quantities_is_a_cardinality_violation() -> None:
    body = (
        "<cac:CreditNoteLine><cbc:ID>L1</cbc:ID>"
        "<cbc:CreditedQuantity>1</cbc:CreditedQuantity>"
        "<cbc:CreditedQuantity>2</cbc:CreditedQuantity>"
        "</cac:CreditNoteLine>"
    )

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


# ── cac:Response: ResponseCode is maxOccurs=1; Description is repeatable ───


def test_a_response_with_a_single_response_code_validates_cleanly() -> None:
    body = "<cac:Response><cbc:ResponseCode>AB</cbc:ResponseCode></cac:Response>"

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is True


def test_a_response_with_two_response_codes_is_a_cardinality_violation() -> None:
    body = (
        "<cac:Response>"
        "<cbc:ResponseCode>AB</cbc:ResponseCode>"
        "<cbc:ResponseCode>AP</cbc:ResponseCode>"
        "</cac:Response>"
    )

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_response_with_multiple_descriptions_is_not_a_violation_the_schema_declares_it_repeatable() -> None:
    """Description is minOccurs=0 maxOccurs=UNBOUNDED in ResponseType --
    genuinely different from ResponseCode's maxOccurs=1, proven directly
    rather than assumed uniform."""
    body = (
        "<cac:Response>"
        "<cbc:Description>first note</cbc:Description>"
        "<cbc:Description>second note</cbc:Description>"
        "</cac:Response>"
    )

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is True


# ── cac:DocumentReference: ID/DocumentTypeCode are each maxOccurs=1 ────────


def test_a_document_reference_with_two_document_type_codes_is_a_cardinality_violation() -> None:
    body = (
        "<cac:BillingReference><cac:DocumentReference>"
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:DocumentTypeCode>380</cbc:DocumentTypeCode>"
        "<cbc:DocumentTypeCode>381</cbc:DocumentTypeCode>"
        "</cac:DocumentReference></cac:BillingReference>"
    )

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_document_reference_with_one_of_each_field_validates_cleanly() -> None:
    body = (
        "<cac:BillingReference><cac:DocumentReference>"
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:DocumentTypeCode>380</cbc:DocumentTypeCode>"
        "</cac:DocumentReference></cac:BillingReference>"
    )

    report = validate(loads(_credit_note_with(body)))

    assert report.is_valid is True
